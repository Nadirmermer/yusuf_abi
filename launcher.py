import os
os.environ["PYDANTIC_DISABLE_PLUGINS"] = "1"
import warnings
warnings.filterwarnings("ignore")
import sys
import time
import webbrowser
import threading
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent

# Uygulama hangi klasorden baslatilirsa baslatilsin proje kokunu kullan.
os.chdir(PROJECT_ROOT)

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
    
    # 1.2 sn sonra tarayıcıyı aç
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()
    
    # Uvicorn sunucusunu başlat
    import uvicorn
    uvicorn.run("web.server:app", host="127.0.0.1", port=8000, log_level="info")

def main():
    while True:
        clear_screen()
        banner = """[bold yellow]╔═════════════════════════════════════════════════════════════════════════╗
║         🧠  @ya_da_psikoloji - İÇERİK KEŞFİ & KAROSEL STÜDYOSU          ║
║               (Editoryal Keşif Masası • Canlı Üretim Merkezi)           ║
╚═════════════════════════════════════════════════════════════════════════╝[/bold yellow]"""
        console.print(banner)
        console.print("  [1] 🌐 [bold green]Web Stüdyosunu Başlat[/bold green] (Tüm Süreçler: Keşif, Scraper, Stüdyo, Arşiv)")
        console.print("  [2] 🎨 [bold cyan]Konsol Menüsü[/bold cyan] (Toplu Karosel & Metin Üretim Merkezi)")
        console.print("  [3] 🕷️ [bold magenta]İçerik Kazıma Motoru[/bold magenta] (Scraper / 4 Büyük Site)")
        console.print("  [0] ❌ Çıkış\n")
        
        secim = Prompt.ask("Lütfen bir işlem seçin", choices=["0", "1", "2", "3"], default="1")
        
        if secim == "0":
            console.print("\n[yellow]İşlem sonlandırıldı. İyi çalışmalar![/yellow]")
            break
        elif secim == "1":
            start_web_studio()
        elif secim == "2":
            subprocess.run([sys.executable, str(PROJECT_ROOT / "analyzer" / "menu.py")])
        elif secim == "3":
            subprocess.run([sys.executable, str(PROJECT_ROOT / "scraper" / "menu.py")])

if __name__ == "__main__":
    main()
