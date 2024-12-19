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
    male_first: Optional[str] = None
    female_first: Optional[str] = None
    male_time: Optional[str] = None
    female_time: Optional[str] = None
    male_athlete_number: Optional[int] = None
    female_athlete_number: Optional[int] = None    

    scraper_success_element = "tr.Results-table-row"

    @classmethod
    def _create_event_from_row(cls, row, course_id:str, country_id:str) -> 'Event':

        male_link = row.select_one('td:nth-of-type(5) a')
        female_link = row.select_one('td:nth-of-type(7) a')

        return cls(
            course_id =             str(course_id),
            country_id =            str(country_id),

            event_id=               str(row.get('data-parkrun')) if row.get('data-parkrun') else None,
            event_date=             str(row.get('data-date')),
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

    raw_course_event_id_lookup: t.Dict[str, t.Dict[str, Event]]


    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.base_path = config.base_path
        self.raw_course_event_history = {}
        self.raw_event_date_lookup = {}
        self.raw_event_id_lookup = {}


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


    def init_raw_course_event_date_lookup(self, course: Course):

        course_id = course.course_id
        events = self.get_raw_course_event_history(course=course)

        if course_id is not None and course_id not in self.raw_course_event_date_lookup:
            self.raw_course_event_date_lookup[course_id] = {event.event_date: event for event in events if event.event_date is not None}

        #What will trigger this init?


    def init_raw_course_event_id_lookup(self, course: Course):

        course_id = course.course_id
        events = self.get_raw_course_event_history(course=course)
        
        if course_id is not None and course_id not in self.raw_course_event_id_lookup:
            self.raw_course_event_id_lookup[course_id] = {str(event.event_id): event for event in events if event.event_id is not None}

        #What will trigger this init?

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


    # Raw methods
    def get_raw_course_event_history(self, course: Course) -> List['Event']:

        course_id = course.course_id

        if course_id is not None and course_id not in self.raw_course_event_history:
            self.init_raw_course_event_history(course=course)

        if course_id is not None and course_id in self.raw_course_event_history:
            return self.raw_course_event_history[course_id]
        else:
            return []

    def get_raw_course_event_ids(self, course: Course) -> List[str]:

        course_id = course.course_id

        events = self.get_raw_course_event_history(course=course)

        if course_id is not None and course_id in self.raw_course_event_history:
            return [event.event_id for event in events if event.event_id is not None]
        else:
            return []

    # Stored methods
    def get_stored_event_history(self, course: Course) -> List[Event]:

        course_id = course.course_id
        country_id = course.country_id
        # course_url = course.course_url

        df_events: pl.LazyFrame|None = self.read_parquet(course_id=course_id, country_id=country_id)

        if df_events is not None:
            return [Event(**row) for row in df_events.collect().to_dicts()]
        else:
            return []

    def get_stored_course_event_ids(self, course: Course) -> List[str]:

        course_id = course.course_id
        country_id = course.country_id

        return self.get_processed_ids(id_column='event_id', course_id=course_id, country_id=country_id)    


    def update_event_history(self, course: Course) -> None:
        
        """Process countries and return list of country IDs to process."""
        
        # config_countries = config.country_ids
        # config_courses = config.course_ids

        # raw_course_ids = list(orchestrator.raw_courses_lookup.keys())
        raw_event_history_ids = self.get_raw_course_event_ids(course=course)
        stored_event_history_ids = self.get_stored_course_event_ids(course=course)

        new_ids = [id_ for id_ in raw_event_history_ids if id_ not in stored_event_history_ids]

        if len(new_ids) > 0:
            print(f"Storing new event ids for course{course.course_id} : {new_ids}")
            raw_event_history = self.get_raw_course_event_history(course=course)
            self.write_parquet(data=raw_event_history, course_id=course.course_id, country_id=course.country_id)





    # def get_course_first_event_date(self, course: Course) -> Event:

    #     events = self.get_raw_course_event_history(course)
    #     event_dates = self.get_raw_course_event_date_lookup(events)
    #     return min(event_dates.keys())




    # #========================

    # @classmethod
    # def process(cls,config: ProcessingConfig,
    #             handlers: HandlerRegistry,
    #             orchestrator: ParkrunDataExtractionOrchestrator,
    #             course_ids: List[str]) -> None:
    #     """Process events and results for specified courses."""
        
    #     for course_id in course_ids:
    #         EventProcessor._process_course(
    #             course_id,
    #             config,
    #             handlers,
    #             orchestrator
    #         )

    # @classmethod
    # def _process_course(cls,course_id: str,
    #                    config: ProcessingConfig,
    #                    handlers: HandlerRegistry,
    #                    orchestrator: ParkrunDataExtractionOrchestrator) -> None:
    #     """Process events and results for a single course."""
    #     course = orchestrator.live_courses_lookup[course_id]
        
    #     # Check course start date
    #     first_event_date = orchestrator.get_course_first_event_date(course)
    #     if parser.parse(first_event_date).date() > parser.parse(config.processing_date).date():
    #         print(f"Course {course_id} starts after processing date. Skipping.")
    #         return

    #     # Process events
    #     EventProcessor._process_course_events(
    #         course,
    #         handlers,
    #         orchestrator
    #     )

    #     # Process results
    #     EventProcessor._process_course_results(
    #         course,
    #         handlers,
    #         orchestrator
    #     )

    # @classmethod
    # def _process_course_events(cls,course,
    #                          handlers: HandlerRegistry,
    #                          orchestrator: ParkrunDataExtractionOrchestrator) -> None:
    #     """Process events for a single course."""
    #     processed_event_ids = handlers.events_handler.get_processed_event_ids(
    #         course_id=course.course_id,
    #         country_id=course.country_id
    #     )

    #     new_events = orchestrator.extract_course_new_event_history(
    #         course,
    #         processed_event_ids
    #     )

    #     if new_events:
    #         events_to_write = list(new_events.values())
    #         handlers.events_handler.write_parquet(
    #             data=events_to_write,
    #             course_id=course.course_id,
    #             country_id=course.country_id
    #         )

    # @classmethod
    # def _process_course_results(cls,course,
    #                           handlers: HandlerRegistry,
    #                           orchestrator: ParkrunDataExtractionOrchestrator) -> None:
    #     """Process results for a single course."""
    #     known_event_ids = handlers.events_handler.get_processed_event_ids(
    #         course_id=course.course_id,
    #         country_id=course.country_id
    #     )
    #     processed_result_event_ids = handlers.results_handler.get_processed_result_event_ids(
    #         course_id=course.course_id,
    #         country_id=course.country_id
    #     )
        
    #     fully_processed_events = [
    #         event_id for event_id in known_event_ids 
    #         if event_id in processed_result_event_ids
    #     ]

    #     unprocessed_results = orchestrator.extract_course_unprocessed_result_events(
    #         course,
    #         fully_processed_events
    #     )

    #     for event in unprocessed_results:
    #         event_result = orchestrator.extract_raw_event_results(course, event)
    #         handlers.results_handler.write_parquet(
    #             event_result,
    #             course_id=course.course_id,
    #             country_id=course.country_id,
    #             event_id=event.event_id
    #         )
