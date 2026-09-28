import re
from typing import List, Dict
from bs4 import BeautifulSoup
from models.article import Article, ArticleSection
from scrapers.base import BaseScraper
from scrapers.network import NetworkResponse, network_client

class ChangingMindsScraper(BaseScraper):
    source_name = "Changing Minds"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "changingminds.org" in url.lower()

    def parse(self, response: NetworkResponse) -> Article:
        soup = BeautifulSoup(response.text, "html.parser")

        # Başlık tespiti
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # Gereksiz menü ve header kısımlarını temizle
        for unwanted in soup.find_all(["script", "style", "nav", "footer"]):
            unwanted.decompose()

        # Standart Changing Minds bölümleri: Description, Example, So What?, See also
        sections: List[ArticleSection] = []
        key_points: List[str] = []

        # Paragrafları ve h2/h3 başlıkları tara
        # changingminds tablolar veya standart p/h2 kullanır
        headings = soup.find_all(["h2", "h3", "p", "td"])
        
        current_section = "Description"
        section_texts: Dict[str, List[str]] = {
            "Description": [],
            "Example": [],
            "So What?": [],
            "Notes": []
        }

        # Bilinen anahtar kelimeler
        known_sections = ["description", "example", "so what", "so what?", "see also", "references", "research"]

        body_text = ""
        # Ana metin alanını bul
        for elem in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            text = elem.get_text(" ", strip=True)
            if not text:
                continue

            clean_lower = text.lower().strip()
            # Bölüm geçişi kontrolü
            matched_section = None
            for ks in known_sections:
                if clean_lower == ks or clean_lower.startswith(ks + " :") or clean_lower.startswith(ks + " -"):
                    matched_section = ks.title()
                    break

            if matched_section:
                current_section = matched_section
                continue

            # Menü bağlantılarını atla
            if any(skip in text.lower() for skip in ["how we change what others think", "| menu |", "quick | books"]):
                continue

            if current_section not in section_texts:
                section_texts[current_section] = []

            section_texts[current_section].append(text)

        order = 1
        summary = ""
        for sec_name, paragraphs in section_texts.items():
            if paragraphs:
                content = "\n\n".join(paragraphs).strip()
                # Çok kısa ve anlamsız bölümleri filtrele
                if len(content) > 15:
                    sections.append(ArticleSection(
                        heading=sec_name,
                        content=content,
                        order=order
                    ))
                    order += 1
                    if sec_name.lower() == "description" and not summary:
                        summary = paragraphs[0]
                    if sec_name.lower() in ["example", "so what", "so what?"]:
                        key_points.append(f"{sec_name}: {paragraphs[0][:120]}...")

        # Raw Markdown oluştur
        raw_markdown = f"# {title}\n\n"
        if summary:
            raw_markdown += f"> {summary}\n\n"
        for s in sections:
            raw_markdown += f"## {s.heading}\n\n{s.content}\n\n"

        return Article(
            url=response.url,
            source=self.source_name,
            title=title or "Changing Minds Theory",
            summary=summary,
            key_points=key_points,
            sections=sections,
            raw_markdown=raw_markdown
        )

    @classmethod
    def extract_index_links(cls, index_url: str = "https://changingminds.org/explanations/theories/a_alphabetic.htm") -> List[Dict[str, str]]:
        """
        Changing Minds alfabe/teori fihrist sayfasındaki tüm teorileri ve linklerini listeler.
        """
        resp = network_client.fetch(index_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        theories = []
        base_url = "https://changingminds.org/explanations/theories/"
        
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            name = a.get_text(strip=True)
            if (
                href.endswith(".htm") 
                and not href.startswith("http") 
                and not href.startswith("#")
                and not href.startswith("..")
                and not href.startswith("a_")  # a_alphabetic vs
                and len(name) > 2
            ):
                full_url = href if href.startswith("http") else base_url + href
                theories.append({
                    "name": name,
                    "url": full_url
                })
        return theories
