import os
from pathlib import Path
import dotenv

# .env yükle
PROJECT_ROOT = Path(__file__).resolve().parent.parent
dotenv_path = PROJECT_ROOT / ".env"
if dotenv_path.exists():
    dotenv.load_dotenv(dotenv_path, override=True)

# Dizin Yolları
DATA_DIR = PROJECT_ROOT / "data"
MAKALELER_DIR = DATA_DIR / "makaleler"

# Tek ve Ana JSON Dosyası
ISLENMIS_MAKALELER_PATH = DATA_DIR / "islenmis_makaleler.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

os.environ["PYDANTIC_DISABLE_PLUGINS"] = "1"

# API Anahtarları (Tüm 11 anahtar döngüsel olarak kullanılır)
raw_keys = os.getenv("GEMINI_API_KEYS", "")
all_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
GEMINI_API_KEYS = all_keys

# Desteklenen Model Havuzu (gemini-api-dev standardı)
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest"
]
