# Meridian Foundation Reserve — Mandate Sort

Case: fictional $100 million reserve. This file covers only the assigned common case.

| ID | Classification | One-line reason |
|---|---|---|
| S1 | Hard constraint | The portfolio must use a seven-year horizon and annual rebalancing, which sets the required planning and trading schedule. |
| S2 | Objective | CPI + 4% net of costs over rolling five-year periods states the reserve's desired investment outcome and measurement period. |
| S3 | Hard constraint | The reserve must fund $0.75 million quarterly and keep twelve months of payouts, or $3.0 million, in cash or daily-liquid government securities. |
| S4 | Preference | The 60% global equity and 40% U.S. investment-grade bond benchmark is a comparison standard, not an allocation requirement. |
| S5 | Hard constraint | Long-only and the prohibitions on borrowing, short sales, and derivatives directly exclude portfolios using those techniques. |
| S6 | Hard constraint | Each issuer weight must remain at or below 8%. |
| S7 | Hard constraint | Annual turnover cannot exceed 25% unless the committee grants approval. |
| S8 | Hard constraint | At least 90% of the portfolio must be redeemable within five business days. |
| S9 | Unverifiable promise | “No calendar-year loss greater than 10%” cannot be guaranteed or tested consistently until loss measurement, timing, probability, and breach treatment are defined. |
| S10 | Missing | No pilot optimization target has been selected, so there is no instruction for choosing among otherwise permitted portfolios. |

## What is permitted now?

A candidate is mandate-permitted under the checkable rules only if it has weights totaling 100%, is long-only, holds at least 3% in reserve-eligible assets, keeps at least 90% redeemable within five business days, and limits each nonexempt company issuer to 8%. S9 is not tested because it is undefined, and passing the coded rules does not prove that a portfolio is suitable.

## Investment policy statement

An investment policy statement, or IPS, is the written agreement that connects a client's purpose to the rules for managing its portfolio. It states the return objective, risk approach, time horizon, liquidity needs, permitted investments, concentration limits, governance rules, and standards for evaluating results. The IPS works by separating desired outcomes from enforceable constraints so a portfolio can first be screened for permission and then evaluated for suitability.

### S1–S10 mapped to the IPS

| Statement | IPS role |
|---|---|
| S1 | Time-horizon and rebalancing policy: seven years with annual rebalancing. |
| S2 | Return objective: CPI + 4% net of costs over rolling five-year periods. |
| S3 | Spending and liquidity constraint: fund four quarterly payouts and hold $3 million in reserve-eligible assets. |
| S4 | Benchmark and evaluation reference: 60% global equity and 40% U.S. investment-grade bonds. |
| S5 | Permitted-investment constraint: long-only with no borrowing, short sales, or derivatives. |
| S6 | Diversification constraint: no nonexempt company issuer above 8%. |
| S7 | Turnover and governance constraint: no more than 25% annually without committee approval. |
| S8 | Liquidity constraint: at least 90% redeemable within five business days. |
| S9 | Incomplete risk statement: the 10% calendar-year loss language lacks a measure and breach rule. |
| S10 | Missing decision rule: the pilot has no stated quantity to optimize. |

## Checker and probe evidence

The calculated reserve minimum is **3.0%** of the portfolio. Candidate A passes every checkable rule, Candidate B fails three rules, and Candidate C fails one rule. In the controlled probe, Candidate A's cash was changed from 2% to −2% and global equity from 60% to 64%; the weights still totaled 100%, the reserve remained 10%, and only the long-only rule failed. The original inputs were then restored and rerun.

## Attack portfolio D

| Holding | Weight |
|---|---:|
| Cash | 3% |
| Treasury 10-year note | 89% |
| Acme Corp stock | 8% |
| All other holdings | 0% |

Candidate D passes every coded rule: weights total 100%, the lowest weight is 0%, reserve-eligible assets equal 92%, all assets are redeemable within five business days, and Acme exposure is exactly 8%. I would still judge D unsuitable because its 89% Treasury-note allocation is far from the S4 benchmark and may not provide a credible path to the S2 CPI + 4% objective. This demonstrates that a checker establishes permission under defined rules, not overall client suitability.

## One question for the CIO

**Among portfolios that pass every hard constraint, should the pilot maximize the probability of meeting CPI + 4%, or minimize portfolio risk while targeting CPI + 4%?**

The answer changes the design: the first choice emphasizes assets and allocations that improve the likelihood of reaching the return objective, while the second favors a more defensive portfolio and requires the CIO to define the risk measure. Until the CIO answers, the team can screen portfolios but cannot claim that one is optimal.

## Reflection

A portfolio can pass every checkable rule and still be wrong because the rules test minimum eligibility, not whether the portfolio is likely to accomplish the client's purpose. Candidate D proves the distinction: it passes the reserve, liquidity, long-only, and issuer tests but conflicts with the benchmark and may not support the real-return objective.

The type I was least sure about was **S4**. I initially considered treating the benchmark as a constraint, but concluded it is a preference and evaluation reference because the CIO did not require the portfolio to hold exactly 60% global equities and 40% investment-grade bonds.

## GitHub checkout

Files to upload:

- `meridian_foundation_mandate_sort.md`
- `mandate.py`

Repository: <https://github.com/Ethan-Todd/HD>

After uploading, verify that both GitHub file links open before pasting them into the Lab 13 quiz. Local files do not update GitHub automatically.

## `portfolio.py` flowchart

```mermaid
flowchart TD
    A[Editable inputs: sleeves, returns, volatility, correlations, objective, reserve assets] --> B[validate_inputs]
    B --> C{Inputs valid?}
    C -- No --> D[Print clear error and stop]
    C -- Yes --> E[build_covariance_matrix]
    E --> F[Covariance = correlation × volatility × volatility]

    F --> G[build_portfolios]
    G --> H[Benchmark weights]
    G --> I[Equal weights]
    G --> J[Inverse-volatility weights]
    H --> K[portfolio_expected_return]
    I --> K
    J --> K
    H --> L[portfolio_volatility]
    I --> L
    J --> L
    H --> M[reserve_eligible_weight]
    I --> M
    J --> M
    K --> N[meets_objective]
    L --> O[print_portfolio]
    M --> O
    N --> O

    P[Optional monthly prices CSV] --> Q[estimate_from_price_csv]
    Q --> R[Check dates and prices]
    R --> S[Calculate monthly returns]
    S --> T{Use last 36 months?}
    T -- Yes --> U[Keep last 36 monthly returns]
    T -- No --> V[Keep all monthly returns]
    U --> W[Annual return = monthly mean × 12]
    V --> W
    U --> X[Annual volatility = monthly standard deviation × √12]
    V --> X
    W --> Y[Calculate correlations]
    X --> Y
    Y --> B

    F --> Z[find_lowest_risk_mix]
    Z --> AA[Generate every long-only mix in 5-point steps]
    AA --> AB{Return ≥ objective and reserve ≥ minimum?}
    AB -- No --> AC[Discard mix]
    AB -- Yes --> AD[Calculate portfolio volatility]
    AD --> AE[Keep lowest-volatility feasible mix]
    AC --> AF{More mixes?}
    AE --> AF
    AF -- Yes --> AA
    AF -- No --> AG{Any feasible mix?}
    AG -- Yes --> AH[Return weights, return, volatility, and reserve weight]
    AG -- No --> AI[Return nothing: no mix meets the objective]
```
