import os
import time
import json
import logging
import threading
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from analyzer.config import GEMINI_API_KEYS
from analyzer.prompts import SYSTEM_INSTRUCTION, build_analysis_prompt
from analyzer.carousel_prompts import CAROUSEL_SYSTEM_INSTRUCTION, build_carousel_prompt

logger = logging.getLogger("AIEngine")

class GeminiRotatorEngine:
    """
    Gunluk-Psikolojik-Gercekler ve Sözlük projelerindeki kanıtlanmış birebir AIEngine mimarisi.
    - 11 anahtarın tamamını döngüsel ve thread-safe olarak yönetir.
    - Geçici 10 saniye kilit ile aynı anahtarın aynı anda birden fazla iş parçacığı tarafından kullanılmasını önler.
    - 429 durumunda tam 60 saniyelik üstel gecikme uygular.
    - Başarılı istek sonrası 4.5 sn güvenli soğuma süresi bırakır.
    """
    def __init__(self, api_keys: list = None, default_model: str = "gemini-3.5-flash-lite"):
        self.lock = threading.Lock()
        raw_keys = api_keys or GEMINI_API_KEYS
        if not raw_keys:
            raise ValueError(".env dosyasında geçerli GEMINI_API_KEYS bulunamadı!")
            
        self.api_keys = raw_keys
        self.clients = [
            genai.Client(api_key=k, http_options=types.HttpOptions(timeout=45000)) 
            for k in self.api_keys
        ]
        self.default_model = default_model
        
        self.current_key_idx = 0
        self.key_status = [{"backoff": 1, "next_available": 0.0} for _ in self.clients]
        self.last_sleep_log_time = 0.0
        self.last_request_time = 0.0
        self.min_request_interval = 0.52  # 11 anahtar için homojen akış (Tren modeli: her 0.52s'de 1 istek)

    def get_next_client(self):
        """Finds the next available key that is not on cooldown. (Thread-Safe & Paced)"""
        while True:
            sleep_needed = 0.0
            with self.lock:
                now = time.time()
                time_since_last = now - self.last_request_time
                if time_since_last < self.min_request_interval:
                    sleep_needed = self.min_request_interval - time_since_last
                else:
                    for _ in range(len(self.clients)):
                        idx = self.current_key_idx
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.clients)
                        if now >= self.key_status[idx]["next_available"]:
                            # Geçici 15 saniye kilit (Aynı anda başka iş parçacığı aynı anahtarı almasın diye)
                            self.key_status[idx]["next_available"] = now + 15.0
                            self.last_request_time = now
                            return self.clients[idx], idx

                    # Eğer hepsi soğumadaysa en erken açılacak olanı bul
                    soonest_time = min(status["next_available"] for status in self.key_status)
                    sleep_needed = max(soonest_time - now, 0.05)

            if sleep_needed > 0:
                if sleep_needed > 3.0 and now - self.last_sleep_log_time > 10.0:
                    logger.info(f"⏳ Anahtar güvenli soğuma döngüsü: {sleep_needed:.1f}s bekleniyor...")
                    self.last_sleep_log_time = now
                time.sleep(min(sleep_needed, 60))

    def report_error(self, key_idx: int, is_429: bool = True, err_msg: str = ""):
        """Applies intelligent backoff to a specific key."""
        with self.lock:
            status = self.key_status[key_idx]
            if is_429:
                backoff = status.get("backoff", 1)
                # Kademeli ceza: 20s -> 45s -> 90s (Tüm anahtarları birden 60s kitleyip domino etkisi yaratmaz)
                if backoff <= 1:
                    new_backoff = 20
                elif backoff <= 20:
                    new_backoff = 45
                else:
                    new_backoff = min(backoff * 2, 1800)
                status["backoff"] = new_backoff
                status["next_available"] = time.time() + new_backoff
                logger.warning(f"⏳ [Key #{key_idx + 1}] KOTA AŞILDI (429)! {new_backoff}s soğumaya alındı.")
            else:
                # Sunucu meşguliyeti (503) veya geçici ağ hatası: anahtarı cezalandırma, kısa dinlendir
                status["next_available"] = time.time() + 4.0

    def report_success(self, key_idx: int):
        """Resets the backoff for a key after a successful request."""
        with self.lock:
            self.key_status[key_idx]["backoff"] = 1
            # 15 RPM = 4.0s minimum. 5.5s güvenli aralık ile anahtar başına dakikada maksimum 10.9 istek (Kota aşımı imkansız).
            self.key_status[key_idx]["next_available"] = time.time() + 5.5

    def clean_json_response(self, text: str) -> str:
        """Extracts exact JSON array or object from AI output."""
        if not text:
            return ""
        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        first_bracket = text.find('[')
        first_brace = text.find('{')

        if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
            last_bracket = text.rfind(']')
            if last_bracket > first_bracket:
                return text[first_bracket:last_bracket+1]
        elif first_brace != -1:
            last_brace = text.rfind('}')
            if last_brace > first_brace:
                return text[first_brace:last_brace+1]

        return text

    def generate_json(self, prompt: str, system_instruction: str = "Sen profesyonel bir içerik yöneticisisin.", temperature: float = 0.3, model: str = None, max_retries: int = 5) -> Optional[Dict[str, Any]]:
        target_model = model or self.default_model
        attempt = 0
        current_prompt = prompt

        while attempt < max_retries:
            client, key_idx = self.get_next_client()
            try:
                response = client.models.generate_content(
                    model=target_model,
                    contents=current_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature,
                        max_output_tokens=8192,
                        response_mime_type="application/json"
                    )
                )
                raw_text = self.clean_json_response(response.text)
                parsed_json = json.loads(raw_text, strict=False)
                if isinstance(parsed_json, dict):
                    parsed_json["_meta_key_idx"] = key_idx + 1
                    
                self.report_success(key_idx)
                return parsed_json

            except json.JSONDecodeError:
                logger.warning(f"⚠️ [API Key #{key_idx + 1}] JSON format uyarısı. Otomatik format düzeltme tekrarı yapılıyor...")
                current_prompt = prompt + "\n\nDİKKAT: Tek satırlı, kaçış karakterleri tam ve geçerli JSON döndür. JSON harici hiçbir yazı, açıklama veya markdown ekleme."
                self.report_error(key_idx, is_429=False)
                time.sleep(3)
                attempt += 1

            except Exception as e:
                err_str = str(e).lower()

                if "429" in err_str or "quota" in err_str or "too_many" in err_str or "resource_exhausted" in err_str:
                    self.report_error(key_idx, is_429=True, err_msg=str(e))
                    continue  # Kota hataları retry sayısını tüketmez!
                elif "503" in err_str or "unavailable" in err_str or "overloaded" in err_str:
                    logger.warning(f"⚠️ [Sunucu Meşgul (503)] Key #{key_idx + 1} kısa dinlendiriliyor: {str(e)[:90]}")
                    self.report_error(key_idx, is_429=False)
                    time.sleep(2)
                    continue
                elif "400" in err_str or "403" in err_str or "invalid_argument" in err_str or "permission_denied" in err_str:
                    logger.error(f"❌ [GEMINI Key #{key_idx + 1}] GEÇERSİZ VEYA BOZUK API KEY! Hata: {str(e)[:150]}")
                    self.report_error(key_idx, is_429=False)
                elif "not_found" in err_str or "model" in err_str:
                    self.default_model = "gemini-3.5-flash-lite"
                    target_model = "gemini-3.5-flash-lite"
                    self.report_error(key_idx, is_429=False)
                else:
                    logger.warning(f"⚠️ [GEMINI Key #{key_idx + 1}] Hata: {str(e)[:120]}")
                    self.report_error(key_idx, is_429=False)

                attempt += 1

        return None

    def analyze_article(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prompt = build_analysis_prompt(article_data)
        return self.generate_json(prompt, system_instruction=SYSTEM_INSTRUCTION, temperature=0.7)

    def generate_carousel(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prompt = build_carousel_prompt(article_data)
        return self.generate_json(prompt, system_instruction=CAROUSEL_SYSTEM_INSTRUCTION, temperature=0.7)

# Singleton motor
gemini_rotator = GeminiRotatorEngine()
