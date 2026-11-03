# Project 2 Client Mandate

## Client and purpose

The clients are a middle-aged couple investing for retirement in approximately 15 years. They care primarily about protecting their savings but still need long-term growth.

## Objective

Build the lowest-volatility portfolio whose estimated annual return is at least **5.0%**. The 5.0% figure is an expected-return estimate, not a promised result.

## Hard constraint

At least **10%** of the portfolio must be invested in a reserve-eligible Treasury-bill or short-term U.S. government fund.

## Permitted investments

The Project 2 investable universe contains four diversified, long-only public funds:

| Ticker | Portfolio role | Reserve-eligible? |
|---|---|---|
| SGOV | Treasury bills and short-term reserve sleeve | Yes |
| IEF | Intermediate U.S. Treasury bonds | No |
| LQD | Investment-grade corporate bonds | No |
| VOO | S&P 500 equity exposure | No |

SGOV is the only fund that counts toward the 10% reserve minimum.

## Prohibited investments

- Borrowing or leverage
- Short sales
- Leveraged or inverse funds
- Individual company securities
- Cryptocurrency
- Illiquid private investments

## Risk and implementation policy

The portfolio prioritizes lower expected volatility and capital preservation subject to the 5.0% return target and 10% reserve requirement. It may still lose value, and “safety” does not mean protection from every market loss. Return, volatility, and correlation will be estimated from five years of monthly adjusted prices. The portfolio will be reviewed and rebalanced annually.

## Decision rule

Among all long-only portfolios tested in five-percentage-point weight increments, choose the portfolio with the lowest estimated volatility that:

1. has an estimated annual return of at least 5.0%; and
2. holds at least 10% in assets designated reserve-eligible.

If no tested mix satisfies both conditions, report **no mix meets the objective**. Do not lower the objective merely to produce an answer.

## Important challenge

Even a 5.0% expected-return target may require meaningful exposure to equities or longer-duration bonds. The all-month and last-36-month results will show whether the mandate is feasible and how sensitive the recommended mix is to the estimation window.

## Price data and verification

The saved `prices.csv` uses Yahoo Finance monthly adjusted-close observations for [SGOV](https://finance.yahoo.com/quote/SGOV/history/), [IEF](https://finance.yahoo.com/quote/IEF/history/), [LQD](https://finance.yahoo.com/quote/LQD/history/), and [VOO](https://finance.yahoo.com/quote/VOO/history/). It contains 61 aligned monthly prices from September 1, 2021 through September 1, 2026, ordered oldest first, which produce 60 monthly returns. Yahoo's adjusted-close field was used so distributions and splits are reflected in the return series.

Verification performed October 22, 2026: every CSV date matched a date in each of the four saved Yahoo responses, and every price matched the corresponding Yahoo adjusted close within the six-decimal rounding used in the CSV. The largest absolute rounding difference was 0.0000004980. The source responses are retained in `price_sources/`; the SHA-256 hash of `prices.csv` is `600b080f99353ef49334eeb0a25af10586b89659692c4ee7a08de420fbbac961`.

This verification establishes that the saved file accurately transcribes the downloaded Yahoo observations. It does not make historical sample returns reliable forecasts of future returns.

## Portfolio results from the saved engine

The engine estimates annual return as the arithmetic mean monthly return multiplied by 12, annual volatility as monthly sample standard deviation multiplied by the square root of 12, and correlations from the same monthly returns. It searches long-only weights in five-percentage-point increments while holding the 5.0% objective and 10% SGOV minimum fixed.

| Estimation window | SGOV | IEF | LQD | VOO | Expected return | Volatility | Reserve-eligible |
|---|---:|---:|---:|---:|---:|---:|---:|
| All 60 monthly returns | 85.00% | 0.00% | 0.00% | 15.00% | 5.28% | 2.45% | 85.00% |
| Last 36 monthly returns | 95.00% | 0.00% | 0.00% | 5.00% | 5.29% | 0.69% | 95.00% |

Both tested windows produce a qualifying mix. The largest allocation change is tied at 10.0 percentage points: SGOV rises from 85% to 95%, while VOO falls from 15% to 5%. The app's largest-change box reads **VOO: −10.0 percentage points**. This large change comes from the last-36-month estimates—particularly VOO's higher historical annualized return—not from a change to the client's mandate, and it shows that the answer is sensitive to the estimation period.

## Provisional allocation call

**Pilot, not adopt:** use the all-month mix of 85% SGOV and 15% VOO as the Project 2 starting allocation, because it meets the 5.0% estimated-return objective and the 10% reserve minimum with the lowest modeled volatility on that sample. Adopt it only if a refreshed estimate or reasonable alternative estimation window does not move either allocation by more than five percentage points; the last-36-month test currently fails that condition because it changes both SGOV and VOO by 10 points.

**Challenge tested:** the mix may depend too heavily on the selected historical window. **Response:** changing from all 60 monthly returns to the last 36 changes the mix from 85% SGOV / 15% VOO to 95% SGOV / 5% VOO, so the challenge is supported and the result should remain a pilot rather than a final adopted allocation.
