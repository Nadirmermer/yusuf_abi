import os
import sys
import json
import logging
import urllib.request
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyzer.config import MAKALELER_DIR, DATA_DIR
from analyzer.gemini_client import gemini_rotator
from analyzer.carousel_models import CarouselPost, CarouselSlide
from analyzer.carousel_renderer import render_carousel_slides, strip_emojis

logger = logging.getLogger("CarouselProcessor")

CAROUSELS_OUTPUT_DIR = DATA_DIR / "carousels"

def extract_best_image_url(article_data: Dict[str, Any]) -> Optional[str]:
    """Makalenin içindeki en uygun yüksek çözünürlüklü kapak görseli URL'sini döner."""
    images = article_data.get("images", [])
    if not images:
        return None
        
    for img in images:
        if img.get("is_cover") and img.get("url"):
            u = img["url"]
            if not u.endswith(".svg"):
                return u

    for img in images:
        u = img.get("url", "")
        if u and not u.endswith(".svg") and "teaser_small" not in u and "75x75" not in u:
            return u
            
    return None

def download_image_locally(url: str, dest_path: Path) -> Optional[str]:
    """Görseli yerel diske indirir ve file URI'sini döner."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
            with open(dest_path, "wb") as f:
                f.write(response.read())
        return dest_path.resolve().as_uri()
    except Exception as e:
        print(f"  [Görsel] İndirme uyarısı ({e}), gradient arka plan kullanılacak.")
        return None

def generate_carousel_from_article(article_json_path: Path, output_base_dir: Optional[Path] = None) -> Optional[CarouselPost]:
    """
    Tek bir makaleyi okur, Gemini ile slayt yapısını ve caption'ını oluşturur,
    puanına göre adlandırılmış klasöre ([PUAN]_id) 1080x1350 PNG ve caption.txt olarak kaydeder.
    """
    try:
        with open(article_json_path, "r", encoding="utf-8") as f:
            art = json.load(f)
    except Exception as e:
        print(f"Hata: {article_json_path.name} okunamadı: {e}")
        return None

    article_id = art.get("id") or article_json_path.stem
    article_url = art.get("url", "")

    print(f"\n🧠 [1/4] Gemini ile Karosel & Caption Üretiliyor: {art.get('title')[:55]}...")
    try:
        ai_data = gemini_rotator.generate_carousel(art)
    except Exception as e:
        print(f"❌ Gemini üretim hatası ({article_id}): {e}")
        return None

    raw_slides = ai_data.get("slides", [])
    if not raw_slides:
        print(f"❌ Slayt verisi boş döndü ({article_id})")
        return None

    puan = int(ai_data.get("puan", 85))
    puan_gerekce = ai_data.get("puan_gerekce", "")
    caption_text = strip_emojis(ai_data.get("caption", ""))

    # Klasör ismine puanı ekle: [94]_makale_id
    folder_name = f"[{puan:02d}]_{article_id}"
    target_dir = (output_base_dir or CAROUSELS_OUTPUT_DIR) / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Görseli yerel diske kaydet
    raw_img_url = extract_best_image_url(art)
    local_bg_uri = None
    if raw_img_url:
        bg_file = target_dir / "bg.jpg"
        local_bg_uri = download_image_locally(raw_img_url, bg_file)

    slides = []
    total_count = len(raw_slides)
    for idx, s in enumerate(raw_slides, 1):
        is_cov = (idx == 1) or s.get("is_cover", False)
        is_last = (idx == total_count)
        
        slide_title = strip_emojis(s.get("title") or s.get("headline") or s.get("heading") or s.get("subtitle") or "Farkındalık")
        slide_tag = strip_emojis(s.get("section_tag") or "FARKINDALIK")
        
        slides.append(CarouselSlide(
            slide_number=idx,
            is_cover=is_cov,
            section_tag=slide_tag,
            title=slide_title,
            subtitle=strip_emojis(s.get("subtitle") or ""),
            body=strip_emojis(s.get("body") or ""),
            highlight_box=strip_emojis(s.get("highlight_box") or ""),
            action_label="KAYDET & PAYLAŞ" if is_last else "KAYDIR →"
        ))

    carousel_post = CarouselPost(
        id=article_id,
        url=article_url,
        category=strip_emojis(ai_data.get("category", "İLİŞKİLER & PSİKOLOJİ")),
        puan=puan,
        puan_gerekce=puan_gerekce,
        total_slides=len(slides),
        cover_image_url=local_bg_uri or raw_img_url,
        slides=slides,
        caption=caption_text
    )

    # 1. caption.txt olarak kaydet
    caption_path = target_dir / "caption.txt"
    with open(caption_path, "w", encoding="utf-8") as cf:
        cf.write(f"=== INSTAGRAM CAPTION (@ya_da_psikoloji) ===\n\n")
        cf.write(carousel_post.caption)
        cf.write(f"\n\n--- Bilgiler ---\n")
        cf.write(f"Puan: {carousel_post.puan}/100\n")
        if carousel_post.puan_gerekce:
            cf.write(f"Gerekçe: {carousel_post.puan_gerekce}\n")
        cf.write(f"Kaynak: {carousel_post.url}\n")

    # 2. carousel.json olarak kaydet
    json_path = target_dir / "carousel.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        jf.write(carousel_post.model_dump_json(indent=2))

    print(f"🎨 [2/4] 1080x1350 PNG Slaytları Render Ediliyor ({len(slides)} Slayt)...")
    rendered_pngs = render_carousel_slides(carousel_post, target_dir)

    print(f"📄 [3/4] Web Önizleme Galerisi Oluşturuluyor...")
    create_preview_gallery(carousel_post, target_dir, rendered_pngs)

    print(f"📝 [4/4] Caption Dosyası Kaydedildi: caption.txt")
    print(f"✅ Karosel başarıyla tamamlandı: {target_dir.name} (Puan: {puan}/100)")
    return carousel_post

def create_preview_gallery(carousel: CarouselPost, target_dir: Path, png_paths: List[Path]):
    """Kullanıcının tarayıcıda tek tıkla tüm slaytları görebileceği modern bir galeri HTML sayfası oluşturur."""
    slide_cards_html = ""
    for idx, png in enumerate(png_paths, 1):
        s_data = carousel.slides[idx-1]
        slide_cards_html += f"""
        <div class="slide-card">
            <div class="slide-header">Slayt #{idx:02d} — <span class="tag">{s_data.section_tag}</span></div>
            <img src="{png.name}" alt="Slayt {idx}" loading="lazy" />
            <div class="slide-desc">
                <strong>{s_data.title}</strong>
                <p>{s_data.body or s_data.subtitle or ''}</p>
                {f'<div class="box">{s_data.highlight_box}</div>' if s_data.highlight_box else ''}
            </div>
        </div>
        """

    caption_formatted = carousel.caption.replace("\n", "<br>")

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[{carousel.puan}] {carousel.category} - @ya_da_psikoloji</title>
<style>
body {{
    margin: 0;
    padding: 40px;
    background: #07090E;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}
.container {{
    max-width: 1400px;
    margin: 0 auto;
}}
.meta-box {{
    background: #11151F;
    padding: 26px 32px;
    border-radius: 16px;
    margin-bottom: 30px;
    border: 1px solid #1E2638;
}}
.badge {{
    display: inline-block;
    background: #F6C90E;
    color: #000;
    padding: 6px 14px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.08em;
    margin-right: 12px;
}}
.puan {{
    display: inline-block;
    background: #38EF7D;
    color: #000;
    padding: 6px 14px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 13px;
}}
.caption-box {{
    background: #0D111A;
    border-left: 4px solid #F6C90E;
    padding: 20px 24px;
    border-radius: 12px;
    margin-top: 20px;
    font-size: 15px;
    line-height: 1.6;
    color: #CBD5E1;
}}
.caption-box h3 {{
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #F6C90E;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.slides-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 30px;
}}
.slide-card {{
    background: #11151F;
    border: 1px solid #1E2638;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}}
.slide-header {{
    padding: 12px 18px;
    background: #161C2A;
    font-size: 13px;
    font-weight: bold;
    color: #94A3B8;
}}
.slide-header .tag {{
    color: #38EF7D;
}}
.slide-card img {{
    width: 100%;
    aspect-ratio: 4/5;
    object-fit: cover;
    display: block;
}}
.slide-desc {{
    padding: 16px 20px;
    font-size: 14px;
    line-height: 1.5;
    color: #CBD5E1;
}}
.slide-desc strong {{
    color: #FFF;
    display: block;
    margin-bottom: 8px;
}}
.slide-desc .box {{
    background: rgba(246, 201, 14, 0.08);
    border-left: 3px solid #F6C90E;
    padding: 8px 12px;
    margin-top: 10px;
    font-size: 12px;
    color: #F6C90E;
}}
</style>
</head>
<body>
<div class="container">
    <div class="meta-box">
        <div>
            <span class="badge">{carousel.category}</span>
            <span class="puan">Viral Puanı: {carousel.puan}/100</span>
        </div>
        <h1 style="margin: 16px 0 8px 0; font-size: 26px;">{carousel.slides[0].title if carousel.slides else ''}</h1>
        <p style="color: #94A3B8; margin: 0 0 15px 0; font-size: 14px;">Hesap: <strong>@ya_da_psikoloji</strong> | Slayt: {carousel.total_slides} | Kaynak: <a href="{carousel.url}" target="_blank" style="color: #38EF7D;">{carousel.url}</a></p>
        
        {f'<p style="color: #38EF7D; font-size: 13px; margin: 0;"><strong>Puanlama Gerekçesi:</strong> {carousel.puan_gerekce}</p>' if carousel.puan_gerekce else ''}

        <div class="caption-box">
            <h3>Instagram Caption (caption.txt)</h3>
            {caption_formatted}
        </div>
    </div>
    
    <div class="slides-grid">
        {slide_cards_html}
    </div>
</div>
</body>
</html>"""

    preview_path = target_dir / "index.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)

def batch_process_carousels(limit: Optional[int] = 5, prioritize_rich: bool = True) -> List[CarouselPost]:
    """Toplu karosel üretimi yapar ve sonuçları listeler."""
    CAROUSELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing_dirs = {d.name for d in CAROUSELS_OUTPUT_DIR.iterdir() if d.is_dir()}
    
    all_json_files = list(MAKALELER_DIR.glob("*.json"))
    
    # Halihazırda üretilmiş makale ID'lerini kontrol et
    done_ids = set()
    for d in existing_dirs:
        # [94]_makale_id formatından makale_id'yi çıkar
        if d.startswith("[") and "]" in d:
            parts = d.split("]_", 1)
            if len(parts) > 1:
                done_ids.add(parts[1])
        else:
            done_ids.add(d)

    pending_files = [f for f in all_json_files if f.stem not in done_ids]
    
    print(f"📊 Toplam Ham Makale: {len(all_json_files)} | Üretilmiş Karosel: {len(done_ids)} | Bekleyen: {len(pending_files)}")
    
    if not pending_files:
        print("Tüm makaleler için karosel zaten oluşturulmuş!")
        return []
        
    if prioritize_rich:
        pending_files.sort(key=lambda p: p.stat().st_size, reverse=True)
        
    if limit:
        pending_files = pending_files[:limit]
        
    print(f"🚀 Bu oturumda {len(pending_files)} adet @ya_da_psikoloji karoseli üretilecek.\n")
    
    results = []
    for idx, f in enumerate(pending_files, 1):
        print(f"[{idx}/{len(pending_files)}] İşleniyor: {f.name}")
        post = generate_carousel_from_article(f)
        if post:
            results.append(post)
            
    print(f"\n🎉 Tamamlandı! {len(results)} karosel üretildi.")
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Instagram Karosel Üretim Motoru (1080x1350 PNG)")
    parser.add_argument("--limit", "-l", type=int, default=2, help="Üretilecek karosel sayısı")
    parser.add_argument("--file", "-f", type=str, default=None, help="Spesifik bir makale JSON dosyası")
    
    args = parser.parse_args()
    if args.file:
        generate_carousel_from_article(Path(args.file))
    else:
        batch_process_carousels(limit=args.limit)
