# Judge validation: gemini-3.5-flash-lite on dev (20/20 notices)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| withdraw_consent | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| rights | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| nomination | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 20 | 0.900 | 0.800 | 1.000 | 0.800 |
| children | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 205 | 0.990 | 0.980 | 1.000 | 0.977 |

Passes whose quoted evidence was not found in the notice: 12 of 119.

## Disagreements

| notice | check | truth | judge | variant |
|---|---|---|---|---|
| bima-1 | no_foreign_law | fail | pass | good |
| fitmitra-1 | no_foreign_law | fail | pass | good |
