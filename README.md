# FIN 439 Project 2

This repository contains the Project 2 mandate, portfolio, point-in-time data, and SEC business-quality exercises. The programs are learning demonstrations built with AI assistance and are not investment advice.

## Contents

- `mandate.py` — checks candidate portfolios against the Meridian Foundation's measurable mandate rules.
- `meridian_foundation_mandate_sort.md` — classifies the Meridian statements and records the policy interpretation.
- `portfolio.py` — reusable return, volatility, covariance, portfolio-search, and price-CSV functions.
- `app.py` — Streamlit interface for the portfolio engine.
- `prices.csv` and `price_sources/` — Project 2 fund-price dataset and retained source downloads.
- `project_2_mandate.md` — client mandate, portfolio results, sensitivity interpretation, and provisional call.
- `asof.py` — known-answer provenance gate for publication dates and revisions.
- `asof_app.py` — FRED/ALFRED current-versus-vintage Streamlit application.
- `asof_data_card.md` — source, lag, revision, hand-check, partner feedback, and admission decision.
- `sec-buffett-quality/` — Codex skill, SEC EDGAR script, Streamlit app, memos, and validation evidence.
- `sec_buffett_request.md` — the student-written request used for the SEC/Buffett exercise.

## Setup and commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python mandate.py
python portfolio.py
streamlit run app.py

python asof.py
streamlit run asof_app.py

python sec-buffett-quality/scripts/sec_facts.py COST \
  --name "YOUR NAME" --email "YOUR EMAIL" \
  --output-dir sec-buffett-quality/outputs
streamlit run sec-buffett-quality/app.py
python sec-buffett-quality/scripts/validate_known_answer.py \
  --outputs sec-buffett-quality/outputs
```

The SEC command requires a truthful name and email in its User-Agent. The Buffett-style analysis evaluates business quality from SEC 10-K facts and intentionally uses no share-price data.
