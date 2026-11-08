import pytest

gr = pytest.importorskip("gradio")

from dpdp_eval import web  # noqa: E402
from dpdp_eval.scenarios import custom_scenario  # noqa: E402

from .conftest import FakeLLM, verdict_json  # noqa: E402


def test_custom_scenario_marks_missing_facts():
    s = custom_scenario("", "name, phone\n- address", True)
    assert s.data == ("name", "phone", "address")
    assert "not provided" in s.facts()
    assert "Privacy contact" not in s.facts()
    assert custom_scenario().data == ()


def test_offline_check_uses_baseline_and_says_so(monkeypatch):
    monkeypatch.setattr(web, "AI_ON", False)
    notice = web._examples()["A compliant notice (kids' learning app)"][0]
    md = web.on_check(notice, "", "", True)
    assert "keyword baseline" in md
    assert "11 of 11" in md


def test_ai_check_falls_back_to_next_model_then_baseline(monkeypatch):
    monkeypatch.setattr(web, "AI_ON", True)
    monkeypatch.setattr(web, "JUDGE_MODELS", ["a", "b"])
    s = custom_scenario("", "", False)

    def fn(model, prompt):
        if model == "a":
            raise web.LLMError("busy")
        return verdict_json(s, {"nomination": "pass"}, {"nomination": "nominate"})

    monkeypatch.setattr(web, "_llm", FakeLLM(fn=fn))
    res, note = web.run_judge("You may nominate a person. " * 5, "", "", False)
    assert "`b`" in note and res.verdicts["nomination"] == "pass"

    monkeypatch.setattr(web, "_llm", FakeLLM(fn=lambda m, p: (_ for _ in ()).throw(web.LLMError("x"))))
    res, note = web.run_judge("You may nominate a person. " * 5, "", "", False)
    assert "keyword baseline" in note


def test_too_short_is_rejected():
    with pytest.raises(gr.Error):
        web.on_check("hi", "", "", False)


def test_app_builds():
    assert web.build() is not None


def test_quoted_list_stays_inside_the_blockquote():
    from dpdp_eval.judge import Result

    res = Result(
        {"data_itemised": "pass"}, {"data_itemised": "* Name\n*   Mobile number"}, {"data_itemised": "Listed."}
    )
    md = web.result_md(res, "note")
    assert "> Name; Mobile number\n\nListed." in md
