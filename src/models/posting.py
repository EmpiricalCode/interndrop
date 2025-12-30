from dataclasses import dataclass


@dataclass
class Posting:
    title: str
    location: str
    work_arrangement: str
    salary: int
    url: str
    term: str
    categories: list[str]
    company: str

    def __str__(self) -> str:
        categories_str = ", ".join(self.categories) if self.categories else "None"
        return (
            f"Posting(\n"
            f"  title: {self.title}\n"
            f"  company: {self.company}\n"
            f"  location: {self.location}\n"
            f"  work_arrangement: {self.work_arrangement}\n"
            f"  salary: {self.salary}\n"
            f"  term: {self.term}\n"
            f"  categories: [{categories_str}]\n"
            f"  url: {self.url}\n"
            f")"
        )
