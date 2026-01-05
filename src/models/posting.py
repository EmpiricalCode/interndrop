from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class Posting:
    title: str
    location: list[str]
    work_arrangement: str
    salary: int
    salary_type: str
    url: str
    term: list[str]
    categories: list[str]
    company: str
    id: str = ""
    date: int = 0

    def __str__(self) -> str:
        categories_str = ", ".join(self.categories) if self.categories else "None"
        location_str = ", ".join(self.location) if self.location else "None"
        term_str = ", ".join(self.term) if self.term else "None"
        salary_str = f"${self.salary} ({self.salary_type})" if self.salary > 0 else f"Not specified ({self.salary_type})"

        # Convert timestamp to EST date
        est_tz = ZoneInfo("America/New_York")
        date_str = datetime.fromtimestamp(self.date, tz=est_tz).strftime("%Y-%m-%d") if self.date > 0 else "Not set"

        return (
            f"Posting(\n"
            f"  id: {self.id}\n"
            f"  title: {self.title}\n"
            f"  company: {self.company}\n"
            f"  location: [{location_str}]\n"
            f"  work_arrangement: {self.work_arrangement}\n"
            f"  salary: {salary_str}\n"
            f"  term: {term_str}\n"
            f"  categories: [{categories_str}]\n"
            f"  url: {self.url}\n"
            f"  date: {date_str}\n"
            f")"
        )
