import json

from dpdp_eval import cli
from dpdp_eval.scenarios import load_scenarios

from .conftest import FakeLLM, verdict_json

S = {s.id: s for s in load_scenarios()}


def test_generate_judge_report_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "RESULTS", tmp_path)
    gen = tmp_path / "generations"
    llm = FakeLLM(fn=lambda model, prompt: f"notice by {model}")
    cli.generate(["m1", "m2"], ("plain",), llm=llm, gen_dir=gen)
    assert len(llm.calls) == 48
    assert sorted(p.name for p in gen.iterdir()) == ["m1.jsonl", "m2.jsonl"]
    cli.generate(["m1", "m2"], ("plain",), llm=llm, gen_dir=gen)  # resumes: nothing new
    assert len(llm.calls) == 48

    def judge_fn(model, prompt):
        sid = next(s for s in S.values() if s.facts() in prompt)
        return verdict_json(sid, {"nomination": "pass", "contact": "pass"})

    out = cli.judge_all("j", llm=FakeLLM(fn=judge_fn), gen_dir=gen)
    rows = [json.loads(x) for x in out.read_text().splitlines()]
    assert len(rows) == 48
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path)
    rep = cli.report("j")
    assert {r["model"] for r in rep["core"]} == {"m1", "m2"}
    assert rep["core"][0]["n"] == 12 and rep["all"][0]["n"] == 24
    r = rep["core"][0]
    assert r["ci95"][0] <= r["score"] <= r["ci95"][1]
    assert r["per_check"]["nomination"] == 1.0 and r["per_check"]["grievance"] == 0.0
    assert (tmp_path / "leaderboard-j.md").exists()
    assert "Core set" in (tmp_path / "leaderboard.md").read_text()


def test_validate_judge_with_baseline(tmp_path):
    s = cli.validate_judge("baseline", "dev", out_dir=tmp_path)
    assert s["notices"] == s["of"] == 20
    assert s["all"]["accuracy"] > 0.8
    assert (tmp_path / "dev-baseline.md").exists()


def test_generate_core_and_max_calls(tmp_path):
    llm = FakeLLM(fn=lambda model, prompt: "n")
    cli.generate(["m"], ("dpdp",), llm=llm, gen_dir=tmp_path, core_only=True, max_calls=5)
    assert len(llm.calls) == 5
    cli.generate(["m"], ("dpdp",), llm=llm, gen_dir=tmp_path, core_only=True)
    assert len(llm.calls) == 12
    rows = cli.load_generations(tmp_path)
    assert {r["scenario"] for r in rows} == set(cli.CORE_IDS)


def test_partial_models_are_marked_and_listed_last():
    from dpdp_eval.rubric import CHECKS

    def row(model, n, score):
        per = {c.id: 0.5 for c in CHECKS}
        return {
            "model": model,
            "condition": "plain",
            "n": n,
            "score": score,
            "ci95": [score, score],
            "fully_compliant": 0.0,
            "per_check": per,
        }

    md = "\n".join(cli._board_md([row("big", 5, 0.9), row("small", 12, 0.5)], expected_n=12))
    assert "`big` (partial: 5 of 12)" in md
    assert md.index("`small`") < md.index("`big`")
