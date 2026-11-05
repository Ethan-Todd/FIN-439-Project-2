---
name: sec-buffett-quality
description: Analyze an operating company's five-year business quality from SEC EDGAR 10-K facts through Buffett, Cathie Wood, and Burry rule sets, write no-price memos, and display a shared-evidence investor panel in Streamlit. Use for ticker-based SEC investor-quality panels; do not use for price valuation or trading advice.
---

# SEC Investor Quality Panel

Use the bundled deterministic script for every number. Do not install FAskills, call its paid data services, fetch prices, or fill missing facts with estimates.

## Workflow

1. Obtain the user's real contact email for the SEC User-Agent. Never invent it.
2. Run:

   ```bash
   python scripts/sec_facts.py TICKER --name "USER NAME" --email "USER EMAIL" --output-dir outputs
   ```

3. Read `outputs/TICKER_script_output.txt`. Treat it as the complete numeric evidence set. If the script reports `not found` or `not known`, preserve that limitation.
4. Write `outputs/TICKER_buffett_memo.md` as a short Buffett-style business-quality memo:
   - choose exactly one verdict: **Own the business**, **Watch it**, or **Pass**;
   - discuss consistent earning power, ROE, owner earnings, and the three printed checks;
   - use only numbers printed by the script, with no arithmetic performed only in prose;
   - judge the business, not its stock price, and state that no price conclusion is made;
   - do not assert a moat, management quality, or debt safety unless the printed evidence supports the statement;
   - do not present invented quotations or imply that Warren Buffett actually reviewed the company.
5. Read `investors/cathie-wood/SKILL.md` and `investors/burry/SKILL.md`, then write their two memos from the same printed report. Do not introduce numbers from another source or calculate new memo-only numbers.
6. Run the app from the skill folder:

   ```bash
   streamlit run app.py
   ```

   Confirm the chart, facts table, investor-by-check panel, three memos, and cross-memo numeric audit all render. Any memo number absent from the script output must remain visibly flagged until corrected or removed.

## Data rules

- Sources: only `company_tickers.json` and SEC `companyfacts`; keyless requests with a named User-Agent and email.
- Filings: 10-K only; latest five fiscal-year-end dates.
- Flow facts require an approximately one-year duration; same-period duplicates use the latest filing date.
- Apply the required tag priorities exactly as implemented in `scripts/sec_facts.py`.
- Report missing facts as `not found`; report derived ratios/checks with missing inputs as `not known`.
- Treat nonpositive equity as making ROE and liabilities/equity `not known`.
- Owner earnings for this assignment are operating cash flow minus capital spending. Do not substitute a different Buffett owner-earnings formula.
- Revenue growth is `(last revenue / first revenue)^(1/4) - 1` for five annual observations.
- Use `ResearchAndDevelopmentExpense` for R&D and `Liabilities` for liabilities. Missing facts and all dependent checks remain `not known`.

The qualitative frame is adapted narrowly from the public FAskills Buffett instruction page: think like a whole-business owner and focus on durable earning power, returns on equity, cash generation, and balance-sheet caution. The assignment's SEC-only evidence and no-price boundary override every broader data or valuation request on that page.
