# file: src/parkrun_scraper_sdk/base_scraper.py

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
from .session_manager import SessionManager

class BaseScraper:

    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }


    @classmethod
    def _fetch_data(cls, url: str) -> str:
        with SessionManager.get_session() as session:
            headers = cls._get_headers()            
            response = session.get(url, headers=headers)
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
    

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def _convert_time(time_str: Optional[str]) -> Optional[str]:
        if not time_str:
            return None
        seconds = int(time_str)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"    