"""Command line: python -m dpdp_eval <command>.

  models                        list Gemini API models your key can use
  build-validation              (re)write data/validation/{dev,test}.jsonl
  validate-judge --judge M      score a judge model (or --judge baseline) against the known labels
  generate --models A,B         ask each model to write a notice for every scenario and condition
  judge --judge M               judge every generated notice
  report --judge M              write results/leaderboard.{md,json}

All model calls are appended to JSONL files as they finish, so an interrupted run (or a used-up
free quota) resumes where it stopped.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from . import synth
from .baseline import baseline_verdicts
from .judge import Result, judge_notice
from .llm import GeminiLLM, LLMError, QuotaExhausted
from .metrics import bootstrap_ci, md_table, per_check
from .rubric import CHECKS
from .scenarios import CONDITIONS, load_scenarios, writer_prompt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _safe(model: str) -> str:
    return model.replace("/", "_")


# ---------- judge validation ----------


def validate_judge(judge: str, split: str, llm=None, out_dir: Path = RESULTS / "judge_validation") -> dict:
    scen = {s.id: s for s in load_scenarios()}
    rows = synth.load(split)
    out = out_dir / f"{split}-{_safe(judge)}.jsonl"
    done = {r["id"] for r in _read_jsonl(out)}
    if judge != "baseline" and any(r["id"] not in done for r in rows):
        llm = llm or GeminiLLM()
    for r in rows:
        if r["id"] in done:
            continue
        s = scen[r["scenario"]]
        if judge == "baseline":
            res = Result(baseline_verdicts(s, r["notice"]))
        else:
            try:
                res = judge_notice(llm, judge, s, r["notice"])
            except QuotaExhausted as e:
                print(f"stopping: {e}", file=sys.stderr)
                break
            except LLMError as e:
                print(f"skip {r['id']}: {e}", file=sys.stderr)
                continue
        _append(out, {"id": r["id"], **res.to_dict()})
        print(f"{r['id']}: {res.score:.2f}", file=sys.stderr)
    return summarise_validation(judge, split, out_dir)


def summarise_validation(judge: str, split: str, out_dir: Path = RESULTS / "judge_validation") -> dict:
    truth = {r["id"]: r for r in synth.load(split)}
    preds = _read_jsonl(out_dir / f"{split}-{_safe(judge)}.jsonl")
    rows, unverified, n_pass = [], 0, 0
    errors = []
    for p in preds:
        t = truth[p["id"]]["labels"]
        for cid, lab in t.items():
            got = p["verdicts"][cid]
            rows.append((cid, lab, got))
            if got != lab:
                errors.append(
                    {"id": p["id"], "check": cid, "truth": lab, "judge": got, "variant": truth[p["id"]]["picks"][cid]}
                )
        n_pass += sum(v == "pass" for v in p["verdicts"].values())
        unverified += len(p.get("unverified", []))
    agg = per_check(rows)
    order = [c.id for c in CHECKS] + ["ALL"]
    table = md_table(
        ["check", "n", "accuracy", "kappa", "fail precision", "fail recall"],
        [[k, *agg[k].row()] for k in order if k in agg],
    )
    summary = {
        "judge": judge,
        "split": split,
        "notices": len(preds),
        "of": len(truth),
        "all": vars(agg["ALL"]) if "ALL" in agg else None,
        "per_check": {k: vars(v) for k, v in agg.items()},
        "unverified_pass_quotes": unverified,
        "passes": n_pass,
        "errors": errors,
    }
    (out_dir / f"{split}-{_safe(judge)}.md").write_text(
        f"# Judge validation: {judge} on {split} ({len(preds)}/{len(truth)} notices)\n\n{table}\n\n"
        f"Passes whose quoted evidence was not found in the notice: {unverified} of {n_pass}.\n\n"
        "## Disagreements\n\n"
        + md_table(
            ["notice", "check", "truth", "judge", "variant"],
            [[e["id"], e["check"], e["truth"], e["judge"], e["variant"]] for e in errors],
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


# ---------- generation + judging ----------


def _gen_dir(gen_dir: Path | None) -> Path:
    return gen_dir or RESULTS / "generations"


def load_generations(gen_dir: Path | None = None) -> list[dict]:
    """All generated notices, one JSONL file per model (so models can run in parallel)."""
    return [r for p in sorted(_gen_dir(gen_dir).glob("*.jsonl")) for r in _read_jsonl(p)]


def generate(models: list[str], conditions=CONDITIONS, llm=None, gen_dir: Path | None = None) -> None:
    llm = llm or GeminiLLM()
    for model in models:
        path = _gen_dir(gen_dir) / f"{_safe(model)}.jsonl"
        done = {(r["model"], r["scenario"], r["condition"]) for r in _read_jsonl(path)}
        for s in load_scenarios():
            for cond in conditions:
                if (model, s.id, cond) in done:
                    continue
                try:
                    text = llm.generate(model, writer_prompt(s, cond), temperature=0.7)
                except QuotaExhausted as e:
                    print(f"{model}: {e}; moving on", file=sys.stderr)
                    break
                except LLMError as e:
                    print(f"skip {model}/{s.id}/{cond}: {e}", file=sys.stderr)
                    continue
                _append(path, {"model": model, "scenario": s.id, "condition": cond, "notice": text})
                print(f"{model} {s.id} {cond}: {len(text)} chars", file=sys.stderr)
            else:
                continue
            break


def judge_all(judge: str, llm=None, gen_dir: Path | None = None) -> Path:
    scen = {s.id: s for s in load_scenarios()}
    out = RESULTS / f"judgments-{_safe(judge)}.jsonl"
    done = {(r["model"], r["scenario"], r["condition"]) for r in _read_jsonl(out)}
    todo = [g for g in load_generations(gen_dir) if (g["model"], g["scenario"], g["condition"]) not in done]
    if judge != "baseline" and todo:
        llm = llm or GeminiLLM()
    for g in todo:
        s = scen[g["scenario"]]
        if judge == "baseline":
            res = Result(baseline_verdicts(s, g["notice"]))
        else:
            try:
                res = judge_notice(llm, judge, s, g["notice"])
            except QuotaExhausted as e:
                print(f"stopping: {e}", file=sys.stderr)
                break
            except LLMError as e:
                print(f"skip: {e}", file=sys.stderr)
                continue
        _append(out, {"model": g["model"], "scenario": g["scenario"], "condition": g["condition"], **res.to_dict()})
        print(f"{g['model']} {g['scenario']} {g['condition']}: {res.score:.2f}", file=sys.stderr)
    return out


def report(judge: str) -> dict:
    rows = _read_jsonl(RESULTS / f"judgments-{_safe(judge)}.jsonl")
    by: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    full: dict[tuple[str, str], list[int]] = defaultdict(list)
    check_rate: dict[tuple[str, str], dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = (r["model"], r["condition"])
        by[key][r["scenario"]].append(r["score"])
        full[key].append(int(all(v == "pass" for v in r["verdicts"].values())))
        for cid, v in r["verdicts"].items():
            check_rate[key][cid].append(int(v == "pass"))
    board = []
    for key, clusters in by.items():
        mean, lo, hi = bootstrap_ci(clusters)
        board.append(
            {
                "model": key[0],
                "condition": key[1],
                "n": sum(len(v) for v in clusters.values()),
                "score": round(mean, 4),
                "ci95": [round(lo, 4), round(hi, 4)],
                "fully_compliant": round(sum(full[key]) / len(full[key]), 4),
                "per_check": {c: round(sum(v) / len(v), 4) for c, v in check_rate[key].items()},
            }
        )
    board.sort(key=lambda b: (b["condition"], -b["score"]))
    out = {"judge": judge, "rows": board}
    (RESULTS / f"leaderboard-{_safe(judge)}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    ids = [c.id for c in CHECKS]
    md = [f"# Leaderboard (judge: {judge})\n"]
    for cond in CONDITIONS:
        sel = [b for b in board if b["condition"] == cond]
        if not sel:
            continue
        md.append(f"\n## Prompt: {cond}\n")
        md.append(
            md_table(
                ["model", "n", "score", "95% CI", "fully compliant"],
                [
                    [
                        b["model"],
                        str(b["n"]),
                        f"{b['score']:.0%}",
                        f"{b['ci95'][0]:.0%}–{b['ci95'][1]:.0%}",
                        f"{b['fully_compliant']:.0%}",
                    ]
                    for b in sel
                ],
            )
        )
        md.append("\nPass rate per check:\n")
        md.append(
            md_table(
                ["model", *ids],
                [[b["model"], *[f"{b['per_check'].get(i, float('nan')):.0%}" for i in ids]] for b in sel],
            )
        )
    (RESULTS / f"leaderboard-{_safe(judge)}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="dpdp_eval")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models")
    sub.add_parser("build-validation")
    v = sub.add_parser("validate-judge")
    v.add_argument("--judge", required=True)
    v.add_argument("--split", default="dev", choices=["dev", "test"])
    g = sub.add_parser("generate")
    g.add_argument("--models", required=True)
    g.add_argument("--conditions", default=",".join(CONDITIONS))
    j = sub.add_parser("judge")
    j.add_argument("--judge", required=True)
    r = sub.add_parser("report")
    r.add_argument("--judge", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "models":
        print("\n".join(GeminiLLM().list_models()))
    elif a.cmd == "build-validation":
        synth.write()
    elif a.cmd == "validate-judge":
        s = validate_judge(a.judge, a.split)
        print(
            json.dumps(
                {k: s[k] for k in ("judge", "split", "notices", "of", "all", "unverified_pass_quotes")}, indent=2
            )
        )
    elif a.cmd == "generate":
        generate([m.strip() for m in a.models.split(",") if m.strip()], tuple(a.conditions.split(",")))
    elif a.cmd == "judge":
        judge_all(a.judge)
    elif a.cmd == "report":
        print(json.dumps(report(a.judge)["rows"], indent=1))
