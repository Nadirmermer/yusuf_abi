import os
os.environ["PYDANTIC_DISABLE_PLUGINS"] = "1"
import warnings
warnings.filterwarnings("ignore")
import sys
import time
import webbrowser
import threading
from pathlib import Path
from rich.console import Console

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
    start_web_studio()

if __name__ == "__main__":
    main()
