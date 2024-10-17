# file: src/parkrun_scraper_sdk/course.py

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from .country import Country



@dataclass
class Course(BaseDataclass, BaseScraper):

    id: Optional[str] = None
    coordinates:  Optional[Tuple[float, float]] = None    
    name: Optional[str] = None    
    long_name: Optional[str] = None
    short_name: Optional[str] = None
    local_long_name: Optional[str] = None
    country_code: Optional[str] = None
    series_id: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def get_all_courses(cls, countries: Optional[List[Country]] = None) -> List['Course']:

        if countries is None:
            countries = Country.get_all_countries()
        countries_json  = {country.id: country.url  for country in countries}

        url = "https://images.parkrun.com/events.json"
        data = cls._fetch_data(url)
        courses_json = cls._parse_json(data)

        return [cls._create_course_from_json(course_json, countries_json) for course_json in courses_json["events"]["features"]]

    @classmethod
    def _create_course_from_json(cls, course_json: dict, countries_json: List[dict]) -> 'Course':

        country_code=str(course_json["properties"]["countrycode"])
        name=course_json["properties"]["eventname"]

        if country_code in countries_json:
            course_url = f"{countries_json[country_code]}/{name}/"
        else:
            course_url = None


        return cls(
            id=course_json["id"],
            coordinates=tuple(course_json["geometry"]["coordinates"]),
            name=course_json["properties"]["eventname"],
            long_name=course_json["properties"]["EventLongName"],
            short_name=course_json["properties"]["EventShortName"],
            local_long_name=course_json["properties"]["LocalisedEventLongName"],
            country_code=course_json["properties"]["countrycode"],
            series_id=course_json["properties"]["seriesid"],
            location=course_json["properties"]["EventLocation"],
            url=course_url
        )
