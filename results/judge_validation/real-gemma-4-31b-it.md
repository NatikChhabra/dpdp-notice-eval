# Judge validation on real notices: gemma-4-31b-it (10 notices, hand-labelled)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| withdraw_consent | 10 | 0.800 | 0.000 | 1.000 | 0.800 |
| rights | 10 | 0.900 | 0.615 | 0.889 | 1.000 |
| nomination | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| children | 6 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 106 | 0.972 | 0.943 | 0.981 | 0.963 |

## Disagreements

| notice | check | label | judge |
|---|---|---|---|
| gemini-3.5-flash-lite/pathshala/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/khelo/dpdp | withdraw_consent | fail | pass |
| gemini-3.5-flash-lite/safar/dpdp | withdraw_consent | fail | pass |
