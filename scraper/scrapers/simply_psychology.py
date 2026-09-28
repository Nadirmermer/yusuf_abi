import re
from typing import List
from bs4 import BeautifulSoup
from models.article import Article, ArticleSection, ArticleImage
from scrapers.base import BaseScraper
from scrapers.network import NetworkResponse

class SimplyPsychologyScraper(BaseScraper):
    source_name = "Simply Psychology"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "simplypsychology.org" in url.lower()

    def parse(self, response: NetworkResponse) -> Article:
        if response.is_markdown:
            article = self.parse_jina_markdown(response.text, response.url)
            article.source = self.source_name
            return article

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Başlık
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "")

        # 2. Yazar ve Tarih
        author = None
        published_date = None
        author_elem = soup.find("a", class_=re.compile(r"author|byline", re.I)) or soup.find("span", class_=re.compile(r"author", re.I))
        if author_elem:
            author = author_elem.get_text(strip=True)

        time_elem = soup.find("time")
        if time_elem:
            published_date = time_elem.get("datetime") or time_elem.get_text(strip=True)

        # 3. Görseller
        images: List[ArticleImage] = []
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            images.append(ArticleImage(url=og_img.get("content"), alt=title, caption="Header Image"))

        # 4. Makale Gövdesi
        article_elem = soup.find("article") or soup.find("div", class_="entry-content") or soup.find("main")
        
        sections: List[ArticleSection] = []
        key_points: List[str] = []
        summary = ""

        if article_elem:
            # İstenmeyen reklam veya yan panel öğelerini temizle
            for unwanted in article_elem.find_all(["div", "section"], class_=re.compile(r"ad-|sidebar|nav|related|sharing", re.I)):
                unwanted.decompose()

            # Görselleri topla
            for img in article_elem.find_all("img"):
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                if src and not any(bad in src.lower() for bad in ["icon", "logo", "avatar", "ad-", "gravatar"]):
                    alt = img.get("alt", "")
                    if not any(existing.url == src for existing in images):
                        images.append(ArticleImage(url=src, alt=alt))

            # Key Takeaways kutusu var mı kontrol et
            takeaways_box = article_elem.find(lambda tag: tag.name in ["div", "aside"] and "takeaway" in (tag.get("class", []) or tag.get("id", "")))
            if takeaways_box:
                for li in takeaways_box.find_all("li"):
                    key_points.append(li.get_text(strip=True))

            # Başlıklar ve paragraflar
            current_heading = "Giriş"
            current_paragraphs: List[str] = []
            order = 1

            for child in article_elem.find_all(["h2", "h3", "p", "ul", "ol"]):
                if child.name in ["h2", "h3"]:
                    if current_paragraphs:
                        sec_text = "\n\n".join(current_paragraphs).strip()
                        if not summary and order == 1:
                            summary = current_paragraphs[0]
                        sections.append(ArticleSection(
                            heading=current_heading,
                            content=sec_text,
                            order=order
                        ))
                        order += 1
                        current_paragraphs = []
                    current_heading = child.get_text(strip=True)
                    # Numaralı veya öne çıkan başlıklar
                    if re.match(r'^(?:\d+[\.\)]|The\s+[A-Z]+)', current_heading):
                        if current_heading not in key_points:
                            key_points.append(current_heading)
                elif child.name == "p":
                    p_text = child.get_text(strip=True)
                    if len(p_text) > 20 and p_text not in current_paragraphs:
                        current_paragraphs.append(p_text)
                elif child.name in ["ul", "ol"]:
                    for li in child.find_all("li"):
                        li_t = li.get_text(strip=True)
                        if len(li_t) > 10:
                            current_paragraphs.append(f"- {li_t}")

            if current_paragraphs:
                sections.append(ArticleSection(
                    heading=current_heading,
                    content="\n\n".join(current_paragraphs).strip(),
                    order=order
                ))

        # Raw Markdown
        raw_markdown = f"# {title}\n\n"
        if summary:
            raw_markdown += f"> {summary}\n\n"
        if key_points:
            raw_markdown += "### Önemli Noktalar / Metotlar\n"
            for kp in key_points:
                raw_markdown += f"- {kp}\n"
            raw_markdown += "\n"
        for s in sections:
            raw_markdown += f"## {s.heading}\n\n{s.content}\n\n"

        return Article(
            url=response.url,
            source=self.source_name,
            title=title or "Simply Psychology Article",
            author=author,
            published_date=published_date,
            summary=summary,
            key_points=key_points,
            sections=sections,
            images=images,
            raw_markdown=raw_markdown
        )
