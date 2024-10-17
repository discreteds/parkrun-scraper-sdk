# file: src/parkrun_scraper_sdk/base_scraper.py

from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .session_manager import SessionManager

class BaseScraper:
    @classmethod
    def _fetch_data(cls, url: str) -> str:
        with SessionManager.get_session() as session:
            response = session.get(url)
            response.raise_for_status()
            return response.text

    @classmethod
    def _parse_html(cls, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    @classmethod
    def _extract_data(cls, soup: BeautifulSoup, selector: str) -> List[Dict[str, Any]]:
        rows = soup.select(selector)
        return [
            {
                cell.get('class', [''])[0]: cell.text.strip()
                for cell in row.find_all('td')
            }
            for row in rows
        ]
    
    @classmethod
    def _parse_json(cls, json_string: str) -> dict:
        import json
        return json.loads(json_string)    