import random

from dpdp_eval import synth
from dpdp_eval.baseline import baseline_verdicts
from dpdp_eval.metrics import agreement, bootstrap_ci
from dpdp_eval.rubric import applicable
from dpdp_eval.scenarios import load_scenarios

S = {s.id: s for s in load_scenarios()}


def test_build_is_deterministic_and_matches_committed_files():
    assert synth.build() == synth.build()
    built = synth.build()
    assert built["dev"] == synth.load("dev")
    assert built["test"] == synth.load("test")


def test_dev_and_test_use_different_businesses():
    assert not set(synth.DEV_IDS) & set(synth.TEST_IDS)


def test_labels_cover_applicable_checks_and_first_notice_is_clean():
    for rows in synth.build().values():
        for r in rows:
            s = S[r["scenario"]]
            assert set(r["labels"]) == {c.id for c in applicable(s.children)}
            if r["id"].endswith("-0"):
                assert set(r["labels"].values()) == {"pass"}


def test_both_labels_are_common():
    rows = [v for r in synth.build()["test"] for v in r["labels"].values()]
    share = rows.count("fail") / len(rows)
    assert 0.3 < share < 0.6


def test_wrong_regulator_also_fails_foreign_law():
    lab = synth.labels_for({"board_complaint": "wrong_body_sa", "no_foreign_law": "good"})
    assert lab["no_foreign_law"] == "fail"


def test_dropped_data_items_really_vanish():
    s = S["udhaar"]
    picks = {c.id: "good" for c in applicable(False)}
    picks["data_itemised"] = "missing"
    text = synth.render(random.Random(1), s, picks)
    assert sum(item not in text for item in s.data) >= 1


def test_baseline_passes_a_clean_notice_and_catches_obvious_gaps():
    clean = next(r for r in synth.build()["dev"] if r["id"] == "pathshala-0")
    v = baseline_verdicts(S["pathshala"], clean["notice"])
    assert set(v.values()) == {"pass"}
    v = baseline_verdicts(S["pathshala"], "We collect your data. Contact the supervisory authority.")
    assert v["board_complaint"] == "fail" and v["no_foreign_law"] == "fail" and v["children"] == "fail"


def test_agreement_metrics():
    a = agreement([("fail", "fail"), ("pass", "pass"), ("fail", "pass"), ("pass", "pass")])
    assert a.accuracy == 0.75
    assert a.fail_recall == 0.5 and a.fail_precision == 1.0
    assert 0 < a.kappa < 1
    perfect = agreement([("fail", "fail"), ("pass", "pass")])
    assert perfect.kappa == 1.0


def test_bootstrap_ci_brackets_mean():
    m, lo, hi = bootstrap_ci({"a": [0.2, 0.4], "b": [0.6], "c": [0.9, 1.0]})
    assert lo <= m <= hi
    m, lo, hi = bootstrap_ci({"a": [0.5], "b": [0.5]})
    assert lo == m == hi == 0.5
