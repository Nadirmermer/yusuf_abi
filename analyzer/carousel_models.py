from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class CarouselSlide(BaseModel):
    slide_number: int = Field(..., description="Slayt numarası (1, 2, 3...)")
    is_cover: bool = Field(default=False, description="Kapak slaytı mı?")
    section_tag: str = Field(default="FARKINDALIK", description="Üst etiket (örn: FARKINDALIK, AYNA ETKİSİ, BİLİMSEL GERÇEK, ADIM 1, EYLEM PLANI)")
    title: str = Field(default="", description="Başlık metni. Vurgulanacak kritik kelimeleri <span class='highlight'>...</span> içine alabilirsin.")
    subtitle: Optional[str] = Field(default=None, description="Kapak veya alt başlık için tamamlayıcı merak cümlesi")
    body: Optional[str] = Field(default=None, description="Açıklayıcı, akıcı ve doyurucu metin (2-3 vurucu cümle veya madde)")
    highlight_box: Optional[str] = Field(default=None, description="Kutucuk içinde öne çıkarılacak altın kural veya aforizma")
    action_label: str = Field(default="KAYDIR →", description="Sağ alt eylem butonu yazısı (örn: KAYDIR → veya KAYDET & PAYLAŞ)")

class CarouselPost(BaseModel):
    id: str = Field(..., description="Makalenin ID'si")
    url: str = Field(..., description="Orijinal makale URL'si")
    category: str = Field(..., description="Kategori (örn: İLİŞKİLER & BAĞLANMA, DUYGU YÖNETİMİ, ÖZDEĞER)")
    puan: int = Field(..., ge=0, le=100, description="Gerçekçi ve ayırt edici viral potansiyel puanı (0-100)")
    puan_gerekce: Optional[str] = Field(default=None, description="Puanın verilme gerekçesi ve hedef kitle uyumu")
    total_slides: int = Field(..., description="Toplam slayt sayısı (konunun derinliğine göre 4-8 arası)")
    cover_image_url: Optional[str] = Field(default=None, description="Arka plan görsel bağlantısı")
    overlay_opacity: float = Field(default=0.55, ge=0.1, le=0.95, description="Arka plan karartma opaklığı (0.20 açık - 0.85 koyu)")
    slides: List[CarouselSlide] = Field(..., description="Slaytların listesi")
    caption: str = Field(default="", description="Instagram gönderisi için kancalı açıklama metni ve hashtagler (asla emoji içermez)")
