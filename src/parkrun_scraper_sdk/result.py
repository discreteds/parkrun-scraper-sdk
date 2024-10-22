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

    event_id:   Optional[str] = " "
    course_id:  Optional[str] = " "
    country_id: Optional[str] = " "
    event_date: Optional[str] = " "

    name:       Optional[str] = " "
    age_group:  Optional[str] = " "
    club:       Optional[str] = " "
    gender:     Optional[str] = " "
    gender_position: Optional[str] = " "
    position:   Optional[str] = " "
    runs:       Optional[str] = " "
    age_grade:  Optional[str] = " "
    achievement: Optional[str] = " "

    volunteer_count:    str = '0'
    time:               str = ' '
    personal_best:      Optional[str] = " "
    athlete_id:         Optional[str] = " "
    is_pb:              str = "0"
    club_membership:    Optional[str] = " "    

    scraper_success_element = "tr.Results-table-row"

    @classmethod
    def _create_result_from_row(cls, row, course_id: str, event_id: str, event_date: str, country_id: str) -> 'Result':


        name_cell = row.select_one('.Results-table-td--name')
        time_cell = row.select_one('.Results-table-td--time')
        # gender_cell = row.select_one('.Results-table-td--gender')

        athlete_link = name_cell.select_one('a')
        athlete_id = cls._extract_athlete_id(athlete_link['href']) if athlete_link else " "

        club_icon = name_cell.select_one('.Results-table--clubIcon')
        club_membership = club_icon['title'] if club_icon else " "

        detailed_div = name_cell.select_one('.detailed')
        gender_position = cls._extract_gender_position(detailed_div.text) if detailed_div else " "

        time_compact = time_cell.select_one('.compact')
        time = time_compact.text.strip() if time_compact else ''

        time_detailed = time_cell.select_one('.detailed')
        personal_best = cls._extract_personal_best(time_detailed.text) if time_detailed else " "
        is_pb = 'PB' in time_detailed.text if time_detailed else False

        return cls(

            course_id=      str(course_id),
            event_id=       str(event_id),
            event_date=     str(event_date),
            country_id=     str(country_id),

            name=           str(row.get('data-name')),
            age_group=      str(row.get('data-agegroup')),
            club=           str(row.get('data-club')),
            gender=         str(row.get('data-gender')),
            gender_position=str(gender_position),
            position=       str(row.get('data-position'))   if row.get('data-position') else " ",
            runs=           str(row.get('data-runs'))       if row.get('data-runs') else " ",
            age_grade=      str(row.get('data-agegrade'))   if row.get('data-agegrade') else " ",
            achievement=    str(row.get('data-achievement')) if row.get('data-achievement') else " ",
            volunteer_count=str(row.get('data-vols'))       if row.get('data-vols') else " ",
            time=           str(time),
            personal_best=  str(personal_best),
            athlete_id=     str(athlete_id),
            is_pb=          str(is_pb),
            club_membership=str(club_membership)            
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

    # def __post_init__(self):
    #     # Ensure numeric fields are of the correct type\

    #     if isinstance(self.position, str):
    #         self.position = int(self.position) if self.position.isdigit() else None
    #     if isinstance(self.runs, str):
    #         self.runs = int(self.runs) if self.runs.isdigit() else None
        
    #     # self.volunteer_count = int(self.volunteer_count) if self.volunteer_count.isdigit() else None

    #     if isinstance(self.age_grade, str):
    #         try:
    #             self.age_grade = float(self.age_grade)
    #         except ValueError:
    #             self.age_grade = None
    #     if self.gender_position:
    #         self.gender_position = int(self.gender_position)                