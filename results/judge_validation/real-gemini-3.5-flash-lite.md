# Judge validation on real notices: gemini-3.5-flash-lite (16 notices, hand-labelled)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| withdraw_consent | 16 | 0.875 | 0.000 | 1.000 | 0.875 |
| rights | 16 | 0.875 | 0.000 | 0.875 | 1.000 |
| nomination | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 16 | 1.000 | 1.000 | 1.000 | 1.000 |
| children | 7 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 167 | 0.976 | 0.952 | 0.976 | 0.976 |

## Disagreements

| notice | check | label | judge |
|---|---|---|---|
| gemini-3.5-flash-lite/pathshala/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/khelo/dpdp | withdraw_consent | fail | pass |
| gemini-3.5-flash-lite/safar/dpdp | withdraw_consent | fail | pass |
| gemini-3.5-flash-lite/safar/dpdp | rights | pass | fail |
