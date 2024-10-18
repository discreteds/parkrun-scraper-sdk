# file: src/parkrun_scraper_sdk/course.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
# from .course import Course

@dataclass
class Event(BaseDataclass, BaseScraper): 

    course_id: Optional[str] = None
    country_id: Optional[str] = None
    event_id: Optional[str] = None
    event_date: Optional[datetime] = None

    finishers: Optional[int] = None
    volunteers: Optional[int] = None
    male_first: Optional[str] = None
    female_first: Optional[str] = None
    male_time: Optional[str] = None
    female_time: Optional[str] = None
    male_athlete_number: Optional[int] = None
    female_athlete_number: Optional[int] = None    



    @classmethod
    def _create_history_from_row(cls, row, course_id:str, country_id:str) -> 'Event':

        male_link = row.select_one('td:nth-of-type(5) a')
        female_link = row.select_one('td:nth-of-type(7) a')

        return cls(
            course_id =             str(course_id),
            country_id =            str(country_id),

            event_id=               str(row.get('data-parkrun')) if row.get('data-parkrun') else None,
            event_date=             str(cls._parse_date(row.get('data-date'))),
            finishers=              str(row.get('data-finishers')) if row.get('data-finishers') else None,
            volunteers=             str(row.get('data-volunteers')) if row.get('data-volunteers') else None,
            male_first=             str(row.get('data-male')) if row.get('data-male') else None,
            female_first=           str(row.get('data-female')) if row.get('data-female') else None,
            male_time=              str(row.get('data-maletime')),
            female_time=            str(row.get('data-femaletime')),
            male_athlete_number=    str(cls._extract_athlete_number(male_link['href'])) if male_link else None,
            female_athlete_number=  str(cls._extract_athlete_number(female_link['href'])) if female_link else None            
        )

    # Getters
    @classmethod
    def get_event_history(cls, course_id: str, course_url: str, country_id: str) -> List['Event']:

        url =           f"{course_url}results/eventhistory/"
        html =          cls._fetch_data(url)
        soup =          cls._parse_html(html)
        history_rows =  soup.select("tr.Results-table-row")
        return [cls._create_history_from_row(row, course_id, country_id) for row in history_rows]


    # Helper methods


    @staticmethod
    def _extract_athlete_number(href: str) -> Optional[int]:
        import re
        match = re.search(r'athleteNumber=(\d+)', href)
        return str(match.group(1)) if match else None

    # def __post_init__(self):
    #     # Ensure numeric fields are of the correct type
    #     for field in ['finishers', 'volunteers', 'male_athlete_number', 'female_athlete_number']:
    #         value = getattr(self, field)
    #         if isinstance(value, str):
    #             setattr(self, field, int(value) if value.isdigit() else None)
        
    #     # Parse date if it's a string
    #     if isinstance(self.event_date, str):
    #         self.event_date = self._parse_date(self.event_date)

    # def to_dict(self):
    #     result = super().to_dict()
    #     # Convert datetime to string for JSON serialization
    #     # if result['event_date']:
    #     #     result['event_date'] = result['event_date'].strftime("%Y-%m-%d")
    #     return result
    
