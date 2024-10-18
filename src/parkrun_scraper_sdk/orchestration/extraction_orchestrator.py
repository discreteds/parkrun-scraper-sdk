# file: src/parkrun_scraper_sdk/orchestration/extraction_orchestrator.py


from json import load
from typing import Optional, Dict, Any, List
from unittest import result
from datetime import datetime
from parkrun_scraper_sdk import Country, Course, Result, Event
from dateutil import parser


from parkrun_scraper_sdk import event
# from mountainash_utils_hamilton import BaseHamiltonOrchestratorMixin

class ParkrunDataExtractionOrchestrator: #(BaseHamiltonOrchestratorMixin):



    def __init__(self, processing_date: str): #, settings_parameters: SettingsParameters):
        # self.settings_parameters = settings_parameters
        # Initialize other necessary components (API client, data storage, etc.)

        self.processing_date = processing_date

        self.live_courses_lookup: Dict[str, Course] = None
        self.live_countries_lookup: Dict[str, Country] = None
        self.country_course_ids: Dict[str, List[str]] = None
        self.country_num_courses: Dict[str, int] = None



        self.load_live_countries_lookup()
        self.load_live_courses_lookup()
        self.load_country_course_ids()
        self.load_country_num_courses()


    # def init_base_hamilton_inputs(self) -> Dict[str, Any]:
    #     return dict(obj_orchestrator=self)

    # def init_base_hamilton_module_names(self) -> str|List[str]:
    #     return 'parkrun_data_extraction.pipeline_parkrun_extraction'

    def extract_raw_countries(self) -> List[Country]:
        # Implementation for extracting countries
        return Country.get_all_countries()
    
    def extract_raw_courses(self) -> List[Course]:
        # Implementation for extracting courses
        return Course.get_all_courses()

    # Methods for each extraction step
    def load_live_countries_lookup(self) -> List[Country]:
        # Implementation for extracting countries
        if self.live_countries_lookup is None:
            self.live_countries_lookup = {country.country_id: country for country in Country.get_all_countries()}
        
    def load_live_courses_lookup(self) -> List[Course]:
        # Implementation for extracting courses
        if self.live_courses_lookup is None:
            self.live_courses_lookup = {course.course_id: course for course in Course.get_all_courses()}


    def load_country_course_ids(self) -> None:
        #course_ids by country

        countries = list(self.live_countries_lookup.values())
        courses =   list(self.live_courses_lookup.values())

        if self.country_course_ids is None:

            self.country_course_ids = {str(country.country_id): []  for country in countries}
            [self.country_course_ids[str(course.country_id)].append(str(course.course_id))  for course in courses]


    def load_country_num_courses(self) -> None:
        #Number of courses by country

        if self.country_num_courses is None:

            if self.country_course_ids is None:
                self.load_country_course_ids()

            self.country_num_courses = {country_id: len(self.country_course_ids[country_id])  for country_id in self.country_course_ids}



    #Events
    def extract_raw_course_event_history(self, course: Course) -> List[Event]:
        # Implementation for extracting events for a specific course
        # course = self.live_courses_lookup[course_id]
        return course.get_event_history()


    def get_course_event_date_lookup(self, events: Dict[str, Event]) -> Dict[str, Event]:
        return {event.event_date: event for event in events}


    def get_course_event_id_lookup(self, events: Dict[str, Event]) -> Dict[str, Event]:
        return {str(event.event_id): event for event in events}



    def get_course_first_event_date(self, course: Course) -> Event:

        events = self.extract_raw_course_event_history(course)
        event_dates = self.get_course_event_date_lookup(events)
        return min(event_dates.keys())



    #Results
    def extract_raw_event_results(self, course: Course, event: Event) -> Dict[str, Result]:
        # Implementation for extracting results for a specific event

        # course = self.live_courses_lookup[course_id]
        # event = self.get_course_event_id_lookup(self.extract_raw_course_events(course_id))[event_id]

        results = Result.get_results(course, event)
        return results


    # Incremental extraction
    def extract_course_new_event_history(self, course: Course, processed_event_ids: List[str] = None) -> List[Dict[str, Event]]:

        if processed_event_ids is None:
            processed_event_ids = []

        #This will get the current events for the course from the website
        events = self.extract_raw_course_event_history(course)

        event_id_lookup = self.get_course_event_id_lookup(events)
        processing_date = parser.parse(self.processing_date).date()

        unprocessed_events = {}

        for event_id in event_id_lookup:

            event = event_id_lookup[event_id]
            event_date =  parser.parse(event.event_date).date()

            if event_id in processed_event_ids:
                continue
            if event_date > processing_date:
                print(f"Course {course.course_id} has an event registered for {event_date}. However, event processing is only being performed up to the processing date: {processing_date}")
                continue

            #We have already scraped the event from the web. Just return it if it meets the criteria!
            #This could just be a boolean flag to indicate if there are new events or not.
            unprocessed_events[event_id] = event_id_lookup[event_id]

        return unprocessed_events

    def extract_course_unprocessed_result_events(self, course: Course, processed_event_ids: List[str] = None) -> List[Event]:

        if processed_event_ids is None:
            processed_event_ids = []

        #This will get the current events for the course from the website, if not cached
        events = self.extract_raw_course_event_history(course)
        event_id_lookup = self.get_course_event_id_lookup(events)

        processing_date = parser.parse(self.processing_date).date()

        unprocessed_event_results = []

        for event_id in event_id_lookup:
            event = event_id_lookup[event_id]
            event_date =  parser.parse(event.event_date).date()

            if event_id in processed_event_ids:
                continue
            if event_date > processing_date:
                print(f"Course {course.course_id} has an event registered for {event_date}. However, result processing is only being performed up to the processing date: {processing_date}")
                continue

            #This will get the cuurent events for the course from the website. If there are a lot, this could take a while. Parallelize?
            unprocessed_event_results.append(event)

            # unprocessed_results[event_id] = self.extract_raw_event_results(course, event)

        return unprocessed_event_results



    # # Method to run the entire extraction process
    # def run_extraction(self):
    #     hamilton_nodes = ["extract_countries", "extract_courses", "extract_events", "extract_results"]
    #     return self.run_hamilton_pipeline(output_nodes=hamilton_nodes)