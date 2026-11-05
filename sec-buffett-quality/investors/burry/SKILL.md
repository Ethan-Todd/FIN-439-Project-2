---
name: sec-burry-quality
description: Write a Burry-style cash-conversion and balance-sheet business-quality memo using only the shared five-year SEC panel report. Use inside the SEC investor-quality panel; do not fetch separate data or discuss stock price.
---

# SEC Burry Quality

Use only numbers printed by `scripts/sec_facts.py`.

Write `outputs/TICKER_burry_memo.md` with one bold `Verdict:` line and a short explanation of these coded checks:

- operating cash flow was at least net income in every year;
- latest-year liabilities were no more than twice equity.

Choose **Own the business**, **Watch it**, or **Pass** as a model judgment. Preserve `not known` when a required fact is missing. Judge business quality only, use no prices, do not invent distress or mispricing claims, and do not imply Michael Burry reviewed the company.

