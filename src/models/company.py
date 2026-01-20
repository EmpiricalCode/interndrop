from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    name: str
    url: str
    paged: bool
    page_query_param: Optional[str]
    id: Optional[str] = None

    def __str__(self) -> str:
        return self.name
