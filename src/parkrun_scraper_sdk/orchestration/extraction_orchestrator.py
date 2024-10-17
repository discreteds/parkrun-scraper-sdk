from json import load
from typing import Optional, Dict, Any, List
from unittest import result
from datetime import datetime


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
            self.live_countries_lookup = {country.id: country for country in Country.get_all_countries()}
        
    def load_live_courses_lookup(self) -> List[Course]:
        # Implementation for extracting courses
        if self.live_courses_lookup is None:
            self.live_courses_lookup = {course.id: course for course in Course.get_all_courses()}


    def load_country_course_ids(self) -> None:
        #course_ids by country

        countries = list(self.live_countries_lookup.values())
        courses =   list(self.live_courses_lookup.values())

        if self.country_course_ids is None:

            self.country_course_ids = {str(country.id): []  for country in countries}
            [self.country_course_ids[str(course.country_code)].append(course.id)  for course in courses]


    def load_country_num_courses(self) -> None:
        #Number of courses by country

        if self.country_num_courses is None:

            if self.country_course_ids is None:
                self.load_country_course_ids()

            self.country_num_courses = {country_id: len(self.country_course_ids[country_id])  for country_id in self.country_course_ids}



    #Events
    def extract_raw_course_events(self, course_id: str) -> List[Event]:
        # Implementation for extracting events for a specific course
        course = self.live_courses_lookup[course_id]
        return Event.get_event_history(course)


    def get_course_event_date_lookup(self, events: Dict[str, Event]) -> Dict[str, Event]:
        return {event.date: event for event in events}


    def get_course_event_id_lookup(self, events: Dict[str, Event]) -> Dict[str, Event]:
        return {event.event_number: event for event in events}



    def get_course_first_event_date(self, course_id) -> Event:
        events = self.extract_raw_course_events(course_id)
        event_dates = self.get_course_event_date_lookup(events)
        return min(event_dates.keys())



    #Results
    def extract_raw_event_results(self, course_id: str, event_id: str) -> Dict[str, Result]:
        # Implementation for extracting results for a specific event

        course = self.live_courses_lookup[course_id]
        results = Result.get_results(course, event_id)
        return results


    # Incremental extraction
    def extract_course_new_event_history(self, course_id, processed_event_numbers: List[str] = None) -> List[Dict[str, Event]]:

        if processed_event_numbers is None:
            processed_event_numbers = []

        events = self.extract_raw_course_events(course_id)
        event_id_lookup = self.get_course_event_id_lookup(events)
        processing_date = datetime.strptime(self.processing_date, "%Y-%m-%d")

        unprocessed_events = {}

        for event_id in event_id_lookup:
            event = event_id_lookup[event_id]
            if event_id in processed_event_numbers:
                continue
            if event.date > processing_date:
                continue

            unprocessed_events[event_id] = event_id_lookup[event_id]

        return unprocessed_events

    def extract_course_new_result_history(self, course_id, processed_event_numbers: List[str] = None) -> List[Dict[str, Result]]:

        if processed_event_numbers is None:
            processed_event_numbers = []

        events = self.extract_raw_course_events(course_id)
        event_id_lookup = self.get_course_event_id_lookup(events)

        processing_date = datetime.strptime(self.processing_date, "%Y-%m-%d")

        unprocessed_results = {}

        for event_id in event_id_lookup:
            event = event_id_lookup[event_id]

            if event_id in processed_event_numbers:
                continue

            if event.date > processing_date:
                continue

            unprocessed_results[event_id] = self.extract_raw_event_results(course_id, event_id)

        return unprocessed_results



    # # Method to run the entire extraction process
    # def run_extraction(self):
    #     hamilton_nodes = ["extract_countries", "extract_courses", "extract_events", "extract_results"]
    #     return self.run_hamilton_pipeline(output_nodes=hamilton_nodes)