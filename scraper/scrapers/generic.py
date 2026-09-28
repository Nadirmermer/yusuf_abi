import re
from typing import List
from bs4 import BeautifulSoup
from models.article import Article, ArticleSection, ArticleImage
from scrapers.base import BaseScraper
from scrapers.network import NetworkResponse

class GenericScraper(BaseScraper):
    source_name = "Generic Web"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        # Tüm URL'ler için en son fallback olarak çalışır
        return True

    def parse(self, response: NetworkResponse) -> Article:
        if response.is_markdown:
            article = self.parse_jina_markdown(response.text, response.url)
            # Domain adından kaynak belirle
            domain = re.sub(r'^https?://(?:www\.)?', '', response.url).split('/')[0]
            article.source = domain.title()
            return article

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Başlık
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "")
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # 2. Yazar, Tarih ve Özet
        author = None
        author_elem = soup.find(class_=re.compile(r"author|byline", re.I))
        if author_elem:
            author = author_elem.get_text(strip=True)

        meta_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        summary = meta_desc.get("content", "").strip() if meta_desc else None

        # 3. Görseller
        images: List[ArticleImage] = []
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            images.append(ArticleImage(url=og_img.get("content"), alt=title, caption="Header Image"))

        # 4. Makale Gövdesi
        main_elem = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile(r"post|content|entry", re.I))
        if not main_elem:
            main_elem = soup.body

        sections: List[ArticleSection] = []
        key_points: List[str] = []

        if main_elem:
            for bad in main_elem.find_all(["nav", "footer", "script", "style", "aside"]):
                bad.decompose()

            current_heading = "Giriş"
            current_paragraphs: List[str] = []
            order = 1

            for child in main_elem.find_all(["h2", "h3", "p", "ul", "ol"]):
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
                elif child.name == "p":
                    p_text = child.get_text(strip=True)
                    if len(p_text) > 25:
                        current_paragraphs.append(p_text)
                elif child.name in ["ul", "ol"]:
                    for li in child.find_all("li"):
                        t = li.get_text(strip=True)
                        if len(t) > 10:
                            key_points.append(t)

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

        domain = re.sub(r'^https?://(?:www\.)?', '', response.url).split('/')[0]
        return Article(
            url=response.url,
            source=domain.title(),
            title=title or "Untitled",
            author=author,
            summary=summary,
            key_points=key_points[:10],
            sections=sections,
            images=images,
            raw_markdown=raw_markdown
        )
