# file: src/parkrun_scraper_sdk/country.py

from dataclasses import dataclass
from typing import List, Optional
import typing as t
from datetime import datetime
import polars as pl
from .base_dataclass import BaseDataclass
from .base_scraper import BaseScraper
from upath import UPath

from .base_parquet import BaseParquetHandler
from .config import ProcessingConfig


@dataclass
class Country(BaseDataclass):
    country_id:     Optional[str] = None
    country_url:    Optional[str] = None

    record_updated_date: Optional[str] = None

    scraper_success_element = "countries"


    @classmethod
    def create_country_from_json(cls, country_id: str, country_data: dict) -> 'Country':

        record_updated_date = datetime.now().strftime("%Y-%m-%d")

        return cls(
            country_id=         str(country_id),
            country_url=        f"https://{country_data['url']}",
            record_updated_date=record_updated_date
        )

    def __post_init__(self):
        if self.country_url and not self.country_url.startswith('http'):
            self.country_url = f"https://{self.country_url}"



class CountriesHandler(BaseParquetHandler, BaseScraper):

    domain_folder: str = "countries"
    # file_name_template = "countries_{processing_date}.parquet"
    file_name_template: str = "countries.parquet"
    partition_keys: List[str] = []

    # Raw Countries
    raw_countries: t.List[Country] = None
    raw_countries_lookup: t.Dict[str, Country] = None

    def __init__(self, config: ProcessingConfig):
        self.config = config

        self.base_path = config.base_path

        self.init_raw_countries()
        self.init_raw_countries_lookup()


    #initialise Raw Data
    def init_raw_countries(self) -> None:

        if self.raw_countries is None:

            url = "https://images.parkrun.com/events.json"
            data = self._fetch_data(url)
            countries_json = self._parse_json(json_string=data)

            self.raw_countries = [Country.create_country_from_json(country_id=country_id, country_data=country_data) 
                for country_id, country_data 
                in countries_json["countries"].items()]
            

    def init_raw_countries_lookup(self) -> None:
        # Implementation for extracting countries

        if not self.raw_countries_lookup:
            self.raw_countries_lookup = {country.country_id: country for country in self.get_raw_countries() if country.country_id is not None}
        
        # return self.raw_countries_lookup


    # Stored Countries
    def get_stored_country_ids(self) -> List[str]:
        return self.get_processed_ids(id_column='country_id')

    def get_stored_record_updated_date(self) -> List[str]:
        return self.get_processed_ids(id_column='record_updated_date')



    def get_stored_countries(self) -> List[Country]:

        df_countries: pl.LazyFrame|None = self.read_parquet()

        if df_countries is not None:
            return [Country(**row) for row in df_countries.collect().to_dicts()]
        else:
            return []

    # Raw Countries

    def get_raw_countries_ids(self) -> t.List[str]:
        # Implementation for extracting countries

        raw_countries_lookup = self.get_raw_countries_lookup()        
        return list(raw_countries_lookup.keys())


    def get_raw_countries_lookup(self) -> t.Dict[str, Country]:
        # Implementation for extracting countries

        if not self.raw_countries_lookup:
            self.init_raw_countries_lookup()
        
        return self.raw_countries_lookup


    def get_raw_countries(self) -> List[Country]:

        if self.raw_countries is None:
            self.init_raw_countries()

        return self.raw_countries

    #Update Countries

    def update_countries(self) -> None:
        """Process countries and return list of country IDs to process."""
        
        raw_country_ids = self.get_raw_countries_ids()
        stored_country_ids = self.get_stored_country_ids()

        new_ids = [id_ for id_ in raw_country_ids if id_ not in stored_country_ids]

        if len(new_ids) > 0:
            print(f"Storing new countries: {new_ids}")
            raw_countries = self.get_raw_countries()
            self.write_parquet(raw_countries)

    
