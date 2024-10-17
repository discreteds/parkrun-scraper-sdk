# file: src/parkrun_scraper_sdk/country.py

from dataclasses import dataclass
from typing import List, Optional
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper


@dataclass
class Country(BaseDataclass, BaseScraper):
    country_id: Optional[str] = None
    country_url:        Optional[str] = None

    @classmethod
    def get_all_countries(cls) -> List['Country']:
        url = "https://images.parkrun.com/events.json"
        data = cls._fetch_data(url)
        countries_json = cls._parse_json(data)
        return [cls._create_country_from_json(country_id, country_data) 
                for country_id, country_data in countries_json["countries"].items()]

    @classmethod
    def _create_country_from_json(cls, country_id: str, country_data: dict) -> 'Country':
        return cls(
            country_id= country_id,
            country_url=        f"https://{country_data['url']}"
        )

    def __post_init__(self):
        if self.country_url and not self.country_url.startswith('http'):
            self.country_url = f"https://{self.country_url}"

