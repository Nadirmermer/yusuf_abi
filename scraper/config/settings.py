import os
import logging
from pathlib import Path
from pydantic import BaseModel

# Tüm pydantic ve log gürültülerini kapat
os.environ["PYDANTIC_DISABLE_PLUGINS"] = "1"
logging.getLogger("NetworkClient").setLevel(logging.ERROR)
logging.getLogger("Crawler").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)

import sys

SCRAPER_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRAPER_DIR.parent

if str(SCRAPER_DIR) not in sys.path:
    sys.path.insert(0, str(SCRAPER_DIR))

BASE_DIR = PROJECT_ROOT

class Settings(BaseModel):
    # Sade ve Doğrudan Dizinler
    DATA_DIR: Path = BASE_DIR / "data"
    MAKALELER_DIR: Path = DATA_DIR / "makaleler"
    KATALOG_PATH: Path = DATA_DIR / "KATALOG.md"
    
    # Ağ Ayarları
    REQUEST_TIMEOUT: int = 25
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    CHROME_IMPERSONATE: str = "chrome120"
    JINA_READER_PREFIX: str = "https://r.jina.ai/"

settings = Settings()
settings.MAKALELER_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
