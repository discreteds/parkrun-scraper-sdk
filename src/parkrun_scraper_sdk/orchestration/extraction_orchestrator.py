# file: src/parkrun_scraper_sdk/orchestration/extraction_orchestrator.py


from json import load
from typing import Optional, Dict, Any, List
from unittest import result
from datetime import datetime
from upath import UPath
from ..dataclasses.country import Country, CountriesHandler
from ..dataclasses.course import Course, CoursesHandler
from ..dataclasses.config import ProcessingConfig
from ..dataclasses.result import Result, ResultsHandler
from ..dataclasses.event import Event, EventsHandler
from dateutil import parser

# from parkrun_scraper_sdk import event
# from mountainash_utils_hamilton import BaseHamiltonOrchestratorMixin

class ParkrunDataExtractionOrchestrator: #(BaseHamiltonOrchestratorMixin):


    # base_path = UPath|str# ("/home/nathanielramm/parkrun_data")
    countries_handler: CountriesHandler
    courses_handler: CoursesHandler
    events_handler: EventsHandler
    results_handler: ResultsHandler

    # raw_countries_lookup:   Optional[Dict[str, Country]]
    # raw_courses_lookup:     Optional[Dict[str, Course]]
    # country_course_ids:     Optional[Dict[str, List[str]]]
    # country_num_courses:    Optional[Dict[str, int]]


    def __init__(self, config: ProcessingConfig): #, settings_parameters: SettingsParameters):
        # self.settings_parameters = settings_parameters
        # Initialize other necessary components (API client, data storage, etc.)

        self.config = config

        # self.processing_date = config.processing_date
        self.countries_handler: CountriesHandler = CountriesHandler(config=config)
        self.courses_handler: CoursesHandler = CoursesHandler(config=config, raw_countries=self.countries_handler.get_raw_countries())

        self.events_handler: EventsHandler = EventsHandler(config=config)
        self.results_handler: ResultsHandler = ResultsHandler(config=config)

        # self.raw_countries_lookup = None
        # self.raw_courses_lookup = None
        # self.country_course_ids = None
        # self.country_num_courses = None

    def update_countries(self) -> None:
        self.countries_handler.update_countries()

    def update_courses(self) -> None:
        self.courses_handler.update_courses()


    def get_courses_in_config_scope(self) -> List[Course]:

        country_course_ids_in_scope = []
        course_course_ids_in_scope = []
        courses_to_process = []

        #All courses in the country
        if self.config.country_ids and len(self.config.country_ids) > 0:
            for country_id in self.config.country_ids:
                temp_course_ids_in_scope = self.courses_handler.get_raw_course_ids_by_country_id(country_id=country_id)
                country_course_ids_in_scope.extend(temp_course_ids_in_scope)

        if self.config.course_ids and len(self.config.course_ids) > 0:
            course_course_ids_in_scope = self.config.course_ids


        # find the ids that are in both lists, but only if both lists are not empty
        if len(country_course_ids_in_scope) > 0 and len(course_course_ids_in_scope) > 0:  

            intersection = set(country_course_ids_in_scope).intersection(set(course_course_ids_in_scope))
            union = set(country_course_ids_in_scope).union(set(course_course_ids_in_scope))

            #Use the intersection of the two lists
            course_ids_to_process = intersection

            if intersection != union:
                print(f"Warning: Whilst Some course ids are in both lists: {intersection}")
                print(f"Warning: Some course ids are NOT in both lists: {set(intersection).symmetric_difference(union)}")
                print(f"Warning: Incorrect course_ids_to_process: {set(intersection).symmetric_difference(course_course_ids_in_scope)}")
                print(f"Warning: Excluded Country course_ids: {set(intersection).symmetric_difference(country_course_ids_in_scope)}")


        elif len(country_course_ids_in_scope) > 0:
            course_ids_to_process = country_course_ids_in_scope
        elif len(course_course_ids_in_scope) > 0:
            course_ids_to_process = course_course_ids_in_scope
        else:
            raise ValueError("No course ids to process")

        courses_to_process = [self.courses_handler.get_raw_course_by_id(course_id=course_id) for course_id in course_ids_to_process]
        return courses_to_process



    # def init_orchestrator(self) -> None:

        # self.init_raw_countries_lookup()
        # self.init_raw_courses_lookup()
        # self.init_country_course_ids()
        # self.init_country_num_courses()


    # def init_base_hamilton_inputs(self) -> Dict[str, Any]:
    #     return dict(obj_orchestrator=self)

    # def init_base_hamilton_module_names(self) -> str|List[str]:
    #     return 'parkrun_data_extraction.pipeline_parkrun_extraction'

    # def extract_raw_countries(self) -> List[Country]:
    #     # Implementation for extracting countries
    #     return Country.scrape_raw_countries()
    
    # def extract_raw_courses(self) -> List[Course]:
    #     # Implementation for extracting courses
    #     return Course.get_all_courses()


    # # Methods for each extraction step
    # def init_raw_countries_lookup(self) -> None:

    #     # Implementation for extracting countries
    #     if not self.raw_countries_lookup:
    #         self.raw_countries_lookup = self.countries_handler.get_raw_countries_lookup()
        
    # def init_raw_courses_lookup(self) -> None:
    #     # Implementation for extracting courses

    #     raw_countries = self.countries_handler.get_raw_countries()
    #     if not self.raw_courses_lookup:
    #         self.raw_courses_lookup = self.courses_handler.get_raw_courses_lookup(raw_countries)

    
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



    # #Events
    # def extract_raw_course_event_history(self, course: Course) -> List[Event]:
    #     # Implementation for extracting events for a specific course
    #     # course = self.live_courses_lookup[course_id]
    #     return course.get_event_history()


    # def get_course_event_date_lookup(self, events: Dict[str, Event]) -> Dict[str, Event]:
    #     return {event.event_date: event for event in events}


    # def get_course_event_id_lookup(self, events: Dict[str, Event]) -> Dict[str, Event]:
    #     return {str(event.event_id): event for event in events}



    # def get_course_first_event_date(self, course: Course) -> Event:

    #     events = self.extract_raw_course_event_history(course)
    #     event_dates = self.get_course_event_date_lookup(events)
    #     return min(event_dates.keys())



    # #Results
    # def extract_raw_event_results(self, course: Course, event: Event) -> Dict[str, Result]:
    #     # Implementation for extracting results for a specific event

    #     # course = self.live_courses_lookup[course_id]
    #     # event = self.get_course_event_id_lookup(self.extract_raw_course_events(course_id))[event_id]

    #     results = Result.get_results(course, event)
    #     return results


    # # Incremental extraction
    # def extract_course_new_event_history(self, course: Course, processed_event_ids: List[str] = None) -> List[Dict[str, Event]]:

    #     if processed_event_ids is None:
    #         processed_event_ids = []

    #     #This will get the current events for the course from the website
    #     events = self.extract_raw_course_event_history(course)

    #     event_id_lookup = self.get_course_event_id_lookup(events)
    #     processing_date = parser.parse(self.processing_date).date()

    #     unprocessed_events = {}

    #     for event_id in event_id_lookup:

    #         event = event_id_lookup[event_id]
    #         event_date =  parser.parse(event.event_date).date()

    #         if event_id in processed_event_ids:
    #             continue
    #         if event_date > processing_date:
    #             print(f"Course {course.course_id} has an event registered for {event_date}. However, event processing is only being performed up to the processing date: {processing_date}")
    #             continue

    #         #We have already scraped the event from the web. Just return it if it meets the criteria!
    #         #This could just be a boolean flag to indicate if there are new events or not.
    #         unprocessed_events[event_id] = event_id_lookup[event_id]

    #     return unprocessed_events

    # def extract_course_unprocessed_result_events(self, course: Course, processed_event_ids: List[str] = None) -> List[Event]:

    #     if processed_event_ids is None:
    #         processed_event_ids = []

    #     #This will get the current events for the course from the website, if not cached
    #     events = self.extract_raw_course_event_history(course)
    #     event_id_lookup = self.get_course_event_id_lookup(events)

    #     processing_date = parser.parse(self.processing_date).date()

    #     unprocessed_event_results = []

    #     for event_id in event_id_lookup:
    #         event = event_id_lookup[event_id]
    #         event_date =  parser.parse(event.event_date).date()

    #         if event_id in processed_event_ids:
    #             continue
    #         if event_date > processing_date:
    #             print(f"Course {course.course_id} has an event registered for {event_date}. However, result processing is only being performed up to the processing date: {processing_date}")
    #             continue

    #         #This will get the cuurent events for the course from the website. If there are a lot, this could take a while. Parallelize?
    #         unprocessed_event_results.append(event)

    #         # unprocessed_results[event_id] = self.extract_raw_event_results(course, event)

    #     return unprocessed_event_results



    # # Method to run the entire extraction process
    # def run_extraction(self):
    #     hamilton_nodes = ["extract_countries", "extract_courses", "extract_events", "extract_results"]
    #     return self.run_hamilton_pipeline(output_nodes=hamilton_nodes)



# class ParkrunDataProcessor:
#     """Main class for processing parkrun data."""
    
#     def __init__(self, config: ProcessingConfig):
#         self.config = config
#         self.handlers = HandlerRegistry(config.base_path)
#         self.orchestrator = ParkrunDataExtractionOrchestrator(config.processing_date)

#     def process(self) -> None:
#         """Main processing method."""
#         # Validate and normalize configuration
#         self.config.validate()
#         self.config.normalize_ids()

#         # Process countries
#         country_ids = CountryProcessor.process(
#             self.config,
#             self.handlers,
#             self.orchestrator
#         )

#         # Process courses
#         course_ids = CourseProcessor.process(
#             self.config,
#             self.handlers,
#             self.orchestrator,
#             country_ids
#         )

#         # Process events and results
#         EventProcessor.process(
#             self.config,
#             self.handlers,
#             self.orchestrator,
#             course_ids
#         )


# def do_it(base_path: Path,
#           processing_date: str = "2014-01-01",
#           country_ids: Optional[List[str]] = None,
#           course_ids: Optional[List[str]] = None) -> None:
#     """Main entry point for parkrun data processing."""
    
#     config = ProcessingConfig(
#         base_path=base_path,
#         processing_date=processing_date,
#         country_ids=country_ids,
#         course_ids=course_ids
#     )
    
#     processor = ParkrunDataProcessor(config)
#     processor.process()    