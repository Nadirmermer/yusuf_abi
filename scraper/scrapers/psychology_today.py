import json
import re
from typing import List
from bs4 import BeautifulSoup
from models.article import Article, ArticleSection, ArticleImage
from scrapers.base import BaseScraper
from scrapers.network import NetworkResponse

class PsychologyTodayScraper(BaseScraper):
    source_name = "Psychology Today"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "psychologytoday.com" in url.lower()

    def parse(self, response: NetworkResponse) -> Article:
        # URL'den blog adını çıkar (Örn: /blog/unhitched/...)
        blog_match = re.search(r'/blog/([a-zA-Z0-9\-]+)/', response.url)
        blog_name = blog_match.group(1) if blog_match else None

        if response.is_markdown:
            article = self.parse_jina_markdown(response.text, response.url)
            article.source = self.source_name
            article.blog_name = blog_name
            self._refine_psychology_today(article, response.text)
            return article

        # HTML parsing
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Başlık
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "")
        elif soup.title:
            title = soup.title.get_text(strip=True).split("|")[0].strip()

        # 2. Yazar, Unvan, Hakem, Tarihler, Konular (JSON-LD ve Meta)
        author = None
        author_title = None
        reviewer = None
        published_date = None
        date_modified = None
        summary = None
        topics = []
        
        json_ld_script = soup.find("script", type="application/ld+json")
        if json_ld_script and json_ld_script.string:
            try:
                data = json.loads(json_ld_script.string)
                graph = data.get("@graph", [data])
                for item in graph:
                    if item.get("@type") in ["NewsArticle", "BlogPosting", "Article"]:
                        if not title and item.get("headline"):
                            title = item.get("headline")
                        if item.get("description"):
                            summary = item.get("description")
                        if item.get("datePublished"):
                            published_date = item.get("datePublished")
                        if item.get("dateModified"):
                            date_modified = item.get("dateModified")
                        
                        # Yazar ve unvan
                        if item.get("author"):
                            auth_data = item.get("author")
                            if isinstance(auth_data, dict):
                                author = auth_data.get("name")
                                author_title = auth_data.get("honorificSuffix")
                            elif isinstance(auth_data, list) and auth_data:
                                author = auth_data[0].get("name")
                                author_title = auth_data[0].get("honorificSuffix")
                        
                        # Editör / Hakem
                        if item.get("editor"):
                            ed_data = item.get("editor")
                            if isinstance(ed_data, dict):
                                reviewer = f"Reviewed by {ed_data.get('name')}"
                            elif isinstance(ed_data, str):
                                reviewer = f"Reviewed by {ed_data}"

                        # Konu / About
                        if item.get("about"):
                            about_data = item.get("about")
                            if isinstance(about_data, dict):
                                topics.append(about_data.get("name", "").strip())
                            elif isinstance(about_data, list):
                                for ab in about_data:
                                    if isinstance(ab, dict):
                                        topics.append(ab.get("name", "").strip())
                        break
            except Exception:
                pass

        if not summary:
            meta_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                summary = meta_desc.get("content", "").strip()

        # 3. Görseller (Kapak görseli ayrımıyla)
        images: List[ArticleImage] = []
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            images.append(ArticleImage(url=og_image.get("content"), alt=title, caption="Cover Image", is_cover=True))

        # 4. Makale Gövdesi ve Bölümleri
        content_div = (
            soup.find("div", class_=re.compile(r"blog-entry__body|article__body|field--name-body"))
            or soup.find("article")
            or soup.find("main")
        )
        
        sections: List[ArticleSection] = []
        key_points: List[str] = []

        if content_div:
            # Görselleri gövdeden topla
            for img in content_div.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src and not any(bad in src.lower() for bad in ["icon", "logo", "avatar", "ad-", "pixel"]):
                    alt = img.get("alt", "")
                    if not any(existing.url == src for existing in images):
                        images.append(ArticleImage(url=src, alt=alt, is_cover=False))

            current_heading = "Giriş"
            current_paragraphs: List[str] = []
            order = 1

            for elem in content_div.children:
                if elem.name in ["h2", "h3", "h4"]:
                    if current_paragraphs:
                        sections.append(ArticleSection(
                            heading=current_heading,
                            content="\n\n".join(current_paragraphs).strip(),
                            order=order
                        ))
                        order += 1
                        current_paragraphs = []
                    current_heading = elem.get_text(strip=True)
                    if re.match(r'^\d+[\.\)]\s+', current_heading):
                        key_points.append(current_heading)
                elif elem.name in ["p", "ul", "ol"]:
                    text = elem.get_text(strip=True)
                    if text:
                        # Bold madde kontrolü: **1. ...**
                        bold_match = re.match(r'^\*\*(?:\d+[\.\)]|[A-Z\d]+[\.\)])\s*([^*]+)\*\*', text)
                        if bold_match:
                            key_points.append(bold_match.group(1).strip())
                        current_paragraphs.append(text)
                        if elem.name in ["ul", "ol"]:
                            for li in elem.find_all("li"):
                                li_text = li.get_text(strip=True)
                                if len(li_text) > 5:
                                    key_points.append(li_text)

            if current_paragraphs:
                sections.append(ArticleSection(
                    heading=current_heading,
                    content="\n\n".join(current_paragraphs).strip(),
                    order=order
                ))

        raw_markdown = f"# {title}\n\n"
        if summary:
            raw_markdown += f"> {summary}\n\n"
        for s in sections:
            raw_markdown += f"## {s.heading}\n\n{s.content}\n\n"

        article = Article(
            url=response.url,
            source=self.source_name,
            blog_name=blog_name,
            title=title or "Psychology Today Article",
            author=author,
            author_title=author_title,
            reviewer=reviewer,
            published_date=published_date,
            date_modified=date_modified,
            summary=summary,
            topics=[t for t in topics if t],
            key_points=key_points,
            sections=sections,
            images=images,
            raw_markdown=raw_markdown
        )
        self._refine_psychology_today(article, response.text)
        return article

    def _refine_psychology_today(self, article: Article, raw_text: str) -> None:
        """Markdown metninden ek metaverileri (reviewer, author, topics) zenginleştirir."""
        # Reviewer tespiti (Örn: Reviewed by Devon Frye)
        if not article.reviewer:
            rev_match = re.search(r'\[Reviewed by\s+([^\]]+)\]', raw_text)
            if rev_match:
                article.reviewer = f"Reviewed by {rev_match.group(1).strip()}"

        # Yazar tespiti
        if not article.author:
            auth_match = re.search(r'Image \d+:\s+([A-Za-z\s\.\,\-]+(?:Ph\.D\.|MSc|MD|LICSW|PsyD))', raw_text)
            if auth_match:
                article.author = auth_match.group(1).strip()

        # Kapak görselini işaretle
        if article.images and not any(img.is_cover for img in article.images):
            # field_blog_entry_images veya teaser_image genellikle kapaktır
            for img in article.images:
                if "field_blog_entry" in img.url or "teaser_image" in img.url or "unsplash" in img.url or "pexels" in img.url:
                    img.is_cover = True
                    break

        # Numaralı başlıklar veya bold maddeler key_points listesine alınmamışsa
        if not article.key_points:
            for s in article.sections:
                if re.match(r'^\d+[\.\)]\s+', s.heading):
                    article.key_points.append(s.heading)
