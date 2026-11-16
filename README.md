OpenAI Codex assisted with the Project 2 audit, implementation, tests, and draft documentation. The student must review and take ownership of the final analysis and investment decision; that human confirmation is pending.

This is educational analysis, not investment advice.

# FIN 439 Project 2 — portfolio review

**Status: pilot only, not submission-ready.** Human Locked Changed-Input evidence, final student review, videos/transcripts, and submission/access checks remain incomplete. The supplied rubric yields a provisional local-package estimate of 230.25/300; see [category evidence and gaps](docs/rubric-status.md). This is not an instructor grade or a completed-submission claim.

The working mandate is [project_2_mandate.md](project_2_mandate.md): minimize estimated volatility on a five-percentage-point grid while meeting a 5% estimated annual return and at least 10% SGOV. The universe is SGOV, IEF, LQD, VOO, fully invested and long-only. Meridian and SEC exercises are separate supporting coursework; they do not replace this mandate or its evidence.

## Clean start

Use **CPython 3.14** (tested 3.14.7). The system Python 3.9 is unsuitable. Install Python 3.14 if `python3.14 --version` is unavailable. Run these commands from the repository root:

```bash
python3.14 --version
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --no-cache-dir -r requirements-lock.txt
python -m pip check
python -m unittest discover -s tests -v
python analysis.py --write
python -m streamlit run app.py --server.headless true --browser.gatherUsageStats false
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). Stop the server with Ctrl+C. Installation needs internet access; the main app, routine tests, and saved analysis run offline. The lock file records the tested environment; `requirements.txt` identifies the two direct dependencies. No credentials or `.env` are needed for the main app.

## Operate the app

1. The app loads bundled prices automatically; no upload or policy-setting changes are needed.
2. Inspect the candidate, equal-weight baseline, and frozen full-sample inverse-volatility baseline. The separate fixed policy benchmark is 100% SGOV, your current proposed selection for a capital-preservation comparison; it is not an original Lab 13 requirement.
3. Change the window, return shift, annual cost deduction, return target, or SGOV minimum. These are scenarios, not amendments to the working mandate. Baseline weights stay fixed when controls change.
4. Read both the working-mandate and scenario verdicts, and the listed violated rules. The 100% SGOV policy-benchmark weights also stay fixed.
5. Read stopping conditions and the DGS3MO monitor. No feasible mix means halt; the window-stability failure means do not adopt.

Replacement data must contain exactly 61 consecutive monthly price observations and the four ticker columns. The date column is first; prices must be finite and positive. Use adjusted closes. The loader checks structure and frequency, but cannot certify an uploaded file's provider or adjustment method.

## Reproduce and inspect evidence

- [Visible output](outputs/analysis.md) and [machine-readable analysis](outputs/analysis.json).
- [Decision memo](docs/decision-memo.md), [validation and AI use](docs/validation-and-ai-use.md), [signal data card](docs/signal-data-card.md).
- [Routine test results](outputs/test-results.txt), [verification record](outputs/verification.json), and [environment lock](requirements-lock.txt).
- [Submission manifest](submission-manifest.csv); publication status and remaining access checks are recorded in the manifest.
- `python portfolio.py` prints the same routine analysis as JSON.

`python verify.py` runs the finance/app tests, dependency and SEC checks, deterministic regeneration, and a temporary localhost server health check, saving evidence under `outputs/`. It requires permission to bind localhost.

`python analysis.py --write` regenerates deterministic analysis files. It does not execute the designated human locked experiment. Test runs are routine AI-assisted validation and must not be relabeled as that evidence.

To deliberately obtain a new archive of the *same requested historical date*, with internet access:

```bash
python fetch_signal.py --cutoff 2026-10-31
python analysis.py --write
```

This refresh changes source retrieval metadata and may change revision comparisons. Preserve the submitted source archive before refreshing. A retrospective ALFRED vintage is not proof of a contemporaneous download or intraday availability. The signal is an October 31 demonstration, not a live November recommendation.

## Interpretation and missing choices

Returns are arithmetic historical estimates, not realized portfolio performance. Volatility annualization assumes monthly sampling and does not establish a loss bound. Annual rebalancing is a mandate policy but **is not simulated**. Costs are explicit hypothetical annual return deductions, not estimates of turnover, taxes, spreads, or trade execution. Adjusted-price data already reflect fund distributions/adjustments; additional costs should not double count fund expenses.

The mandate does not specify a benchmark, numerical volatility ceiling, cost budget, or quantitative signal policy. The user now selects 100% SGOV as the proposed fixed benchmark. At zero additional cost its full-sample estimated return is 3.7151%, so it fails the 5% objective despite satisfying the reserve constraint. No numerical risk ceiling is invented. Cost scenarios and the reserve-yield review rule are disclosed implementation choices, not assertions about Lab 13. The student must approve final policy decisions.

## Human-only work

See [human evidence checklist](docs/human-evidence.md). Close AI tools before selecting and writing the designated prediction; commit and push that original prediction before running its experiment. This repository does not supply that prediction or claim it happened. Videos, transcripts, feedback, and historical records must be genuine.

## Separate exercises

```bash
python mandate.py
python asof.py
python sec-buffett-quality/scripts/validate_known_answer.py --outputs sec-buffett-quality/outputs
python -m streamlit run asof_app.py
python -m streamlit run sec-buffett-quality/app.py
```

The FRED comparison app needs internet. The SEC panel can display saved outputs offline. Its refresh requires truthful SEC User-Agent contact information; use the UI without committing that information. Its number-membership audit is not a semantic fact check. These exercises are not Project 2 policy benchmarks or historical trading backtests.
