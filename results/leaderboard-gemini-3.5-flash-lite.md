## Leaderboard (judge: `gemini-3.5-flash-lite`)

Score = share of applicable checks passed (10, or 11 if the business has users under 18). 95% CI from a bootstrap over businesses. Fully compliant = passes every check. Columns on the right are pass rates per check.

### Core set: 12 businesses, every model

**Prompt: plain request (no law named)**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.1-flash-lite` | 12 | **48%** | 46%–50% | 0% | 100% | 100% | 8% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.5-flash-lite` | 12 | **47%** | 44%–49% | 0% | 100% | 100% | 0% | 0% | 0% | 83% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-26b-a4b-it` | 12 | **46%** | 43%–48% | 0% | 100% | 92% | 0% | 0% | 0% | 83% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-31b-it` | 12 | **45%** | 42%–48% | 0% | 100% | 92% | 0% | 0% | 0% | 75% | 0% | 100% | 0% | 100% | 0% |

**Prompt: request names the DPDP Act and Rules**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.5-flash-lite` | 12 | **65%** | 59%–70% | 0% | 100% | 100% | 58% | 75% | 8% | 100% | 17% | 100% | 0% | 100% | 40% |
| `gemma-4-31b-it` | 12 | **61%** | 58%–63% | 0% | 100% | 100% | 50% | 83% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.1-flash-lite` | 12 | **60%** | 54%–65% | 0% | 100% | 100% | 58% | 67% | 8% | 92% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-26b-a4b-it` | 12 | **56%** | 52%–60% | 0% | 100% | 100% | 0% | 58% | 0% | 100% | 8% | 100% | 0% | 100% | 40% |

**Prompt: names the law and adds 'use only the facts below' (comparison)**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemma-4-26b-a4b-it` | 12 | **50%** | 47%–53% | 0% | 100% | 100% | 8% | 8% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.5-flash-lite` | 12 | **50%** | 48%–52% | 0% | 100% | 100% | 17% | 0% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-31b-it` | 12 | **50%** | 47%–52% | 0% | 100% | 100% | 25% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.1-flash-lite` | 12 | **47%** | 45%–49% | 0% | 100% | 100% | 0% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |

### Full set: 24 businesses (models with enough free quota)

**Prompt: plain request (no law named)**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.1-flash-lite` | 24 | **49%** | 47%–50% | 0% | 100% | 100% | 4% | 0% | 0% | 96% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.5-flash-lite` | 24 | **47%** | 45%–49% | 0% | 100% | 96% | 0% | 0% | 0% | 88% | 0% | 100% | 0% | 100% | 0% |
| `gemma-4-26b-a4b-it` | 24 | **47%** | 45%–49% | 0% | 100% | 96% | 0% | 0% | 0% | 88% | 0% | 100% | 0% | 100% | 0% |

**Prompt: names the law and adds 'use only the facts below' (comparison)**

| model | notices | score | 95% CI | fully compliant | data | purpose | withdraw | rights | nominate | grievance | Board | contact | language | no GDPR | children |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemma-4-26b-a4b-it` | 24 | **51%** | 49%–53% | 0% | 100% | 100% | 8% | 8% | 0% | 100% | 4% | 100% | 0% | 100% | 0% |
| `gemma-4-31b-it` | 24 | **51%** | 49%–53% | 0% | 100% | 100% | 21% | 0% | 0% | 96% | 0% | 100% | 0% | 100% | 14% |
| `gemini-3.5-flash-lite` | 24 | **50%** | 48%–52% | 0% | 100% | 100% | 12% | 4% | 0% | 96% | 0% | 100% | 0% | 100% | 0% |
| `gemini-3.1-flash-lite` | 24 | **48%** | 46%–50% | 0% | 100% | 96% | 4% | 0% | 0% | 92% | 0% | 100% | 0% | 100% | 0% |
