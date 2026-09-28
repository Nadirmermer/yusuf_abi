import re
import json
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from bs4 import BeautifulSoup
from scrapers.network import network_client
from scrapers.changing_minds import ChangingMindsScraper
from scrapers.decision_lab import TheDecisionLabScraper
from config.settings import settings

logger = logging.getLogger("Crawler")
logger.setLevel(logging.ERROR)

# Kullanıcının özellikle belirttiği 4 ana blog
CORE_PSYCHOLOGY_TODAY_BLOGS = [
    "unhitched",
    "quirks-of-memory",
    "wire-your-mind-for-love",
    "in-practice"
]

# Psychology Today'in tüm temel konu alanları
PT_TOPIC_LIST = [
    "relationships", "dating", "marriage", "divorce", "attachment",
    "memory", "neuroscience", "artificial-intelligence", "cognition",
    "narcissism", "anxiety", "depression", "trauma", "stress", "grief",
    "child-development", "parenting", "family-dynamics",
    "happiness", "personality", "adhd", "addiction", "sleep", "emotions"
]

# Simply Psychology Kategori ve Bölümleri
SIMPLY_PSYCHOLOGY_CATEGORIES = [
    ("Relationships", "https://www.simplypsychology.org/how-to-have-a-better-relationship"),
    ("Adult Attachment", "https://www.simplypsychology.org/how-to-have-a-better-relationship/adult-attachment"),
    ("Dating Tips", "https://www.simplypsychology.org/how-to-have-a-better-relationship/dating-tips-and-strategies"),
    ("Unhealthy Relationships", "https://www.simplypsychology.org/how-to-have-a-better-relationship/signs-that-youre-in-an-unhealthy-relationship"),
    ("Theories", "https://www.simplypsychology.org/theories"),
    ("Experiments & Key Studies", "https://www.simplypsychology.org/theories/famous-psychological-experiments"),
    ("Biopsychology", "https://www.simplypsychology.org/theories/biological-approach"),
    ("Cognitive Psychology", "https://www.simplypsychology.org/theories/cognitive-science"),
    ("Learning Theories", "https://www.simplypsychology.org/theories/learning-theories"),
    ("Personality", "https://www.simplypsychology.org/theories/personality"),
    ("Social Psychology", "https://www.simplypsychology.org/theories/social-science"),
    ("Self-Care & Anxiety", "https://www.simplypsychology.org/self-care/how-to-deal-with-anxiety"),
    ("ADHD", "https://www.simplypsychology.org/self-care/adhd"),
    ("Emotions", "https://www.simplypsychology.org/self-care/emotions")
]

class UniversalArchiveCrawler:
    """Tüm kaynaklardaki yüzlerce blogu ve binlerce makaleyi keşfeden ve yöneten evrensel crawler motoru."""

    def __init__(self):
        self.discovered_file = settings.DATA_DIR / "discovered_universe.json"

    def discover_all_pt_blogs(self, force_refresh: bool = False) -> List[str]:
        """Psychology Today'deki tüm blog slug'larını çıkarır veya önbellekten okur."""
        pt_blogs_file = settings.DATA_DIR / "psychology_today_blogs.txt"
        if not force_refresh and pt_blogs_file.exists():
            with open(pt_blogs_file, "r", encoding="utf-8") as f:
                slugs = [line.strip().split("/blog/")[-1].strip() for line in f if "/blog/" in line]
            if slugs:
                return sorted(list(set(slugs)))

        all_slugs: Set[str] = set(CORE_PSYCHOLOGY_TODAY_BLOGS)

        # 1. Ana sayfa
        try:
            r_home = network_client.fetch("https://www.psychologytoday.com/us")
            for s in re.findall(r'/us/blog/([a-zA-Z0-9\-]+)(?:/|\b|\?)', r_home.text):
                clean_s = s.strip().lower()
                if clean_s and not any(bad in clean_s for bad in ["index", "archive", "search", "docs", "basics", "tests"]):
                    all_slugs.add(clean_s)
        except Exception as e:
            logger.warning(f"Ana sayfa blog taramasında hata: {e}")

        # 2. Tüm Topic sayfaları
        for topic in PT_TOPIC_LIST:
            url = f"https://www.psychologytoday.com/us/basics/{topic}"
            try:
                resp = network_client.fetch(url)
                found = re.findall(r'/us/blog/([a-zA-Z0-9\-]+)(?:/|\b|\?)', resp.text)
                for s in found:
                    clean_s = s.strip().lower()
                    if clean_s and not any(bad in clean_s for bad in ["index", "archive", "search", "docs", "basics", "tests"]):
                        all_slugs.add(clean_s)
                logger.info(f"Konu '{topic}' tarandı -> Şu ana kadar toplam {len(all_slugs)} blog keşfedildi.")
            except Exception as e:
                logger.warning(f"Konu '{topic}' taranamadı: {e}")

        # Blog listesini dosyaya kaydet
        blog_list = sorted(list(all_slugs))
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        pt_blogs_file = settings.DATA_DIR / "psychology_today_blogs.txt"
        try:
            with open(pt_blogs_file, "w", encoding="utf-8") as f:
                for b in blog_list:
                    f.write(f"https://www.psychologytoday.com/us/blog/{b}\n")
        except Exception:
            pass
        return blog_list

    def discover_pt_blog_articles(self, blog_slug: str, max_pages: Optional[int] = None, stop_on_existing: bool = False) -> List[Dict[str, Any]]:
        """
        Bir Psychology Today blogunun makalelerini çıkarır.
        stop_on_existing=True ise ve ilk sayfadaki makaleler zaten kayıtlıysa sonraki sayfalara gitmez (hızlı yeni kontrolü).
        max_pages=None ise blogdaki tüm sayfaları sonuna kadar çeker.
        """
        from storage.exporter import get_saved_urls_cache
        saved_cache = get_saved_urls_cache()

        discovered = []
        seen = set()
        base_url = f"https://www.psychologytoday.com/us/blog/{blog_slug}"
        page = 0
        consecutive_empty = 0

        while True:
            if max_pages is not None and page >= max_pages:
                break

            current_url = base_url if page == 0 else f"{base_url}?page={page}"
            try:
                resp = network_client.fetch(current_url)
                pattern = rf'(?:https://www\.psychologytoday\.com)?/us/blog/{blog_slug}/(\d{{6}})/([a-zA-Z0-9\-]+)'
                matches = re.findall(pattern, resp.text)

                new_count = 0
                has_unsaved = False

                for yyyymm, slug in matches:
                    full_url = f"https://www.psychologytoday.com/us/blog/{blog_slug}/{yyyymm}/{slug}"
                    if full_url not in seen:
                        seen.add(full_url)
                        new_count += 1
                        date_est = f"{yyyymm[:4]}-{yyyymm[4:6]}"
                        is_saved = full_url.strip().lower() in saved_cache
                        if not is_saved:
                            has_unsaved = True

                        discovered.append({
                            "url": full_url,
                            "source": "Psychology Today",
                            "blog": blog_slug,
                            "date_estimate": date_est,
                            "slug": slug,
                            "is_already_saved": is_saved
                        })

                if new_count == 0:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        break
                else:
                    consecutive_empty = 0

                # Hızlı modda ilk sayfadaki her şey zaten kayıtlıysa eski sayfalara vakit harcama
                if stop_on_existing and page == 0 and not has_unsaved and new_count > 0:
                    break

                page += 1
            except Exception as e:
                break

        return sorted(discovered, key=lambda x: str(x.get("date_estimate", "")), reverse=True)

    def discover_simply_psychology_all(self, use_sitemap: bool = True) -> List[Dict[str, Any]]:
        """
        Simply Psychology'deki makaleleri keşfeder.
        use_sitemap=True olduğunda sitemap üzerinden istisnasız 1.486 makalenin TAMAMINI çeker.
        """
        discovered = []
        seen = set()

        if use_sitemap:
            sitemap_urls = [
                "https://www.simplypsychology.org/post-sitemap1.xml",
                "https://www.simplypsychology.org/post-sitemap2.xml"
            ]
            for sm_url in sitemap_urls:
                try:
                    resp = network_client.fetch(sm_url)
                    # Markdown veya XML formatından URL ve tarihleri ayıkla
                    # Regex: https://www.simplypsychology.org/xxx.html
                    found_urls = re.findall(r'https://www\.simplypsychology\.org/([a-zA-Z0-9_\-]+)\.html', resp.text)
                    dates = re.findall(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2})', resp.text)

                    for i, slug in enumerate(found_urls):
                        full_url = f"https://www.simplypsychology.org/{slug}.html"
                        if any(bad in slug for bad in ["privacy", "about", "contact", "author", "editorial", "terms", "advertise"]):
                            continue
                        if full_url not in seen:
                            seen.add(full_url)
                            date_est = dates[i][:10] if i < len(dates) else "2026-09-01"
                            title = slug.replace("-", " ").title()
                            discovered.append({
                                "url": full_url,
                                "source": "Simply Psychology",
                                "category": "General Psychology",
                                "title": title,
                                "date_estimate": date_est
                            })
                except Exception as e:
                    logger.warning(f"Sitemap {sm_url} çekilemedi: {e}")

            if discovered:
                return sorted(discovered, key=lambda x: str(x.get("date_estimate", "")), reverse=True)

        # Fallback: Kategori sayfaları
        for cat_name, cat_url in SIMPLY_PSYCHOLOGY_CATEGORIES:
            try:
                resp = network_client.fetch(cat_url)
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.endswith(".html") and "simplypsychology.org" in href:
                        if any(bad in href for bad in ["privacy", "about", "contact", "author", "editorial"]):
                            continue
                        if href not in seen:
                            seen.add(href)
                            title = a.get_text(strip=True)
                            discovered.append({
                                "url": href,
                                "source": "Simply Psychology",
                                "category": cat_name,
                                "title": title if len(title) > 3 else None,
                                "date_estimate": "2026-09"
                            })
            except Exception as e:
                pass

        return discovered

    def discover_decision_lab_all(self) -> List[Dict[str, Any]]:
        """The Decision Lab'in tüm içeriklerini (116 Önyargı + 45 Big Problems + Insights) keşfeder."""
        discovered = []
        seen = set()

        # Biases
        try:
            biases = TheDecisionLabScraper.extract_biases_links()
            for b in biases:
                if b["url"] not in seen:
                    seen.add(b["url"])
                    discovered.append({
                        "url": b["url"],
                        "source": "The Decision Lab",
                        "category": "Cognitive Biases",
                        "title": b["name"],
                        "date_estimate": "2026-08"
                    })
        except Exception:
            pass

        # Big Problems & Insights
        for sec_name, sec_url in [("Big Problems", "https://thedecisionlab.com/big-problems"), ("Insights", "https://thedecisionlab.com/behavioral-insights")]:
            try:
                resp = network_client.fetch(sec_url)
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if any(prefix in href for prefix in ["/big-problems/", "/insights/"]):
                        if href.endswith("/big-problems") or href.endswith("/behavioral-insights"):
                            continue
                        full_url = href if href.startswith("http") else f"https://thedecisionlab.com{href}"
                        if full_url not in seen:
                            seen.add(full_url)
                            discovered.append({
                                "url": full_url,
                                "source": "The Decision Lab",
                                "category": sec_name,
                                "date_estimate": "2026-09"
                            })
            except Exception:
                pass

        return discovered

    def discover_changing_minds_all(self) -> List[Dict[str, Any]]:
        """Changing Minds sitesindeki 299 teoriyi çıkarır."""
        discovered = []
        try:
            theories = ChangingMindsScraper.extract_index_links()
            for t in theories:
                discovered.append({
                    "url": t["url"],
                    "source": "Changing Minds",
                    "category": "Theories",
                    "title": t["name"],
                    "date_estimate": "2025-01"
                })
        except Exception:
            pass
        return discovered

    def discover_entire_universe(self, max_blogs: Optional[int] = None, max_pages_per_blog: Optional[int] = 3) -> List[Dict[str, Any]]:
        """
        Tüm kaynaklardaki tüm makaleleri keşfeder, tarihe göre sıralar ve havuz dosyasına kaydeder.
        """
        universe: List[Dict[str, Any]] = []
        seen_urls = set()

        # 1. Simply Psychology
        logger.info("=== Simply Psychology Keşfi Başlıyor ===")
        sp_items = self.discover_simply_psychology_all()
        for itm in sp_items:
            if itm["url"] not in seen_urls:
                seen_urls.add(itm["url"])
                universe.append(itm)

        # 2. The Decision Lab
        logger.info("=== The Decision Lab Keşfi Başlıyor ===")
        dl_items = self.discover_decision_lab_all()
        for itm in dl_items:
            if itm["url"] not in seen_urls:
                seen_urls.add(itm["url"])
                universe.append(itm)

        # 3. Changing Minds
        logger.info("=== Changing Minds Keşfi Başlıyor ===")
        cm_items = self.discover_changing_minds_all()
        for itm in cm_items:
            if itm["url"] not in seen_urls:
                seen_urls.add(itm["url"])
                universe.append(itm)

        # 4. Psychology Today Tüm Bloglar
        logger.info("=== Psychology Today Blogları Keşfediliyor ===")
        all_pt_blogs = self.discover_all_pt_blogs()
        if max_blogs:
            all_pt_blogs = all_pt_blogs[:max_blogs]

        for i, blog_slug in enumerate(all_pt_blogs, 1):
            logger.info(f"[{i}/{len(all_pt_blogs)}] PT Blog taranıyor: {blog_slug}")
            articles = self.discover_pt_blog_articles(blog_slug, max_pages=max_pages_per_blog)
            for itm in articles:
                if itm["url"] not in seen_urls:
                    seen_urls.add(itm["url"])
                    universe.append(itm)

        # Tarihsel Sıralama (En yeni yayınlanan en üstte)
        sorted_universe = sorted(
            universe,
            key=lambda x: str(x.get("date_estimate", "1900-01")),
            reverse=True
        )

        # Havuz dosyasına kaydet
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.discovered_file, "w", encoding="utf-8") as f:
                json.dump(sorted_universe, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return sorted_universe

crawler = UniversalArchiveCrawler()
