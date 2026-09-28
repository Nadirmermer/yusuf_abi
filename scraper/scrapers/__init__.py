from typing import List, Type
from .base import BaseScraper
from .psychology_today import PsychologyTodayScraper
from .changing_minds import ChangingMindsScraper
from .simply_psychology import SimplyPsychologyScraper
from .decision_lab import TheDecisionLabScraper
from .generic import GenericScraper

# Scraper sınıflarının öncelik sırası (GenericScraper en sonda olmalı)
SCRAPER_REGISTRY: List[Type[BaseScraper]] = [
    PsychologyTodayScraper,
    ChangingMindsScraper,
    SimplyPsychologyScraper,
    TheDecisionLabScraper,
    GenericScraper,
]

def get_scraper(url: str) -> BaseScraper:
    """Verilen URL'yi destekleyen uygun scraper motorunu örneklendirir ve döndürür."""
    for scraper_cls in SCRAPER_REGISTRY:
        if scraper_cls.can_handle(url):
            return scraper_cls()
    return GenericScraper()

__all__ = [
    "BaseScraper",
    "PsychologyTodayScraper",
    "ChangingMindsScraper",
    "SimplyPsychologyScraper",
    "TheDecisionLabScraper",
    "GenericScraper",
    "get_scraper",
    "SCRAPER_REGISTRY",
]
