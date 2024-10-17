# file: src/parkrun_scraper_sdk/result.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .course import Course
from .event import Event

@dataclass
class Result(BaseDataclass, BaseScraper):

    event_id: Optional[str] = None
    course_id: Optional[str] = None
    country_id: Optional[str] = None
    event_date: Optional[datetime] = None

    name: Optional[str] = None
    age_group: Optional[str] = None
    club: Optional[str] = None
    gender: Optional[str] = None
    gender_position: Optional[int] = None
    position: Optional[int] = None
    runs: Optional[int] = None
    age_grade: Optional[float] = None
    achievement: Optional[str] = None

    volunteer_count: int = 0
    time: str = ''
    personal_best: Optional[str] = None
    athlete_id: Optional[int] = None
    is_pb: bool = False
    club_membership: Optional[str] = None    



    @classmethod
    def _create_result_from_row(cls, row, course_id: str, event_id: str, event_date: str, country_id: str) -> 'Result':


        name_cell = row.select_one('.Results-table-td--name')
        time_cell = row.select_one('.Results-table-td--time')
        # gender_cell = row.select_one('.Results-table-td--gender')

        athlete_link = name_cell.select_one('a')
        athlete_id = cls._extract_athlete_id(athlete_link['href']) if athlete_link else None

        club_icon = name_cell.select_one('.Results-table--clubIcon')
        club_membership = club_icon['title'] if club_icon else None

        detailed_div = name_cell.select_one('.detailed')
        gender_position = cls._extract_gender_position(detailed_div.text) if detailed_div else None

        time_compact = time_cell.select_one('.compact')
        time = time_compact.text.strip() if time_compact else ''

        time_detailed = time_cell.select_one('.detailed')
        personal_best = cls._extract_personal_best(time_detailed.text) if time_detailed else None
        is_pb = 'PB' in time_detailed.text if time_detailed else False

        return cls(

            course_id=      course_id,
            event_id=       event_id,
            event_date=     event_date,
            country_id=     country_id,

            name=           row.get('data-name'),
            age_group=      row.get('data-agegroup'),
            club=           row.get('data-club'),
            gender=         row.get('data-gender'),
            gender_position=gender_position,
            position=       int(row.get('data-position'))   if row.get('data-position') else None,
            runs=           int(row.get('data-runs'))       if row.get('data-runs') else None,
            age_grade=      float(row.get('data-agegrade')) if row.get('data-agegrade') else None,
            achievement=    row.get('data-achievement')     if row.get('data-achievement') else None,
            volunteer_count=int(row.get('data-vols'))       if row.get('data-vols') else None,
            time=           time,
            personal_best=  personal_best,
            athlete_id=     athlete_id,
            is_pb=          is_pb,
            club_membership=club_membership            
        )

    #Getters
    @classmethod
    def get_latest_results(cls, course: Course) -> List['Result']:
        return cls.get_results(course, "latestresults")

    @classmethod
    def get_results(cls, course: Course, event: Event) -> List['Result']:

        course_id =     course.course_id
        country_id =    course.country_id
        event_id =      event.event_id
        event_date =    event.event_date

        url =           f"{course.course_url}results/{event_id}/"
        html =          cls._fetch_data(url)
        soup =          cls._parse_html(html)
        result_rows =   soup.select("tr.Results-table-row")
        return [cls._create_result_from_row(row, course_id, event_id, event_date, country_id) for row in result_rows]


    #Helper methods
    @staticmethod
    def _extract_athlete_id(href: str) -> Optional[int]:
        import re
        match = re.search(r'parkrunner/(\d+)', href)
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_gender_position(text: str) -> Optional[int]:
        import re
        match = re.search(r'(\d+)\s*$', text)
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_personal_best(text: str) -> Optional[str]:
        import re
        match = re.search(r'PB\s*(\d{2}:\d{2})', text)
        return match.group(1) if match else None

    @classmethod
    def get_latest_results(cls, event):
        return cls.get_results(event, "latestresults")

    def __post_init__(self):
        # Ensure numeric fields are of the correct type
        if isinstance(self.position, str):
            self.position = int(self.position) if self.position.isdigit() else None
        if isinstance(self.runs, str):
            self.runs = int(self.runs) if self.runs.isdigit() else None
        
        # self.volunteer_count = int(self.volunteer_count) if self.volunteer_count.isdigit() else None

        if isinstance(self.age_grade, str):
            try:
                self.age_grade = float(self.age_grade)
            except ValueError:
                self.age_grade = None
        if self.gender_position:
            self.gender_position = int(self.gender_position)                