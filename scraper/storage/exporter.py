import json
import shutil
import atexit
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from models.article import Article
from config.settings import settings

_SAVED_URLS_CACHE: Optional[Set[str]] = None
_CATALOG_DATA_CACHE: Optional[List[Dict[str, Any]]] = None

def get_saved_urls_cache() -> Set[str]:
    """Tüm indirilmiş URL'leri hafızaya alır (RAM önbellek). Her dosya için diske gitmez."""
    global _SAVED_URLS_CACHE
    if _SAVED_URLS_CACHE is None:
        _SAVED_URLS_CACHE = set()
        for jf in settings.MAKALELER_DIR.glob("*.json"):
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    u = data.get("url", "").strip().lower()
                    if u:
                        _SAVED_URLS_CACHE.add(u)
            except Exception:
                pass
    return _SAVED_URLS_CACHE

def save_article(article: Article) -> Dict[str, Path]:
    """
    Article nesnesini doğrudan kök dizindeki 'makaleler/' klasörüne
    hem zengin JSON hem de AI Markdown olarak kaydeder.
    """
    out_dir = settings.MAKALELER_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    file_stem = article.id

    # 1. JSON Kaydetme
    json_path = out_dir / f"{file_stem}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(article.model_dump_json(indent=2))

    # 2. AI-Dostu Formatlanmış Markdown Kaydetme
    md_path = out_dir / f"{file_stem}.md"
    md_content = _build_ai_ready_markdown(article)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Önbelleğe ekle
    if article.url:
        get_saved_urls_cache().add(article.url.strip().lower())

    # Bellekteki katalog listesine de ekle
    _append_to_catalog_cache(article)

    return {
        "json": json_path,
        "markdown": md_path
    }

class BatchArticleSaver:
    """
    SSD Yorgunluğunu Önleyen 5'li Toplu Yazıcı (Batch Saver).
    Makaleleri RAM'de biriktirir, 5 adet olduğunda topluca diske yazar ve kataloğu günceller.
    """
    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size
        self.buffer: List[Article] = []

    def add(self, article: Article) -> bool:
        """
        Makaleyi RAM tamponuna ekler. 
        5 adet dolduğunda diske döker (flush) ve True döner, dolmadıysa False döner.
        """
        self.buffer.append(article)
        if len(self.buffer) >= self.batch_size:
            self.flush()
            return True
        return False

    def flush(self) -> int:
        """Tampondaki tüm makaleleri tek bir blokta diske yazar ve kataloğu günceller."""
        if not self.buffer:
            return 0
        
        flushed_count = len(self.buffer)
        for art in self.buffer:
            try:
                save_article(art)
            except Exception as e:
                pass
        
        self.buffer.clear()
        # Toplu yazım bitince kataloğu RAM'den hızlıca yaz
        write_master_catalog_file()
        return flushed_count

batch_saver = BatchArticleSaver(batch_size=5)
atexit.register(lambda: batch_saver.flush())

def _build_ai_ready_markdown(article: Article) -> str:
    """Yapay zeka ajanı tarafından işlenecek zengin ve düzenli markdown üretir."""
    lines: List[str] = []
    
    lines.append(f"# {article.title}\n")
    if article.subtitle:
        lines.append(f"**Alt Başlık**: {article.subtitle}\n")
        
    lines.append(f"- **Kaynak Platform**: {article.source}")
    if article.blog_name:
        lines.append(f"- **Blog / Kategori**: {article.blog_name}")
    lines.append(f"- **Orijinal URL**: {article.url}")
    if article.author:
        title_str = f" ({article.author_title})" if article.author_title else ""
        lines.append(f"- **Yazar / Uzman**: {article.author}{title_str}")
    if article.reviewer:
        lines.append(f"- **Hakem / Editör**: {article.reviewer}")
    if article.published_date:
        lines.append(f"- **Yayın Tarihi**: {article.published_date}")
    if article.date_modified:
        lines.append(f"- **Son Güncelleme**: {article.date_modified}")
    if article.read_time_minutes:
        lines.append(f"- **Okuma Süresi / Kelime**: ~{article.read_time_minutes} dk ({article.word_count} kelime)")
    if article.topics:
        lines.append(f"- **Konu Etiketleri**: {', '.join(article.topics)}")
    lines.append(f"- **Çekilme Zamanı**: {article.scraped_at}")
    lines.append("\n---\n")

    if article.summary:
        lines.append("## 📌 Giriş / Özet")
        lines.append(article.summary)
        lines.append("\n")

    if article.key_points:
        lines.append("## 🎯 Ana Maddeler & Odak Noktaları (Carousel / Post Çekirdeği)")
        for i, kp in enumerate(article.key_points, 1):
            lines.append(f"{i}. {kp}")
        lines.append("\n")

    if article.images:
        lines.append("## 🖼️ Konuyla İlgili Görseller (Arka Plan & Tasarım İçin)")
        for img in article.images:
            caption_str = f" - *{img.caption}*" if img.caption else ""
            cover_tag = " `[Kapak Görseli]`" if img.is_cover else ""
            lines.append(f"- ![{img.alt or 'Görsel'}]({img.url}){cover_tag}{caption_str}")
        lines.append("\n")

    lines.append("## 📝 Makale Bölümleri ve Detaylı İçerik\n")
    if article.sections:
        for sec in article.sections:
            lines.append(f"### {sec.heading}\n")
            lines.append(f"{sec.content}\n")
            if sec.items:
                lines.append("**Alt Maddeler:**")
                for itm in sec.items:
                    lines.append(f"- {itm}")
                lines.append("\n")
    else:
        lines.append(article.raw_markdown)

    return "\n".join(lines)

def list_saved_articles() -> List[Path]:
    """Tüm kayıtlı JSON dosyalarını listeler."""
    return list(settings.MAKALELER_DIR.glob("*.json"))

def migrate_existing_data():
    """Mevcut 'data/' içindeki tüm JSON ve Markdown dosyalarını doğrudan 'makaleler/' klasörüne taşır/kopyalar."""
    settings.MAKALELER_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. JSON dosyalarını taşı
    for jf in settings.DATA_DIR.glob("*/json/*.json"):
        target_json = settings.MAKALELER_DIR / jf.name
        if not target_json.exists():
            shutil.copy2(str(jf), str(target_json))

    # 2. Markdown dosyalarını taşı
    for mf in settings.DATA_DIR.glob("*/markdown/*.md"):
        target_md = settings.MAKALELER_DIR / mf.name
        if not target_md.exists():
            shutil.copy2(str(mf), str(target_md))

CATALOG_INDEX_FILE = settings.DATA_DIR / "catalog_index.json"

def _load_catalog_cache() -> List[Dict[str, Any]]:
    """Katalog metaverilerini diskteki tek bir özet indeks dosyasından yükler (0.02 sn). 5000 dosyayı tek tek açmaz!"""
    global _CATALOG_DATA_CACHE
    if _CATALOG_DATA_CACHE is not None:
        return _CATALOG_DATA_CACHE

    if CATALOG_INDEX_FILE.exists():
        try:
            with open(CATALOG_INDEX_FILE, "r", encoding="utf-8") as f:
                _CATALOG_DATA_CACHE = json.load(f)
                return _CATALOG_DATA_CACHE
        except Exception:
            pass

    json_files = list(settings.MAKALELER_DIR.glob("*.json"))
    articles_data = []

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                articles_data.append({
                    "title": data.get("title", ""),
                    "published_date": data.get("published_date"),
                    "scraped_at": data.get("scraped_at", ""),
                    "source": data.get("source", ""),
                    "blog_name": data.get("blog_name"),
                    "key_points": data.get("key_points", []),
                    "images": data.get("images", []),
                    "read_time_minutes": data.get("read_time_minutes", 1),
                    "_file_stem": jf.stem
                })
        except Exception:
            pass

    _CATALOG_DATA_CACHE = articles_data
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CATALOG_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(articles_data, f, ensure_ascii=False)
    except Exception:
        pass

    return _CATALOG_DATA_CACHE

def _append_to_catalog_cache(article: Article):
    """Yeni inen makaleyi doğrudan RAM'deki katalog listesine ekler."""
    global _CATALOG_DATA_CACHE
    if _CATALOG_DATA_CACHE is not None:
        data = {
            "title": article.title,
            "published_date": article.published_date,
            "scraped_at": article.scraped_at,
            "source": article.source,
            "blog_name": article.blog_name,
            "key_points": article.key_points,
            "images": article.images,
            "read_time_minutes": article.read_time_minutes,
            "_file_stem": article.id
        }
        # Varsa güncelle, yoksa ekle
        existing_idx = next((i for i, d in enumerate(_CATALOG_DATA_CACHE) if d.get("_file_stem") == article.id), None)
        if existing_idx is not None:
            _CATALOG_DATA_CACHE[existing_idx] = data
        else:
            _CATALOG_DATA_CACHE.append(data)

def write_master_catalog_file() -> Path:
    """RAM'deki katalog indeksini KATALOG.md dosyasına tek seferde yazar (Diski yormaz)."""
    articles_data = _load_catalog_cache()

    def get_sort_key(item: dict) -> str:
        pub = item.get("published_date") or ""
        if pub and len(pub) >= 7:
            return pub
        return item.get("scraped_at", "")

    sorted_articles = sorted(articles_data, key=get_sort_key, reverse=True)

    catalog_path = settings.KATALOG_PATH
    lines: List[str] = []
    lines.append("# 📚 İndirilen Makaleler Kataloğu (En Yeniler En Üstte)\n")
    lines.append(f"**Toplam Makale Sayısı:** {len(sorted_articles)} Adet  ")
    lines.append(f"**Makaleler Klasörü:** [`makaleler/`](file:///./makaleler)  \n")
    lines.append("---\n")
    lines.append("| # | Yayın Tarihi | Kaynak | Kategori / Blog | Başlık | Madde | Görsel | Okuma Süresi | Dosyalar |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for i, a in enumerate(sorted_articles, 1):
        pub = a.get("published_date") or a.get("scraped_at", "")[:10]
        short_date = pub[:10] if len(pub) >= 10 else pub
        source = a.get("source", "Bilinmiyor")
        blog = a.get("blog_name") or "-"
        title = a.get("title", "Başlıksız").replace("|", "-")
        kp_count = len(a.get("key_points", []))
        img_count = len(a.get("images", []))
        read_time = f"{a.get('read_time_minutes', 1)} dk"
        stem = a.get("_file_stem", "")

        md_rel = f"makaleler/{stem}.md"
        json_rel = f"makaleler/{stem}.json"
        dosya_linki = f"[MD]({md_rel}) • [JSON]({json_rel})"

        lines.append(f"| {i} | `{short_date}` | **{source}** | `{blog}` | {title} | {kp_count} | {img_count} | {read_time} | {dosya_linki} |")

    lines.append("\n---\n")
    lines.append("> 💡 **Kullanım:** Yukarıdaki tablodan istediğiniz makalenin [MD] veya [JSON] linkine tıklayarak doğrudan içeriğine gidebilir, sosyal medya postlarınız veya carousel tasarımlarınız için içerikten faydalanabilirsiniz.\n")

    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    try:
        with open(CATALOG_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_articles, f, ensure_ascii=False)
    except Exception:
        pass

    return catalog_path

def build_master_catalog() -> Path:
    """Dışarıdan çağrılan katalog derleyici."""
    return write_master_catalog_file()

def reorganize_and_clean_data_dir():
    """Tüm eski verileri makaleler/ altına toplar ve kataloğu yeniler."""
    migrate_existing_data()
    build_master_catalog()

_STATS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None

def get_source_stats(force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Her kaynağın kaç makale indirdiğini ve yaklaşık kaç makalenin sırada beklediğini hesaplar.
    """
    global _STATS_CACHE
    if _STATS_CACHE is not None and not force_refresh:
        return _STATS_CACHE

    stats = {
        "Psychology Today": {"indirilen": 0, "toplam_tahmini": 5000, "kaynak_tipi": "276 Popüler Blog"},
        "Simply Psychology": {"indirilen": 0, "toplam_tahmini": 1486, "kaynak_tipi": "Resmi Sitemap"},
        "The Decision Lab": {"indirilen": 0, "toplam_tahmini": 200, "kaynak_tipi": "Önyargılar & Kararlar"},
        "Changing Minds": {"indirilen": 0, "toplam_tahmini": 299, "kaynak_tipi": "Psikoloji Teorileri"}
    }

    # Hızlı sayım: JSON dosyalarını tara
    for jf in settings.MAKALELER_DIR.glob("*.json"):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                src = data.get("source", "")
                if src in stats:
                    stats[src]["indirilen"] += 1
                elif "Psychology Today" in src:
                    stats["Psychology Today"]["indirilen"] += 1
                elif "Simply" in src:
                    stats["Simply Psychology"]["indirilen"] += 1
                elif "Decision" in src:
                    stats["The Decision Lab"]["indirilen"] += 1
                elif "Changing" in src:
                    stats["Changing Minds"]["indirilen"] += 1
        except Exception:
            pass

    for k, v in stats.items():
        v["kalan"] = max(0, v["toplam_tahmini"] - v["indirilen"])
        if v["toplam_tahmini"] > 0:
            v["yuzde"] = min(100.0, round((v["indirilen"] / v["toplam_tahmini"]) * 100, 1))
        else:
            v["yuzde"] = 0.0

    _STATS_CACHE = stats
    return stats
