# file: src/parkrun_scraper_sdk/result.py

from dataclasses import dataclass
from typing import List, Optional
import typing as t
from datetime import datetime
from dateutil import parser

from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .course import Course
from .event import Event, EventsHandler
from .base_parquet import BaseParquetHandler
from .config import ProcessingConfig

@dataclass
class Result(BaseDataclass):

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
    result_url:         Optional[str] = " "

    # _scraper_success_element = "tr.Results-table-row"

    @classmethod
    def _create_result_from_row(cls, row, course_id: str, event_id: str, event_date: str, country_id: str, result_url: str) -> 'Result':


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

        #Format event_date as a string YYYY-MMM-DD

        event_date_str = datetime.strptime(event_date, "%Y-%m-%d").strftime("%Y-%b-%d") if event_date else " "

        return cls(

            course_id=      str(course_id),
            event_id=       str(event_id),
            event_date=     str(event_date_str),
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
            club_membership=str(club_membership),
            result_url = str(result_url)            
        )

    #Getters

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


class ResultsHandler(BaseParquetHandler, BaseScraper):

    domain_folder: str = "results"
    file_name_template: str = "results_{course_id}_{event_id}.parquet"
    partition_keys: List[str] = ['country_id', 'course_id']


    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.base_path = config.base_path

    # ================================
    # Stored Result Getters
    # ================================
    def get_stored_result_event_ids(self, course: Course ) -> List[str]:

        course_id = course.course_id
        country_id = course.country_id

        event_ids =  self.get_processed_ids('event_id', course_id=course_id, country_id=country_id, event_id="*")
        
        return list(set(event_ids))

    # ================================
    # Raw Result Getters
    # ================================
    def get_raw_latest_results(self, course: Course) -> List['Result']:

        course_id =     course.course_id
        country_id =    course.country_id

        url =           f"{course.course_url}results/latestresults/"
        html =          self._fetch_data(url=url)
        soup =          self._parse_html(html=html)
        result_rows =   soup.select(selector="tr.Results-table-row")

        return [Result._create_result_from_row(row=row, course_id=course_id, event_id="latestresults", event_date=None, country_id=country_id, result_url=url) for row in result_rows]

    def get_raw_event_result(self, course: Course, event: Event) -> List['Result']:

        course_id =     course.course_id
        country_id =    course.country_id

        if event.course_id != course_id:
            raise ValueError(f"Event {event.event_id} is not from course {course_id}")

        event_id =      event.event_id
        event_date =    event.event_date

        url =           f"{course.course_url}results/{event_id}/"
        html =          self._fetch_data(url)
        soup =          self._parse_html(html)
        result_rows =   soup.select("tr.Results-table-row")

        return [Result._create_result_from_row(row=row, course_id=course_id, event_id=event_id, event_date=event_date, country_id=country_id, result_url=url) for row in result_rows]


    # ================================
    # Stored Result Updaters
    # ================================
    def process_event_results(self, events_handler: EventsHandler, course: Course) -> None:

        course_id = course.course_id
        country_id = course.country_id
        processing_date: datetime = datetime.strptime(self.config.processing_date, "%Y-%m-%d")

        known_event_ids =            events_handler.get_processed_ids(id_column='event_id', course_id=course_id, country_id=country_id)
        processed_result_event_ids = self.get_processed_ids(id_column='event_id', course_id=course_id, country_id=country_id, event_id="*")

        fully_processed_result_event_ids =  [event_id for event_id in known_event_ids if event_id in processed_result_event_ids]
        unprocessed_result_event_ids =      [event_id for event_id in known_event_ids if event_id not in processed_result_event_ids]

        processable_result_event_ids = [event_id for event_id in unprocessed_result_event_ids if self.is_event_result_processable(events_handler=events_handler, course=course, event_id=event_id, processing_date=processing_date)]

        print(f"processed_result_event_ids: {fully_processed_result_event_ids}")
        print(f"unprocessed_result_events: {unprocessed_result_event_ids}")
        print(f"processable_result_events: {processable_result_event_ids}")

        for event_id in processable_result_event_ids:

            event: Event|None = events_handler.get_raw_course_event_id_lookup(course=course, event_id=event_id)

            if event is not None:

                event_result = self.get_raw_event_result(course=course, event=event)
                self.write_parquet(event_result, course_id=course.course_id, country_id=course.country_id, event_id=event.event_id)




    def is_event_result_processable(self, events_handler: EventsHandler, course: Course, event_id: str, processing_date: datetime) -> bool:

        raw_event_date = events_handler.get_raw_course_event_id_date_lookup(course=course, event_id=event_id)

        # event_id = event.event_id
        event_date =  datetime.strptime( str(raw_event_date), "%Y-%m-%d") if raw_event_date is not None else None

        if event_date is None:
            return False
        if event_date > processing_date:
            return False

        return True


