# file: src/parkrun_scraper_sdk/course.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .course import Course

@dataclass
class Event(BaseDataclass, BaseScraper): 
    course_id: Optional[str] = None

    event_number: Optional[int] = None
    date: Optional[datetime] = None
    finishers: Optional[int] = None
    volunteers: Optional[int] = None
    male_first: Optional[str] = None
    female_first: Optional[str] = None
    male_time: Optional[str] = None
    female_time: Optional[str] = None
    male_athlete_number: Optional[int] = None
    female_athlete_number: Optional[int] = None    



    @classmethod
    def _create_history_from_row(cls, row, course_id) -> 'Event':


        male_link = row.select_one('td:nth-of-type(5) a')
        female_link = row.select_one('td:nth-of-type(7) a')

        return cls(
            course_id = course_id,

            event_number=int(row.get('data-parkrun')) if row.get('data-parkrun') else None,
            date=cls._parse_date(row.get('data-date')),
            finishers=int(row.get('data-finishers')) if row.get('data-finishers') else None,
            volunteers=int(row.get('data-volunteers')) if row.get('data-volunteers') else None,
            male_first=str(row.get('data-male')) if row.get('data-male') else None,
            female_first=str(row.get('data-female')) if row.get('data-female') else None,
            male_time=row.get('data-maletime'),
            female_time=row.get('data-femaletime'),
            male_athlete_number=cls._extract_athlete_number(male_link['href']) if male_link else None,
            female_athlete_number=cls._extract_athlete_number(female_link['href']) if female_link else None            
        )

    # Getters
    @classmethod
    def get_event_history(cls, course: Course) -> List['Event']:

        course_id = course.id
        url = f"{course.url}results/eventhistory/"
        html = cls._fetch_data(url)
        soup = cls._parse_html(html)
        history_rows = soup.select("tr.Results-table-row")
        return [cls._create_history_from_row(row, course_id) for row in history_rows]


    # Helper methods
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

    @staticmethod
    def _extract_athlete_number(href: str) -> Optional[int]:
        import re
        match = re.search(r'athleteNumber=(\d+)', href)
        return int(match.group(1)) if match else None

    def __post_init__(self):
        # Ensure numeric fields are of the correct type
        for field in ['event_number', 'finishers', 'volunteers', 'male_athlete_number', 'female_athlete_number']:
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, int(value) if value.isdigit() else None)
        
        # Parse date if it's a string
        if isinstance(self.date, str):
            self.date = self._parse_date(self.date)

    def to_dict(self):
        result = super().to_dict()
        # Convert datetime to string for JSON serialization
        if result['date']:
            result['date'] = result['date'].strftime("%Y-%m-%d")
        return result