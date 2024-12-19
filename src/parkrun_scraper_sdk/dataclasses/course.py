# file: src/parkrun_scraper_sdk/course.py

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import typing as t
import polars as pl
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .country import Country
# from .event import Event
from .base_parquet import BaseParquetHandler
from .config import ProcessingConfig
from upath import UPath

@dataclass
class Course(BaseDataclass):

    course_id:      Optional[str] = None
    country_id:     Optional[str] = None

    coordinates:    Optional[Tuple[str, str]] = None    
    eventname:      Optional[str] = None    
    long_name:      Optional[str] = None
    short_name:     Optional[str] = None
    local_long_name: Optional[str] = None
    country_code:   Optional[str] = None
    series_id:      Optional[str] = None
    location:       Optional[str] = None
    course_url:     Optional[str] = None

    # event_history: List['Event'] = field(default_factory=list)

    scraper_success_element = "countries"

    # def scrape_course_event_history(self) -> List['Event']:

    #     if len(self.event_history) == 0:    
    #         if self.course_id and self.course_url and self.country_id:
    #             self.event_history = Event.scrape_raw_event_history(course_id=self.course_id, course_url=self.course_url, country_id=self.country_id)
    #         else:
    #             raise ValueError("Course ID, course URL, and country ID are required to scrape event history")

    #     return self.event_history
    

    @classmethod
    def create_course_from_raw_json(cls, course_json: dict, countries_json: List[dict]) -> 'Course':

        country_id =str(course_json["properties"]["countrycode"])
        eventname=course_json["properties"]["eventname"]

        if country_id in countries_json:
            course_url = f"{countries_json[country_id]}/{eventname}/"
        else:
            course_url = None


        return cls(           
            course_id=      str(course_json["id"]),
            country_id=     str(country_id),
            coordinates=    tuple(course_json["geometry"]["coordinates"]),
            eventname=      str(course_json["properties"]["eventname"]),
            long_name=      str(course_json["properties"]["EventLongName"]),
            short_name=     str(course_json["properties"]["EventShortName"]),
            local_long_name=str(course_json["properties"]["LocalisedEventLongName"]),
            country_code=   str(course_json["properties"]["countrycode"]),
            series_id=      str(course_json["properties"]["seriesid"]),
            location=       str(course_json["properties"]["EventLocation"]),
            course_url=     str(course_url)
        )





class CoursesHandler(BaseParquetHandler, BaseScraper):

    domain_folder: str = "courses"
    # file_name_template = "courses_{processing_date}.parquet"
    file_name_template: str = "courses.parquet"
    partition_keys: t.List[str] = []

    raw_courses: t.List[Course]  = None
    raw_courses_lookup:     t.Dict[str, Course]  = None

    country_course_ids:     Optional[t.Dict[str, List[str]]] = None
    country_num_courses:    Optional[t.Dict[str, int]] = None


    def __init__(self, config: ProcessingConfig, raw_countries: List[Country]):

        self.config = config

        self.base_path = config.base_path

        self.init_raw_courses(raw_countries=raw_countries)
        self.init_raw_courses_lookup()
        self.init_country_course_ids()
        self.init_country_num_courses()

    def init_raw_courses(self, raw_countries: List[Country]) -> None:

        if self.raw_courses is None:

            countries_json  = {country.country_id: country.country_url  for country in raw_countries}

            url = "https://images.parkrun.com/events.json"
            data = self._fetch_data(url)
            courses_json = self._parse_json(data)

            self.raw_courses = [Course.create_course_from_raw_json(course_json=course_json, countries_json=countries_json) for course_json in courses_json["events"]["features"]]

    def init_raw_courses_lookup(self) -> None:
        # Implementation for extracting courses

        if self.raw_courses is None:
            raise ValueError("Raw courses are not initialized")

        if not self.raw_courses_lookup:
            self.raw_courses_lookup = {course.course_id: course for course in self.raw_courses if course.course_id is not None}


    def init_country_course_ids(self) -> None:

        if self.raw_courses is None:
            raise ValueError("Raw courses are not initialized")

        if self.country_course_ids is None:

            #initialize country_course_id dictionary
            self.country_course_ids = {course.country_id: [] for course in self.raw_courses if course.country_id is not None}

            #populate country_course_id dictionary
            [self.country_course_ids[course.country_id].append(course.course_id) for course in self.raw_courses if course.country_id is not None and course.course_id is not None]


    def init_country_num_courses(self) -> None:

        if self.country_course_ids is None:
            raise ValueError("Country course ids are not initialized")

        if self.country_num_courses is None:
            self.country_num_courses = {country_id: len(self.country_course_ids[country_id]) for country_id in self.country_course_ids}


    # def init_country_course_ids(self) -> None:
    #     #course_ids by country

    #     if not self.raw_countries_lookup:
    #         self.init_raw_countries_lookup()

    #     if not self.raw_courses_lookup:
    #         self.init_raw_courses_lookup()

    #     countries = list(self.raw_countries_lookup.values())
    #     courses =   list(self.raw_courses_lookup.values())

    #     if self.country_course_ids is None:

    #         self.country_course_ids = {str(country.country_id): []  for country in countries}
    #         [self.country_course_ids[str(course.country_id)].append(str(course.course_id))  for course in courses]

    # def init_country_num_courses(self) -> None:
    #     #Number of courses by country

    #     if self.country_num_courses is None:
    #         if self.country_course_ids is None:
    #             self.init_country_course_ids()

    #         self.country_num_courses = {country_id: len(self.country_course_ids[country_id])  for country_id in self.country_course_ids}





    # Stored Courses
    def get_stored_course_ids(self) -> List[str]:
        return self.get_processed_ids('course_id')


    def get_stored_courses(self) -> List[Course]:

        df_courses: pl.LazyFrame|None = self.read_parquet()

        if df_courses is not None:
            return [Course(**row) for row in df_courses.collect().to_dicts()]
        else:
            return []


    # Raw Courses


    def get_raw_courses(self) -> List['Course']:
        return self.raw_courses

    def get_raw_courses_lookup(self) -> t.Dict[str, Course]:
        # Implementation for extracting courses

        if not self.raw_courses_lookup:
            self.init_raw_courses_lookup()

        return self.raw_courses_lookup

    def get_raw_course_ids(self) -> t.List[str]:
        # Implementation for extracting countries
        raw_courses_lookup = self.get_raw_courses_lookup()
        return list(raw_courses_lookup.keys())


    def get_raw_course_by_id(self, course_id: str) -> Course:
        raw_courses_lookup = self.get_raw_courses_lookup()
        return raw_courses_lookup[course_id]

    def get_raw_courses_by_country_id(self, country_id: str) -> List[Course]:

        if self.country_course_ids is None:
            raise ValueError("Country course ids are not initialized")

        country_course_ids = self.country_course_ids[country_id]
        return [self.get_raw_course_by_id(course_id=course_id) for course_id in country_course_ids]





    #Update Courses

    def update_courses(self) -> None:
        
        """Process countries and return list of country IDs to process."""
        
        # config_countries = config.country_ids
        # config_courses = config.course_ids

        # raw_course_ids = list(orchestrator.raw_courses_lookup.keys())
        raw_course_ids = self.get_raw_course_ids()
        stored_course_ids = self.get_stored_course_ids()

        new_ids = [id_ for id_ in raw_course_ids if id_ not in stored_course_ids]

        if len(new_ids) > 0:
            print(f"Storing new courses: {new_ids}")
            raw_courses = self.get_raw_courses()
            self.write_parquet(raw_courses)



