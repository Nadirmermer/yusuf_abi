import os
import sys
import json
import logging
import warnings
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Uyarı ve log kirliliğini tamamen kapat
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)

# Proje dizinini sys.path'e ekle
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scrapers.crawler import crawler, CORE_PSYCHOLOGY_TODAY_BLOGS
from scrapers import get_scraper
from storage.exporter import (
    save_article, build_master_catalog, list_saved_articles, 
    migrate_existing_data, get_saved_urls_cache, get_source_stats
)
from config.settings import settings

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║      🧠  PSİKOLOJİ & DAVRANIŞ BİLİMLERİ İÇERİK KAZIMA MERKEZİ         ║
    ║        (Psychology Today • Simply Psychology • The Decision Lab)      ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def show_stats():
    stats = get_source_stats()
    total_indirilen = sum(s["indirilen"] for s in stats.values())
    total_kalan = sum(s["kalan"] for s in stats.values())

    table = Table(
        title=f"📊 Kaynak Bazlı İçerik Durum Raporu (Toplam {total_indirilen} Makale İndirildi)",
        title_style="bold green",
        show_header=True,
        header_style="bold magenta",
        border_style="dim"
    )
    table.add_column("Platform / Kaynak", style="cyan", width=22)
    table.add_column("İndirilen", justify="right", style="bold green", width=12)
    table.add_column("Bekleyen (Tahmini)", justify="right", style="yellow", width=18)
    table.add_column("Toplam Havuz", justify="right", style="white", width=14)
    table.add_column("Kapsam / Açıklama", style="dim", width=24)

    for name, s in stats.items():
        kalan_str = f"~{s['kalan']} makale" if s['kalan'] > 0 else "Tamamlandı ✔"
        table.add_row(
            name,
            f"{s['indirilen']} adet",
            kalan_str,
            f"~{s['toplam_tahmini']}",
            s['kaynak_tipi']
        )

    table.add_section()
    table.add_row(
        "[bold white]GENEL TOPLAM[/bold white]",
        f"[bold green]{total_indirilen} adet[/bold green]",
        f"[bold yellow]~{total_kalan} makale[/bold yellow]",
        "[bold white]~6.985[/bold white]",
        "[bold cyan]Tüm Siteler[/bold cyan]"
    )

    console.print(table)
    console.print(f"📁 [dim]Kayıt Klasörü:[/dim] [cyan]{settings.MAKALELER_DIR}[/cyan] | 📋 [dim]Katalog:[/dim] [green]{settings.KATALOG_PATH.name}[/green]")
    console.print("─" * 75, style="dim")

def run_single_url():
    console.print("\n[bold cyan]🔗 TEKİL URL KAZIMA[/bold cyan]")
    url = Prompt.ask("Kazımak istediğiniz makale linkini yapıştırın")
    if not url.strip():
        return

    console.print(f"\n[yellow]⏳ İçerik çekiliyor...[/yellow]")
    try:
        scraper = get_scraper(url)
        article = scraper.scrape(url)
        paths = save_article(article)
        build_master_catalog()
        console.print(f"\n[bold green]✔ Başarıyla indirildi ve kaydedildi:[/bold green]")
        console.print(f"  📌 [bold white]{article.title}[/bold white]")
        console.print(f"  📅 Yayın Tarihi: {article.published_date or 'Belirtilmemiş'}")
        console.print(f"  🎯 Madde Sayısı: {len(article.key_points)} adet")
        console.print(f"  🖼️ Görsel Sayısı: {len(article.images)} adet")
        console.print(f"  📄 Dosya: [cyan]{paths['markdown'].name}[/cyan] ve [cyan]{paths['json'].name}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]❌ Hata oluştu:[/bold red] {e}")

def run_quick_new_crawl():
    console.print("\n[bold green]⚡ SADECE YENİ ÇIKAN MAKALELERİ ÇEK (Hızlı Günlük Kontrol)[/bold green]")
    console.print("Tüm sitelerin en güncel sayfaları taranır, bizde olmayan yeni içerikler anında indirilir.")
    from main import crawl_all_continuous
    crawl_all_continuous(only_new=True)

def run_full_universe_crawl():
    console.print("\n[bold green]📚 TÜM SİTELERİN GEÇMİŞ ARŞİVİNİ İNDİR (Kapsamlı Arşiv)[/bold green]")
    console.print("Simply Psychology (1.486 Makale) + Psychology Today (276 Blog) + The Decision Lab + Changing Minds")
    limit_str = Prompt.ask("Kaç adet yeni makale çekilsin? (Örn: 50, 100 ya da [bold yellow]Tümü için Enter[/bold yellow])", default="")
    limit = int(limit_str) if limit_str.isdigit() else None

    from main import crawl_all_continuous
    crawl_all_continuous(limit=limit, only_new=False)

def run_pt_core_or_custom():
    console.print("\n[bold cyan]🧠 PSYCHOLOGY TODAY: BLOG KAZIMA[/bold cyan]")
    console.print("Seçenekler:")
    console.print("  [1] 4 Temel Blog (unhitched, quirks-of-memory, wire-your-mind, in-practice)")
    console.print("  [2] Tüm 276 Psychology Today Blogu (Sırayla)")
    console.print("  [3] Özel Bir Blog Adı Yaz (Örn: unhitched)")
    
    sub = Prompt.ask("Seçiminiz", choices=["1", "2", "3"], default="1")
    limit_str = Prompt.ask("Kaç adet makale çekilsin? ([bold yellow]Tümü için Enter'a basın[/bold yellow])", default="")
    limit = int(limit_str) if limit_str.isdigit() else None

    from main import batch_crawl
    if sub == "1":
        all_articles = []
        for slug in CORE_PSYCHOLOGY_TODAY_BLOGS:
            arts = crawler.discover_pt_blog_articles(slug, max_pages=10)
            all_articles.extend(arts)
        sorted_articles = sorted(all_articles, key=lambda x: str(x.get("date_estimate", "")), reverse=True)
        batch_crawl(sorted_articles, limit=limit)
    elif sub == "2":
        all_slugs = crawler.discover_all_pt_blogs()
        all_articles = []
        for slug in all_slugs:
            arts = crawler.discover_pt_blog_articles(slug, max_pages=10)
            all_articles.extend(arts)
        sorted_articles = sorted(all_articles, key=lambda x: str(x.get("date_estimate", "")), reverse=True)
        batch_crawl(sorted_articles, limit=limit)
    elif sub == "3":
        blog = Prompt.ask("Blog slug adını yazın (örn: unhitched)").strip().lower()
        if blog:
            articles = crawler.discover_pt_blog_articles(blog, max_pages=None)
            batch_crawl(articles, limit=limit)

def run_simply_psychology():
    console.print("\n[bold cyan]📖 SIMPLY PSYCHOLOGY: TÜM SİTEYİ KAZIMA (1.486 Makale)[/bold cyan]")
    limit_str = Prompt.ask("Kaç adet makale çekilsin? ([bold yellow]Tümü için Enter'a basın[/bold yellow])", default="")
    limit = int(limit_str) if limit_str.isdigit() else None

    from main import batch_crawl
    items = crawler.discover_simply_psychology_all(use_sitemap=True)
    batch_crawl(items, limit=limit)

def run_decision_lab():
    console.print("\n[bold cyan]⚖️ THE DECISION LAB: BİLİŞSEL ÖNYARGILAR & MAKALELER[/bold cyan]")
    limit_str = Prompt.ask("Kaç adet makale çekilsin? ([bold yellow]Tümü için Enter'a basın[/bold yellow])", default="")
    limit = int(limit_str) if limit_str.isdigit() else None

    from main import batch_crawl
    items = crawler.discover_decision_lab_all()
    batch_crawl(items, limit=limit)

def run_changing_minds():
    console.print("\n[bold cyan]💡 CHANGING MINDS: 299 PSİKOLOJİ TEORİSİ[/bold cyan]")
    limit_str = Prompt.ask("Kaç adet teori çekilsin? ([bold yellow]Tümü için Enter'a basın[/bold yellow])", default="")
    limit = int(limit_str) if limit_str.isdigit() else None

    from main import batch_crawl
    items = crawler.discover_changing_minds_all()
    batch_crawl(items, limit=limit)

def view_catalog():
    if not settings.KATALOG_PATH.exists():
        build_master_catalog()

    with open(settings.KATALOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    console.print("\n[bold green]📋 İNDİRİLEN MAKALELER KATALOĞU (En Yeniler En Üstte)[/bold green]\n")
    lines = content.splitlines()
    for l in lines[:30]:
        console.print(l)
    if len(lines) > 30:
        console.print(f"\n[dim]... ve {len(lines) - 30} satır daha. Tam liste için KATALOG.md dosyasını açabilirsiniz.[/dim]")

def open_makaleler_folder():
    settings.MAKALELER_DIR.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.startfile(str(settings.MAKALELER_DIR))
        console.print("[green]✔ 'makaleler/' klasörü Windows Gezgini'nde açıldı.[/green]")
    else:
        console.print(f"Klasör yolu: {settings.MAKALELER_DIR}")

def open_catalog_file():
    build_master_catalog()
    if os.name == "nt" and settings.KATALOG_PATH.exists():
        os.startfile(str(settings.KATALOG_PATH))
        console.print("[green]✔ KATALOG.md dosyası açıldı.[/green]")
    else:
        console.print(f"Katalog yolu: {settings.KATALOG_PATH}")

def main_menu():
    migrate_existing_data()
    build_master_catalog()

    while True:
        clear_screen()
        print_banner()
        show_stats()

        console.print("""
  [bold green][1][/bold green] ⚡ [bold green]Sadece YENİ Çıkan Makaleleri Çek[/bold green] (Hızlı Günlük Kontrol)
  [bold yellow][2][/bold yellow] 📚 [bold]Tüm Sitelerin Geçmiş Arşivini İndir[/bold] (Simply + PT 276 Blog + Decision Lab)
  [bold yellow][3][/bold yellow] 🧠 [bold]Psychology Today Bloglarını Çek[/bold] (276 Blog / Unhitched vs.)
  [bold yellow][4][/bold yellow] 📖 [bold]Simply Psychology Makalelerini Çek[/bold] (1.486 Makale Havuzu)
  [bold yellow][5][/bold yellow] ⚖️ [bold]The Decision Lab Makalelerini Çek[/bold] (Bilişsel Önyargılar)
  [bold yellow][6][/bold yellow] 💡 [bold]Changing Minds Teorilerini Çek[/bold] (299 Psikoloji Teorisi)
  [bold yellow][7][/bold yellow] 🔗 [bold]Tek Bir Link Yapıştır ve Çek[/bold]
  [bold yellow][8][/bold yellow] 📋 [bold]Kataloğu Konsolda Gör[/bold] (Tarih Sıralı)
  [bold yellow][9][/bold yellow] 📂 [bold cyan]Makaleler Klasörünü Aç[/bold cyan] (Windows Gezgini)
  [bold yellow][0][/bold yellow] ❌ [bold red]Çıkış[/bold red]
        """)

        choice = Prompt.ask("Yapmak istediğiniz işlemi seçin", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], default="1")

        if choice == "0":
            console.print("\n[yellow]İşlem sonlandırıldı. İyi çalışmalar dilerim![/yellow]\n")
            break
        elif choice == "1":
            run_quick_new_crawl()
        elif choice == "2":
            run_full_universe_crawl()
        elif choice == "3":
            run_pt_core_or_custom()
        elif choice == "4":
            run_simply_psychology()
        elif choice == "5":
            run_decision_lab()
        elif choice == "6":
            run_changing_minds()
        elif choice == "7":
            run_single_url()
        elif choice == "8":
            view_catalog()
        elif choice == "9":
            open_makaleler_folder()

        console.print("\n[dim]Menüye dönmek için Enter'a basın...[/dim]")
        input()

if __name__ == "__main__":
    main_menu()
