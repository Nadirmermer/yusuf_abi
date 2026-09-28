import re
from typing import Dict, Any, Tuple

# Psikolojik virallik sözlükleri
CONFLICT_KEYWORDS = [
    "myth", "wrong", "paradox", "illusion", "lie", "truth about", "actually",
    "why you shouldn't", "fake", "secretly", "mistake", "warning", "hidden",
    "danger", "cost of", "stop doing", "don't do", "never say", "shocking"
]

MIRROR_KEYWORDS = [
    "relationship", "partner", "attachment", "overthink", "boundary", "boundaries",
    "narciss", "people pleas", "guilt", "silent treatment", "burnout", "gaslight",
    "breakup", "lonel", "insecure", "validation", "shame", "rejection", "jealous",
    "toxic", "empathy", "communication", "codepend", "anxious", "avoidant"
]

SAVE_KEYWORDS = [
    "ways to", "steps to", "how to", "signs of", "strategies", "habits",
    "rules", "checklist", "guide", "methods", "tips", "skills", "reasons"
]

CATEGORY_RULES = [
    (["narciss", "toxic", "gaslight", "manipul", "silent treatment", "triangulat"], "Narsizm & Toksik İlişkiler"),
    (["attachment", "anxious", "avoidant", "breakup", "codepend", "rebound"], "Bağlanma & Ayrılık"),
    (["boundary", "boundaries", "people pleas", "say no", "guilt"], "Sınırlar & Özsaygı"),
    (["anxiety", "panic", "overthink", "rumination", "worry", "stress", "burnout"], "Kaygı & Zihin Yönetimi"),
    (["trauma", "childhood", "inner child", "healing", "grief", "wound"], "İçsel İyileşme & Travma"),
    (["relationship", "couple", "love", "marriage", "dating", "friendship"], "İlişkiler & İletişim")
]

def score_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir makalenin Instagram virallik potansiyelini 4 temel parametreye göre
    kesin, gerçekçi ve ayırt edici bir şekilde puanlar.
    """
    title = (article_data.get("title") or "").strip()
    title_lower = title.lower()
    key_points = article_data.get("key_points") or []
    kp_count = len(key_points)
    read_time = article_data.get("read_time_minutes") or 3
    images = article_data.get("images") or []
    
    # 1. Çatışma & Tezat Gücü (0-25 Puan)
    conflict_score = 12
    for word in CONFLICT_KEYWORDS:
        if word in title_lower:
            conflict_score += 10
            break
    if any(q in title_lower for q in ["why", "how", "what", "is it"]):
        conflict_score += 3
    conflict_score = min(25, conflict_score)

    # 2. Ayna Etkisi (Relatability & DM Paylaşımı) (0-30 Puan)
    mirror_score = 10
    matched_mirror = [w for w in MIRROR_KEYWORDS if w in title_lower]
    if len(matched_mirror) >= 2:
        mirror_score += 18
    elif len(matched_mirror) == 1:
        mirror_score += 12
    else:
        # Genel psikoloji
        mirror_score += 4
    mirror_score = min(30, mirror_score)

    # 3. Kaydetme Değeri (Adım Adım / Rehber Değeri) (0-25 Puan)
    save_score = 8
    # Başlıkta sayı var mı? (Örn: "7 Signs", "5 Steps")
    if re.search(r'\b\d+\b', title):
        save_score += 7
    if any(w in title_lower for w in SAVE_KEYWORDS):
        save_score += 5
    if kp_count >= 6:
        save_score += 5
    elif kp_count >= 3:
        save_score += 3
    save_score = min(25, save_score)

    # 4. İçerik ve Görsel Zenginliği (0-20 Puan)
    visual_score = 5
    has_cover = any(i.get("is_cover") and i.get("url") for i in images)
    valid_images = [i for i in images if i.get("url") and not i.get("url", "").endswith(".svg")]
    if has_cover:
        visual_score += 9
    elif len(valid_images) >= 2:
        visual_score += 6
    if read_time >= 4:
        visual_score += 6
    elif read_time >= 2:
        visual_score += 3
    visual_score = min(20, visual_score)

    total_score = conflict_score + mirror_score + save_score + visual_score

    # Kategori Belirle
    category_name = "Kişisel Gelişim & Farkındalık"
    for keywords, cat in CATEGORY_RULES:
        if any(k in title_lower for k in keywords):
            category_name = cat
            break

    # Algoritmik Etkileşim Skoru Kriterleri (Şeffaf Metrikler)
    kriterler = []
    if mirror_score >= 20:
        kriterler.append("Yüksek Özdeşleşme (İlişkisel/Duygusal Bağ)")
    if save_score >= 18:
        kriterler.append("Rehber Niteliği (Maddeli & Adım Adım)")
    if conflict_score >= 18:
        kriterler.append("Merak & Tezat Unsuru (Kanca Potansiyeli)")
    if visual_score >= 14:
        kriterler.append("Kapsamlı İçerik & Çoklu Görsel")

    return {
        "puan": total_score,
        "kategori": category_name,
        "catisma_puani": conflict_score,
        "ayna_puani": mirror_score,
        "kaydetme_puani": save_score,
        "gorsel_puani": visual_score,
        "kriterler": kriterler
    }
