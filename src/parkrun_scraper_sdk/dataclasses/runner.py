import typing as t
from .base_parquet import BaseParquetHandler


class RunnersHandler(BaseParquetHandler):
    domain_folder: str = "runners"
    file_name_template: str = "{athlete_id}.parquet"
    partition_keys: t.List[str] = ['athlete_id']

    def get_processed_runner(self, athlete_id: str) -> bool:
        return self.file_exists(athlete_id=athlete_id)