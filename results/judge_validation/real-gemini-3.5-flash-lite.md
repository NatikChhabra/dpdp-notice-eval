# Judge validation on real notices: gemini-3.5-flash-lite (20 notices, hand-labelled)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| withdraw_consent | 20 | 0.850 | 0.625 | 0.867 | 0.929 |
| rights | 20 | 0.900 | 0.737 | 0.875 | 1.000 |
| nomination | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| children | 9 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 209 | 0.976 | 0.952 | 0.959 | 0.989 |

## Disagreements

| notice | check | label | judge |
|---|---|---|---|
| gemini-3.5-flash-lite/pathshala/dpdp | withdraw_consent | pass | fail |
| gemini-3.5-flash-lite/pathshala/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/khelo/dpdp | withdraw_consent | fail | pass |
| gemini-3.5-flash-lite/safar/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/library/dpdp_open | withdraw_consent | pass | fail |
