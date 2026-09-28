from abc import ABC, abstractmethod
import re
from typing import List, Optional
from bs4 import BeautifulSoup
from models.article import Article, ArticleSection, ArticleImage
from scrapers.network import network_client, NetworkResponse

class BaseScraper(ABC):
    source_name: str = "Generic"

    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        """Bu scraper sınıfının verilen URL'yi işleyip işleyemeyeceğini döndürür."""
        pass

    def scrape(self, url: str, force_jina: bool = False) -> Article:
        """Belirtilen URL'yi çeker ve Article nesnesine dönüştürür."""
        response = network_client.fetch(url, force_jina=force_jina)
        article = self.parse(response)
        return article

    @abstractmethod
    def parse(self, response: NetworkResponse) -> Article:
        """Ağ yanıtını (HTML veya Jina Markdown) ayrıştırarak Article nesnesi üretir."""
        pass

    # --- Yardımcı Metotlar ---

    def parse_jina_markdown(self, markdown_text: str, url: str) -> Article:
        """
        Jina Reader çıktısından standart Article modeli çıkarır.
        Jina çıktısı genellikle şöyle başlar:
        Title: ...
        URL Source: ...
        Published Time: ...
        Markdown Content:
        ...
        """
        title = ""
        published_date = None
        
        # Meta başlıkları ayıkla
        lines = markdown_text.splitlines()
        content_start_idx = 0
        
        for i, line in enumerate(lines[:30]):
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Published Time:"):
                published_date = line.replace("Published Time:", "").strip()
            elif line.startswith("Markdown Content:"):
                content_start_idx = i + 1
                break

        body = "\n".join(lines[content_start_idx:]).strip()
        if not title:
            # Markdown içerisindeki ilk # başlığı ara
            h1_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            else:
                title = "Untitled Article"

        # Bölümleri ve maddeleri ayıkla
        sections: List[ArticleSection] = []
        key_points: List[str] = []
        images: List[ArticleImage] = []

        # Görselleri bul ![alt](url)
        img_matches = re.findall(r'!\[(.*?)\]\((https?://[^\s\)]+)\)', body)
        bad_image_patterns = [
            'icon', 'logo', 'pixel', 'avatar', 'ad-', 'cookie', 'flag', 
            'magazine', 'self-test', 'badge', 'widget', 'banner'
        ]
        for alt, img_url in img_matches:
            if not any(bad in img_url.lower() or bad in alt.lower() for bad in bad_image_patterns):
                if not any(existing.url == img_url for existing in images):
                    images.append(ArticleImage(url=img_url, alt=alt or None))

        # Markdown bölümlerini ayrıştır (#, ##, ###)
        section_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
        parts = section_pattern.split(body)

        summary = ""
        # İlk parça (başlıktan önceki kısım) özet/giriş olabilir
        if parts and parts[0].strip():
            raw_paragraphs = [
                p.strip() for p in parts[0].split("\n\n") 
                if p.strip() and not any(bad in p.lower() for bad in ["cookie", "privacy policy", "do not sell", "subscribe", "terms of use"])
            ]
            if raw_paragraphs:
                summary = raw_paragraphs[0]

        # parts: [preamble, hashes, heading, body, hashes, heading, body...]
        order = 1
        for i in range(1, len(parts), 3):
            if i + 2 <= len(parts):
                heading = parts[i + 1].strip()
                content = parts[i + 2].strip()
                
                # İçerikten maddeleri ayıkla (1. Madde veya - Madde veya **1. Madde**)
                items = []
                for line in content.splitlines():
                    clean_l = line.strip()
                    # **1. Başlık** veya 1. Başlık kontrolü
                    bold_match = re.match(r'^\*\*(?:\d+[\.\)]|[A-Z\d]+[\.\)])\s*([^*]+)\*\*', clean_l)
                    if bold_match:
                        bold_point = bold_match.group(1).strip()
                        key_points.append(bold_point)
                    elif re.match(r'^(?:\d+[\.\)]|[-*•])\s+', clean_l):
                        item_text = re.sub(r'^(?:\d+[\.\)]|[-*•])\s+', '', clean_l).strip()
                        if len(item_text) > 5:
                            items.append(item_text)

                sections.append(ArticleSection(
                    heading=heading,
                    content=content,
                    order=order,
                    items=items
                ))
                order += 1

                # Eğer başlık numaralı bir listeyse (Örn: "1. Not giving yourself time")
                if re.match(r'^\d+[\.\)]\s+', heading):
                    key_points.append(heading)

        return Article(
            url=url,
            source=self.source_name,
            title=title,
            published_date=published_date,
            summary=summary,
            key_points=key_points,
            sections=sections,
            images=images,
            raw_markdown=body
        )

    def clean_text(self, text: str) -> str:
        """Gereksiz boşlukları ve satır sonlarını temizler."""
        if not text:
            return ""
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()
