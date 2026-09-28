import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyzer.config import MAKALELER_DIR, DATA_DIR, ISLENMIS_MAKALELER_PATH
from analyzer.gemini_client import gemini_rotator
from analyzer.models import ViralIcerik

console = Console()
logging.basicConfig(level=logging.ERROR)

def load_master_dataset() -> Dict[str, Dict[str, Any]]:
    """Tek ana JSON dosyasındaki tüm işlenmiş makaleleri ID anahtarlı sözlük olarak yükler."""
    if not ISLENMIS_MAKALELER_PATH.exists():
        return {}
    try:
        with open(ISLENMIS_MAKALELER_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {item["id"]: item for item in data if "id" in item}
            elif isinstance(data, dict):
                return data
    except Exception as e:
        console.print(f"[yellow]Uyarı: Ana JSON dosyası okunamadı ({e})[/yellow]")
    return {}

def save_master_dataset(dataset: Dict[str, Dict[str, Any]]):
    """Tüm analizleri puana göre (en yüksekten en düşüğe) sıralayarak tek ana JSON dosyasına yazar."""
    sorted_items = sorted(dataset.values(), key=lambda x: x.get("puan", 0), reverse=True)
    with open(ISLENMIS_MAKALELER_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_items, f, ensure_ascii=False, indent=2)

def cleanup_legacy_individual_files():
    """Eski geçici veya tekil dosyaları temizler."""
    for f in DATA_DIR.glob("*_analiz.json"):
        try: f.unlink()
        except: pass
    old_skor = DATA_DIR / "skor_siralamasi.json"
    if old_skor.exists():
        try: old_skor.unlink()
        except: pass

def analyze_single_article(article_json_path: Path) -> Optional[ViralIcerik]:
    """Tek bir makaleyi Gemini ile analiz eder ve kancası metnine gömülü ViralIcerik modeli döner."""
    try:
        with open(article_json_path, "r", encoding="utf-8") as f:
            art = json.load(f)
    except Exception as e:
        console.print(f"[red]Dosya okunamadı: {article_json_path.name} ({e})[/red]")
        return None
        
    article_id = art.get("id") or article_json_path.stem
    article_url = art.get("url", "")
    
    try:
        ai_result = gemini_rotator.analyze_article(art)
        puan = int(ai_result.get("puan", 85))

        report = ViralIcerik(
            id=article_id,
            url=article_url,
            baslik=ai_result.get("baslik", art.get("title", "")),
            kategori=ai_result.get("kategori", "Genel Psikoloji"),
            metin=ai_result.get("metin", "İçerik metni oluşturulamadı."),
            puan=puan
        )
        return report
        
    except Exception as e:
        console.print(f"[red]Analiz hatası ({article_id}): {e}[/red]")
        return None

def process_batch(limit: Optional[int] = None, prioritize_rich: bool = True):
    """Makaleleri toplu analiz eder ve tek ana JSON dosyasında biriktirir."""
    cleanup_legacy_individual_files()
    master_data = load_master_dataset()
    already_done_ids = set(master_data.keys())
    
    all_json_files = list(MAKALELER_DIR.glob("*.json"))
    console.print(f"[bold cyan]🔍 Havuzdaki Toplam Ham Makale:[/bold cyan] {len(all_json_files)}")
    console.print(f"[bold green]✅ Ana JSON'da Kayıtlı:[/bold green] {len(already_done_ids)}")
    
    pending_files = [f for f in all_json_files if f.stem not in already_done_ids]
    
    if not pending_files:
        console.print("[bold yellow]Tüm makaleler zaten analiz edilmiş![/bold yellow]")
        show_top_scores(limit=10)
        return
        
    if prioritize_rich:
        sample = pending_files[:100]
        sample.sort(key=lambda x: x.stat().st_size, reverse=True)
        pending_files = sample + pending_files[100:]
        
    if limit:
        pending_files = pending_files[:limit]
        
    console.print(f"[bold magenta]🚀 Bu Oturumda İşlenecek Makale Sayısı:[/bold magenta] {len(pending_files)}\n")
    
    success_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Kapsamlı Viral İçerikler Hazırlanıyor...", total=len(pending_files))
        
        for p_file in pending_files:
            rep = analyze_single_article(p_file)
            if rep:
                master_data[rep.id] = rep.model_dump()
                save_master_dataset(master_data)
                success_count += 1
                progress.console.print(
                    f"[green]✔ [{rep.puan}/100][/green] "
                    f"[bold white]{rep.baslik[:42]}[/bold white] "
                    f"([yellow]{rep.kategori}[/yellow])"
                )
            progress.advance(task)
            
    console.print(f"\n[bold green]🎉 Tamamlandı! {success_count} kapsamlı viral içerik üretildi ve '{ISLENMIS_MAKALELER_PATH.name}' dosyasına kaydedildi.[/bold green]\n")
    show_top_scores(limit=limit or 10)

def show_top_scores(limit: int = 15):
    """Ana JSON dosyasından en yüksek puan alan içerikleri şık bir tablo olarak gösterir."""
    master_data = load_master_dataset()
    if not master_data:
        console.print("[yellow]Henüz işlenmiş içerik bulunamadı.[/yellow]")
        return
        
    sorted_items = sorted(master_data.values(), key=lambda x: x.get("puan", 0), reverse=True)
    
    table = Table(title=f"🏆 En Yüksek Puanlı Viral İçerikler ({ISLENMIS_MAKALELER_PATH.name})", show_lines=True)
    table.add_column("Sıra", justify="center", style="cyan", width=4)
    table.add_column("Puan", justify="center", style="bold green", width=6)
    table.add_column("Başlık", style="white", min_width=32)
    table.add_column("Kategori", style="yellow", width=18)
    table.add_column("Açılış Kancası (Metnin Başı)", style="dim", min_width=45)
    
    for idx, item in enumerate(sorted_items[:limit], start=1):
        metin = item.get("metin", "")
        acilis = metin[:65] + "..." if len(metin) > 65 else metin
        table.add_row(
            str(idx),
            f"{item.get('puan', 0)}",
            item.get("baslik", "")[:42],
            item.get("kategori", "")[:18],
            acilis
        )
        
    console.print(table)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Kapsamlı & Kancası Metne Yedirilmiş Viral İçerik Motoru")
    parser.add_argument("--limit", "-l", type=int, default=None, help="Analiz edilecek makale sayısı")
    parser.add_argument("--top", "-t", type=int, default=15, help="En yüksek skorlu içerikleri göster")
    
    args = parser.parse_args()
    process_batch(limit=args.limit)
