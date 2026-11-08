<div align="center">

# 🔏 DPDP Notice Eval

**Can AI models write a privacy notice that follows India's new data protection law?**
An open eval: 24 Indian businesses, 11 legal checks (each cited to the Act or Rules), an LLM judge that was tested against known answers before it was trusted, and a leaderboard.

[![tests](https://github.com/NatikChhabra/dpdp-notice-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/NatikChhabra/dpdp-notice-eval/actions/workflows/ci.yml)
[![Live demo](https://img.shields.io/badge/Live%20demo-Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/Natik22may/dpdp-notice-check)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<!--DEMO_GIF-->

</div>

## Why

India's **Digital Personal Data Protection Act, 2023** and the **DPDP Rules, 2025** (G.S.R. 846(E), notified 13 Nov 2025) say exactly what a consent notice must contain. The notice duties (Rule 3) apply from about **13 May 2027**, so thousands of Indian startups are rewriting their privacy notices now, and many will ask an AI to do it.

YC's Fall 2026 Requests for Startups asks for [**AI-Native Compliance Infrastructure**](https://www.ycombinator.com/rfs) (Daivik Goel). That request is about financial compliance; this project applies the same idea to privacy law and asks a narrower question first: **when an AI writes a compliance document, how do you check it, at scale, in a way you can trust?** That is an eval problem.

<!--HEADLINE-->

## What it measures

Each model gets the facts of a business (what data it collects, why, who the privacy contact is, whether children use it) and is asked to write the consent notice. Two versions of the request:

- **plain**: "write the privacy notice we show users when they sign up". The law isn't named. Does the model know an Indian business needs a DPDP notice?
- **dpdp**: the same, plus "it must comply with India's DPDP Act, 2023 and DPDP Rules, 2025". Does it know what the law requires?

Every notice is scored on these checks (the children check applies only to the 7 businesses with users under 18):

| Check | What the law asks | Source |
|---|---|---|
| Lists the personal data, item by item | an itemised description of the personal data | Act s.5(1)(i); Rules r.3(b)(i) |
| States specific purposes | specified purposes and the goods/services they enable | Act s.5(1)(i); Rules r.3(b)(ii) |
| Explains how to withdraw consent | how to withdraw, as easily as consent was given | Act s.6(4), s.5(1)(ii); r.3(c)(i) |
| Explains the rights to access, correct and erase | how to exercise the rights under the Act | Act ss.11–12; r.3(c)(ii), r.14(1) |
| Mentions the right to nominate | nominate someone to act on death or incapacity | Act s.14; r.14(4) |
| Grievance route with a reply time ≤ 90 days | how to raise a grievance, and the reply period | Act s.13; r.14(3) |
| Explains how to complain to the Data Protection Board | the manner of complaining to the Board | Act s.5(1)(iii); r.3(c)(iii) |
| Contact for a DPO or a person who can answer questions | business contact information | Act s.8(9), s.6(3); r.9 |
| Offers the notice in English or an Indian language | option to read it in English or an Eighth Schedule language | Act s.5(3) |
| Doesn't import foreign-law ideas | no GDPR "legitimate interests", "data portability", "supervisory authority"… | Act ss.4, 7, 11–14, 18 |
| Handles children's data correctly | verifiable parental consent for under-18s; no tracking or targeted ads | Act s.2(f), s.9; r.10 |

The rubric only covers what the law says a *notice* must contain. It does not judge whether the processing itself is lawful, and it gives no credit for extra content.

## Can the judge be trusted?

An LLM judge is only useful if it agrees with the right answer. So before judging any model, each candidate judge was tested in three ways:

1. **Synthetic notices with known answers** (`dpdp_eval/data/validation/`). Notices are built from sections. For each check we pick a compliant section or a realistic mistake: a vague data list, a 120-day reply period, "the relevant supervisory authority", withdrawal only by registered post, children defined as under 13, personalised ads for children, and so on. The correct verdicts follow from the choices. The set is split by business: **dev** (4 businesses, 20 notices) was used to pick the judge, **test** (8 businesses, 40 notices) was held out.
2. **Real notices, hand-labelled** (`dpdp_eval/data/validation/real_labels.jsonl`). Real model notices were labelled before any judge saw them (see the commit history and [the labelling rules](docs/labelling.md)).
3. **Quote checking.** For every check the judge must quote the line it relied on. The code then confirms the quote exists in the notice, which catches a judge inventing support for a "pass".

| Judge | Synthetic dev (20 notices) | Synthetic held-out test (40 notices) | Real notices, hand-labelled (20) |
|---|---|---|---|
| **`gemini-3.5-flash-lite`** (chosen) | 99.0% agreement, κ 0.98 | **98.8%, κ 0.98** | **97.6%, κ 0.95** |
| `gemma-4-31b-it` (open weights; second judge) | 100%, κ 1.00 (16 of 20 notices; the free API returned errors on 4) | – | 97.2%, κ 0.94 (10 notices) |
| Keyword baseline (no AI) | 95.6%, κ 0.91 | 97.8%, κ 0.96 | 94.3%, κ 0.88 |

Agreement is over every (notice, check) pair; κ is Cohen's kappa, which corrects for agreement by chance. Full tables, including every disagreement, are in [`results/judge_validation/`](results/judge_validation/).

Where the judges differ is the interesting part. On the children's-data check in real notices, the keyword baseline was right **1 time in 9**, and Flash Lite was right **9 in 9**. On withdrawal, all of them struggle (Flash Lite 85%), because "you can withdraw consent at any time" with no stated method is a borderline case even for people.

Flash Lite was chosen because it was the most accurate judge that finished every notice, and because its free quota (500 requests a day) can cover the whole eval. 3.6 and 3.8 Flash get only 20 a day, and Gemma's free API often answered "500" or "503".

**Why not just use keywords?** A keyword checker (`dpdp_eval/baseline.py`) scores almost perfectly on the synthetic set, because the same person wrote both the templates and the keywords. On real notices it falls apart exactly where the law is subtle. It passes "you may withdraw consent at any time" even when the notice never says *how*. It also passes a children's section that mentions parents and the age of 18 but says nothing about tracking or targeted ads. This was the most useful lesson of the project: **a synthetic test set you wrote yourself flatters simple methods, so you need real, hand-labelled outputs to see the difference.**

## Leaderboard

<!--LEADERBOARD-->

## Run it

```bash
git clone https://github.com/NatikChhabra/dpdp-notice-eval && cd dpdp-notice-eval
pip install -r requirements-dev.txt
pytest                                                    # 30 tests, no API key needed
python -m dpdp_eval validate-judge --judge baseline --split test

export GEMINI_API_KEY=...                                  # free key from Google AI Studio
python -m dpdp_eval validate-judge --judge gemini-3.5-flash-lite --split test
python -m dpdp_eval generate --models gemma-4-31b-it --core
python -m dpdp_eval judge --judge gemini-3.5-flash-lite
python -m dpdp_eval report --judge gemini-3.5-flash-lite
python app.py                                             # the demo, at http://127.0.0.1:7860
```

Every model call is appended to a JSONL file as soon as it returns, so a run that hits the free daily quota stops cleanly and resumes from the same point next time. The results in `results/` were produced by the [`run eval`](.github/workflows/run-eval.yml) GitHub Action, which uses the API key stored as a repository secret and commits its outputs, so every number here can be traced to a logged run.

| AI engineering skill | Where it is |
|---|---|
| Designing a rubric from a legal text | `dpdp_eval/rubric.py` |
| LLM-as-judge with structured output (evidence → reasoning → verdict) | `dpdp_eval/judge.py` |
| Validating a judge: known-answer set, dev/test split, hand labels, Cohen's kappa | `dpdp_eval/synth.py`, `cli.py validate-*`, `metrics.py` |
| Catching hallucinated evidence | `judge.evidence_found` |
| Prompt-injection guard (the notice is untrusted input) | `JUDGE_SYSTEM` in `judge.py` |
| Bootstrap confidence intervals, clustered by business | `metrics.bootstrap_ci` |
| An ablation to rule out a prompt confound | `ABLATIONS` in `scenarios.py` |
| Working inside tiny free-tier rate limits (pacing, resume, per-model files) | `llm.py`, `cli.py` |
| Testing LLM code without API calls | `tests/` (a fake model) |

## Limits (please read)

- **Not legal advice.** It checks the minimum content the Act and Rules require in a notice, as read by the author. Courts and the Data Protection Board have not interpreted these rules yet.
- **Small and synthetic.** 24 made-up businesses, and only the models a free Gemini API key can reach (Gemini Flash/Flash Lite and open-weight Gemma 4). Frontier "Pro" models are not on the free tier, so they aren't here.
- **The judge is a Google model judging Google models.** Self-preference is a known LLM-judge bias. The hand-labelled real notices and a second judge from a different model family (Gemma, open weights) are there to show how much it matters; see the judge table.
- **The hand labels were made by Claude** (the AI that helped build this) under the rules in `docs/labelling.md`, written before the judges ran. Natik spot-checked them. Two lawyers would still disagree on some borderline cases, such as whether "manage your settings" counts as a way to withdraw consent.
- **The synthetic judge-test set is easy.** It is templated, so near-perfect scores on it mean little alone. The real-notice numbers matter more.
- **Phrasing matters.** Results are for two fixed prompts (plus one ablation). A founder who pastes the full text of the Rules will get better notices.

## Built with AI, openly

I built this with **Claude (Anthropic) as a coding and research partner**. Claude wrote most of the code under my direction. I chose the problem, the legal scope and the quality bar, and reviewed the rubric against the Act and the Rules. The models being tested and the judge are Google's Gemini and Gemma, run on a free API key.

Built by [Natik Chhabra](https://github.com/NatikChhabra) · MIT licence · Legal text used (Gazette copies, via dpdpa.com): [DPDP Act, 2023](https://dpdpa.com/DPDPA_2023_official.pdf) (Act No. 22 of 2023) · [DPDP Rules, 2025](https://dpdpa.com/DPDP_Rules_2025_English_only.pdf) (G.S.R. 846(E), 13 Nov 2025)
