import json

import pytest

from dpdp_eval.rubric import applicable


class FakeLLM:
    """Returns canned answers and records every call, so no test touches the network."""

    def __init__(self, answers=None, fn=None):
        self.answers = list(answers or [])
        self.fn = fn
        self.calls = []

    def generate(self, model, prompt, *, system=None, schema=None, temperature=None):
        self.calls.append({"model": model, "prompt": prompt, "system": system, "schema": schema})
        if self.fn:
            return self.fn(model, prompt)
        return self.answers.pop(0)


def verdict_json(scenario, verdicts=None, evidence=None):
    verdicts = verdicts or {}
    evidence = evidence or {}
    return json.dumps(
        {
            "checks": [
                {
                    "check_id": c.id,
                    "evidence": evidence.get(c.id, ""),
                    "reasoning": "r",
                    "verdict": verdicts.get(c.id, "fail"),
                }
                for c in applicable(scenario.children)
            ]
        }
    )


@pytest.fixture
def fake():
    return FakeLLM
