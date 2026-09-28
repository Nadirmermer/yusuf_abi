import os
os.environ["PYDANTIC_DISABLE_PLUGINS"] = "1"
import warnings
warnings.filterwarnings("ignore")
import sys
import json
import logging
import random
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyzer.config import MAKALELER_DIR, DATA_DIR
from analyzer.gemini_client import gemini_rotator
from analyzer.carousel_models import CarouselPost, CarouselSlide
from analyzer.carousel_renderer import render_carousel_slides, strip_emojis, AVATAR_PATH
from analyzer.carousel_processor import create_preview_gallery, download_image_locally
from analyzer.scoring_engine import score_article
from analyzer.batch_processor import batch_processor, AI_CATALOG_PATH, AI_PROCESSED_DIR
from web.image_library import get_4_image_suggestions, ALL_PHOTOS

logger = logging.getLogger("StudioServer")
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Gürültülü üçüncü parti logları sustur (Terminal temizliği)
for _noisy in ["httpx", "httpcore", "google_genai", "google", "urllib3", "uvicorn.access"]:
    logging.getLogger(_noisy).setLevel(logging.WARNING)

app = FastAPI(title="@ya_da_psikoloji - İçerik Keşfi & Karosel Stüdyosu", version="2.6")

CATALOG_PATH = DATA_DIR / "catalog_index.json"
CAROUSELS_DIR = DATA_DIR / "carousels"
CAROUSELS_DIR.mkdir(parents=True, exist_ok=True)

LIKED_ARTICLES_PATH = DATA_DIR / "liked_articles.json"
PASSED_ARTICLES_PATH = DATA_DIR / "passed_articles.json"

# Bellekteki Sıralı Katalog Önbelleği (Yüksek puandan düşüğe)
SORTED_CATALOG: List[Dict[str, Any]] = []

def load_or_init_json(path: Path, default: Any):
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{path.name} okunamadı: {e}")
        return default

def save_json(path: Path, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_article_full_data(article_id: str) -> Dict[str, Any]:
    json_path = MAKALELER_DIR / f"{article_id}.json"
    if not json_path.exists():
        matches = list(MAKALELER_DIR.glob(f"*{article_id}*.json"))
        if matches:
            json_path = matches[0]
        else:
            return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Makale detay okuma hatası {article_id}: {e}")
        return {}

def init_sorted_catalog():
    global SORTED_CATALOG
    if SORTED_CATALOG:
        return SORTED_CATALOG
    if not CATALOG_PATH.exists():
        SORTED_CATALOG = []
        return SORTED_CATALOG

    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            raw_items = json.load(f)
    except Exception as e:
        logger.error(f"Katalog okuma hatası: {e}")
        raw_items = []

    scored_items = []
    for it in raw_items:
        score_info = score_article(it)
        stem = it.get("_file_stem") or ""
        
        # Kapak görseli
        cover = None
        for img in it.get("images", []):
            u = img.get("url", "")
            if u and not u.endswith(".svg") and "teaser_small" not in u and "75x75" not in u:
                cover = u
                break

        item_dict = {
            "id": stem,
            "title": it.get("title", "Başlıksız"),
            "published_date": it.get("published_date"),
            "read_time": it.get("read_time_minutes", 3),
            "key_points": it.get("key_points", []),
            "key_points_count": len(it.get("key_points", [])),
            "cover_image": cover,
            "source": it.get("source", "Simply Psychology"),
            "score": score_info["puan"],
            "category": score_info["kategori"],
            "score_breakdown": {
                "catisma": score_info["catisma_puani"],
                "ayna": score_info["ayna_puani"],
                "kaydetme": score_info["kaydetme_puani"],
                "gorsel": score_info["gorsel_puani"]
            },
            "kriterler": score_info.get("kriterler", [])
        }
        scored_items.append(item_dict)

    # En yüksek puandan en düşük puana sırala (Gerçek veri!)
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    SORTED_CATALOG = scored_items
    logger.info(f"Katalog sıralandı: {len(SORTED_CATALOG)} makale hazır (En yüksek puan: {SORTED_CATALOG[0]['score'] if SORTED_CATALOG else 0}).")
    return SORTED_CATALOG

def enrich_card_with_full_details(card: Dict[str, Any]) -> Dict[str, Any]:
    """Kart ekrana gelirken diskteki gerçek makale JSON'undan giriş metnini ve tam maddelerini ekler."""
    if not card or not card.get("id"):
        return card
    full = get_article_full_data(card["id"])
    if not full:
        return card
    
    enriched = dict(card)
    enriched["url"] = full.get("url") or card.get("source_url") or ""
    enriched["word_count"] = full.get("word_count") or 0
    enriched["all_key_points"] = full.get("key_points") or card.get("key_points") or []
    
    # Gerçek giriş metni (ilk bölüm veya özet)
    sections = full.get("sections") or []
    intro = ""
    for sec in sections:
        content = (sec.get("content") or "").strip()
        if content and len(content) > 60:
            intro = content
            break
    if not intro:
        intro = full.get("summary") or "Makale metni yüklenemedi."
    
    # Giriş metnini temizle ve ilk 500 karakterini al
    intro_clean = intro.replace("\n\n", " ").replace("\n", " ").strip()
    enriched["intro_text"] = intro_clean[:650] + ("..." if len(intro_clean) > 650 else "")
    return enriched

@app.on_event("startup")
def on_startup():
    init_sorted_catalog()

# --- GERİYE DÖNÜK UYUMLULUK ENDPOINTLERİ ---

@app.get("/api/articles")
def list_articles_legacy(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50), q: Optional[str] = None):
    catalog = init_sorted_catalog()
    if q:
        query = q.lower().strip()
        matched = [it for it in catalog if query in it.get("title", "").lower() or query in it.get("hap_fikir", "").lower()]
    else:
        matched = catalog
    total = len(matched)
    start = (page - 1) * limit
    items = matched[start:start + limit]
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "items": items
    }

@app.get("/api/articles/random10")
def get_random_10_legacy():
    catalog = init_sorted_catalog()
    count = min(10, len(catalog))
    items = random.sample(catalog, count) if catalog else []
    return {"count": len(items), "items": items}

# --- İÇERİK KEŞFİ & HIZLI ELEME ENDPOINTLERİ ---

def get_next_discovery_card_internal():
    """Sıradaki en yüksek puanlı, henüz incelenmemiş makaleyi döner.
    Öncelikle Gemini tarafından işlenmiş zengin editoryal paketi (ai_catalog.json) kontrol eder."""
    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    passed = load_or_init_json(PASSED_ARTICLES_PATH, [])
    
    reviewed_ids = {item["id"] for item in liked if isinstance(item, dict) and "id" in item}
    reviewed_ids.update(set(passed))
    
    # 1. Önce yapay zeka tarafından işlenmiş zengin kataloğa bak (RAM'den anında okur)
    ai_catalog = batch_processor.get_catalog_list()
    unreviewed_ai = [item for item in ai_catalog if item["id"] not in reviewed_ids]
    
    if unreviewed_ai:
        ai_card = unreviewed_ai[0]
        
        # Orijinal makaleden kaynak URL ve tam metin oku
        raw_source_url = ai_card.get("source_url") or ""
        orig_author = ""
        orig_text = ""
        raw_path = MAKALELER_DIR / f"{ai_card.get('id')}.json"
        if raw_path.exists():
            try:
                with open(raw_path, "r", encoding="utf-8") as rf:
                    raw_art = json.load(rf)
                    if not raw_source_url:
                        raw_source_url = raw_art.get("url") or ""
                    orig_author = raw_art.get("author") or ""
                    if raw_art.get("summary"):
                        orig_text = raw_art.get("summary")
                    elif raw_art.get("sections"):
                        sec_texts = [s.get("title", "") + ":\n" + s.get("content", "") for s in raw_art.get("sections")[:4] if s.get("content")]
                        orig_text = "\n\n".join(sec_texts)
                    elif raw_art.get("raw_markdown"):
                        orig_text = raw_art.get("raw_markdown")[:1500]
            except Exception:
                pass
        
        if not orig_text:
            orig_text = ai_card.get("editoryal_genis_metin") or ""

        enriched_card = {
            "id": ai_card.get("id"),
            "title": ai_card.get("turkce_baslik") or ai_card.get("original_title"),
            "original_title": ai_card.get("original_title"),
            "original_author": orig_author,
            "original_text": orig_text,
            "kanca_sorusu": ai_card.get("kanca_sorusu"),
            "score": ai_card.get("score", 85),
            "puan_nedeni": ai_card.get("puan_nedeni"),
            "category": ai_card.get("category", "İlişkiler & İletişim"),
            "read_time": ai_card.get("read_time_minutes", 5),
            "source": ai_card.get("source", "Simply Psychology"),
            "url": raw_source_url,
            "intro_text": ai_card.get("editoryal_genis_metin") or ai_card.get("kanca_sorusu"),
            "all_key_points": [s.get("title") for s in ai_card.get("karosel_slaytlari", []) if s.get("title")],
            "reels_kancasi": ai_card.get("reels_kancasi", {}),
            "slides_count": len(ai_card.get("karosel_slaytlari", [])),
            "karosel_slaytlari": ai_card.get("karosel_slaytlari", []),
            "editoryal_genis_metin": ai_card.get("editoryal_genis_metin", ""),
            "caption": ai_card.get("caption", ""),
            "is_ai_processed": True
        }
        return {
            "has_next": True,
            "card": enriched_card,
            "total_liked": len(liked),
            "total_passed": len(passed),
            "remaining": len(unreviewed_ai)
        }
        
    # 2. Eğer henüz AI kataloğunda işlenmiş yoksa ham katalogdan fallback
    catalog = init_sorted_catalog()
    unreviewed = [item for item in catalog if item["id"] not in reviewed_ids]
    
    if not unreviewed:
        return {
            "has_next": False,
            "card": None,
            "total_liked": len(liked),
            "total_passed": len(passed),
            "remaining": 0
        }
        
    next_card = unreviewed[0]
    enriched_card = enrich_card_with_full_details(next_card)
    enriched_card["is_ai_processed"] = False
    return {
        "has_next": True,
        "card": enriched_card,
        "total_liked": len(liked),
        "total_passed": len(passed),
        "remaining": len(unreviewed)
    }

@app.get("/api/discovery/next")
def get_next_discovery_card():
    return get_next_discovery_card_internal()

def swipe_discovery_card_internal(payload: Dict[str, Any]):
    article_id = payload.get("article_id")
    action = payload.get("action")  # 'like' | 'pass'
    
    if not article_id or action not in ["like", "pass"]:
        raise HTTPException(status_code=400, detail="Geçersiz eleme isteği.")
        
    # 1. Önce Yapay Zeka Kataloğundan ara (RAM ve Tekil Dosya)
    ai_item = None
    with batch_processor.lock:
        if article_id in batch_processor.catalog_cache:
            ai_item = batch_processor.catalog_cache[article_id]
            
    if not ai_item:
        ai_file = AI_PROCESSED_DIR / f"{article_id}.json"
        if ai_file.exists():
            try:
                with open(ai_file, "r", encoding="utf-8") as af:
                    ai_item = json.load(af)
            except Exception:
                pass

    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    passed = load_or_init_json(PASSED_ARTICLES_PATH, [])
    
    if action == "like":
        if not any(item["id"] == article_id for item in liked):
            if ai_item:
                # Yapay Zeka tarafından üretilmiş tam Türkçe paket
                liked_entry = {
                    "id": article_id,
                    "title": ai_item.get("turkce_baslik") or ai_item.get("original_title"),
                    "original_title": ai_item.get("original_title"),
                    "score": ai_item.get("score", 85),
                    "puan_nedeni": ai_item.get("puan_nedeni"),
                    "category": ai_item.get("category", "İlişkiler & İletişim"),
                    "kanca_sorusu": ai_item.get("kanca_sorusu"),
                    "editoryal_genis_metin": ai_item.get("editoryal_genis_metin"),
                    "karosel_slaytlari": ai_item.get("karosel_slaytlari", []),
                    "reels_kancasi": ai_item.get("reels_kancasi", {}),
                    "caption": ai_item.get("caption"),
                    "source": ai_item.get("source"),
                    "url": ai_item.get("source_url") or "",
                    "slides_count": len(ai_item.get("karosel_slaytlari", [])),
                    "is_ai_processed": True,
                    "liked_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "havuzda"
                }
            else:
                # Fallback: Ham katalogdan zenginleştir
                catalog = init_sorted_catalog()
                target_item = next((item for item in catalog if item["id"] == article_id or article_id in item["id"]), None)
                if not target_item:
                    raise HTTPException(status_code=404, detail="Makale bulunamadı.")
                enriched = enrich_card_with_full_details(target_item)
                liked_entry = dict(enriched)
                liked_entry["liked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                liked_entry["status"] = "havuzda"

            liked.append(liked_entry)
            liked.sort(key=lambda x: x.get("score", 0), reverse=True)
            save_json(LIKED_ARTICLES_PATH, liked)
    elif action == "pass":
        if article_id not in passed:
            passed.append(article_id)
            save_json(PASSED_ARTICLES_PATH, passed)
            
    return get_next_discovery_card_internal()

@app.post("/api/discovery/swipe")
def swipe_discovery_card(payload: Dict[str, Any] = Body(...)):
    return swipe_discovery_card_internal(payload)

@app.post("/api/discovery/ai-summary")
def get_ai_summary_for_card(payload: Dict[str, Any] = Body(...)):
    """Kullanıcı kartı incelerken Gemini'den anında gerçek Türkçe Instagram analizi, kanca ve özet alır."""
    article_id = payload.get("article_id")
    if not article_id:
        raise HTTPException(status_code=400, detail="article_id gereklidir.")
    full_data = get_article_full_data(article_id)
    if not full_data:
        raise HTTPException(status_code=404, detail="Makale bulunamadı.")
    
    title = full_data.get("title", "")
    key_points = full_data.get("key_points", [])
    sections = full_data.get("sections", [])
    intro = ""
    for s in sections:
        c = (s.get("content") or "").strip()
        if c:
            intro += c[:500] + "\n"
        if len(intro) > 1200:
            break

    prompt = f"""Sen @ya_da_psikoloji Instagram hesabının baş psikolog ve editoryal direktörüsün.
Aşağıdaki İngilizce psikoloji makalesini oku ve Instagram için hızlı bir içerik değerlendirmesi yap.
Kesinlikle emoji kullanma.

Makale Başlığı: {title}
Anahtar Maddeler: {json.dumps(key_points, ensure_ascii=False)}
İçerik Özeti / Giriş: {intro}

SADECE geçerli bir JSON nesnesi olarak Türkçe yanıt ver. Markdown blokları koyma.
JSON Şeması:
{{
  "turkce_baslik": "İlgi çekici, merak uyandıran Türkçe Instagram başlığı",
  "kanca_sorusu": "Kaydırmayı ilk 2 saniyede durduran 1 cümlelik vurucu soru veya tespit",
  "turkce_ozet": "Makalenin özünü anlatan 2-3 cümlelik sade Türkçe açıklama",
  "instagram_puani": 92,
  "neden_tutar": "Bu konunun Instagram'da neden tutacağına dair gerçekçi editoryal yorum",
  "onemli_maddeler": ["Madde 1", "Madde 2", "Madde 3", "Madde 4"]
}}"""

    try:
        sys_inst = "Sen @ya_da_psikoloji Instagram hesabının baş psikoloğu ve editoryal direktörüsün. Kesinlikle emoji kullanma."
        parsed = gemini_rotator.generate_json(prompt, system_instruction=sys_inst)
        return parsed
    except Exception as e:
        logger.error(f"Gemini AI kart analizi hatası: {e}")
        # Hata durumunda temel Türkçe fallback
        return {
            "turkce_baslik": title,
            "kanca_sorusu": "Bu durumu ilişkinizde veya hayatınızda sık sık fark ediyor musunuz?",
            "turkce_ozet": intro[:300] if intro else "Makale psikolojik ve ilişkisel dinamikleri derinlemesine ele almaktadır.",
            "instagram_puani": 85,
            "neden_tutar": "Yüksek ayna etkisi ve ilişkisel empati potansiyeli.",
            "onemli_maddeler": key_points[:5]
        }

# --- BEĞENİLENLER HAVUZU ENDPOINTLERİ ---

@app.get("/api/liked")
def get_liked_articles():
    """Onaylanan ve havuzda biriken makaleleri döner."""
    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    liked.sort(key=lambda x: x.get("score", 0), reverse=True)
    return liked

@app.delete("/api/liked/{article_id}")
def remove_liked_article(article_id: str):
    """Beğenilenler havuzundan bir makaleyi çıkarır."""
    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    liked = [item for item in liked if item.get("id") != article_id]
    save_json(LIKED_ARTICLES_PATH, liked)
    return {"status": "ok", "remaining": len(liked)}

# --- KAROSEL STÜDYOSU ENDPOINTLERİ ---

@app.post("/api/carousel/draft")
def generate_draft_carousel(payload: Optional[Dict[str, Any]] = Body(None), article_id: Optional[str] = Query(None)):
    """Beğenilen bir makale için Gemini ile tam Instagram kurgusunu ve 4'lü görsel önerisini getirir."""
    target_id = None
    if payload and isinstance(payload, dict):
        target_id = payload.get("article_id") or payload.get("id") or payload.get("stem")
    if not target_id and article_id:
        target_id = article_id
        
    if not target_id:
        raise HTTPException(status_code=400, detail="article_id gereklidir.")
        
    json_path = MAKALELER_DIR / f"{target_id}.json"
    if not json_path.exists():
        matches = list(MAKALELER_DIR.glob(f"*{target_id}*.json"))
        if not matches:
            raise HTTPException(status_code=404, detail=f"Makale dosyası bulunamadı: {target_id}")
        json_path = matches[0]

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            article_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Makale okuma hatası: {e}")

    # 1. Önce Yapay Zeka Tarafından İşlenmiş Hazır Paket Var mı Kontrol Et
    ai_record_path = AI_PROCESSED_DIR / f"{target_id}.json"
    if ai_record_path.exists():
        try:
            with open(ai_record_path, "r", encoding="utf-8") as f:
                ai_record = json.load(f)
            
            raw_slides = ai_record.get("karosel_slaytlari", [])
            slides = []
            total_count = len(raw_slides)
            for idx, s in enumerate(raw_slides, 1):
                is_cov = (idx == 1) or s.get("is_cover", False)
                is_last = (idx == total_count)
                slides.append({
                    "slide_number": idx,
                    "is_cover": is_cov,
                    "section_tag": strip_emojis(s.get("section_tag") or "FARKINDALIK"),
                    "title": strip_emojis(s.get("title") or "Farkındalık"),
                    "subtitle": strip_emojis(s.get("subtitle") or ""),
                    "body": strip_emojis(s.get("body") or ""),
                    "highlight_box": strip_emojis(s.get("highlight_box") or ""),
                    "action_label": "KAYDET & PAYLAŞ" if is_last else "KAYDIR →"
                })
            
            category = ai_record.get("category", "İLİŞKİLER & PSİKOLOJİ")
            image_suggestions = get_4_image_suggestions(article_data, category)

            return {
                "article_id": target_id,
                "title": ai_record.get("turkce_baslik") or article_data.get("title", ""),
                "original_title": ai_record.get("original_title") or article_data.get("title", ""),
                "url": ai_record.get("source_url") or article_data.get("url", ""),
                "puan": ai_record.get("score", 90),
                "category": strip_emojis(category),
                "slides": slides,
                "caption": strip_emojis(ai_record.get("caption") or ""),
                "image_suggestions": image_suggestions,
                "selected_image": image_suggestions[0] if image_suggestions else "https://images.unsplash.com/photo-1518495973542-4542c06a5843",
                "overlay_opacity": 0.55,
                "reels_kancasi": ai_record.get("reels_kancasi", {}),
                "editoryal_genis_metin": ai_record.get("editoryal_genis_metin", "")
            }
        except Exception as e:
            logger.warning(f"Hazır AI kurgusu okunamadı, Gemini'ye yönlendiriliyor: {e}")

    try:
        ai_data = gemini_rotator.generate_carousel(article_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini analiz hatası: {e}")

    raw_slides = ai_data.get("slides", [])
    slides = []
    total_count = len(raw_slides)
    for idx, s in enumerate(raw_slides, 1):
        is_cov = (idx == 1) or s.get("is_cover", False)
        is_last = (idx == total_count)
        slides.append({
            "slide_number": idx,
            "is_cover": is_cov,
            "section_tag": strip_emojis(s.get("section_tag") or "FARKINDALIK"),
            "title": strip_emojis(s.get("title") or "Farkındalık"),
            "subtitle": strip_emojis(s.get("subtitle") or ""),
            "body": strip_emojis(s.get("body") or ""),
            "highlight_box": strip_emojis(s.get("highlight_box") or ""),
            "action_label": "KAYDET & PAYLAŞ" if is_last else "KAYDIR →"
        })

    image_suggestions = get_4_image_suggestions(article_data, ai_data.get("category"))

    # Beğenilenler listesinde statüyü güncelle
    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    for it in liked:
        if it.get("id") == target_id:
            it["status"] = "taslak_hazir"
            break
    save_json(LIKED_ARTICLES_PATH, liked)

    return {
        "article_id": target_id,
        "title": article_data.get("title", ""),
        "url": article_data.get("url", ""),
        "category": strip_emojis(ai_data.get("category", "İLİŞKİLER & PSİKOLOJİ")),
        "slides": slides,
        "caption": strip_emojis(ai_data.get("caption", "")),
        "image_suggestions": image_suggestions,
        "selected_image": image_suggestions[0] if image_suggestions else "https://images.unsplash.com/photo-1518495973542-4542c06a5843",
        "overlay_opacity": 0.55
    }

# --- ARKA PLAN YAPAY ZEKA İŞLEME (BATCH) ENDPOINTLERİ ---

@app.get("/api/batch/status")
def get_batch_status():
    return batch_processor.get_status()

@app.post("/api/batch/start")
def start_batch_processing():
    started = batch_processor.start()
    return {"status": "ok" if started else "already_running", "is_running": batch_processor.is_running}

@app.post("/api/batch/stop")
def stop_batch_processing():
    stopped = batch_processor.stop()
    return {"status": "ok", "is_running": batch_processor.is_running}

@app.post("/api/carousel/search-images")
def search_images(payload: Dict[str, Any] = Body(...)):
    """Farklı 4 duygusal fotoğraf önerisi döner."""
    count = min(4, len(ALL_PHOTOS))
    sample_pool = random.sample(ALL_PHOTOS, count) if ALL_PHOTOS else []
    return {"images": sample_pool}

@app.post("/api/carousel/render")
def render_carousel_endpoint(payload: Dict[str, Any] = Body(...)):
    """Son onayı verilen karoseli 1080x1350 PNG ve caption.txt olarak kaydeder."""
    article_id = payload.get("article_id") or "custom_carousel"
    url = payload.get("url", "")
    category = strip_emojis(payload.get("category", "İLİŞKİLER & PSİKOLOJİ"))
    puan = int(payload.get("puan", 90))
    puan_gerekce = payload.get("puan_gerekce", "")
    caption_text = strip_emojis(payload.get("caption", ""))
    selected_image = payload.get("selected_image") or ""
    overlay_opacity = float(payload.get("overlay_opacity", 0.55))
    raw_slides = payload.get("slides", [])

    if not raw_slides:
        raise HTTPException(status_code=400, detail="En az 1 slayt gereklidir.")

    folder_name = f"[{puan:02d}]_{article_id}"
    target_dir = CAROUSELS_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    local_bg_uri = None
    if selected_image:
        bg_file = target_dir / "bg.jpg"
        local_bg_uri = download_image_locally(selected_image, bg_file)

    slides = []
    total_count = len(raw_slides)
    for idx, s in enumerate(raw_slides, 1):
        is_cov = (idx == 1) or s.get("is_cover", False)
        is_last = (idx == total_count)
        slides.append(CarouselSlide(
            slide_number=idx,
            is_cover=is_cov,
            section_tag=strip_emojis(s.get("section_tag") or "FARKINDALIK"),
            title=strip_emojis(s.get("title") or "Farkındalık"),
            subtitle=strip_emojis(s.get("subtitle") or ""),
            body=strip_emojis(s.get("body") or ""),
            highlight_box=strip_emojis(s.get("highlight_box") or ""),
            action_label="KAYDET & PAYLAŞ" if is_last else "KAYDIR →"
        ))

    carousel_post = CarouselPost(
        id=article_id,
        url=url,
        category=category,
        puan=puan,
        puan_gerekce=puan_gerekce,
        total_slides=len(slides),
        cover_image_url=local_bg_uri or selected_image,
        overlay_opacity=overlay_opacity,
        slides=slides,
        caption=caption_text
    )

    caption_path = target_dir / "caption.txt"
    with open(caption_path, "w", encoding="utf-8") as cf:
        cf.write(f"=== INSTAGRAM CAPTION (@ya_da_psikoloji) ===\n\n")
        cf.write(carousel_post.caption)
        cf.write(f"\n\n--- Bilgiler ---\n")
        cf.write(f"Puan: {carousel_post.puan}/100\n")
        if carousel_post.puan_gerekce:
            cf.write(f"Gerekçe: {carousel_post.puan_gerekce}\n")
        cf.write(f"Kaynak: {carousel_post.url}\n")

    json_path = target_dir / "carousel.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        jf.write(carousel_post.model_dump_json(indent=2))

    rendered_pngs = render_carousel_slides(carousel_post, target_dir)
    create_preview_gallery(carousel_post, target_dir, rendered_pngs)

    # Beğenilenler listesinde statüyü 'png_uretildi' yap
    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    for it in liked:
        if it.get("id") == article_id:
            it["status"] = "png_uretildi"
            it["folder_name"] = folder_name
            break
    save_json(LIKED_ARTICLES_PATH, liked)

    slide_urls = [f"/carousels/{folder_name}/{p.name}" for p in rendered_pngs]

    return {
        "status": "success",
        "folder_name": folder_name,
        "folder_path": str(target_dir.resolve()),
        "total_slides": len(rendered_pngs),
        "slides": slide_urls,
        "caption": caption_text
    }

# --- ARŞİV ENDPOINTLERİ ---

@app.get("/api/carousels/recent")
def list_recent_carousels():
    """Üretilmiş tüm karoselleri listeler."""
    if not CAROUSELS_DIR.exists():
        return []
    results = []
    for d in sorted(CAROUSELS_DIR.iterdir(), reverse=True):
        if d.is_dir() and (d / "carousel.json").exists():
            try:
                with open(d / "carousel.json", "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                slide_files = sorted(list(d.glob("slide_*.png")), key=lambda p: int(p.stem.split("_")[1]) if p.stem.split("_")[1].isdigit() else 0)
                results.append({
                    "folder_name": d.name,
                    "id": cdata.get("id"),
                    "category": cdata.get("category"),
                    "puan": cdata.get("puan"),
                    "total_slides": len(slide_files),
                    "cover_slide": f"/carousels/{d.name}/{slide_files[0].name}" if slide_files else None,
                    "caption": cdata.get("caption", ""),
                    "has_index": (d / "index.html").exists()
                })
            except Exception as e:
                logger.warning(f"Okuma hatası {d.name}: {e}")
    return results

@app.post("/api/carousels/open")
def open_carousel_folder(payload: Dict[str, Any] = Body(...)):
    """Klasörü Windows Explorer veya sistem dosya yöneticisinde anında açar."""
    folder_name = payload.get("folder_name")
    if not folder_name:
        raise HTTPException(status_code=400, detail="folder_name gereklidir.")
    target_dir = CAROUSELS_DIR / folder_name
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Klasör bulunamadı.")
    
    resolved_path = str(target_dir.resolve())
    try:
        if sys.platform == "win32":
            os.startfile(resolved_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", resolved_path])
        else:
            subprocess.Popen(["xdg-open", resolved_path])
        return {"status": "ok", "path": resolved_path}
    except Exception as e:
        logger.error(f"Klasör açma hatası: {e}")
        return {"status": "error", "message": str(e), "path": resolved_path}

@app.get("/api/carousels/download/{folder_name}")
def download_carousel_zip(folder_name: str):
    """Karosel klasörünü zip arşivi olarak tarayıcıya doğrudan indirir."""
    target_dir = CAROUSELS_DIR / folder_name
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Klasör bulunamadı.")
    
    import io
    import zipfile
    from fastapi.responses import StreamingResponse

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(target_dir.iterdir()):
            if f.is_file() and (f.suffix.lower() in [".png", ".txt", ".json", ".jpg"]):
                zf.write(f, arcname=f.name)
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{folder_name}.zip"'}
    )

# --- KONTROL MERKEZİ & İŞLEMLER ENDPOINTLERİ ---

@app.get("/api/system/status")
def get_system_status():
    """Sistem, veri tabanı, kota ve makale durumlarını döner."""
    catalog = init_sorted_catalog()
    liked = load_or_init_json(LIKED_ARTICLES_PATH, [])
    passed = load_or_init_json(PASSED_ARTICLES_PATH, [])
    
    recent_carousels = []
    if CAROUSELS_DIR.exists():
        recent_carousels = [d.name for d in CAROUSELS_DIR.iterdir() if d.is_dir() and (d / "carousel.json").exists()]

    from analyzer.config import GEMINI_API_KEYS
    return {
        "total_articles": len(catalog),
        "liked_count": len(liked),
        "passed_count": len(passed),
        "remaining_count": max(0, len(catalog) - len(liked) - len(passed)),
        "produced_carousels": len(recent_carousels),
        "api_keys_count": len(GEMINI_API_KEYS),
        "catalog_file_exists": CATALOG_PATH.exists()
    }

@app.post("/api/system/reset-passed")
def reset_passed_articles():
    """Pas geçilen makaleleri sıfırlar, böylece kullanıcı keşfe kaldığı yerden veya baştan devam edebilir."""
    save_json(PASSED_ARTICLES_PATH, [])
    return {"status": "ok", "message": "Pas geçilen makaleler sıfırlandı."}

@app.post("/api/system/reset-all")
def reset_all_history():
    """Hem pas geçilenleri hem beğenilenleri sıfırlar (Sıfırdan başlama)."""
    save_json(PASSED_ARTICLES_PATH, [])
    save_json(LIKED_ARTICLES_PATH, [])
    return {"status": "ok", "message": "Tüm eleme geçmişi sıfırlandı."}

@app.post("/api/system/reindex-catalog")
def reindex_catalog():
    """7.639 makaleyi baştan tarar ve puanları yeniden sıralar."""
    global SORTED_CATALOG
    SORTED_CATALOG = []
    catalog = init_sorted_catalog()
    return {"status": "ok", "total_indexed": len(catalog)}

# Arka plan scraper görevi
SCRAPER_RUNNING = False

@app.post("/api/scraper/start")
def start_scraper_task(payload: Dict[str, Any] = Body(...)):
    """Web arayüzünden tek tıkla arka planda kazıma işlemini başlatır."""
    global SCRAPER_RUNNING
    site = payload.get("site", "simplypsychology")
    limit = int(payload.get("limit", 20))
    
    if SCRAPER_RUNNING:
        return {"status": "busy", "message": "Zaten çalışan bir kazıma işlemi var."}

    import subprocess
    import threading
    
    def run_worker():
        global SCRAPER_RUNNING
        SCRAPER_RUNNING = True
        try:
            cmd = [sys.executable, "-m", "scraper.runner", "--site", site, "--limit", str(limit)]
            subprocess.run(cmd, cwd=str(PROJECT_ROOT))
            # Kazıma bitince kataloğu yeniden indeksle
            global SORTED_CATALOG
            SORTED_CATALOG = []
            init_sorted_catalog()
        except Exception as e:
            logger.error(f"Scraper hatası: {e}")
        finally:
            SCRAPER_RUNNING = False

    t = threading.Thread(target=run_worker, daemon=True)
    t.start()

    return {"status": "started", "message": f"{site.upper()} kazıma işlemi arka planda başlatıldı."}

@app.get("/api/scraper/status")
def get_scraper_status():
    global SCRAPER_RUNNING
    return {"running": SCRAPER_RUNNING}

# Statik Karosel Klasörlerini Sun
app.mount("/carousels", StaticFiles(directory=str(CAROUSELS_DIR)), name="carousels")

# Statik Dosyalar (Logo, vb.)
STATIC_DIR = PROJECT_ROOT / "web" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/logo.jpg")
@app.get("/api/logo")
def serve_logo():
    logo_file = STATIC_DIR / "logo.jpg"
    if not logo_file.exists():
        logo_file = PROJECT_ROOT / "analyzer" / "assets" / "avatar.jpg"
    if logo_file.exists():
        return FileResponse(logo_file, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Logo bulunamadı")


# Ana HTML Sayfasını Sun
TEMPLATES_DIR = PROJECT_ROOT / "web" / "templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Index bulunamadı</h1>", status_code=404)
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.server:app", host="127.0.0.1", port=8000, reload=True)
