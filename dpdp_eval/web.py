"""Web demo (Gradio): paste a privacy notice, get it checked against the DPDP Act and Rules.

Run: python app.py. With GEMINI_API_KEY set, the LLM judge is used. Without it (or when the free
quota is used up) the keyword baseline answers instead, and the page says so.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import gradio as gr

from . import synth
from .baseline import baseline_verdicts
from .judge import Result, judge_notice
from .llm import GeminiLLM, LLMError
from .rubric import BY_ID, CHECKS
from .scenarios import DATA_DIR, custom_scenario

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/NatikChhabra/dpdp-notice-eval"
JUDGE_MODELS = [
    m.strip()
    for m in os.environ.get("DPDP_JUDGE_MODELS", "gemma-4-31b-it,gemini-3.5-flash-lite").split(",")
    if m.strip()
]
AI_ON = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
_llm = None


def _esc(t: str) -> str:
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _get_llm():
    global _llm
    if _llm is None:
        _llm = GeminiLLM(min_interval=0, max_attempts=2)
    return _llm


def run_judge(notice: str, description: str, data: str, children: bool) -> tuple[Result, str]:
    """Returns the result and a line saying who judged it."""
    s = custom_scenario(description, data, children)
    if AI_ON:
        errors = []
        for model in JUDGE_MODELS:
            try:
                return judge_notice(_get_llm(), model, s, notice), f"Judged by `{model}` (LLM judge)."
            except LLMError as e:
                errors.append(str(e))
        note = "The AI judge is busy or out of free quota right now, so the **keyword baseline** answered. It is less reliable (see the validation results)."
    else:
        note = (
            "No API key is set, so the **keyword baseline** answered. It is less reliable (see the validation results)."
        )
    return Result(baseline_verdicts(s, notice)), note


def result_md(res: Result, note: str) -> str:
    passed = sum(v == "pass" for v in res.verdicts.values())
    total = len(res.verdicts)
    head = "🟢" if passed == total else ("🟠" if passed >= total * 0.6 else "🔴")
    out = [f"## {head} {passed} of {total} DPDP requirements met", f"<small>{note}</small>", ""]
    for cid, v in sorted(res.verdicts.items(), key=lambda kv: kv[1] != "fail"):
        c = BY_ID[cid]
        mark = "✅" if v == "pass" else "❌"
        out.append(f"{mark} **{_esc(c.title)}**  <small>({_esc(c.cites)})</small>")
        if res.evidence.get(cid):
            out.append(f"> {_esc(res.evidence[cid])}")
        if res.reasoning.get(cid):
            out.append(f"{_esc(res.reasoning[cid])}")
        if v == "fail":
            out.append(f"<small>What the law asks: {_esc(c.requirement)}</small>")
        if cid in res.unverified:
            out.append("<small>⚠️ The judge's quote was not found in your notice, so treat this pass with care.</small>")
        out.append("")
    out.append(
        "<small>General guidance only, not legal advice. Notice duties in the DPDP Rules apply from about 13 May 2027.</small>"
    )
    return "\n".join(out)


def on_check(notice, description, data, children):
    notice = (notice or "").strip()
    if len(notice) < 80:
        raise gr.Error("Paste a privacy notice first (at least a few sentences).")
    if len(notice) > 30_000:
        raise gr.Error("That's too long for the demo. Paste up to about 30,000 characters.")
    res, note = run_judge(notice, description or "", data or "", bool(children))
    return result_md(res, note)


def _examples() -> dict[str, tuple[str, str, str, bool]]:
    rows = {r["id"]: r for r in synth.load("dev")}
    from .scenarios import load_scenarios

    scen = {s.id: s for s in load_scenarios()}
    out = {}
    real = json.loads((DATA_DIR / "example_real.json").read_text(encoding="utf-8"))
    s = scen[real["scenario"]]
    out["A notice Gemini wrote when asked for DPDP compliance (children's clinic)"] = (
        real["notice"],
        s.description,
        "\n".join(s.data),
        s.children,
    )
    for label, rid in (
        ("A compliant notice (kids' learning app)", "pathshala-0"),
        ("A flawed notice (grocery app)", "kiranakart-3"),
    ):
        r = rows[rid]
        s = scen[r["scenario"]]
        out[label] = (r["notice"], s.description, "\n".join(s.data), s.children)
    return out


def _leaderboard_md() -> str:
    p = DATA_DIR / "leaderboard.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return f"Results will appear here. See the [repo]({REPO_URL})."


def _rubric_md() -> str:
    rows = ["| Check | What the law asks | Source |", "|---|---|---|"]
    for c in CHECKS:
        extra = " *(only if users are under 18)*" if c.children_only else ""
        rows.append(f"| **{c.title}**{extra} | {c.requirement} | {c.cites} |")
    return "\n".join(rows)


def build() -> gr.Blocks:
    ex = _examples()
    with gr.Blocks(title="DPDP Notice Check") as demo:
        gr.Markdown(
            "# 🔏 DPDP Notice Check\n"
            "Paste a privacy notice. An AI judge checks it against the **11 things India's Digital Personal Data "
            "Protection Act, 2023 and DPDP Rules, 2025 require a consent notice to say**, and quotes the line it "
            f"relied on for each. This is the live judge from an open eval of AI models. [Code, data and results]({REPO_URL})."
        )
        with gr.Tab("Check a notice"):
            with gr.Row():
                with gr.Column():
                    notice = gr.Textbox(
                        label="Privacy notice",
                        lines=16,
                        placeholder="Paste the notice users see when they give consent…",
                    )
                    with gr.Accordion("About the business (optional, makes the check stricter)", open=False):
                        desc = gr.Textbox(label="What the business does", lines=2)
                        data = gr.Textbox(label="Personal data it collects (one per line)", lines=4)
                    kids = gr.Checkbox(label="Some users are under 18")
                    with gr.Row():
                        go = gr.Button("Check it", variant="primary")
                        pick = gr.Dropdown(list(ex), label="…or try an example", value=None)
                with gr.Column():
                    out = gr.Markdown()
            go.click(on_check, [notice, desc, data, kids], out)
            pick.change(lambda k: ex[k] if k else (gr.skip(),) * 4, pick, [notice, desc, data, kids])
        with gr.Tab("Model leaderboard"):
            gr.Markdown(_leaderboard_md())
        with gr.Tab("The 11 checks"):
            gr.Markdown(_rubric_md())
            gr.Markdown(f"Full method, judge validation and limits: [README]({REPO_URL}#readme)")
    return demo


def main() -> None:
    build().launch()


if __name__ == "__main__":
    main()
