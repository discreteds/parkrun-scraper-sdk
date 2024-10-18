# file: src/parkrun_scraper_sdk/course.py

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .country import Country
from .event import Event



@dataclass
class Course(BaseDataclass, BaseScraper):

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

    event_history: List['Event'] = field(default_factory=list)


    def get_event_history(self) -> List['Event']:

        if len(self.event_history) == 0:            
            self.event_history = Event.get_event_history(self.course_id, self.course_url, self.country_id)
        return self.event_history
    

    @classmethod
    def get_all_courses(cls, countries: Optional[List[Country]] = None) -> List['Course']:

        if countries is None:
            countries = Country.get_all_countries()

        countries_json  = {country.country_id: country.country_url  for country in countries}

        url = "https://images.parkrun.com/events.json"
        data = cls._fetch_data(url)
        courses_json = cls._parse_json(data)

        return [cls._create_course_from_json(course_json, countries_json) for course_json in courses_json["events"]["features"]]

    @classmethod
    def _create_course_from_json(cls, course_json: dict, countries_json: List[dict]) -> 'Course':

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
