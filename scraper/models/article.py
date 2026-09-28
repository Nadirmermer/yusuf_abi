from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import hashlib
import re

class ArticleImage(BaseModel):
    url: str
    alt: Optional[str] = None
    caption: Optional[str] = None
    is_cover: bool = False

class ArticleSection(BaseModel):
    heading: str
    content: str
    order: int = 0
    items: List[str] = Field(default_factory=list)

class Article(BaseModel):
    id: str = ""
    url: str
    source: str
    blog_name: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    author_title: Optional[str] = None  # Örn: Ph.D., LICSW, MD
    reviewer: Optional[str] = None      # Örn: Reviewed by Devon Frye
    published_date: Optional[str] = None
    date_modified: Optional[str] = None
    read_time_minutes: int = 0
    word_count: int = 0
    summary: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    sections: List[ArticleSection] = Field(default_factory=list)
    images: List[ArticleImage] = Field(default_factory=list)
    raw_markdown: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            clean_url = self.url.strip().lower()
            slug = re.sub(r'[^a-zA-Z0-9]', '_', clean_url.split('/')[-1] or clean_url)
            hash_suffix = hashlib.md5(clean_url.encode('utf-8')).hexdigest()[:8]
            self.id = f"{slug[:40]}_{hash_suffix}"
            
        # Kelime sayısı ve okuma süresi otomatik hesaplama
        if not self.word_count and self.raw_markdown:
            words = len(re.findall(r'\b\w+\b', self.raw_markdown))
            self.word_count = words
            self.read_time_minutes = max(1, round(words / 200))
