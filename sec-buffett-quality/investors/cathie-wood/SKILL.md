---
name: sec-cathie-wood-quality
description: Write a Cathie Wood-style growth and R&D business-quality memo using only the shared five-year SEC panel report. Use inside the SEC investor-quality panel; do not fetch separate data or discuss stock price.
---

# SEC Cathie Wood Quality

Use only numbers printed by `scripts/sec_facts.py`.

Write `outputs/TICKER_wood_memo.md` with one bold `Verdict:` line and a short explanation of these coded checks:

- revenue grew at least 15% annually from the first year to the last, using `(last revenue / first revenue)^(1/4) - 1`;
- R&D was at least 5% of revenue in the latest year.

Choose **Own the business**, **Watch it**, or **Pass** as a model judgment. Preserve `not known` when a required fact is missing. Judge business quality only, use no prices, do not invent claims about innovation, and do not imply Cathie Wood reviewed the company.
