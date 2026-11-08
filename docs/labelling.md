# How the real notices were hand-labelled

`dpdp_eval/data/validation/real_labels.jsonl` holds verdicts for real notices written by the models under test.
They were labelled **before any LLM judge saw these notices** (check the commit times), by reading
each notice against the rubric in `dpdp_eval/rubric.py`. The labeller was Claude, working under
Natik's direction; Natik spot-checks a sample (see README).

Rules used where the rubric leaves room for judgement, applied the same way to every notice:

- **Withdrawal** passes only if the notice says *how* to withdraw (a setting, button, link or
  contact given for withdrawal). "You may withdraw consent at any time" next to a general
  "manage your settings under Settings" line is not enough: the Rules ask for a description of
  the means to withdraw (r.3(c)(i)).
- **Rights** passes only if access (or a summary), correction and erasure are all named **and** the
  notice says how to make the request (e.g. "to exercise your rights, contact our DPO at ...").
- **Grievance**: "contact our officer with complaints" plus a reply period of 90 days or less passes.
- **Contact**: an email for a Grievance Officer who takes privacy questions counts as "a person who
  can answer questions" (Rules r.9).
- **Nomination**: a "nominee name" collected as insurance data is not the s.14 right to nominate.
- **Children** passes only with both parts: verifiable parent/guardian consent for under-18s, and a
  statement that children are not tracked, behaviourally monitored or targeted with ads (s.9(1), 9(3)).
- **Withdrawal listed among the rights**: if the notice lists withdrawal as one of the user's rights
  and says how to exercise those rights ("to exercise your rights, contact our DPO"), withdrawal passes.

## Consistency audit (done after the first judge run, disclosed here)

Re-reading the labels against the rules above, two of the first 16 broke the last rule:
`gemini-3.5-flash-lite/pathshala/dpdp` and `gemini-3.5-flash-lite/safar/dpdp` had withdrawal marked
"fail" although withdrawal was listed among the rights and the notice said how to exercise them. Both
were changed to "pass" (the rows carry an `audit` field). This was noticed while reading the judge's
disagreements, so it is a known risk of bias; the change helps the judge on one notice and hurts it on
the other, so the agreement score is unchanged by it.

Four `dpdp_open` notices were added later. They were labelled after the Flash Lite judge had run on
them, without looking at its verdicts.

Three `gemma-4-31b-it` `dpdp_open` notices were added last, so the second judge is also tested on
open-prompt notices. They were labelled after the final Flash Lite judge run had started, without
looking at its verdicts.
