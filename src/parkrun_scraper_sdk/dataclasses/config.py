import typing as t
from dataclasses import dataclass
from upath import UPath
from datetime import datetime


@dataclass
class ProcessingConfig:
    
    base_path: UPath
    processing_date: str = "2014-01-01"
    country_ids: t.Optional[t.List[str]] = None
    course_ids: t.Optional[t.List[str]] = None


    def normalize_ids(self) -> None:

        """Normalize country and course IDs to strings."""
        if self.country_ids is None:
            self.country_ids = []
        elif isinstance(self.country_ids, (str, int)):
            self.country_ids = [str(self.country_ids)]
        self.country_ids = [str(id_) for id_ in self.country_ids]

        if self.course_ids is None:
            self.course_ids = []
        elif isinstance(self.course_ids, (str, int)):
            self.course_ids = [str(self.course_ids)]
            
        self.course_ids = [str(id_) for id_ in self.course_ids]

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not isinstance(self.base_path, UPath):
            raise ValueError("base_path must be a Path object")
        
        try:
            datetime.strptime(self.processing_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("processing_date must be in YYYY-MM-DD format")


# class HandlerRegistry:
#     """Registry for all data handlers."""

#     def __init__(self, base_path: UPath):
#         self.countries_handler = CountriesHandler(base_path)
#         self.courses_handler = CoursesHandler(base_path)
#         self.events_handler = EventsHandler(base_path)
#         self.results_handler = ResultsHandler(base_path)
#         self.runners_handler = RunnersHandler(base_path)