# My AI Request — Three-Investor SEC Panel

Extend my existing `sec-buffett-quality` skill and Streamlit app without removing any Buffett feature. Keep the Lab 18 SEC EDGAR sources, five-year 10-K selection rules, tag priorities, missing-data handling, owner-earnings formula, checks, chart, table, memo, and numeric audit.

Use one shared SEC facts dataset for all three investors. Add `Liabilities` and `ResearchAndDevelopmentExpense`, and calculate revenue growth as `(last revenue / first revenue)^(1/4) - 1`. Do not install FAskills or use its paid data. Every calculation must be performed in code; every missing input and dependent check must remain `not found` or `not known`.

Add separate Cathie Wood and Burry skill instructions. Wood's coded checks are revenue growth of at least 15% annually from the first year to the last and latest-year R&D of at least 5% of revenue. Burry's coded checks are operating cash flow of at least net income in every year and latest-year liabilities no more than twice equity. Each investor writes a short no-price memo using only numbers printed by the shared script and chooses a business-quality verdict without claiming the real investor reviewed the company.

Extend the app with an investor-by-check panel showing `pass`, `fail`, or `not known`, each memo's verdict, and all three memos side by side. Run the existing unprinted-number audit across every memo. Continue to say under the title: “Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.”

Validate the known Costco values, the existing JPM missing-capex probe, the new panel checks, the app, and all three skill folders. Use Costco as the saved demonstration and report missing R&D honestly.

## Reading used for the investor lenses

- [Cathie Wood lesson](https://www.stockeducation.com/courses/stock-education-ai-powered-investing-courses/lessons/cathie-wood/)
- [Michael Burry lesson](https://www.stockeducation.com/courses/stock-education-ai-powered-investing-courses/lessons/michael-burry/)
- [Streamlit documentation](https://docs.streamlit.io/)

