# Visible Project 2 executed output

Routine validation; not Locked Changed-Input evidence

**Decision: PILOT ONLY / NOT APPROVED FOR ADOPTION**

Policy: 5% estimated return; at least 10% SGOV; long-only, fully invested SGOV/IEF/LQD/VOO; 5-point search grid.

Data period labels: 2021-09-01 through 2026-09-01; 60 returns. Price SHA-256: `600b080f99353ef49334eeb0a25af10586b89659692c4ee7a08de420fbbac961`. Signal cutoff: 2026-10-31.

## Comparisons (historical estimates, not realized performance)

| Portfolio | SGOV / IEF / LQD / VOO | Net return | Volatility | Verdict / violations |
|---|---|---:|---:|---|
| Equal weight | 25.00% / 25.00% / 25.00% / 25.00% | 3.8242% | 7.4726% | FAIL: net estimated return below 5.00% |
| Inverse volatility (frozen full sample) | 87.11% / 5.68% / 4.44% / 2.77% | 3.4920% | 1.3427% | FAIL: net estimated return below 5.00% |
| Policy benchmark | 100.00% / 0.00% / 0.00% / 0.00% | 3.7151% | 0.4989% | FAIL: net estimated return below 5.00% |
| Constrained candidate | 85.00% / 0.00% / 0.00% / 15.00% | 5.2843% | 2.4519% | PASS: all coded rules |

## Routine sensitivity

| Scenario | Selected SGOV / IEF / LQD / VOO | Net return | Volatility | Largest change | Original allocation verdict |
|---|---|---:|---:|---:|---|
| Reference | 85% / 0% / 0% / 15% | 5.2843% | 2.4519% | 0.0% | PASS |
| All expected returns -1 percentage point | 75% / 0% / 0% / 25% | 5.3304% | 3.9919% | 10.0% | FAIL |
| All expected returns +1 percentage point | 95% / 0% / 0% / 5% | 5.2381% | 0.9765% | 10.0% | PASS |
| VOO volatility +25% | 85% / 0% / 0% / 15% | 5.2843% | 3.0324% | 0.0% | PASS |
| Last 36 returns | 95% / 0% / 0% / 5% | 5.2926% | 0.6881% | 10.0% | PASS |
| Annual cost 25 bp | 85% / 0% / 0% / 15% | 5.0343% | 2.4519% | 0.0% | PASS |
| Annual cost 100 bp | 75% / 0% / 0% / 25% | 5.3304% | 3.9919% | 10.0% | FAIL |
| SGOV minimum 25% | 85% / 0% / 0% / 15% | 5.2843% | 2.4519% | 0.0% | PASS |
| SGOV minimum 100% | INFEASIBLE | — | — | — | FAIL |
| Return target 6% | 75% / 0% / 0% / 25% | 6.3304% | 3.9919% | 10.0% | FAIL |

## Point-in-time monitor

```json
{
  "yield_percent": 4.18,
  "sgov_historical_estimate": 0.03715074894092623,
  "gap_percentage_points": 0.4649251059073767,
  "status": "NO YIELD SHORTFALL FLAG",
  "action": "Continue monitoring; this flag does not authorize adoption or establish expected SGOV return.",
  "cutoff": "2026-10-31",
  "observation_date": "2026-10-29",
  "retrieved_at_utc": "2026-11-16T22:14:58.746257+00:00",
  "evidence": "signal_sources/2026-10-31/metadata.json",
  "revised_shared_dates": 0,
  "later_observations": 10,
  "availability": "Retrospectively retrieved ALFRED date vintage; not contemporaneous capture or intraday proof."
}
```

## Adoption blocks

- Alternative-window change exceeds the mandate five-percentage-point adoption limit

## Limitations

- Annual rebalancing is NOT simulated. No realized-performance backtest.
- Costs are deterministic annual portfolio-level deductions, not estimated trading costs.
- The 5% objective is tested after the stated cost deduction as a conservative sensitivity convention; the mandate did not specify costs.
- Stress envelope is not a confidence interval, suitable allocation range, or trading permission.
- Human evidence, approval, and submission materials remain incomplete.
