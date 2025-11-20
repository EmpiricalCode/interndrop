from dataclasses import dataclass


@dataclass
class Job:
    title: str
    location: list[str]
    department: str
    work_arrangement: str
    id: str = ""

    def __str__(self) -> str:
        locations_str = ", ".join(self.location)
        return f"{self.title} ({self.department}) - {locations_str} - {self.work_arrangement}"
