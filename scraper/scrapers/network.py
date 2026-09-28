import logging
from typing import Optional, Dict
from dataclasses import dataclass
from curl_cffi import requests
from config.settings import settings

logger = logging.getLogger("NetworkClient")
logger.setLevel(logging.ERROR)

@dataclass
class NetworkResponse:
    url: str
    status_code: int
    text: str
    is_markdown: bool = False
    source_method: str = "direct"
    headers: Optional[Dict[str, str]] = None

class NetworkClient:
    def __init__(self, timeout: int = settings.REQUEST_TIMEOUT):
        self.timeout = timeout

    def fetch(self, url: str, force_jina: bool = False) -> NetworkResponse:
        """Sessiz ve akıllı ağ istemcisi."""
        if not force_jina:
            try:
                resp = requests.get(
                    url,
                    impersonate=settings.CHROME_IMPERSONATE,
                    timeout=self.timeout,
                    headers={
                        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                    }
                )
                if resp.status_code == 200 and len(resp.text) > 1000:
                    lower_text = resp.text.lower()
                    if "502 bad gateway" not in lower_text and "just a moment..." not in lower_text:
                        return NetworkResponse(
                            url=url,
                            status_code=200,
                            text=resp.text,
                            is_markdown=False,
                            source_method="direct",
                            headers=dict(resp.headers)
                        )
            except Exception:
                pass

        # Fallback: Jina Reader API
        return self._fetch_jina(url)

    def _fetch_jina(self, url: str) -> NetworkResponse:
        import requests as std_requests
        jina_url = f"{settings.JINA_READER_PREFIX}{url}"
        
        try:
            resp = std_requests.get(
                jina_url,
                timeout=self.timeout + 10,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "X-Return-Format": "markdown"
                }
            )
            
            if resp.status_code == 200 and len(resp.text) > 200:
                return NetworkResponse(
                    url=url,
                    status_code=200,
                    text=resp.text,
                    is_markdown=True,
                    source_method="jina_fallback",
                    headers=dict(resp.headers)
                )
            else:
                raise RuntimeError(f"Sayfa çekilemedi (HTTP {resp.status_code})")
        except Exception as e:
            raise

network_client = NetworkClient()
