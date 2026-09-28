import re
from typing import List, Dict
from bs4 import BeautifulSoup
from models.article import Article, ArticleSection, ArticleImage
from scrapers.base import BaseScraper
from scrapers.network import NetworkResponse, network_client

class TheDecisionLabScraper(BaseScraper):
    source_name = "The Decision Lab"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "thedecisionlab.com" in url.lower()

    def parse(self, response: NetworkResponse) -> Article:
        if response.is_markdown:
            article = self.parse_jina_markdown(response.text, response.url)
            article.source = self.source_name
            return article

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Başlık ve Alt Başlık
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "")

        subtitle = None
        sub_elem = soup.find("h2", class_=re.compile(r"sub|subtitle|lead", re.I))
        if sub_elem:
            subtitle = sub_elem.get_text(strip=True)

        # 2. Yazar ve Özet
        author = None
        author_elem = soup.find("a", href=re.compile(r"/contributors/|/author/", re.I))
        if author_elem:
            author = author_elem.get_text(strip=True)

        meta_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        summary = meta_desc.get("content", "").strip() if meta_desc else None

        # 3. Görseller
        images: List[ArticleImage] = []
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            images.append(ArticleImage(url=og_img.get("content"), alt=title, caption="Header Image"))

        # 4. Gövde ve Bölümler
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|body", re.I))
        
        sections: List[ArticleSection] = []
        key_points: List[str] = []

        if main_content:
            # Görselleri topla
            for img in main_content.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src and not any(bad in src.lower() for bad in ["icon", "logo", "avatar", "analytics"]):
                    alt = img.get("alt", "")
                    if not any(existing.url == src for existing in images):
                        images.append(ArticleImage(url=src, alt=alt))

            current_heading = "Giriş"
            current_paragraphs: List[str] = []
            order = 1

            for child in main_content.find_all(["h2", "h3", "p", "ul", "ol"]):
                if child.name in ["h2", "h3"]:
                    if current_paragraphs:
                        sections.append(ArticleSection(
                            heading=current_heading,
                            content="\n\n".join(current_paragraphs).strip(),
                            order=order
                        ))
                        order += 1
                        current_paragraphs = []
                    current_heading = child.get_text(strip=True)
                    key_points.append(current_heading)
                elif child.name == "p":
                    p_text = child.get_text(strip=True)
                    if len(p_text) > 20:
                        current_paragraphs.append(p_text)
                elif child.name in ["ul", "ol"]:
                    for li in child.find_all("li"):
                        li_text = li.get_text(strip=True)
                        if len(li_text) > 10:
                            current_paragraphs.append(f"- {li_text}")

            if current_paragraphs:
                sections.append(ArticleSection(
                    heading=current_heading,
                    content="\n\n".join(current_paragraphs).strip(),
                    order=order
                ))

        # Raw Markdown
        raw_markdown = f"# {title}\n\n"
        if subtitle:
            raw_markdown += f"**{subtitle}**\n\n"
        if summary:
            raw_markdown += f"> {summary}\n\n"
        for s in sections:
            raw_markdown += f"## {s.heading}\n\n{s.content}\n\n"

        return Article(
            url=response.url,
            source=self.source_name,
            title=title or "The Decision Lab Article",
            subtitle=subtitle,
            author=author,
            summary=summary,
            key_points=key_points[:10],
            sections=sections,
            images=images,
            raw_markdown=raw_markdown
        )

    @classmethod
    def extract_biases_links(cls, index_url: str = "https://thedecisionlab.com/biases") -> List[Dict[str, str]]:
        """
        The Decision Lab Biases sayfasındaki tüm bilişsel önyargı makalelerinin bağlantılarını çeker.
        """
        resp = network_client.fetch(index_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        biases = []
        base_url = "https://thedecisionlab.com"

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            name = a.get_text(strip=True)
            if "/biases/" in href and not href.endswith("/biases") and not href.endswith("/biases/"):
                full_url = href if href.startswith("http") else base_url + href
                if not any(b["url"] == full_url for b in biases) and len(name) > 2:
                    biases.append({
                        "name": name,
                        "url": full_url
                    })
        return biases
