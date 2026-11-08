"""A keyword baseline: the cheapest possible judge.

It exists to answer "do we even need an LLM judge?". If plain keyword rules matched the
hand labels as well as the LLM, the LLM would be wasted money. See the judge validation results.
"""

from __future__ import annotations

import re

from .rubric import applicable
from .scenarios import Scenario

_STOP = {"and", "the", "for", "of", "or", "a", "an", "to", "in", "by", "at", "on", "with", "from", "user", "users"}


def _words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 2 and w not in _STOP}


def _has(t: str, *pats: str) -> bool:
    return any(re.search(p, t, re.I) for p in pats)


_FOREIGN = [
    r"legitimate interests?\b",
    r"data portability",
    r"right to object",
    r"restrict(ion of)? (the )?processing",
    r"supervisory authority",
    r"data protection authority",
    r"do not sell",
    r"sale of (your )?(personal )?(data|information)",
]

_CATCHALL = [
    r"any other (lawful |legitimate )?purpose",
    r"other business purposes",
    r"as we (may )?deem (fit|appropriate|necessary)",
    r"purposes? that we consider",
]


def baseline_verdicts(s: Scenario, notice: str) -> dict[str, str]:
    t = notice
    low = t.lower()
    v: dict[str, bool] = {}

    # Every data item from the facts should be recognisable: at least half its content words appear.
    notice_words = _words(t)

    def covered(item: str) -> bool:
        w = _words(item)
        return not w or len(w & notice_words) / len(w) >= 0.5

    v["data_itemised"] = all(covered(x) for x in s.data) and not _has(
        t, r"such as .{0,80}(and|or) other", r"and other (details|information)"
    )
    v["purpose_specific"] = not _has(t, *_CATCHALL) and sum(covered(p) for p in s.purposes) >= len(s.purposes) / 2
    v["withdraw_consent"] = _has(t, r"withdraw") and not _has(
        t, r"registered post", r"by post", r"notari[sz]ed", r"signed (written )?request"
    )
    v["rights"] = _has(t, r"summary|access") and _has(t, r"correct|rectif|updat") and _has(t, r"eras|delet")
    v["nomination"] = _has(t, r"nominat")
    days = [int(d) for d in re.findall(r"(\d+)\s*(?:working |business |calendar )?days", low)]
    v["grievance"] = _has(t, r"grievance|complain") and bool(days) and max(days) <= 90
    v["board_complaint"] = _has(t, r"data protection board")
    v["contact"] = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t)) or _has(t, r"\+?91[\s-]?\d{5}")
    v["language"] = _has(
        t, r"eighth schedule", r"hindi", r"indian languages?", r"regional languages?", r"22 languages"
    ) and not _has(t, r"english only")
    v["no_foreign_law"] = not _has(t, *_FOREIGN)
    v["children"] = (
        _has(t, r"\b18\b|eighteen")
        and _has(t, r"parent|guardian")
        and not _has(t, r"under (the age of )?1[36]\b")
        and not _has(t, r"personali[sz]ed ads?.{0,60}(includ|child|minor|student)")
    )
    return {c.id: ("pass" if v[c.id] else "fail") for c in applicable(s.children)}
