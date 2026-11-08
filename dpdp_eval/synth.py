"""Build the judge-validation set: privacy notices whose correct verdicts are known by construction.

Each notice is assembled from sections. For every check we pick either a compliant section or one
of several realistic mistakes (a vague data list, a 120-day reply period, "supervisory authority",
withdrawal only by registered post, children defined as under 13, ...). The labels follow from the
choices, so we can measure how often a judge agrees with the truth.

This set is synthetic and templated, so it is easier than real model output. The README reports
it as such, next to a second check on real notices.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

from .rubric import applicable
from .scenarios import DATA_DIR, Scenario, load_scenarios

GOOD = "good"


def _bullets(rng: random.Random, items, prefix: str = "") -> str:
    style = rng.choice(["-", "*", "num"])
    out = []
    for i, x in enumerate(items, 1):
        mark = f"{i}." if style == "num" else style
        out.append(f"{mark} {prefix}{x[0].upper() + x[1:] if not prefix else x}")
    return "\n".join(out)


def _content_words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 4}


def _droppable(s: Scenario) -> list[str]:
    """Data items whose words don't appear in the purposes, so dropping them really leaves them unlisted."""
    purpose_words = _content_words(" ".join(s.purposes) + " " + s.description)
    return [x for x in s.data if not (_content_words(x) & purpose_words)]


VARIANTS: dict[str, list[str]] = {
    "data_itemised": [GOOD, "vague", "missing"],
    "purpose_specific": [GOOD, "catchall", "generic"],
    "withdraw_consent": [GOOD, "absent", "hard"],
    "rights": [GOOD, "access_only", "no_erasure"],
    "nomination": [GOOD, "absent"],
    "grievance": [GOOD, "too_long", "no_period", "absent"],
    "board_complaint": [GOOD, "absent", "wrong_body_dpa", "wrong_body_sa"],
    "contact": [GOOD, "vague", "absent"],
    "language": [GOOD, "absent", "english_only"],
    "no_foreign_law": [GOOD, "legit_interest", "portability", "object", "do_not_sell"],
    "children": [GOOD, "under13", "ads", "absent"],
}


def choose(rng: random.Random, s: Scenario, p_good: float = 0.5) -> dict[str, str]:
    picks = {}
    for c in applicable(s.children):
        opts = list(VARIANTS[c.id])
        if c.id == "data_itemised" and not _droppable(s):
            opts.remove("missing")
        p = 0.65 if c.id == "no_foreign_law" else p_good
        picks[c.id] = GOOD if rng.random() < p else rng.choice(opts[1:])
    # "Right to object" next to a missing withdrawal clause could be read as a withdrawal route.
    if picks.get("no_foreign_law") == "object" and picks["withdraw_consent"] != GOOD:
        picks["no_foreign_law"] = "portability"
    return picks


def labels_for(picks: dict[str, str]) -> dict[str, str]:
    lab = {k: ("pass" if v == GOOD else "fail") for k, v in picks.items()}
    # Naming a GDPR-style regulator is also an imported-law error.
    if picks.get("board_complaint") in ("wrong_body_dpa", "wrong_body_sa"):
        lab["no_foreign_law"] = "fail"
    return lab


def render(rng: random.Random, s: Scenario, picks: dict[str, str]) -> str:
    """Write the notice text for these picks."""
    h = rng.choice([lambda t: f"## {t}", lambda t: f"**{t}**", lambda t: t.upper()])
    sec: dict[str, str] = {}
    site = s.website.removeprefix("https://")

    # Data
    v = picks["data_itemised"]
    if v == GOOD:
        sec["data"] = h("What personal data we collect") + "\n" + _bullets(rng, s.data)
    elif v == "vague":
        sec["data"] = (
            h("What personal data we collect")
            + f"\nWe collect information such as your {s.data[0]}, {s.data[1]} and other details you provide while using our services."
        )
    else:
        drop = set(rng.sample(_droppable(s), k=min(2, len(_droppable(s)))))
        sec["data"] = h("What personal data we collect") + "\n" + _bullets(rng, [x for x in s.data if x not in drop])

    # Purposes (+ maybe a "legitimate interests" sentence)
    v = picks["purpose_specific"]
    if v == "generic":
        body = "We use your personal data to provide, maintain and improve our services."
    else:
        body = "We use this data only to:\n" + _bullets(rng, s.purposes)
        if v == "catchall":
            body += "\n" + rng.choice(
                [
                    "We may also use it for any other purpose that we consider necessary for our business.",
                    "We may also use your data for any other lawful purpose.",
                ]
            )
    if picks["no_foreign_law"] == "legit_interest":
        body += "\nWe process your personal data on the basis of our legitimate interests in running and improving our business."
    sec["purpose"] = h("Why we use it") + "\n" + body

    # Withdrawal
    v = picks["withdraw_consent"]
    if v == GOOD:
        sec["withdraw"] = (
            h("Withdrawing your consent")
            + "\n"
            + rng.choice(
                [
                    "You can withdraw your consent at any time under Settings > Privacy > Manage consent. It takes the same few taps as giving consent. Withdrawal does not affect processing done before it.",
                    f"To withdraw consent, use the 'Withdraw consent' button in your account settings or at {site}/privacy. It is as easy as giving consent was.",
                ]
            )
        )
    elif v == "hard":
        sec["withdraw"] = (
            h("Withdrawing your consent")
            + f"\nIf you wish to withdraw your consent, you must send a signed written request by registered post to our registered office in {s.city}. Requests are processed within 60 days."
        )

    # Rights (+ maybe portability / object)
    v = picks["rights"]
    rights = {
        GOOD: rng.choice(
            [
                "You can ask for a summary of the personal data we hold about you and how we process it. You can also ask us to correct, complete or update it, or to erase it when it is no longer needed.",
                "You have the right to access a summary of your personal data and our processing of it, and to have it corrected, completed, updated or erased.",
            ]
        ),
        "access_only": "You can ask us for a summary of the personal data we hold about you and how we process it.",
        "no_erasure": "You can ask for a summary of your personal data, and ask us to correct, complete or update it.",
    }[v]
    rights += " " + rng.choice(
        ["Make a request under Help > My data.", f"Send your request through {site}/privacy-requests."]
    )
    if picks["no_foreign_law"] == "portability":
        rights += " You also have the right to data portability, which lets you receive your data in a machine-readable format and move it to another service."
    if picks["no_foreign_law"] == "object":
        rights += " You also have the right to object to our processing of your personal data at any time."
    if picks["nomination"] == GOOD:
        rights += " " + rng.choice(
            [
                "You can also nominate another person to exercise these rights for you if you die or become unable to do so. Add a nominee under Settings > Nominee.",
                "You may nominate someone who can exercise your rights on your behalf in the event of your death or incapacity.",
            ]
        )
    sec["rights"] = h("Your rights") + "\n" + rights

    # Grievance + Board
    g = ""
    v = picks["grievance"]
    route = rng.choice(["raise it under Help > Raise a grievance", f"use the grievance form at {site}/grievance"])
    if v == GOOD:
        g = f"If you have a grievance about how we handle your data, {route}. We will respond within {s.grievance_days} days."
    elif v == "too_long":
        g = f"If you have a grievance about how we handle your data, {route}. We will respond within {rng.choice([120, 180])} days."
    elif v == "no_period":
        g = f"If you have a grievance about how we handle your data, {route}. We will look into it and get back to you."
    v = picks["board_complaint"]
    board = {
        GOOD: rng.choice(
            [
                "If you are not satisfied with our response, you can complain to the Data Protection Board of India through its online portal.",
                "You may also file a complaint with the Data Protection Board of India, using the digital office on its website.",
            ]
        ),
        "absent": "",
        "wrong_body_dpa": "If you are not satisfied with our response, you can complain to the Data Protection Authority of India.",
        "wrong_body_sa": "You also have the right to lodge a complaint with the relevant supervisory authority.",
    }[v]
    text = " ".join(x for x in (g, board) if x)
    if text:
        sec["grievance"] = h("Complaints") + "\n" + text

    # Contact
    v = picks["contact"]
    if v == GOOD:
        sec["contact"] = (
            h("Contact us")
            + "\n"
            + rng.choice(
                [
                    f"Questions about this notice or your data? Contact our {s.contact_title}, {s.contact_name}, at {s.contact_email}.",
                    f"{s.contact_title}: {s.contact_name} ({s.contact_email})",
                ]
            )
        )
    elif v == "vague":
        sec["contact"] = h("Contact us") + "\nFor any questions, please contact us through our website."

    # Language
    v = picks["language"]
    if v == GOOD:
        sec["language"] = rng.choice(
            [
                "This notice is available in English and in Hindi and the other languages listed in the Eighth Schedule to the Constitution. Choose your language at the top of this page.",
                "You can read this notice in English or in any of the 22 languages of the Eighth Schedule of the Constitution of India. Tap 'Change language'.",
            ]
        )
    elif v == "english_only":
        sec["language"] = "This notice is available in English only."

    # Children
    if "children" in picks:
        v = picks["children"]
        good_consent = "If you are under 18, we will process your personal data only after we get verifiable consent from your parent or lawful guardian."
        no_track = "We do not track or behaviourally monitor children, and we do not show them targeted advertising."
        child = {
            GOOD: f"{good_consent} {no_track}",
            "under13": f"If you are under 13, we will need your parent's consent before you can use {s.name}. {no_track}",
            "ads": f"{good_consent} We may show personalised ads to all users, including children, based on their activity on {s.name}.",
            "absent": "",
        }[v]
        if child:
            sec["children"] = h("Children") + "\n" + child

    # Neutral filler that real notices have.
    sec["security"] = (
        h("Keeping your data safe")
        + "\n"
        + rng.choice(
            [
                "We protect your data with encryption and access controls, and we keep it only as long as needed for these purposes.",
                "We use reasonable security safeguards and delete your data once it is no longer needed for the purposes above.",
            ]
        )
    )
    if picks["no_foreign_law"] == "do_not_sell":
        sec["security"] += (
            "\nWe do not sell your personal information. To opt out of any sale of your data, click 'Do Not Sell My Personal Information'."
        )

    intro = rng.choice(
        [
            f"{s.name} ('we') respects your privacy. This notice explains how we handle your personal data when you use {s.name}.",
            f"Welcome to {s.name}. Please read this notice before you agree to let us process your personal data.",
        ]
    )
    title = f"# Privacy Notice - {s.name}"
    order = ["data", "purpose", "rights", "withdraw", "grievance", "children", "security", "contact"]
    if rng.random() < 0.5:
        order = ["data", "purpose", "withdraw", "rights", "children", "grievance", "contact", "security"]
    parts = [title, sec.pop("language", "") if rng.random() < 0.5 else "", intro]
    parts += [sec[k] for k in order if k in sec]
    if "language" in sec:
        parts.append(sec["language"])
    return "\n\n".join(p for p in parts if p).strip() + "\n"


# Scenario ids for the validation set. Dev is used while writing the judge prompt; test is not looked at until the end.
DEV_IDS = ["kiranakart", "pathshala", "bima", "fitmitra"]
TEST_IDS = ["udhaar", "sehat", "khelo", "safar", "naukri", "bachpan", "coachify", "ride"]


def build(seed: int = 2026, per_scenario: int = 5) -> dict[str, list[dict]]:
    scen = {s.id: s for s in load_scenarios()}
    rng = random.Random(seed)
    out: dict[str, list[dict]] = {"dev": [], "test": []}
    for split, ids in (("dev", DEV_IDS), ("test", TEST_IDS)):
        for sid in ids:
            s = scen[sid]
            for k in range(per_scenario):
                picks = choose(rng, s)
                if k == 0:  # one fully compliant notice per scenario, to catch judges that fail everything
                    picks = {c: GOOD for c in picks}
                out[split].append(
                    {
                        "id": f"{sid}-{k}",
                        "scenario": sid,
                        "picks": picks,
                        "labels": labels_for(picks),
                        "notice": render(rng, s, picks),
                    }
                )
    return out


def write(path: Path | None = None) -> None:
    path = path or DATA_DIR / "validation"
    path.mkdir(parents=True, exist_ok=True)
    for split, rows in build().items():
        with open(path / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load(split: str, path: Path | None = None) -> list[dict]:
    path = path or DATA_DIR / "validation"
    with open(path / f"{split}.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
