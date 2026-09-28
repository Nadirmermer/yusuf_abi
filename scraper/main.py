import argparse
import sys
import logging
import warnings
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)
# Scraper dizinini sys.path'e ekle
SCRAPER_DIR = Path(__file__).resolve().parent
if str(SCRAPER_DIR) not in sys.path:
    sys.path.insert(0, str(SCRAPER_DIR))

from scrapers import get_scraper, ChangingMindsScraper, TheDecisionLabScraper
from scrapers.crawler import crawler, CORE_PSYCHOLOGY_TODAY_BLOGS, PT_TOPIC_LIST
from storage.exporter import (
    save_article, list_saved_articles, build_master_catalog, 
    reorganize_and_clean_data_dir, get_saved_urls_cache, batch_saver
)
from config.settings import settings

console = Console()

def is_already_saved(url: str) -> bool:
    """Verilen URL'nin daha önceden indirilip indirilmediğini RAM önbellekten anında kontrol eder."""
    return url.strip().lower() in get_saved_urls_cache()

def process_single_url(url: str, force_jina: bool = False, quiet: bool = False, use_batch: bool = False):
    """Tek bir URL'yi çeker, uygun parser'ı çalıştırır ve kaydeder."""
    clean_url = url.strip()
    if not clean_url or clean_url.startswith("#"):
        return None

    if not quiet:
        console.print(f"\n[bold cyan]🔍 URL İşleniyor:[/bold cyan] {clean_url}")
    scraper = get_scraper(clean_url)
    if not quiet:
        console.print(f"[dim]⚡ Seçilen Scraper Motoru:[/dim] [green]{scraper.source_name}[/green]")

    try:
        article = scraper.scrape(clean_url, force_jina=force_jina)
        if use_batch:
            did_flush = batch_saver.add(article)
            if did_flush and not quiet:
                console.print("[dim green]💾 [SSD Koruma] 5 makale blok halinde diske yazıldı ve katalog güncellendi.[/dim green]")
            paths = {"json": settings.MAKALELER_DIR / f"{article.id}.json", "markdown": settings.MAKALELER_DIR / f"{article.id}.md"}
        else:
            paths = save_article(article)
        
        if not quiet:
            table = Table(title="✅ İçerik Başarıyla Çekildi ve Kaydedildi", show_header=True, header_style="bold magenta")
            table.add_column("Özellik", style="cyan", width=20)
            table.add_column("Değer", style="white")

            table.add_row("Başlık", article.title)
            table.add_row("Kaynak", article.source)
            table.add_row("Blog Serisi", article.blog_name or "-")
            table.add_row("Yazar", f"{article.author or '-'} {f'({article.author_title})' if article.author_title else ''}")
            table.add_row("Hakem / Editör", article.reviewer or "-")
            table.add_row("Yayın Tarihi", article.published_date or "-")
            table.add_row("Okuma Süresi", f"~{article.read_time_minutes} dk ({article.word_count} kelime)")
            table.add_row("Bölüm Sayısı", str(len(article.sections)))
            table.add_row("Madde / Çıkarım", str(len(article.key_points)))
            table.add_row("Görsel Sayısı", str(len(article.images)))
            table.add_row("JSON Çıktısı", str(paths["json"].relative_to(settings.BASE_DIR)))
            table.add_row("Markdown Çıktısı", str(paths["markdown"].relative_to(settings.BASE_DIR)))

            console.print(table)

            if article.key_points:
                console.print("\n[bold yellow]🎯 Öne Çıkan Maddeler (AI Parafraze Odakları):[/bold yellow]")
                for i, kp in enumerate(article.key_points[:7], 1):
                    console.print(f"  [green]{i}.[/green] {kp}")

        return article
    except Exception as e:
        if not quiet:
            console.print(f"[bold red]❌ Hata oluştu ({clean_url}):[/bold red] {e}")
        return None

def batch_crawl(items: list, limit: int = None):
    """Verilen link listesini tarihsel sırayla çeker ve kataloğu günceller."""
    if limit:
        items = items[:limit]

    console.print(f"\n[bold green]🚀 Toplam {len(items)} makale işlenmek üzere sıraya alındı (En yeni tarihten başlanıyor).[/bold green]\n")
    
    success = 0
    skipped = 0
    errors = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Makaleler Çekiliyor...", total=len(items))

        for item in items:
            url = item["url"]
            source = item.get("source", "")
            title = item.get("title") or item.get("slug") or url.split("/")[-1]

            if is_already_saved(url):
                progress.console.print(f"[dim]⏩ Zaten İndirilmiş (Atlandı): {title[:45]} ({source})[/dim]")
                skipped += 1
                progress.advance(task)
                continue

            progress.update(task, description=f"[cyan]Çekiliyor: {title[:35]}...")
            art = process_single_url(url, quiet=True, use_batch=True)
            if art:
                success += 1
                progress.console.print(f"[green]✔ İndirildi: {art.title[:45]} [{art.published_date or item.get('date_estimate') or '-'}] ({source})[/green]")
            else:
                errors += 1
                progress.console.print(f"[red]✖ Başarısız: {url}[/red]")

            progress.advance(task)

    # Tamponda bekleyen son makaleleri diske dök
    batch_saver.flush()
    console.print(f"\n[bold green]İşlem Tamamlandı! Başarılı: {success} | Önceden Kayıtlı: {skipped} | Hatalı: {errors}[/bold green]")
    
    # Master kataloğu güncelle
    cat_path = build_master_catalog()
    console.print(f"[bold cyan]📚 Master Katalog Güncellendi:[/bold cyan] [green]{cat_path.relative_to(settings.BASE_DIR)}[/green]\n")

def crawl_all_continuous(limit: int = None, max_pages: int = 10, only_new: bool = False):
    """
    Tüm kaynakları (Simply Psychology, Psychology Today 276 blog, The Decision Lab, Changing Minds)
    sırayla tarar; bulduğu makaleyi bekletmeden ANINDA indirir ve kataloğu günceller.
    only_new=True ise: Her kaynağın en güncel sayfalarını hızlıca tarar, yenileri indirir.
    only_new=False ise: Tüm geçmiş arşivi sonuna kadar tarar ve eksikleri tamamlar.
    """
    mode_name = "⚡ YENİ MAKALELERİ ÇEKME MODU" if only_new else "📚 TAM EVRENSEL ARŞİVLEME MODU"
    console.print(f"\n[bold green]🚀 KESİNTİSİZ İNDİRME MOTORU: {mode_name}[/bold green]")
    console.print("[dim]Her yeni makale anında 'makaleler/' klasörüne kaydedilir ve KATALOG.md güncellenir.[/dim]\n")
    
    total_downloaded = 0
    total_skipped = 0

    # 1. Aşama: Simply Psychology (Sitemap üzerinden 1.486 makale)
    console.print("[bold cyan]>>> 1. Aşama: Simply Psychology Taranıyor (1.486 Makale Havuzu)...[/bold cyan]")
    sp_items = crawler.discover_simply_psychology_all(use_sitemap=True)
    if only_new:
        sp_items = sp_items[:80]  # En güncel 80 makaleyi kontrol et

    for item in sp_items:
        if limit and total_downloaded >= limit:
            break
        url = item["url"]
        if is_already_saved(url):
            total_skipped += 1
            continue
        art = process_single_url(url, quiet=True, use_batch=True)
        if art:
            total_downloaded += 1
            console.print(f"[green][{total_downloaded}] ✔ İndirildi (RAM'de): {art.title[:50]} [{art.published_date or '-'}] (Simply Psychology)[/green]")
            if total_downloaded % 5 == 0:
                console.print("[dim green]💾 [SSD Koruma] 5 makale tek blok halinde diske yazıldı.[/dim green]")

    # 2. Aşama: Psychology Today (276 Blog)
    console.print("\n[bold cyan]>>> 2. Aşama: Psychology Today Blogları Taranıyor (276 Blog)...[/bold cyan]")
    all_pt_blogs = crawler.discover_all_pt_blogs()
    priority_blogs = [b for b in CORE_PSYCHOLOGY_TODAY_BLOGS if b in all_pt_blogs]
    other_blogs = [b for b in all_pt_blogs if b not in priority_blogs]
    ordered_blogs = priority_blogs + other_blogs

    pt_max_pages = 1 if only_new else max_pages
    pt_stop_on_existing = True if only_new else False

    for blog_slug in ordered_blogs:
        if limit and total_downloaded >= limit:
            break
        arts = crawler.discover_pt_blog_articles(blog_slug, max_pages=pt_max_pages, stop_on_existing=pt_stop_on_existing)
        for item in arts:
            if limit and total_downloaded >= limit:
                break
            url = item["url"]
            if is_already_saved(url):
                total_skipped += 1
                continue
            art = process_single_url(url, quiet=True, use_batch=True)
            if art:
                total_downloaded += 1
                console.print(f"[green][{total_downloaded}] ✔ İndirildi (RAM'de): {art.title[:50]} [{art.published_date or '-'}] (PT: {blog_slug})[/green]")
                if total_downloaded % 5 == 0:
                    console.print("[dim green]💾 [SSD Koruma] 5 makale tek blok halinde diske yazıldı.[/dim green]")

    # 3. Aşama: The Decision Lab
    if not limit or total_downloaded < limit:
        console.print("\n[bold cyan]>>> 3. Aşama: The Decision Lab Taranıyor...[/bold cyan]")
        dl_items = crawler.discover_decision_lab_all()
        for item in dl_items:
            if limit and total_downloaded >= limit:
                break
            url = item["url"]
            if is_already_saved(url):
                total_skipped += 1
                continue
            art = process_single_url(url, quiet=True, use_batch=True)
            if art:
                total_downloaded += 1
                console.print(f"[green][{total_downloaded}] ✔ İndirildi (RAM'de): {art.title[:50]} [{art.published_date or '-'}] (Decision Lab)[/green]")
                if total_downloaded % 5 == 0:
                    console.print("[dim green]💾 [SSD Koruma] 5 makale tek blok halinde diske yazıldı.[/dim green]")

    # 4. Aşama: Changing Minds
    if not limit or total_downloaded < limit:
        console.print("\n[bold cyan]>>> 4. Aşama: Changing Minds (299 Teori) Taranıyor...[/bold cyan]")
        cm_items = crawler.discover_changing_minds_all()
        for item in cm_items:
            if limit and total_downloaded >= limit:
                break
            url = item["url"]
            if is_already_saved(url):
                total_skipped += 1
                continue
            art = process_single_url(url, quiet=True, use_batch=True)
            if art:
                total_downloaded += 1
                console.print(f"[green][{total_downloaded}] ✔ İndirildi (RAM'de): {art.title[:50]} [{art.published_date or '-'}] (Changing Minds)[/green]")
                if total_downloaded % 5 == 0:
                    console.print("[dim green]💾 [SSD Koruma] 5 makale tek blok halinde diske yazıldı.[/dim green]")

    # Tamponda kalan son makaleleri diske dök
    batch_saver.flush()
    cat_path = build_master_catalog()
    console.print(f"\n[bold green]🎉 Tarama Bitti! Yeni İndirilen: {total_downloaded} | Önceden Var Olan: {total_skipped}[/bold green]")
    console.print(f"[bold cyan]📁 Makaleler:[/bold cyan] {settings.MAKALELER_DIR}")
    console.print(f"[bold cyan]📋 Master Katalog:[/bold cyan] {cat_path.name}\n")

def main():
    parser = argparse.ArgumentParser(description="Modüler Psikoloji & Davranış Bilimleri Evrensel İçerik Kazıma Sistemi")
    parser.add_argument("--url", "-u", type=str, help="Kazınacak tekil URL")
    parser.add_argument("--file", "-f", type=str, help="İçerisinde URL listesi olan metin dosyası")
    parser.add_argument("--force-jina", action="store_true", help="Doğrudan Jina Reader fallback'ini zorla")
    parser.add_argument("--clean", action="store_true", help="Dizini temizle, kaynak bazlı hiyerarşiyi uygula ve kataloğu derle")
    parser.add_argument("--build-catalog", action="store_true", help="Kayıtlı makalelerden Master Kataloğu derle")

    # Evrensel Kesintisiz Kazıma
    parser.add_argument("--crawl-all", action="store_true", help="Tüm siteleri sırayla keşfet ve anında indir")
    parser.add_argument("--discover-universe", action="store_true", help="Tüm sitelerdeki TÜM makaleleri keşfet ve listele")
    parser.add_argument("--crawl-universe", action="store_true", help="Keşfedilen tüm evrendeki makaleleri sırayla çek")
    parser.add_argument("--crawl-pt-all", action="store_true", help="Psychology Today'deki tüm blogların (294 blog) tamamını çek")
    parser.add_argument("--crawl-pt-core", action="store_true", help="Belirttiğiniz 4 ana PT blogunun tamamını çek")
    parser.add_argument("--crawl-full-blog", type=str, help="Belirli bir PT blogunu 1. sayfadan son sayfaya kadar çek")
    parser.add_argument("--crawl-topic", type=str, help=f"Belirli bir PT konusunu çek ({', '.join(PT_TOPIC_LIST[:8])}...)")
    parser.add_argument("--crawl-simply", action="store_true", help="Simply Psychology kategorilerindeki tüm makaleleri çek")
    parser.add_argument("--crawl-decision", action="store_true", help="The Decision Lab tüm içeriklerini çek")

    # Sınırlandırma ve Mod Parametreleri
    parser.add_argument("--only-new", action="store_true", help="Sadece en yeni çıkan makaleleri hızlıca tara ve indir")
    parser.add_argument("--max-blogs", type=int, default=None, help="Taranacak maksimum blog sayısı")
    parser.add_argument("--max-pages", type=int, default=10, help="Blog başına taranacak maksimum sayfa sayısı (varsayılan: 10)")
    parser.add_argument("--limit", type=int, default=None, help="Çekilecek maksimum makale sayısı")

    args = parser.parse_args()

    if args.crawl_all or args.only_new:
        crawl_all_continuous(limit=args.limit, max_pages=args.max_pages, only_new=args.only_new)
    elif args.clean:
        reorganize_and_clean_data_dir()
        cat = build_master_catalog()
        console.print(f"[bold green]✔ Dizin temizlendi ve düzenlendi. Master katalog hazır:[/bold green] {cat}")
    elif args.url:
        process_single_url(args.url, force_jina=args.force_jina)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        items = [{"url": u, "source": "List"} for u in urls]
        batch_crawl(items, limit=args.limit)
    elif args.discover_universe:
        console.print("[bold cyan]🌌 Evrensel İçerik Keşfi Başlatılıyor (Tüm Siteler)...[/bold cyan]")
        universe = crawler.discover_entire_universe(max_blogs=args.max_blogs, max_pages_per_blog=args.max_pages)
        console.print(f"\n[bold green]Tebrikler! Toplam {len(universe)} makale keşfedildi ve 'data/discovered_universe.json' dosyasına kaydedildi.[/bold green]")
    elif args.crawl_universe:
        # Önce keşfedilmiş dosya var mı kontrol et, yoksa keşfet
        if not crawler.discovered_file.exists():
            console.print("[yellow]Önceden oluşturulmuş evrensel liste bulunamadı. Keşif başlatılıyor...[/yellow]")
            universe = crawler.discover_entire_universe(max_blogs=args.max_blogs, max_pages_per_blog=args.max_pages)
        else:
            with open(crawler.discovered_file, "r", encoding="utf-8") as f:
                universe = json.load(f)
        batch_crawl(universe, limit=args.limit)
    elif args.crawl_pt_all:
        all_slugs = crawler.discover_all_pt_blogs()
        if args.max_blogs:
            all_slugs = all_slugs[:args.max_blogs]
        console.print(f"[bold cyan]Psychology Today'deki {len(all_slugs)} blogun makaleleri taranıyor...[/bold cyan]")
        all_items = []
        for slug in all_slugs:
            arts = crawler.discover_pt_blog_articles(slug, max_pages=args.max_pages)
            all_items.extend(arts)
        # Tarihe göre sırala
        all_items = sorted(all_items, key=lambda x: str(x.get("date_estimate", "")), reverse=True)
        batch_crawl(all_items, limit=args.limit)
    elif args.crawl_pt_core:
        all_items = []
        for slug in CORE_PSYCHOLOGY_TODAY_BLOGS:
            arts = crawler.discover_pt_blog_articles(slug, max_pages=args.max_pages)
            all_items.extend(arts)
        all_items = sorted(all_items, key=lambda x: str(x.get("date_estimate", "")), reverse=True)
        batch_crawl(all_items, limit=args.limit)
    elif args.crawl_full_blog:
        items = crawler.discover_pt_blog_articles(args.crawl_full_blog, max_pages=args.max_pages)
        batch_crawl(items, limit=args.limit)
    elif args.crawl_simply:
        items = crawler.discover_simply_psychology_all()
        batch_crawl(items, limit=args.limit)
    elif args.crawl_decision:
        items = crawler.discover_decision_lab_all()
        batch_crawl(items, limit=args.limit)
    elif args.build_catalog:
        cat = build_master_catalog()
        console.print(f"[bold green]Master katalog güncellendi:[/bold green] {cat}")
    else:
        # Hiçbir argüman verilmediğinde otomatik interaktif CMD menüsünü başlat
        from menu import main_menu
        main_menu()

if __name__ == "__main__":
    main()
