# file: src/parkrun_scraper_sdk/base_dataclass.py

from dataclasses import dataclass, asdict
from typing import Any, Dict

@dataclass
class BaseDataclass:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)