"""Business scenarios and the prompts that ask a model to write their privacy notice."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

# Two ways a founder might ask. "plain" never mentions the law: does the model know an Indian
# business needs a DPDP notice? "dpdp" names the Act and Rules: does it know what they require?
CONDITIONS = ("plain", "dpdp")
# Ablation: the "dpdp" request without the line telling the model to stick to the facts, to check that
# this line isn't what stops models adding the legally required parts (Board, nomination, language...).
ABLATIONS = ("dpdp_open",)

# Every other scenario (12, five with children). Models with a tiny free quota (20 requests a day)
# are run on these only, and the headline leaderboard compares all models on this same set.
CORE_IDS = (
    "pathshala", "sehat", "khelo", "safar", "fitmitra", "bima",
    "coachify", "rasoi", "swasthya", "library", "gym", "scholar",
)  # fmt: skip


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
        """The business facts, as given to both the writer model and the judge.

        Facts left empty (in a notice someone pastes into the demo) are marked as not provided,
        so the judge checks the notice on its own terms instead of against made-up facts.
        """
        unknown = "  (not provided: judge only whether the notice itself is specific)"
        lines = [
            f"Business: {self.name}, {self.city}, India. {self.description}".replace(", , India", ", India"),
            f"Website: {self.website or '(not provided)'}",
            "Personal data collected:",
            *([f"  - {x}" for x in self.data] or [unknown]),
            "Purposes:",
            *([f"  - to {x}" for x in self.purposes] or [unknown]),
            f"Users under 18: {'yes' if self.children else 'no'}",
        ]
        if self.contact_email:
            lines.append(f"Privacy contact: {self.contact_name}, {self.contact_title}, {self.contact_email}")
        if self.grievance_days:
            lines.append(f"We reply to complaints within {self.grievance_days} days.")
        if self.id != "custom":
            lines.append("Users can manage settings in the app/website under Settings, and get help under Help.")
        return "\n".join(lines)


def custom_scenario(description: str = "", data: str = "", children: bool = False) -> Scenario:
    """A scenario for a notice pasted into the demo, where we only know what the user tells us."""
    items = tuple(x.strip(" -•*\t") for x in data.replace(",", "\n").splitlines() if x.strip(" -•*\t"))
    return Scenario(
        id="custom",
        name="The business",
        sector="",
        city="",
        description=description.strip() or "(description not provided)",
        website="",
        data=items,
        purposes=(),
        children=children,
        contact_title="",
        contact_name="",
        contact_email="",
        grievance_days=0,
    )


def load_scenarios(path: Path | None = None) -> list[Scenario]:
    path = path or DATA_DIR / "scenarios.jsonl"
    with open(path, encoding="utf-8") as f:
        return [Scenario.from_dict(json.loads(line)) for line in f if line.strip()]


def writer_prompt(s: Scenario, condition: str) -> str:
    """What we ask each model under test. Same facts in both conditions; only the last line differs."""
    if condition not in CONDITIONS + ABLATIONS:
        raise ValueError(f"unknown condition {condition!r}")
    stick = "" if condition == "dpdp_open" else "Use only the facts below; don't invent other data or purposes. "
    ask = (
        "We are launching soon. Write the privacy notice we will show users when they sign up and give consent. "
        f"{stick}Write only the notice, in English, ready to publish."
    )
    if condition in ("dpdp", "dpdp_open"):
        ask += (
            " It must comply with India's Digital Personal Data Protection Act, 2023 and the "
            "Digital Personal Data Protection Rules, 2025."
        )
    return f"{ask}\n\n{s.facts()}"
