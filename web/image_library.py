import json
import random
from typing import List, Dict, Any, Optional

# Unsplash üzerinden seçilmiş, doğrudan yüksek çözünürlüklü, duygusal, sinematik psikoloji fotoğrafları
CURATED_EMOTIONAL_PHOTOS = {
    "relationships": [
        "https://images.unsplash.com/photo-1518199266791-5375a83190b7?auto=format&fit=crop&w=1080&q=85", # Mesafe, soğuk ve sıcak ışık
        "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?auto=format&fit=crop&w=1080&q=85", # İki el, duygusal bağ
        "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?auto=format&fit=crop&w=1080&q=85", # Cam kenarında düşünen figür
        "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=1080&q=85", # Sinematik gölgeli portre
        "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1080&q=85", # Dostluk ve insan bağı
        "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1080&q=85", # Düşünceli, derin bakış
    ],
    "anxiety": [
        "https://images.unsplash.com/photo-1508672019048-805c876b67e2?auto=format&fit=crop&w=1080&q=85", # Ufka bakan yalnız silüet
        "https://images.unsplash.com/photo-1494774157365-9e04c6720e47?auto=format&fit=crop&w=1080&q=85", # Duygusal, sıcak karanlık portre
        "https://images.unsplash.com/photo-1474552226712-ac0f0961a954?auto=format&fit=crop&w=1080&q=85", # Gölgeler ve yüz hatları
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1080&q=85", # Yoğun göz teması, samimi portre
        "https://images.unsplash.com/photo-1488161628813-04466f872be2?auto=format&fit=crop&w=1080&q=85", # Yalnız yürüyen insan silüeti
        "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1080&q=85", # Sisli, atmosferik atmosfer
    ],
    "healing": [
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1080&q=85", # Huzurlu sabah ışığı
        "https://images.unsplash.com/photo-1518495973542-4542c06a5843?auto=format&fit=crop&w=1080&q=85", # Yumuşak güneş huzmeleri
        "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1080&q=85", # Dingin orman yolu
        "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?auto=format&fit=crop&w=1080&q=85", # Sıcak gün batımı, özşefkat
        "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=1080&q=85", # Sakin çalışma, odaklanma
    ],
    "narcissism": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1080&q=85", # Takım elbiseli karizmatik figür, karanlık
        "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=1080&q=85", # Keskin bakış, çift renkli ışık
        "https://images.unsplash.com/photo-1500485035595-cbe6f645feb1?auto=format&fit=crop&w=1080&q=85", # Yüzün yarısı gölgede, gizem
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1080&q=85", # Düşünceli kadın portresi
    ]
}

ALL_PHOTOS = []
for plist in CURATED_EMOTIONAL_PHOTOS.values():
    ALL_PHOTOS.extend(plist)

def get_4_image_suggestions(article_data: Dict[str, Any], query_theme: Optional[str] = None) -> List[str]:
    """
    Kullanıcıya Midjourney tarzı 4 farklı duygusal görsel alternatifi sunar:
    1. Makalenin kendi orijinal kapak görseli (varsa)
    2-4. Konunun duygu tonuna uygun sinematik, insan odaklı editoryal fotoğraflar
    """
    suggestions = []
    
    # 1. Makalenin kendi kapak görseli
    images = article_data.get("images", [])
    if images:
        for img in images:
            u = img.get("url", "")
            if u and not u.endswith(".svg") and "75x75" not in u and "teaser_small" not in u:
                suggestions.append(u)
                break
                
    # 2. Konu kategorisine göre tema belirle
    title_and_text = ((article_data.get("title") or "") + " " + (query_theme or "")).lower()
    
    if any(k in title_and_text for k in ["narcis", "manipul", "gaslight", "toxic"]):
        theme_pool = CURATED_EMOTIONAL_PHOTOS["narcissism"] + CURATED_EMOTIONAL_PHOTOS["relationships"]
    elif any(k in title_and_text for k in ["heal", "recovery", "peace", "calm", "self", "mindful"]):
        theme_pool = CURATED_EMOTIONAL_PHOTOS["healing"]
    elif any(k in title_and_text for k in ["anxiety", "fear", "panic", "overthink", "burnout", "rumination"]):
        theme_pool = CURATED_EMOTIONAL_PHOTOS["anxiety"]
    else:
        theme_pool = CURATED_EMOTIONAL_PHOTOS["relationships"] + CURATED_EMOTIONAL_PHOTOS["anxiety"]

    # Havuzdan rastgele 4'e tamamlayacak kadar görsel seç
    remaining_needed = 4 - len(suggestions)
    available = [p for p in theme_pool if p not in suggestions]
    if len(available) < remaining_needed:
        available = [p for p in ALL_PHOTOS if p not in suggestions]
        
    random.shuffle(available)
    suggestions.extend(available[:remaining_needed])
    
    return suggestions[:4]
