# file: src/parkrun_scraper_sdk/result.py

from dataclasses import dataclass
from typing import List, Optional, Dict
import typing as t
from datetime import datetime
from dateutil import parser
import polars

from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .course import Course
from .event import Event, EventsHandler
from .base_parquet import BaseParquetHandler
from .config import ProcessingConfig

@dataclass
class Result(BaseDataclass):

    event_id:   Optional[str] = " "
    event_id_int: Optional[int] = None
    course_id:  Optional[str] = " "
    country_id: Optional[str] = " "
    series_id: Optional[str] = None
    event_date: Optional[str] = " "

    athlete_id:         Optional[str] = " "
    name:       Optional[str] = " "
    club:       Optional[str] = " "
    club_id:    Optional[str] = " "
    club_membership:    Optional[str] = " "    

    age_group_raw: Optional[str] = " "    
    age_group:  Optional[str] = " "
    age_bracket_local: Optional[str] = " "
    gender_flag_local: Optional[str] = " "
    gender_local:      Optional[str] = " "
    
    # gender_position: Optional[str] = " "
    position:   Optional[str] = " "
    age_grade_pct:  Optional[str] = " "

    time_formatted:     Optional[str] = ' '
    time_seconds:       Optional[int] = None
    # personal_best_formatted: Optional[str] = " "
    # personal_best_seconds:   Optional[int] = None
    # is_pb:                  str = "0" 

    achievement: Optional[str] = " "
    runs:       Optional[str] = " "
    volunteer_count:    str = '0'

    result_url:             Optional[str] = " "
    record_updated_date: Optional[str] = None

    # _scraper_success_element = "tr.Results-table-row"

    @classmethod
    def _create_result_from_row(cls, row, course_id: str, event_id: str, event_date: str, country_id: str, series_id: str,result_url: str) -> 'Result':


        record_updated_date = datetime.now().strftime("%Y-%m-%d")

        name_cell = row.select_one('.Results-table-td--name')
        time_cell = row.select_one('.Results-table-td--time')

        club_cell = row.select_one('.Results-table-td--club')
        club_link = club_cell.select_one('a')
        club_url = club_link['href'] if club_link else " "
        club_id = cls._extract_club_id(club_url) if club_url else " "
        # gender_cell = row.select_one('.Results-table-td--gender')

        athlete_link = name_cell.select_one('a')
        athlete_id = cls._extract_athlete_id(athlete_link['href']) if athlete_link else " "

        club_icon = name_cell.select_one('.Results-table--clubIcon')
        club_membership = club_icon['title'] if club_icon else " "

        # detailed_div = name_cell.select_one('.detailed')
        # gender_position = cls._extract_gender_position(detailed_div.text) if detailed_div else " "

        time_compact = time_cell.select_one('.compact')
        time = time_compact.text.strip() if time_compact else ''
        time_formatted = cls.format_time(time_str=time) if time_compact else " "
        time_seconds = cls.time_to_seconds(time_str=time) if time_compact else None

        time_detailed = time_cell.select_one('.detailed')
        # personal_best = cls._extract_personal_best(time_detailed.text) if time_detailed else " "
        # personal_best_formatted = cls.format_time(time_str=personal_best) if personal_best else " "
        # personal_best_seconds = cls.time_to_seconds(time_str=personal_best) if personal_best else None
        # is_pb = 'PB' in time_detailed.text if time_detailed else False

        age_group_detailed = row.get('data-agegroup')
        gender_flag_local = cls._extract_gender_flag_local(age_group_detailed) if age_group_detailed else " "
        age_group = cls._extract_age_group(age_group_detailed) if age_group_detailed else " "
        age_bracket_local = cls._extract_age_bracket(age_group_detailed) if age_group_detailed else " "


        event_date_str = datetime.strptime(event_date, "%Y-%m-%d").strftime("%Y-%m-%d") if event_date else " "

        return cls(

            course_id=      str(course_id),
            event_id=       str(event_id),
            event_id_int=   int(event_id),
            event_date=     str(event_date_str),
            country_id=     str(country_id),
            series_id =     str(object=series_id),

            athlete_id=     str(athlete_id),
            name=           str(row.get('data-name')),
            club=           str(row.get('data-club')),
            club_id=        str(club_id) if club_id is not None else " ",
            club_membership=str(club_membership),
 
            age_group_raw=      str(row.get('data-agegroup')),
            age_group=         str(age_group),
            age_bracket_local=str(age_bracket_local),
            gender_flag_local=                  str(gender_flag_local),
            gender_local=   str(row.get('data-gender')),

            # gender_position=str(gender_position),
            position=       str(row.get('data-position'))   if row.get('data-position') else " ",
            age_grade_pct=      str(row.get('data-agegrade'))   if row.get('data-agegrade') else " ",
            
            time_formatted= str(time_formatted),
            time_seconds=   int(time_seconds) if time_seconds is not None else None,
            # personal_best_formatted=  str(personal_best_formatted),
            # personal_best_seconds=   int(personal_best_seconds) if personal_best_seconds is not None else None,
            # is_pb=          str(is_pb),

            achievement=    str(row.get('data-achievement')) if row.get('data-achievement') else " ",
            runs=           str(row.get('data-runs'))       if row.get('data-runs') else " ",
            volunteer_count=str(row.get('data-vols'))       if row.get('data-vols') else " ",

            result_url = str(result_url),     
            record_updated_date = record_updated_date       
        )

    #Getters

    #Helper methods
    @staticmethod
    def _extract_athlete_id(href: str) -> Optional[int]:
        import re
        match = re.search(r'parkrunner/(\d+)', href)
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_club_id(href: str) -> Optional[str]:
        import re
        match = re.search(r'groups/(\d+)', href)
        return str(match.group(1)) if match else None


    # @staticmethod
    # def _extract_gender_position(text: str) -> Optional[int]:
    #     import re
    #     match = re.search(r'(\d+)\s*$', text)
    #     return int(match.group(1)) if match else None

    @staticmethod
    def _extract_personal_best(text: str) -> Optional[str]:
        import re
        match = re.search(r'PB\s*(\d{2}:\d{2})', text)
        return match.group(1) if match else None


    @staticmethod
    def _extract_gender_flag_local(text: str) -> Optional[str]:
        #The second character in the string, use substring of length 1
        return text[1] if len(text) > 1 else None

    @staticmethod
    def _extract_age_group(text: str) -> Optional[str]:
        return text[2:] if len(text) > 1 else None


    @staticmethod
    def _extract_age_bracket(text: str) -> Optional[str]:
        return text[0] if len(text) > 0 else None

    @classmethod
    def format_time(cls, time_str: Optional[str] = None) -> str|None:

        if time_str is None:
            return None

        # Remove any existing colons
        clean_time = time_str.replace(':', '')
        
        # Pad left with zeros to ensure 6 digits
        padded = clean_time.zfill(6)
        
        # Extract hours, minutes, seconds
        hours = padded[0:2]
        minutes = padded[2:4]
        seconds = padded[4:6]
        
        # Combine with colons
        return f"{hours}:{minutes}:{seconds}"
    
    @classmethod
    def time_to_seconds(cls, time_str: Optional[str] = None) -> int|None:

        formatted_time = cls.format_time(time_str)        
        if formatted_time is None:
            return None
        # Split on colons and get components
        hours, minutes, seconds = formatted_time.split(':')
        
        # Convert to integers and calculate total seconds
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


    # @classmethod
    # def format_time(cls, time_col):

    #     clean_time = time_col.replace(':', '')
    #     # Convert to string and pad left with zeros to ensure 6 digits
    #     padded = clean_time.cast('string').lpad(6, '0')
        
    #     # Extract hours, minutes, seconds
    #     hours = padded.substr(0, 2)
    #     minutes = padded.substr(2, 2)
    #     seconds = padded.substr(4, 2)
        
    #     # Combine with colons
    #     return hours + ':' + minutes + ':' + seconds

    # @classmethod
    # def time_to_seconds(cls, time_col) -> int:

    #     formatted = cls.format_time(time_col)
    #     # Split on colons and get components

    #     parts = formatted.split(':')
    #     hours = parts[0].cast('int64')
    #     minutes = parts[1].cast('int64')
    #     seconds = parts[2].cast('int64')
        
    #     # Convert to total seconds
    #     # hours * 3600 + minutes * 60 + seconds
    #     return (hours * 3600) + (minutes * 60) + seconds


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

    processed_course_event_ids: Dict[str, List[str]] = None

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.base_path = config.base_path
        self.init_stored_result_event_ids_by_course()

    # ================================
    # Stored Result Getters
    # ================================
    def get_stored_result_event_ids(self, course: Course ) -> List[str]:

        course_id = course.course_id
        if self.processed_course_event_ids is None:
            self.init_stored_result_event_ids_by_course()

        return self.processed_course_event_ids[course_id] if course_id in self.processed_course_event_ids else []
    

    def init_stored_result_event_ids_by_course(self) -> t.Dict[str, List[str]]:

        if self.processed_course_event_ids is None or self.processed_course_event_ids == {}:

            print("Initialising stored result event ids by course")

            table: polars.LazyFrame|None = self.read_parquet(country_id="*", course_id="*",  event_id="*")

            if table is not None:

                #Just get unique values of the id column
                course_ids: Dict[str, List[str]] = table.select("course_id").unique().collect().to_dict(as_series=False)
                course_event_ids: List[Dict[str, str]] = table.select("course_id", "event_id").unique().collect().to_dicts()

                #unique course_id
                unique_course_ids: t.Set[str] = set(course_ids["course_id"])
                self.processed_course_event_ids = {course_id: [] for course_id in unique_course_ids}
                
                #populate processed_course_event_ids dictionary
                {self.processed_course_event_ids[event_record["course_id"]].append(event_record["event_id"]) for event_record in course_event_ids}
            else:
                return {}

        return self.processed_course_event_ids



    # ================================
    # Raw Result Getters
    # ================================
    def get_raw_latest_results(self, course: Course) -> List['Result']:

        course_id =     course.course_id
        country_id =    course.country_id
        series_id =     course.series_id
        url =           f"{course.course_url}results/latestresults/"
        html =          self._fetch_data(url=url)
        soup =          self._parse_html(html=html)
        result_rows =   soup.select(selector="tr.Results-table-row")

        return [Result._create_result_from_row(row=row, course_id=course_id, event_id="latestresults", event_date=None, country_id=country_id, series_id=series_id, result_url=url) for row in result_rows]

    def get_raw_event_result(self, course: Course, event: Event) -> List['Result']:

        course_id =     course.course_id
        country_id =    course.country_id
        series_id =     course.series_id

        if event.course_id != course_id:
            raise ValueError(f"Event {event.event_id} is not from course {course_id}")

        event_id =      event.event_id
        event_date =    event.event_date

        url =           f"{course.course_url}results/{event_id}/"
        html =          self._fetch_data(url)
        soup =          self._parse_html(html)
        result_rows =   soup.select("tr.Results-table-row")

        return [Result._create_result_from_row(row=row, course_id=course_id, event_id=event_id, event_date=event_date, country_id=country_id, series_id=series_id, result_url=url) for row in result_rows]


    # ================================
    # Stored Result Updaters
    # ================================
    def process_event_results(self, events_handler: EventsHandler, course: Course) -> None:

        course_id = course.course_id
        country_id = course.country_id
        processing_date: datetime = datetime.strptime(self.config.processing_date, "%Y-%m-%d")

        known_event_ids =            events_handler.get_stored_course_event_ids(course=course)
        # processed_result_event_ids = self.get_processed_ids(id_column='event_id', course_id=course_id, country_id=country_id, event_id="*")
        # fully_processed_result_event_ids =  [event_id for event_id in known_event_ids if event_id in processed_result_event_ids]
        fully_processed_result_event_ids = self.get_stored_result_event_ids(course=course)

        unprocessed_result_event_ids =      [event_id for event_id in known_event_ids if event_id not in fully_processed_result_event_ids]
        processable_result_event_ids = [event_id for event_id in unprocessed_result_event_ids if self.is_event_result_processable(events_handler=events_handler, course=course, event_id=event_id, processing_date=processing_date)]

        print(f"known_event_ids: {known_event_ids}")
        print(f"fully_processed_result_event_ids: {fully_processed_result_event_ids}")
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


