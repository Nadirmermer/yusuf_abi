import re
import json
import base64
from pathlib import Path
from typing import List, Optional
from jinja2 import Template
from playwright.sync_api import sync_playwright

from analyzer.carousel_models import CarouselPost, CarouselSlide

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AVATAR_PATH = PROJECT_ROOT / "analyzer" / "assets" / "logo.jpg"
if not AVATAR_PATH.exists():
    AVATAR_PATH = PROJECT_ROOT / "analyzer" / "assets" / "avatar.jpg"



SLIDE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  width: 1080px;
  height: 1350px;
  background-color: #07090E;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #FFFFFF;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 85px 80px;
}

/* Arka Plan Görseli ve Karanlık Overlay */
.bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  {% if bg_image_url %}
  background-image: url('{{ bg_image_url }}');
  background-size: cover;
  background-position: center;
  filter: brightness(0.82) saturate(1.1) contrast(1.05);
  transform: scale(1.03);
  {% else %}
  background: radial-gradient(circle at 80% 20%, #151C28 0%, #07090E 70%);
  {% endif %}
  z-index: 0;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, 
    rgba(7, 9, 14, {{ (overlay_opacity * 0.5) | round(2) }}) 0%, 
    rgba(7, 9, 14, {{ (overlay_opacity * 0.35) | round(2) }}) 35%, 
    rgba(7, 9, 14, {{ overlay_opacity | round(2) }}) 72%, 
    rgba(4, 5, 8, 0.96) 100%);
  z-index: 1;
}

/* Dekoratif Işık Hüzmesi (Glow) */
.ambient-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  top: 8%;
  right: -150px;
  background: radial-gradient(circle, rgba(246, 201, 14, 0.11) 0%, rgba(56, 239, 125, 0.04) 45%, transparent 70%);
  border-radius: 50%;
  z-index: 1;
  pointer-events: none;
}

.ambient-glow-bottom {
  position: absolute;
  width: 500px;
  height: 500px;
  bottom: 4%;
  left: -120px;
  background: radial-gradient(circle, rgba(56, 239, 125, 0.07) 0%, transparent 65%);
  border-radius: 50%;
  z-index: 1;
  pointer-events: none;
}

/* Üst Bar */
.header-bar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.category-badge {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  padding: 10px 24px;
  border-radius: 999px;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #F6C90E;
}

.slide-counter {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #94A3B8;
  letter-spacing: 0.1em;
  background: rgba(0, 0, 0, 0.5);
  padding: 8px 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.slide-counter span {
  color: #FFFFFF;
}

/* Ana İçerik Bloğu */
.content-wrapper {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin: auto 0;
  gap: 32px;
}

.section-tag {
  font-size: 20px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #38EF7D;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-tag::before {
  content: "";
  display: inline-block;
  width: 28px;
  height: 4px;
  background: #38EF7D;
  border-radius: 2px;
}

.main-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.22;
  letter-spacing: -0.025em;
  color: #FFFFFF;
  text-wrap: balance;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.75);
}

.main-title .highlight {
  color: #F6C90E;
  display: inline;
}

.hook-subtitle {
  font-size: 34px;
  font-weight: 500;
  line-height: 1.55;
  color: #CBD5E1;
  border-left: 5px solid #38EF7D;
  padding-left: 24px;
  margin-top: 10px;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.75);
}

.main-body {
  font-size: 32px;
  font-weight: 400;
  line-height: 1.62;
  color: #E2E8F0;
  letter-spacing: -0.01em;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.65);
}

.highlight-box {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-left: 6px solid #F6C90E;
  border-radius: 16px;
  padding: 28px 34px;
  font-size: 29px;
  font-weight: 600;
  line-height: 1.5;
  color: #F8FAFC;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

/* Kapak Özel Tasarımı (Slide 1) */
.is-cover .main-title {
  font-size: 72px;
  line-height: 1.14;
  letter-spacing: -0.035em;
}

/* Alt Bar (Footer) */
.footer-bar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.author-brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar-img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: #000000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.avatar-fallback {
  width: 46px;
  height: 46px;
  background: #111;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 20px;
  color: #FFFFFF;
}

.handle {
  font-size: 22px;
  font-weight: 700;
  color: #E2E8F0;
  letter-spacing: 0.02em;
}

.action-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(246, 201, 14, 0.14);
  border: 1px solid rgba(246, 201, 14, 0.4);
  color: #F6C90E;
  padding: 12px 26px;
  border-radius: 999px;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

/* İlerleme Çubuğu (En Altta) */
.progress-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 7px;
  background: rgba(255, 255, 255, 0.08);
  z-index: 10;
}

.progress-fill {
  height: 100%;
  width: {{ progress_pct }}%;
  background: linear-gradient(90deg, #38EF7D, #F6C90E);
  box-shadow: 0 0 12px rgba(246, 201, 14, 0.6);
}
</style>
</head>
<body>

<div class="bg-image"></div>
<div class="gradient-overlay"></div>
<div class="ambient-glow"></div>
<div class="ambient-glow-bottom"></div>

<!-- Üst Bilgi -->
<div class="header-bar">
  <div class="category-badge">
    <span>{{ category }}</span>
  </div>
  <div class="slide-counter">
    <span>{{ '%02d' % current_slide }}</span> / {{ '%02d' % total_slides }}
  </div>
</div>

<!-- Ana İçerik -->
<div class="content-wrapper {{ 'is-cover' if is_cover else '' }}">
  {% if section_tag %}
  <div class="section-tag">{{ section_tag }}</div>
  {% endif %}

  <h1 class="main-title">{{ title_html | safe }}</h1>

  {% if is_cover and subtitle %}
  <div class="hook-subtitle">{{ subtitle }}</div>
  {% endif %}

  {% if body %}
  <div class="main-body">{{ body | safe }}</div>
  {% endif %}

  {% if highlight_box %}
  <div class="highlight-box">{{ highlight_box | safe }}</div>
  {% endif %}
</div>

<!-- Alt Bar -->
<div class="footer-bar">
  <div class="author-brand">
    {% if avatar_url %}
    <img src="{{ avatar_url }}" class="avatar-img" alt="ya da psikoloji" />
    {% else %}
    <div class="avatar-fallback">Y</div>
    {% endif %}
    <div class="handle">@ya_da_psikoloji</div>
  </div>
  <div class="action-pill">
    {{ action_label }}
  </div>
</div>

<!-- İlerleme Çubuğu -->
<div class="progress-container">
  <div class="progress-fill"></div>
</div>

</body>
</html>
"""

def strip_emojis(text: str) -> str:
    """Metindeki tüm emojileri ve süs ikonlarını tamamen temizler."""
    if not text:
        return ""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        u"\U00002600-\U000026FF"  # miscellaneous symbols
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub(r'', text)
    return cleaned.strip()

def format_text_html(text: Optional[str]) -> str:
    if not text:
        return ""
    text = strip_emojis(text)
    # Bold **text** -> <strong style="color: #FFFFFF; font-weight: 700;">text</strong>
    t = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #FFFFFF; font-weight: 700;">\1</strong>', text)
    # Satır sonları -> <br>
    t = t.replace('\n', '<br>')
    return t

def render_carousel_slides(carousel: CarouselPost, output_dir: Path) -> List[Path]:
    """
    Bir Karosel nesnesinin tüm slaytlarını 1080x1350 PNG dosyaları olarak üretir.
    Tek bir Playwright tarayıcı oturumunda sırayla render ederek maksimum hız ve kararlılık sağlar.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    template = Template(SLIDE_HTML_TEMPLATE)
    total = carousel.total_slides
    avatar_data_url = None
    if AVATAR_PATH.exists():
        try:
            with open(AVATAR_PATH, "rb") as af:
                avatar_data_url = f"data:image/jpeg;base64,{base64.b64encode(af.read()).decode('utf-8')}"
        except Exception:
            avatar_data_url = None
    
    # Bellekte HTML şablonlarını hazırla
    rendered_image_paths = []
    slide_contents = []
    for s in carousel.slides:
        progress_pct = int((s.slide_number / total) * 100)
        html = template.render(
            category=strip_emojis(carousel.category),
            current_slide=s.slide_number,
            total_slides=total,
            progress_pct=progress_pct,
            is_cover=s.is_cover,
            section_tag=strip_emojis(s.section_tag),
            title_html=strip_emojis(s.title),
            subtitle=strip_emojis(s.subtitle or ""),
            body=format_text_html(s.body),
            highlight_box=format_text_html(s.highlight_box),
            action_label=strip_emojis(s.action_label),
            bg_image_url=carousel.cover_image_url,
            avatar_url=avatar_data_url,
            overlay_opacity=getattr(carousel, 'overlay_opacity', 0.55)
        )
        slide_contents.append((s.slide_number, html))

    # Tek Playwright oturumunda tüm slaytları doğrudan bellekten ekran görüntüsü al
    launch_kwargs = {
        "headless": True,
        "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        
        for num, html in slide_contents:
            img_path = output_dir / f"slide_{num}.png"
            page.set_content(html, wait_until="domcontentloaded")
            try:
                page.evaluate("document.fonts.ready")
            except Exception:
                pass
            page.screenshot(path=str(img_path.resolve()), type="png")
            rendered_image_paths.append(img_path)
                
        browser.close()
        
    return rendered_image_paths
