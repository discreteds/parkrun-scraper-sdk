# file: src/parkrun_scraper_sdk/course.py

from dataclasses import dataclass
from typing import List, Optional
import typing as t
from datetime import datetime
import polars as pl
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .course import Course
from .base_parquet import BaseParquetHandler
from .config import ProcessingConfig

@dataclass
class Event(BaseDataclass): 

    course_id: Optional[str] = None
    country_id: Optional[str] = None
    event_id: Optional[str] = None
    event_date: Optional[datetime] = None

    finishers: Optional[int] = None
    volunteers: Optional[int] = None

    male_first_athlete_name: Optional[str] = None
    female_first_athlete_name: Optional[str] = None
    male_time: Optional[str] = None
    female_time: Optional[str] = None
    male_athlete_number: Optional[int] = None
    female_athlete_number: Optional[int] = None    

    # male_athlete_link: Optional[int] = None
    # female_athlete_link: Optional[int] = None    

    _scraper_success_element = "tr.Results-table-row"

    @classmethod
    def _create_event_from_row(cls, row, course_id:str, country_id:str) -> 'Event':

        # print(row)

        male_link =     row.select_one('td:nth-of-type(5) a')
        female_link =   row.select_one('td:nth-of-type(7) a')

        # male_time_raw = row.select_one('data-maletime')
        # male_time =     male_time_raw.text.strip() if male_time_raw else ''

        # female_time_raw = row.select_one('data-femaletime')
        # female_time =   female_time_raw.text.strip() if female_time_raw else ''



        return cls(
            course_id =             str(course_id),
            country_id =            str(country_id),

            event_id=               str(row.get('data-parkrun')) if row.get('data-parkrun') else None,
            event_date=             str(row.get('data-date')),
            finishers=              str(row.get('data-finishers')) if row.get('data-finishers') else None,
            volunteers=             str(row.get('data-volunteers')) if row.get('data-volunteers') else None,

            male_first_athlete_name=             str(row.get('data-male')) if row.get('data-male') else None,
            female_first_athlete_name=           str(row.get('data-female')) if row.get('data-female') else None,
            male_time=              str(row.get('data-maletime')) if row.get('data-maletime') else None,
            female_time=            str(row.get('data-femaletime')) if row.get('data-femaletime') else None,
            male_athlete_number=    str(cls._extract_athlete_number(male_link['href'])) if male_link else None,
            female_athlete_number=  str(cls._extract_athlete_number(female_link['href'])) if female_link else None,            
        )

    # Getters


    # Helper methods


    @staticmethod
    def _extract_athlete_number(href: str) -> Optional[int]:
        import re
        match = re.search(r'parkrunner/(\d+)', href)

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
    


class EventsHandler(BaseParquetHandler, BaseScraper):

    domain_folder: str = "events"
    file_name_template: str = "events_{course_id}.parquet"
    partition_keys: List[str] = ['country_id']

    raw_course_event_history: t.Dict[str, List['Event']]
    raw_course_event_date_lookup: t.Dict[str, t.Dict[datetime, Event]]
    raw_course_event_id_date_lookup: t.Dict[str, t.Dict[str, datetime]]
    raw_course_event_id_lookup: t.Dict[str, t.Dict[str, Event]]


    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.base_path = config.base_path
        self.raw_course_event_history = {}
        self.raw_course_event_date_lookup = {}
        self.raw_course_event_id_date_lookup = {}
        self.raw_course_event_id_lookup = {}


    # ================================
    # Raw Event Initialisers
    # ================================
    def init_raw_course_event_history(self, course: Course) -> None:

        course_id = course.course_id
        country_id = course.country_id
        course_url = course.course_url

        if course_id is not None and course_id not in self.raw_course_event_history:

            url =           f"{course_url}results/eventhistory/"
            html =          self._fetch_data(url)
            soup =          self._parse_html(html)
            history_rows =  soup.select("tr.Results-table-row")

            self.raw_course_event_history[course_id] = [Event._create_event_from_row(row, course_id, country_id) for row in history_rows]


    # ================================
    # Raw Event Lookup Initialisers
    # ================================
    def init_raw_course_event_date_lookup(self, course: Course):

        course_id = course.course_id
        events = self.get_raw_course_event_history(course=course)

        if course_id is not None and course_id not in self.raw_course_event_date_lookup:
            self.raw_course_event_date_lookup[course_id] = {event.event_date: event for event in events if event.event_date is not None}


    def init_raw_course_event_id_date_lookup(self, course: Course):

        course_id = course.course_id
        events = self.get_raw_course_event_history(course=course)

        if course_id is not None and course_id not in self.raw_course_event_id_date_lookup:
            self.raw_course_event_id_date_lookup[course_id] = {event.event_id: event.event_date for event in events if event.event_id is not None and event.event_date is not None}


    def init_raw_course_event_id_lookup(self, course: Course):

        course_id = course.course_id
        events = self.get_raw_course_event_history(course=course)
        
        if course_id is not None and course_id not in self.raw_course_event_id_lookup:
            self.raw_course_event_id_lookup[course_id] = {str(event.event_id): event for event in events if event.event_id is not None}


    # ================================
    # Raw Event Lookup Getters
    # ================================
    def get_raw_course_event_id_lookup(self, course: Course, event_id: str) -> Event|None:
        course_id = course.course_id

        if course_id is not None and course_id not in self.raw_course_event_id_lookup:
            self.init_raw_course_event_id_lookup(course=course)

        if course_id is not None and course_id in self.raw_course_event_id_lookup:
            if event_id is not None and event_id in self.raw_course_event_id_lookup[course_id]:
                return self.raw_course_event_id_lookup[course_id][event_id]
            else:
                return None
        else:
            return None


    def get_raw_course_event_date_lookup(self, course: Course, event_date: datetime) -> Event|None:
        course_id = course.course_id

        if course_id is not None and course_id not in self.raw_course_event_date_lookup:
            self.init_raw_course_event_date_lookup(course=course)


        if course_id is not None and course_id in self.raw_course_event_date_lookup:
            if event_date is not None and event_date in self.raw_course_event_date_lookup[course_id]:
                return self.raw_course_event_date_lookup[course_id][event_date]
            else:
                return None
        else:
            return None


    def get_raw_course_event_id_date_lookup(self, course: Course, event_id: str) -> datetime|None:
        course_id = course.course_id

        if course_id is not None and course_id not in self.raw_course_event_id_date_lookup:
            self.init_raw_course_event_id_date_lookup(course=course)


        if course_id is not None and course_id in self.raw_course_event_id_date_lookup:
            if event_id is not None and event_id in self.raw_course_event_id_date_lookup[course_id]:
                return self.raw_course_event_id_date_lookup[course_id][event_id]
            else:
                return None
        else:
            return None

    # ================================
    # Raw Event Getters
    # ================================
    def get_raw_course_event_history(self, course: Course) -> List['Event']:

        course_id = course.course_id

        if course_id is not None and course_id not in self.raw_course_event_history:
            self.init_raw_course_event_history(course=course)

        return self.raw_course_event_history[course_id]  if course_id is not None and course_id in self.raw_course_event_history else []

    def get_raw_course_event_ids(self, course: Course) -> List[str]:

        course_id = course.course_id

        events = self.get_raw_course_event_history(course=course)

        return [event.event_id for event in events if event.event_id is not None] if course_id is not None and course_id in self.raw_course_event_history else []

    # ================================
    # Stored Event Getters
    # ================================
    def get_stored_event_history(self, course: Course) -> List[Event]:

        course_id = course.course_id
        country_id = course.country_id

        df_events: pl.LazyFrame|None = self.read_parquet(course_id=course_id, country_id=country_id)

        return [Event(**row) for row in df_events.collect().to_dicts()] if df_events is not None else []


    def get_stored_course_event_ids(self, course: Course) -> List[str]:

        course_id = course.course_id
        country_id = course.country_id

        return self.get_processed_ids(id_column='event_id', course_id=course_id, country_id=country_id)    


    # ================================
    # Stored Event Updaters
    # ================================
    def update_event_history(self, course: Course) -> None:
        """Process countries and return list of country IDs to process."""

        raw_event_history_ids = self.get_raw_course_event_ids(course=course)
        stored_event_history_ids = self.get_stored_course_event_ids(course=course)

        new_ids = [id_ for id_ in raw_event_history_ids if id_ not in stored_event_history_ids]

        if len(new_ids) > 0:
            print(f"Storing new event ids for course{course.course_id} : {new_ids}")
            raw_event_history = self.get_raw_course_event_history(course=course)
            self.write_parquet(data=raw_event_history, course_id=course.course_id, country_id=course.country_id)

