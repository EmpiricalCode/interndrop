from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    name: str
    url: str
    paged: bool
    page_query_param: Optional[str]

    def __str__(self) -> str:
        return self.name
