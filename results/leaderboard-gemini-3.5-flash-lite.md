## Leaderboard (judge: `gemini-3.5-flash-lite`)

Score = share of applicable checks passed (10, or 11 if the business has users under 18). 95% CI from a bootstrap over businesses. Fully compliant = passes every check. Columns on the right are pass rates per check.

### Core set: 12 businesses, every model

**Prompt: plain request (no law named)**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.1-flash-lite` | 12 | **48%** | 46%–50% | 0% | 100% | 100% | 8% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.5-flash-lite` | 12 | **47%** | 44%–49% | 0% | 100% | 100% | 0% | 0% | 0% | 83% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-26b-a4b-it` | 10 | **46%** | 43%–49% | 0% | 100% | 90% | 0% | 0% | 0% | 90% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-31b-it` | 11 | **44%** | 41%–48% | 0% | 100% | 91% | 0% | 0% | 0% | 73% | 0% | 100% | 0% | 100% | 0% |

**Prompt: request names the DPDP Act and Rules**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemma-4-26b-a4b-it` | 11 | **50%** | 47%–53% | 0% | 100% | 100% | 9% | 9% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.5-flash-lite` | 12 | **50%** | 48%–52% | 0% | 100% | 100% | 17% | 0% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-31b-it` | 10 | **49%** | 46%–52% | 0% | 100% | 100% | 10% | 0% | 0% | 90% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.1-flash-lite` | 12 | **47%** | 45%–49% | 0% | 100% | 100% | 0% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |

### Full set: 24 businesses (models with enough free quota)

**Prompt: plain request (no law named)**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.1-flash-lite` | 24 | **49%** | 47%–50% | 0% | 100% | 100% | 4% | 0% | 0% | 96% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.5-flash-lite` | 24 | **47%** | 45%–49% | 0% | 100% | 96% | 0% | 0% | 0% | 88% | 0% | 100% | 0% | 100% | 0% |

**Prompt: request names the DPDP Act and Rules**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.5-flash-lite` | 24 | **50%** | 48%–52% | 0% | 100% | 100% | 12% | 4% | 0% | 96% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.1-flash-lite` | 24 | **48%** | 46%–50% | 0% | 100% | 96% | 4% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |
