import sys
import os
import webbrowser
import threading
import time
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

# Kök dizini sys.path'e ekle
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyzer.processor import process_batch, show_top_scores, load_master_dataset, MAKALELER_DIR, ISLENMIS_MAKALELER_PATH
from analyzer.carousel_processor import batch_process_carousels, CAROUSELS_OUTPUT_DIR

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def open_browser_delayed(url: str, delay: float = 1.2):
    time.sleep(delay)
    webbrowser.open(url)

def start_web_studio():
    clear_screen()
    url = "http://localhost:8000"
    console.print(f"\n[bold green]🚀 Web Karosel Stüdyosu Başlatılıyor...[/bold green]")
    console.print(f"🌐 Tarayıcı otomatik açılıyor: [bold cyan]{url}[/bold cyan]")
    console.print("[dim]Durdurmak için pencereyi kapatabilir veya CTRL+C tuşlarına basabilirsiniz.[/dim]\n")
    
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()
    
    import uvicorn
    uvicorn.run("web.server:app", host="127.0.0.1", port=8000, log_level="info")

def main_menu():
    while True:
        clear_screen()
        all_count = len(list(MAKALELER_DIR.glob("*.json")))
        carousel_count = len([d for d in CAROUSELS_OUTPUT_DIR.iterdir() if d.is_dir()]) if CAROUSELS_OUTPUT_DIR.exists() else 0
        master_data = load_master_dataset()
        analyzed_count = len(master_data)
        
        banner = f"""[bold yellow]╔═════════════════════════════════════════════════════════════════════════╗
║     🎨  YAPAY ZEKA INSTAGRAM KAROSEL & İÇERİK ÜRETİM STÜDYOSU           ║
║       (1080x1350 Dikey • Web Stüdyosu • @ya_da_psikoloji Tasarımı)      ║
╚═════════════════════════════════════════════════════════════════════════╝[/bold yellow]
📊 [bold cyan]Havuzdaki Toplam Ham Makale:[/bold cyan] {all_count} Adet
🖼️ [bold green]Üretilmiş Instagram Karoseli:[/bold green] {carousel_count} Adet ([yellow]data/carousels/[/yellow])
📝 [bold magenta]Kayıtlı Metin Analizi:[/bold magenta] {analyzed_count} Adet ([yellow]{ISLENMIS_MAKALELER_PATH.name}[/yellow])
"""
        console.print(banner)
        console.print("  [1] 🌐 [bold green]Web Karosel Stüdyosunu Başlat[/bold green] (İçerik Havuzu, Görsel Seçici, Slayt Editörü)")
        console.print("  [2] 🎨 [bold cyan]Konsoldan Otomatik Karosel Üret[/bold cyan] (1080x1350 PNG + caption.txt)")
        console.print("  [3] 📂 [bold yellow]Üretilen Karosellerin Web Galerisini Aç[/bold yellow]")
        console.print("  [4] 📝 [bold magenta]Toplu Viral Metin Analizi Yap[/bold magenta] (Tek JSON'a kaydet)")
        console.print("  [5] 🏆 [bold white]En Yüksek Puanlı İçerikleri Listele[/bold white] (Top 20)")
        console.print("  [0] ❌ Çıkış\n")
        
        choice = Prompt.ask("Seçiminiz", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            console.print("\n[yellow]İşlem sonlandırıldı. İyi çalışmalar![/yellow]")
            break
        elif choice == "1":
            start_web_studio()
        elif choice == "2":
            lim_str = Prompt.ask("\nKaç adet Instagram karoseli üretilsin?", default="3")
            try:
                lim = int(lim_str)
                batch_process_carousels(limit=lim)
            except ValueError:
                console.print("[red]Geçersiz sayı girdiniz.[/red]")
            Prompt.ask("\nDevam etmek için Enter'a basın")
        elif choice == "3":
            if not CAROUSELS_OUTPUT_DIR.exists():
                console.print("[yellow]Henüz üretilmiş bir karosel bulunmuyor.[/yellow]")
            else:
                folders = [d for d in CAROUSELS_OUTPUT_DIR.iterdir() if d.is_dir() and (d / "index.html").exists()]
                if not folders:
                    console.print("[yellow]Önizleme galerisi bulunamadı.[/yellow]")
                else:
                    console.print(f"\n[cyan]Son üretilen karosel galerisi açılıyor: {folders[0].name}[/cyan]")
                    webbrowser.open((folders[0] / "index.html").resolve().as_uri())
            Prompt.ask("\nDevam etmek için Enter'a basın")
        elif choice == "4":
            lim_str = Prompt.ask("\nKaç adet makale analiz edilsin?", default="10")
            try:
                lim = int(lim_str)
                process_batch(limit=lim)
            except ValueError:
                console.print("[red]Geçersiz sayı girdiniz.[/red]")
            Prompt.ask("\nDevam etmek için Enter'a basın")
        elif choice == "5":
            console.print("\n")
            show_top_scores(limit=20)
            Prompt.ask("\nDevam etmek için Enter'a basın")

if __name__ == "__main__":
    main_menu()
