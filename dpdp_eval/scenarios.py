"""Business scenarios and the prompts that ask a model to write their privacy notice."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Two ways a founder might ask. "plain" never mentions the law: does the model know an Indian
# business needs a DPDP notice? "dpdp" names the Act and Rules: does it know what they require?
CONDITIONS = ("plain", "dpdp")


@dataclass(frozen=True)
class Scenario:
    id: str
    name: str
    sector: str
    city: str
    description: str
    website: str
    data: tuple[str, ...]
    purposes: tuple[str, ...]
    children: bool
    contact_title: str
    contact_name: str
    contact_email: str
    grievance_days: int

    @classmethod
    def from_dict(cls, d: dict) -> Scenario:
        c = d["contact"]
        return cls(
            id=d["id"],
            name=d["name"],
            sector=d["sector"],
            city=d["city"],
            description=d["description"],
            website=d["website"],
            data=tuple(d["data"]),
            purposes=tuple(d["purposes"]),
            children=bool(d["children"]),
            contact_title=c["title"],
            contact_name=c["name"],
            contact_email=c["email"],
            grievance_days=int(d["grievance_days"]),
        )

    def facts(self) -> str:
        """The business facts, as given to both the writer model and the judge."""
        lines = [
            f"Business: {self.name}, {self.city}, India. {self.description}",
            f"Website: {self.website}",
            "Personal data collected:",
            *[f"  - {x}" for x in self.data],
            "Purposes:",
            *[f"  - to {x}" for x in self.purposes],
            f"Users under 18: {'yes' if self.children else 'no'}",
            f"Privacy contact: {self.contact_name}, {self.contact_title}, {self.contact_email}",
            f"We reply to complaints within {self.grievance_days} days.",
            "Users can manage settings in the app/website under Settings, and get help under Help.",
        ]
        return "\n".join(lines)


def load_scenarios(path: Path | None = None) -> list[Scenario]:
    path = path or DATA_DIR / "scenarios.jsonl"
    with open(path, encoding="utf-8") as f:
        return [Scenario.from_dict(json.loads(line)) for line in f if line.strip()]


def writer_prompt(s: Scenario, condition: str) -> str:
    """What we ask each model under test. Same facts in both conditions; only the last line differs."""
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}")
    ask = (
        "We are launching soon. Write the privacy notice we will show users when they sign up and give consent. "
        "Use only the facts below; don't invent other data or purposes. Write only the notice, in English, ready to publish."
    )
    if condition == "dpdp":
        ask += (
            " It must comply with India's Digital Personal Data Protection Act, 2023 and the "
            "Digital Personal Data Protection Rules, 2025."
        )
    return f"{ask}\n\n{s.facts()}"
