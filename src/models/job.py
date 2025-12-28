from dataclasses import dataclass
import hashlib


@dataclass
class Job:
    title: str
    location: list[str]
    department: str
    work_arrangement: str
    href: str
    id: str = ""

    def __str__(self) -> str:
        locations_str = ", ".join(self.location)
        return f"{self.title} ({self.department}) - {locations_str} - {self.work_arrangement}"

    def hash(self) -> str:
        title_part = self.title.lower().replace(" ", "")
        location_part = ",".join(sorted([loc.lower().replace(" ", "") for loc in self.location]))
        hash_input = title_part + location_part
        return hashlib.sha256(hash_input.encode()).hexdigest()
