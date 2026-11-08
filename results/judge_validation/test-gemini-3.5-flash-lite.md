# Judge validation: gemini-3.5-flash-lite on test (40/40 notices)

| check | n | accuracy | kappa | fail precision | fail recall |
|---|---|---|---|---|---|
| data_itemised | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| purpose_specific | 40 | 0.975 | 0.947 | 1.000 | 0.938 |
| withdraw_consent | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| rights | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| nomination | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| grievance | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| board_complaint | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| contact | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| language | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| no_foreign_law | 40 | 0.900 | 0.801 | 1.000 | 0.810 |
| children | 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| ALL | 415 | 0.988 | 0.975 | 1.000 | 0.972 |

Passes whose quoted evidence was not found in the notice: 0 of 217 (no quote is needed for a "no foreign law" pass).

## Disagreements

| notice | check | truth | judge | variant |
|---|---|---|---|---|
| udhaar-1 | no_foreign_law | fail | pass | good |
| khelo-1 | purpose_specific | fail | pass | catchall |
| khelo-3 | no_foreign_law | fail | pass | good |
| naukri-4 | no_foreign_law | fail | pass | good |
| bachpan-2 | no_foreign_law | fail | pass | good |
