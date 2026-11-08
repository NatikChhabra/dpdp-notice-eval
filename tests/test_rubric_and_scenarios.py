import pytest

from dpdp_eval.rubric import BY_ID, CHECKS, applicable
from dpdp_eval.scenarios import CONDITIONS, load_scenarios, writer_prompt


def test_every_check_cites_the_law():
    for c in CHECKS:
        assert ("Act" in c.cites) or ("Rules" in c.cites), c.id
        assert c.passes_if and c.fails_if and c.requirement


def test_ids_unique():
    assert len(BY_ID) == len(CHECKS)


def test_children_check_only_when_children():
    assert "children" in [c.id for c in applicable(True)]
    assert "children" not in [c.id for c in applicable(False)]
    assert len(applicable(True)) == len(applicable(False)) + 1


def test_scenarios_load_and_are_varied():
    s = load_scenarios()
    assert len(s) == 24
    assert len({x.id for x in s}) == 24
    assert 5 <= sum(x.children for x in s) <= 10
    assert all(x.grievance_days <= 90 for x in s)
    assert all(x.contact_email in x.facts() for x in s)


def test_prompts_differ_only_in_the_law_line():
    s = load_scenarios()[0]
    plain, dpdp = writer_prompt(s, "plain"), writer_prompt(s, "dpdp")
    assert set(CONDITIONS) == {"plain", "dpdp", "dpdp_open"}
    assert "Digital Personal Data Protection" not in plain
    assert "Digital Personal Data Protection Act, 2023" in dpdp
    assert s.facts() in plain and s.facts() in dpdp
    with pytest.raises(ValueError):
        writer_prompt(s, "nope")


def test_open_ablation_drops_only_the_stick_to_facts_line():
    s = load_scenarios()[0]
    dpdp, open_ = writer_prompt(s, "dpdp"), writer_prompt(s, "dpdp_open")
    assert "Use only the facts" in dpdp and "Use only the facts" not in open_
    assert open_ == dpdp.replace("Use only the facts below; don't invent other data or purposes. ", "")
