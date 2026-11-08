# Judge validation on real notices: gemma-4-31b-it (15 notices, hand-labelled)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| withdraw_consent | 15 | 0.667 | 0.286 | 0.778 | 0.700 |
| rights | 15 | 0.800 | 0.571 | 0.889 | 0.800 |
| nomination | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| children | 9 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 159 | 0.950 | 0.898 | 0.957 | 0.931 |

## Disagreements

| notice | check | label | judge |
|---|---|---|---|
| gemini-3.5-flash-lite/pathshala/dpdp | withdraw_consent | pass | fail |
| gemini-3.5-flash-lite/pathshala/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/khelo/dpdp | withdraw_consent | fail | pass |
| gemini-3.5-flash-lite/khelo/dpdp_open | withdraw_consent | pass | fail |
| gemma-4-31b-it/pathshala/dpdp_open | withdraw_consent | fail | pass |
| gemma-4-31b-it/pathshala/dpdp_open | rights | fail | pass |
| gemma-4-31b-it/gym/dpdp_open | withdraw_consent | fail | pass |
| gemma-4-31b-it/gym/dpdp_open | rights | fail | pass |
