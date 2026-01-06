from dataclasses import dataclass
import hashlib


@dataclass
class Listing:
    title: str
    location: list[str]
    term: list[str]
    department: str
    work_arrangement: str
    href: str
    href_is_url: bool
    company: str

    def __str__(self) -> str:
        locations_str = ", ".join(self.location)
        term_str = ", ".join(self.term)
        return f"{self.company} - {self.title} ({self.department}) - {locations_str} - {term_str} - {self.work_arrangement}"

    def hash(self) -> str:
        title_part = self.title.lower().replace(" ", "")
        location_part = ",".join(sorted([loc.lower().replace(" ", "") for loc in self.location]))
        term_part = ",".join(sorted([term.lower().replace(" ", "") for term in self.term]))
        company_part = self.company.lower().replace(" ", "")
        hash_input = company_part + title_part + location_part + term_part
        return hashlib.sha256(hash_input.encode()).hexdigest()
