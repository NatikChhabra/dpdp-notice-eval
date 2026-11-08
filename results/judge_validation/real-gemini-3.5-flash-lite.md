# Judge validation on real notices: gemini-3.5-flash-lite (23 notices, hand-labelled)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| withdraw_consent | 23 | 0.826 | 0.553 | 0.833 | 0.938 |
| rights | 23 | 0.826 | 0.589 | 0.875 | 0.875 |
| nomination | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 23 | 1.000 | 1.000 | 1.000 | 1.000 |
| children | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 240 | 0.967 | 0.933 | 0.955 | 0.972 |

## Disagreements

| notice | check | label | judge |
|---|---|---|---|
| gemini-3.5-flash-lite/pathshala/dpdp | withdraw_consent | pass | fail |
| gemini-3.5-flash-lite/pathshala/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/khelo/dpdp | withdraw_consent | fail | pass |
| gemini-3.5-flash-lite/safar/dpdp | rights | pass | fail |
| gemini-3.5-flash-lite/library/dpdp_open | withdraw_consent | pass | fail |
| gemma-4-31b-it/pathshala/dpdp_open | rights | fail | pass |
| gemma-4-31b-it/rasoi/dpdp_open | withdraw_consent | pass | fail |
| gemma-4-31b-it/gym/dpdp_open | rights | fail | pass |
