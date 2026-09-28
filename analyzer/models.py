from pydantic import BaseModel, Field

class ViralIcerik(BaseModel):
    id: str = Field(..., description="Makalenin benzersiz kimliği")
    url: str = Field(..., description="Orijinal makalenin kaynak URL bağlantısı")
    baslik: str = Field(..., description="Kaydırmayı durduran merak uyandırıcı Türkçe başlık")
    kategori: str = Field(..., description="İçerik kategorisi (Örn: İlişkiler, Özgüven, Duygu Yönetimi)")
    metin: str = Field(..., description="İlk cümlesinde güçlü bir kanca (hook) barındıran, konuyu adam akıllı, derinlemesine ve akıcı bir sosyal medya diliyle anlatan, kaydetmeyi tetikleyen kapsamlı içerik metni")
    puan: int = Field(..., ge=0, le=100, description="Genel viral potansiyel puanı (0-100)")
