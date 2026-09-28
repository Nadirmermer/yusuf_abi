import os
os.environ["PYDANTIC_DISABLE_PLUGINS"] = "1"
import warnings
warnings.filterwarnings("ignore")
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from analyzer.editorial_ai import analyze_and_transform_article
from analyzer.gemini_client import gemini_rotator

logger = logging.getLogger("BatchProcessor")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ARTICLES_DIR = DATA_DIR / "makaleler"
AI_PROCESSED_DIR = DATA_DIR / "ai_processed"
AI_CATALOG_PATH = DATA_DIR / "ai_catalog.json"
BATCH_STATUS_PATH = DATA_DIR / "batch_status.json"

AI_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

class EditorialBatchProcessor:
    """
    7.639 makalelik arşivi 11 API anahtarı ile ultra hızlı işleyen yüksek verimli motor.
    - Bellek içi (in-memory) katalog önbelleği: Sıfır I/O kilitlenmesi, anında yanıt.
    - 11 Paralel Worker: 11 API anahtarının tamamını %100 verimle kullanır.
    - Atomik ve güvenli kayıt: Her makale bağımsız JSON'a yazılır, ana katalog her 5 makalede flush edilir.
    - İlişki, bağlanma, narsizm gibi Instagram'da tutan konuları önceliklendirir.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.current_title = ""
        self.processed_count = 0
        self.total_eligible = 0
        self.last_error = None
        self.catalog_cache: Dict[str, Dict[str, Any]] = {}
        self.dirty_count = 0
        self._init_in_memory_catalog()

    def _init_in_memory_catalog(self):
        """Kataloğu RAM'e 1 defa yükler; gerekirse ai_processed klasöründeki bağımsız dosyalarla senkronize eder."""
        loaded_items = {}
        if AI_CATALOG_PATH.exists():
            try:
                with open(AI_CATALOG_PATH, "r", encoding="utf-8") as f:
                    cat = json.load(f)
                    for it in cat:
                        if isinstance(it, dict) and "id" in it:
                            loaded_items[it["id"]] = it
            except Exception as e:
                logger.error(f"AI katalog okuma hatası: {e}")

        # ai_processed dizinindeki tekil dosyaları kontrol et (Eğer diskteki ana katalog eksik kalmışsa)
        single_files = list(AI_PROCESSED_DIR.glob("*.json"))
        if len(single_files) > len(loaded_items):
            for p in single_files:
                stem = p.stem
                if stem not in loaded_items:
                    try:
                        with open(p, "r", encoding="utf-8") as sf:
                            rec = json.load(sf)
                            if isinstance(rec, dict) and "id" in rec:
                                loaded_items[rec["id"]] = rec
                    except Exception:
                        pass

        with self.lock:
            self.catalog_cache = loaded_items
            self.processed_count = len(self.catalog_cache)

        logger.info(f"⚡ In-Memory AI Katalog hazır: {self.processed_count} makale yüklendi.")

    def get_catalog_list(self) -> List[Dict[str, Any]]:
        """Hafızadaki kataloğu en yüksek puandan en düşüğe sıralı liste olarak anında döner (0.01 ms)."""
        with self.lock:
            items = list(self.catalog_cache.values())
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        return items

    def _flush_catalog_to_disk(self, items: Optional[List[Dict[str, Any]]] = None):
        """Hafızadaki kataloğu güvenle ve atomik şekilde AI_CATALOG_PATH dosyasına yazar."""
        if items is None:
            items = self.get_catalog_list()
        try:
            tmp_path = AI_CATALOG_PATH.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            tmp_path.replace(AI_CATALOG_PATH)
            logger.info(f"💾 [Katalog Senkronize] {len(items)} makale diske kaydedildi.")
        except Exception as e:
            logger.error(f"Katalog diske yazma hatası: {e}")

    def get_status(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "is_running": self.is_running,
                "processed_count": self.processed_count,
                "total_eligible": self.total_eligible,
                "current_article": self.current_title,
                "last_error": self.last_error
            }

    def get_eligible_articles(self) -> List[Path]:
        """Diskteki makaleleri tarar; catalog_index üzerinden anında öncelik sırasına koyar."""
        catalog_file = DATA_DIR / "catalog_index.json"
        with self.lock:
            already_processed = set(self.catalog_cache.keys())

        priority_keywords = [
            "attachment", "narciss", "gaslight", "relationship", "partner", "toxic",
            "overthink", "boundary", "boundaries", "breakup", "people pleas", "silent treatment",
            "trauma", "anxious", "avoidant", "guilt", "shame", "rejection", "jealous",
            "communication", "healing", "conflict", "red flag", "green flag", "emotional"
        ]

        eligible = []

        if catalog_file.exists():
            try:
                with open(catalog_file, "r", encoding="utf-8") as f:
                    catalog_items = json.load(f)
            except Exception as e:
                logger.error(f"Catalog okunamadı: {e}")
                catalog_items = []

            for it in catalog_items:
                stem = it.get("_file_stem") or ""
                if not stem or stem in already_processed:
                    continue

                json_path = ARTICLES_DIR / f"{stem}.json"
                if not json_path.exists():
                    continue

                title = (it.get("title") or "").lower()
                if not title:
                    continue
                kp = it.get("key_points") or []
                priority_score = 0

                # Kilit maddeleri olanlar (Karosel için harika)
                if len(kp) >= 5:
                    priority_score += 40
                elif len(kp) >= 3:
                    priority_score += 20

                # Instagram psikoloji anahtar kelimeleri
                matched_kw = sum(1 for kw in priority_keywords if kw in title)
                priority_score += matched_kw * 15

                # Simply Psychology maddeli rehber bonusu
                if it.get("source") == "Simply Psychology":
                    priority_score += 10

                eligible.append((priority_score, json_path))
        else:
            # Fallback
            for p in list(ARTICLES_DIR.glob("*.json"))[:300]:
                if p.stem not in already_processed:
                    eligible.append((10, p))

        # En yüksek öncelikliden en düşüğe sırala
        eligible.sort(key=lambda x: x[0], reverse=True)
        with self.lock:
            self.total_eligible = len(eligible) + len(already_processed)

        logger.info(f"Filtrelenmiş ve önceliklendirilmiş işlenebilir makale sayısı: {len(eligible)} (Kuyruk hazır)")
        return [item[1] for item in eligible]

    def _process_single_article(self, path: Path):
        """Tek bir makaleyi bağımsız thread içinde işler (Thread-Safe & Lock-Free)."""
        with self.lock:
            if not self.is_running:
                return

        try:
            with open(path, "r", encoding="utf-8") as f:
                article_data = json.load(f)
        except Exception:
            return

        article_id = path.stem
        title = article_data.get("title", "Başlıksız")

        with self.lock:
            self.current_title = title

        try:
            processed_result = analyze_and_transform_article(article_data)

            if processed_result:
                full_record = {
                    "id": article_id,
                    "original_title": title,
                    "source": article_data.get("source"),
                    "source_url": article_data.get("url"),
                    "published_date": article_data.get("published_date"),
                    "read_time_minutes": article_data.get("read_time_minutes", 5),
                    "original_images": article_data.get("images", []),
                    "word_count": article_data.get("word_count", 0),
                    "turkce_baslik": processed_result.get("turkce_baslik"),
                    "kanca_sorusu": processed_result.get("kanca_sorusu"),
                    "score": processed_result.get("kati_puan", 75),
                    "puan_nedeni": processed_result.get("puan_nedeni"),
                    "category": processed_result.get("kategori", "İlişkiler & İletişim"),
                    "editoryal_genis_metin": processed_result.get("editoryal_genis_metin"),
                    "karosel_slaytlari": processed_result.get("karosel_slaytlari", []),
                    "reels_kancasi": processed_result.get("reels_kancasi", {}),
                    "caption": processed_result.get("caption"),
                    "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # 1. Tekil JSON dosyasına yaz (sadece 8 KB, anında biter, veri kaybı riski sıfır)
                record_path = AI_PROCESSED_DIR / f"{article_id}.json"
                with open(record_path, "w", encoding="utf-8") as rf:
                    json.dump(full_record, rf, ensure_ascii=False, indent=2)

                # 2. Bellek kataloğunu mikrosaniyelik kilitle güncelle
                items_to_flush = None
                with self.lock:
                    self.catalog_cache[article_id] = full_record
                    self.processed_count = len(self.catalog_cache)
                    self.dirty_count += 1
                    if self.dirty_count >= 5:  # Her 5 makalede bir ana kataloğu diske yaz
                        self.dirty_count = 0
                        items_to_flush = sorted(list(self.catalog_cache.values()), key=lambda x: x.get("score", 0), reverse=True)

                # 3. Kilit DIŞINDA diske yaz (diğer worker thread'leri ASLA bekletmez!)
                if items_to_flush is not None:
                    self._flush_catalog_to_disk(items_to_flush)

                key_used = processed_result.get("_meta_key_idx", "?")
                logger.info(f"✨ [{self.processed_count}/{self.total_eligible}] [{full_record['score']} Puan] {full_record['turkce_baslik']} (🔑 Key #{key_used})")
                time.sleep(0.5)  # Anahtar soğuma süresi ve pacing AIEngine tarafından yönetildiği için işçi beklemesi optimize edildi (Sözlük projesi standardı)

        except Exception as e:
            logger.error(f"Makale işleme hatası ({title}): {e}")
            with self.lock:
                self.last_error = str(e)
            time.sleep(1.0)

    def _worker_loop(self):
        eligible_paths = self.get_eligible_articles()
        # 11 API anahtarının tamamını sözlük projesindeki gibi tam kapasiteyle çalıştırır
        num_workers = len(gemini_rotator.clients) if gemini_rotator.clients else 9
        logger.info(f"🚀 Yapay Zeka Editoryal Fabrikası Başlatıldı ({num_workers} Paralel Worker • 11 API Key • Sırada: {len(eligible_paths)} makale)")

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for path in eligible_paths:
                with self.lock:
                    if not self.is_running:
                        break
                futures.append(executor.submit(self._process_single_article, path))
                time.sleep(0.3)

            for future in as_completed(futures):
                with self.lock:
                    if not self.is_running:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

        # İşlem bittiğinde veya durdurulduğunda son durumu diske kesin olarak yaz
        self._flush_catalog_to_disk()

        with self.lock:
            self.is_running = False
            self.current_title = "Tamamlandı"
        logger.info("Yapay zeka işleme döngüsü sona erdi.")

    def start(self) -> bool:
        with self.lock:
            if self.is_running:
                return False
            self.is_running = True
            self.last_error = None
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            return True

    def stop(self) -> bool:
        with self.lock:
            if not self.is_running:
                return False
            self.is_running = False
        # Durdurulunca bellekteki son durumu diske kaydet
        self._flush_catalog_to_disk()
        return True

# Singleton motor
batch_processor = EditorialBatchProcessor()
