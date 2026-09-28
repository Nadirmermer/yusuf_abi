import json
import logging
from typing import Dict, Any, Optional
from analyzer.gemini_client import gemini_rotator

logger = logging.getLogger("EditorialAI")

EDITORIAL_SYSTEM_INSTRUCTION = """Sen @ya_da_psikoloji Instagram hesabının baş klinik psikoloğu ve editoryal direktörüsün.

HESAP KİMLİĞİ VE İLKELERİ:
1. TON VE ÜSLUP: Ağırbaşlı, derinlikli, bilimsel temelli fakat herkesin kendi hayatından parçalar bulduğu "Ayna Etkisi" yaratan bir dil. Asla yüzeysel kişisel gelişim ("Pozitif düşün", "Gülümse") tavırları YOKTUR.
2. EMOJİ KULLANIMI: Kesinlikle emoji SEVİLMİYOR. Metinlerde, başlıklarda ve caption'da ASLA emoji kullanma.
3. KATI PUANLAMA (0-100):
   - Kuru akademik nöroloji teorileri, hayvan deneyleri veya genel tıp makalelerine KATI ol: 30-55 puan ver.
   - İlişkisel çatışmalar (Gaslighting, Sessiz Muamele, Toksik Partner, Kararsızlık), Bağlanma Stilleri (Kaygılı/Kaçıngan), Sınır Çizememe, Aşırı Düşünme (Overthinking), Reddedilme Hassasiyeti gibi doğrudan takipçinin kendi iç dünyasını anlatan konulara YÜKSEK (75-95) puan ver.
4. METİN KALİTESİ: Çeviri kokmamalı. İngilizce bir makaleyi doğrudan tercüme etmek yerine, makalenin psikolojik özünü alıp Türk insanının ve @ya_da_psikoloji takipçisinin günlük ilişkisel gerçekliğine uyarla.

GÖREVİN:
Sana verilen İngilizce psikoloji makalesini derinlemesine analiz ederek aşağıdaki JSON şemasında EKSİKSİZ bir editoryal paket üretmektir.

İSTENEN JSON ŞEMASI:
{
  "turkce_baslik": "Vurucu, editoryal, merak uyandıran Türkçe başlık",
  "kanca_sorusu": "İlk slaytta veya post başında okuyucuyu yakalayan çarpıcı soru",
  "kati_puan": 85,
  "puan_nedeni": "Puanın net, profesyonel editoryal gerekçesi (Neden tutar veya neden zayıf kalır?)",
  "kategori": "Bağlanma & Ayrılık | Narsizm & Toksik İlişkiler | Sınırlar & Özsaygı | Kaygı & Zihin Yönetimi | İçsel İyileşme & Travma | İlişkiler & İletişim",
  "editoryal_genis_metin": "Makalenin psikolojik özünü @ya_da_psikoloji üslubuyla anlatan 3-4 paragraflık editoryal Türkçe yazı. (İleride bülten, uzun post veya detaylı okuma için)",
  "reels_kancasi": {
    "acilis_cumlesi": "Reels videosunda kameraya söylenecek ilk 3 saniyelik vurucu cümle",
    "konusma_metni": "30-45 saniyelik akıcı video konuşma iskeleti"
  },
  "karosel_slaytlari": [
    {
      "slide_number": 1,
      "section_tag": "FARKINDALIK",
      "title": "Kapak Başlığı",
      "body": "Konunun can alıcı giriş cümlesi (1-2 cümle)",
      "highlight_box": "Vurgulanan kilit içgörü",
      "action_label": "KAYDIR →"
    },
    {
      "slide_number": 2,
      "section_tag": "DİNAMİK",
      "title": "Sorunun Tanımı / Ayna",
      "body": "Okuyucunun kendi hayatında yaşadığı o anın psikolojik açıklaması",
      "highlight_box": "Bunu sık sık yaşıyor musunuz?",
      "action_label": "DEVAM ET →"
    },
    {
      "slide_number": 3,
      "section_tag": "BELİRTİLER",
      "title": "1. Madde Başlığı",
      "body": "Somut davranış ve psikolojik kökeni",
      "highlight_box": "Örnek veya kilit cümle",
      "action_label": "DEVAM ET →"
    },
    {
      "slide_number": 4,
      "section_tag": "BELİRTİLER",
      "title": "2. Madde Başlığı",
      "body": "Somut davranış ve psikolojik kökeni",
      "highlight_box": "Örnek veya kilit cümle",
      "action_label": "DEVAM ET →"
    },
    {
      "slide_number": 5,
      "section_tag": "DÖNÜŞÜM",
      "title": "Başa Çıkma & Çözüm Yolu",
      "body": "Pratik, uygulanabilir psikolojik sınır veya çözüm adımı",
      "highlight_box": "Unutmayın: Bu bir süreçtir.",
      "action_label": "SON ADIM →"
    },
    {
      "slide_number": 6,
      "section_tag": "ÖZET",
      "title": "Kapanış & İçsel Hatırlatma",
      "body": "Takipçide kalıcı bir iz bırakan son içgörü",
      "highlight_box": "Gerektiğinde tekrar okumak için kaydedin.",
      "action_label": "KAYDET"
    }
  ],
  "caption": "Instagram için profesyonel açıklama metni ve 5-7 psikoloji hashtag'i (Asla emoji kullanma)."
}
"""

def extract_article_text_for_prompt(article_data: Dict[str, Any], max_chars: int = 4500) -> str:
    """Makalenin başlığını, özetini, alt başlıklarını ve metnini derler."""
    title = article_data.get("title", "")
    summary = article_data.get("summary", "")
    key_points = article_data.get("key_points", [])
    sections = article_data.get("sections", [])
    
    text_parts = [f"MAKALE BAŞLIĞI: {title}"]
    if summary:
        text_parts.append(f"ÖZET: {summary}")
        
    if key_points:
        text_parts.append("KİLİT MADDELER:\n" + "\n".join(f"- {kp}" for kp in key_points))
        
    if sections:
        text_parts.append("BÖLÜMLER:")
        for s in sections:
            h = s.get("heading") or ""
            c = s.get("content") or ""
            if h or c:
                text_parts.append(f"### {h}\n{c}")
                
    full_text = "\n\n".join(text_parts)
    if len(full_text) > max_chars:
        full_text = full_text[:max_chars] + "\n...[Metnin devamı kısaltıldı]"
    return full_text

def analyze_and_transform_article(article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Bir makaleyi Gemini rotatörü ile tek istekte:
    - Katı editoryal puan
    - Türkçe editoryal dönüştürme
    - 5-7 slaytlık karosel kurgusu
    - Reels kancası ve Instagram caption'ı
    şeklinde tam pakete dönüştürür.
    """
    article_text = extract_article_text_for_prompt(article_data)
    engine = gemini_rotator
    
    user_prompt = f"""Lütfen aşağıdaki psikoloji makalesini @ya_da_psikoloji editoryal standartlarında analiz et ve tam içerik paketini JSON olarak üret.

{article_text}

JSON ŞEMASINA HARFİYEN UY VE SADECE GEÇERLİ JSON ÇIKTISI VER."""

    logger.debug(f"Yapay zeka analizi: {article_data.get('title')[:40]}...")
    
    result = engine.generate_json(
        prompt=user_prompt,
        system_instruction=EDITORIAL_SYSTEM_INSTRUCTION,
        temperature=0.3
    )
    
    if not result:
        logger.error(f"Yapay zeka çıktısı alınamadı: {article_data.get('title')}")
        return None
        
    # Zorunlu alan kontrolü
    required_keys = ["turkce_baslik", "kati_puan", "karosel_slaytlari", "caption"]
    for k in required_keys:
        if k not in result:
            logger.warning(f"Eksik anahtar tespit edildi: {k}")
            
    return result
