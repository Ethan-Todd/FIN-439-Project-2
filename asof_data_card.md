# FRED/ALFRED As-Of Validation and Data Card

## Required October 5, 2026 check

The `asof_app.py` downloads produced the following values as known on October 5, 2026:

| Series | Last date known then | Value |
|---|---|---:|
| BAA | September 2026 | 6.47 |
| FEDFUNDS | September 2026 | 3.75 |
| DGS10 | October 2, 2026 | 5.28 |
| MORTGAGE30US | October 1, 2026 | 7.28 |

All four values match the published check.

## PAYEMS vintage probe

With `PAYEMS` selected and the as-of date set to January 15, 2025, the last observation known then is December 2024 at **159,536 thousand jobs**. Today's download reports December 2024 at **158,316 thousand jobs**, and the app counts **59 revised shared dates** from January 2020 onward. The nonzero revision count confirms that the app compares ALFRED's historical vintage with today's FRED data rather than downloading today's data twice.

## My series data card: DGS3MO

| Field | Record |
|---|---|
| Series | [DGS3MO — Market Yield on U.S. Treasury Securities at 3-Month Constant Maturity, Quoted on an Investment Basis](https://fred.stlouisfed.org/series/DGS3MO) |
| Source | FRED and ALFRED, Federal Reserve Bank of St. Louis; underlying source: Board of Governors of the Federal Reserve System (US) |
| What it measures | The market yield on a 3-month constant-maturity U.S. Treasury security, quoted on an investment basis |
| Units and frequency | Percent, not seasonally adjusted; daily on business days |
| Publication lag observed | As of October 31, 2026, the latest available observation was October 29 at 4.18%. The October 30 observation, 4.16%, appeared in FRED's November 2 update. This test therefore shows roughly a one-business-day reporting lag, extended by the weekend. |
| Revision behavior observed | Zero shared dates changed between the October 31 vintage and the November 3 download. This daily market-rate test shows no revisions in the tested interval; it does not claim that revision is impossible. |
| Download date | November 3, 2026 |

### Three values checked against FRED

| Date measured | DGS3MO value |
|---|---:|
| October 28, 2026 | 4.18% |
| October 29, 2026 | 4.18% |
| October 30, 2026 | 4.16% |

## Point-in-time result

On October 31, the October 30 value had not yet been published: the app reports one value in today's data after the last date known then and zero revised shared dates. On November 3, the latest known observation and today's latest observation are both October 30 at 4.16%, with zero later values and zero revisions. The value that vanished under the earlier vintage was not yet published; it was not removed because of a revision.

## Project 2 data-gate call

**Admit DGS3MO:** it is a daily market rate with approximately a one-business-day publication lag and zero revisions in the tested comparison. Use only observations available by each decision date; quarantine it if later evidence shows meaningful revisions, a longer publication delay, or a definition that no longer matches the Treasury-bill sleeve.

## Fresh-eyes challenge and response

**Challenge received from Mark Beatty on November 3, 2026:** “For your write-up is whether the yield you cite was already public when you made the decision. Your screenshot shows the historical trend, but you’ll need the decision date and cutoff to verify the exact value you can use.”

**Decision and evidence:** Accept. The Project 2 cutoff tested here is October 31, 2026. The ALFRED vintage dated October 31 shows that the latest knowable DGS3MO observation was October 29 at **4.18%**. Today's FRED data also contains October 30 at **4.16%**, but the FRED page reports that update on November 2, so the October 30 value was not admissible for an October 31 decision. A screenshot of today's historical chart is therefore insufficient by itself; the model must use the ALFRED vintage for each decision date.
