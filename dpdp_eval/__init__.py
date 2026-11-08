"""Open eval: can AI models write privacy notices that follow India's DPDP Act?"""

from .rubric import CHECKS, applicable
from .scenarios import Scenario, load_scenarios

__all__ = ["CHECKS", "Scenario", "applicable", "load_scenarios"]
