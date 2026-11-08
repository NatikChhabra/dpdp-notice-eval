"""Command line: python -m dpdp_eval <command>.

  models                        list Gemini API models your key can use
  build-validation              (re)write dpdp_eval/data/validation/{dev,test}.jsonl
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
from .scenarios import ABLATIONS, CONDITIONS, CORE_IDS, DATA_DIR, load_scenarios, writer_prompt

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


def validate_real(judge: str, llm=None, out_dir: Path | None = None) -> dict:
    """Agreement with hand labels on real model notices. Reuses (and adds to) the judge's judgments file."""
    out_dir = out_dir or RESULTS / "judge_validation"
    scen = {s.id: s for s in load_scenarios()}
    labels = _read_jsonl(DATA_DIR / "validation" / "real_labels.jsonl")
    gens = {(g["model"], g["scenario"], g["condition"]): g for g in load_generations()}
    jpath = RESULTS / f"judgments-{_safe(judge)}.jsonl"
    judged = {(r["model"], r["scenario"], r["condition"]): r for r in _read_jsonl(jpath)}
    rows = []
    for lab in labels:
        key = (lab["model"], lab["scenario"], lab["condition"])
        g = gens[key]
        if key not in judged:
            s = scen[g["scenario"]]
            if judge == "baseline":
                res = Result(baseline_verdicts(s, g["notice"]))
            else:
                llm = llm or GeminiLLM()
                try:
                    res = judge_notice(llm, judge, s, g["notice"])
                except QuotaExhausted as e:
                    print(f"stopping: {e}", file=sys.stderr)
                    break
                except LLMError as e:
                    print(f"skip: {e}", file=sys.stderr)
                    continue
            judged[key] = {"model": key[0], "scenario": key[1], "condition": key[2], **res.to_dict()}
            if judge != "baseline":
                _append(jpath, judged[key])
        for cid, t in lab["labels"].items():
            rows.append((cid, t, judged[key]["verdicts"][cid], key))
    agg = per_check([(c, t, p) for c, t, p, _ in rows])
    order = [c.id for c in CHECKS] + ["ALL"]
    errors = [[f"{k[0]}/{k[1]}/{k[2]}", c, t, p] for c, t, p, k in rows if t != p]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"real-{_safe(judge)}.md").write_text(
        f"# Judge validation on real notices: {judge} ({len({r[3] for r in rows})} notices, hand-labelled)\n\n"
        + md_table(
            ["check", "n", "accuracy", "kappa", "fail precision", "fail recall"],
            [[k, *agg[k].row()] for k in order if k in agg],
        )
        + "\n\n## Disagreements\n\n"
        + md_table(["notice", "check", "label", "judge"], errors)
        + "\n",
        encoding="utf-8",
    )
    return {
        "judge": judge,
        "all": vars(agg["ALL"]) if "ALL" in agg else None,
        "per_check": {k: vars(v) for k, v in agg.items()},
    }


# ---------- generation + judging ----------


def _gen_dir(gen_dir: Path | None) -> Path:
    return gen_dir or RESULTS / "generations"


def load_generations(gen_dir: Path | None = None) -> list[dict]:
    """All generated notices, one JSONL file per model (so models can run in parallel)."""
    return [r for p in sorted(_gen_dir(gen_dir).glob("*.jsonl")) for r in _read_jsonl(p)]


def generate(
    models: list[str],
    conditions=CONDITIONS,
    llm=None,
    gen_dir: Path | None = None,
    core_only: bool = False,
    max_calls: int | None = None,
) -> None:
    """max_calls caps calls per model per run, to leave free quota for the live apps."""
    llm = llm or GeminiLLM()
    scenarios = [s for s in load_scenarios() if not core_only or s.id in CORE_IDS]
    for model in models:
        path = _gen_dir(gen_dir) / f"{_safe(model)}.jsonl"
        done = {(r["model"], r["scenario"], r["condition"]) for r in _read_jsonl(path)}
        calls = 0
        for s in scenarios:
            for cond in conditions:
                if (model, s.id, cond) in done:
                    continue
                if max_calls is not None and calls >= max_calls:
                    break
                calls += 1
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


SHORT = {
    "data_itemised": "data",
    "purpose_specific": "purpose",
    "withdraw_consent": "withdraw",
    "rights": "rights",
    "nomination": "nominate",
    "grievance": "grievance",
    "board_complaint": "Board",
    "contact": "contact",
    "language": "language",
    "no_foreign_law": "no GDPR",
    "children": "children",
}


def _board(rows: list[dict]) -> list[dict]:
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
    return board


def _board_md(board: list[dict]) -> list[str]:
    ids = [c.id for c in CHECKS]
    md = []
    labels = {
        "plain": "plain request (no law named)",
        "dpdp_open": "request names the DPDP Act and Rules",
        "dpdp": "names the law and adds 'use only the facts below' (comparison)",
    }
    for cond in CONDITIONS + ABLATIONS:
        sel = [b for b in board if b["condition"] == cond]
        if not sel:
            continue
        label = labels[cond]
        md.append(f"\n**Prompt: {label}**\n")
        md.append(
            md_table(
                ["model", "notices", "score", "95% CI", "fully compliant", *[SHORT[i] for i in ids]],
                [
                    [
                        f"`{b['model']}`",
                        str(b["n"]),
                        f"**{b['score']:.0%}**",
                        f"{b['ci95'][0]:.0%}–{b['ci95'][1]:.0%}",
                        f"{b['fully_compliant']:.0%}",
                        *[f"{b['per_check'][i]:.0%}" if i in b["per_check"] else "–" for i in ids],
                    ]
                    for b in sel
                ],
            )
        )
    return md


def report(judge: str) -> dict:
    """Leaderboard: all models on the 12 core scenarios, plus all 24 for models that have them."""
    rows = _read_jsonl(RESULTS / f"judgments-{_safe(judge)}.jsonl")
    core = _board([r for r in rows if r["scenario"] in CORE_IDS])
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for r in rows:
        counts[(r["model"], r["condition"])] += 1
    n_all = len(load_scenarios())
    full = _board([r for r in rows if counts[(r["model"], r["condition"])] == n_all])
    out = {"judge": judge, "core": core, "all": full}
    (RESULTS / f"leaderboard-{_safe(judge)}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    md = [
        f"## Leaderboard (judge: `{judge}`)\n",
        "Score = share of applicable checks passed (10, or 11 if the business has users under 18). "
        "95% CI from a bootstrap over businesses. Fully compliant = passes every check. "
        "Columns on the right are pass rates per check.\n",
        f"### Core set: {len(CORE_IDS)} businesses, every model",
        *_board_md(core),
    ]
    if full:
        md += [f"\n### Full set: {n_all} businesses (models with enough free quota)", *_board_md(full)]
    text = "\n".join(md) + "\n"
    (RESULTS / f"leaderboard-{_safe(judge)}.md").write_text(text, encoding="utf-8")
    (DATA_DIR / "leaderboard.md").write_text(text, encoding="utf-8")
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
    g.add_argument("--core", action="store_true", help="only the 12 core scenarios")
    g.add_argument("--max-calls", type=int, default=None, help="cap on calls per model in this run")
    j = sub.add_parser("judge")
    j.add_argument("--judge", required=True)
    vr = sub.add_parser("validate-real")
    vr.add_argument("--judge", required=True)
    r = sub.add_parser("report")
    r.add_argument("--judge", required=True)
    sp = sub.add_parser("smoke-space", help="call the live Hugging Face demo with an example notice")
    sp.add_argument("--space", default="Natik22may/dpdp-notice-check")
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
    elif a.cmd == "smoke-space":
        from gradio_client import Client

        notice = synth.load("dev")[0]["notice"]
        out = Client(a.space).predict(notice, "", "", False, api_name="/on_check")
        print(out)
        if "requirements met" not in out:
            sys.exit("demo did not return a result")
    elif a.cmd == "validate-real":
        print(json.dumps(validate_real(a.judge)["all"], indent=2))
    elif a.cmd == "generate":
        generate(
            [m.strip() for m in a.models.split(",") if m.strip()],
            tuple(a.conditions.split(",")),
            core_only=a.core,
            max_calls=a.max_calls,
        )
    elif a.cmd == "judge":
        judge_all(a.judge)
    elif a.cmd == "report":
        print(json.dumps(report(a.judge)["core"], indent=1))
