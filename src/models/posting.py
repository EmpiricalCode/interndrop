from dataclasses import dataclass


@dataclass
class Posting:
    title: str
    location: str
    work_arrangement: str
    salary: int
    salary_type: str
    url: str
    term: str
    categories: list[str]
    company: str
    id: str = ""

    def __str__(self) -> str:
        categories_str = ", ".join(self.categories) if self.categories else "None"
        salary_str = f"${self.salary} ({self.salary_type})" if self.salary > 0 else f"Not specified ({self.salary_type})"
        return (
            f"Posting(\n"
            f"  id: {self.id}\n"
            f"  title: {self.title}\n"
            f"  company: {self.company}\n"
            f"  location: {self.location}\n"
            f"  work_arrangement: {self.work_arrangement}\n"
            f"  salary: {salary_str}\n"
            f"  term: {self.term}\n"
            f"  categories: [{categories_str}]\n"
            f"  url: {self.url}\n"
            f")"
        )
