# Validation and AI use — Project 2

## Scope, version, and evidence boundary

Routine AI-assisted validation was performed November 16, 2026. It remains separate from the designated human-run November 17 experiment, whose completed evidence bundle is linked below. Base Git commit was `ab163ab`; this implementation is an interim package, not the final submission freeze. The manifest records its published snapshot separately from missing human evidence. [Verification record](../outputs/verification.json) records actual execution, environment, and source hashes. [Executed report](../outputs/analysis.md) and [machine-readable values](../outputs/analysis.json) are reproducible offline.

The user designated `project_2_mandate.md` as the working mandate. No original submitted Lab 13 document was independently supplied. The user has now supplied the analytic 300-point rubric; see [category assessment](rubric-status.md). The user’s current proposed fixed benchmark is 100% SGOV, chosen for a capital-preservation comparison; this is not an original Lab 13 requirement. Final cost assumption, student ownership confirmation, and final allocation-range approval remain pending. No numerical risk ceiling has been invented.

## Data and convention ledger

| Input | Source / cutoff | Treatment | Limit |
|---|---|---|---|
| Monthly prices | `prices.csv`, retained Yahoo JSONs; labels September 2021–September 2026 | 61 prices / 60 returns; distributions and splits via adjusted close; sample covariance | Labels are not availability timestamps; no historical price-vintage safety claim |
| Return and volatility | Arithmetic monthly mean ×12; sample standard deviation ×√12 | Same aligned returns for covariance; exhaustive five-point grid | Historical estimates, not realized performance; no serial-correlation adjustment |
| Constraints | Working mandate | Long-only, fully invested, permitted four funds, ≥10% SGOV, ≥5% estimated return | No arbitrary issuer/turnover/volatility limit imported from Meridian |
| Costs | 0, 25, 100 bp annual scenario deductions | Subtract from estimated return; optimize to meet target after deduction | Not a trading-cost estimate or rebalancing simulation; avoid double counting embedded fund expenses |
| Signal | ALFRED date vintage 2026-10-31, retrieved 2026-11-16 | Retain source CSV, URL, timestamp, SHA-256; monitor only | Retrospective date vintage, not contemporaneous capture or intraday proof |
| Baselines | Equal weights; inverse sample volatility normalized and frozen | Same scenario estimates/costs applied to fixed weights | Separate user-selected 100% SGOV benchmark; 3.7151% estimated return fails 5% objective |

## Validation register

| Claim / risk | Test | Result / disposition | Evidence |
|---|---|---|---|
| Risk/return arithmetic | Analytic two-asset known answer; direct NumPy return-series calculation and independent grid enumeration | Reference 85/15, return 5.2843%, volatility 2.4519%; independently matches | `tests/test_finance.py` |
| Data transcription | Recompute raw price hash; compare every ticker/date to saved adjusted-close JSON | Matches original SHA-256; all differences ≤0.0000005 | Same tests; `price_sources/` |
| Window dependence | Full sample versus exactly 36 returns | 95/5 alternative; 10-point move; adoption condition fails | `outputs/analysis.md` |
| Estimate sensitivity | Shift every estimated return ±1 percentage point; raise VOO volatility 25% | Selected allocations span 75/25–95/5; original fails downside stress | Same report |
| Cost sensitivity | 25 and 100 bp deductions; inspect held-original and reoptimized allocations | 25 bp preserves 85/15; 100 bp selects 75/25, original fails | Same report |
| Constraint sensitivity | 25% and 100% SGOV minimum; 6% return target | 25% nonbinding; 100% infeasible; 6% selects 75/25 | Same report |
| Invalid financial inputs | Bad diagonal, indefinite/asymmetric/nonfinite matrices; negative/nonfinite/constant prices; irregular/missing months; short window; invalid weights | Rejected with clear errors; no false zero-risk output | Test results |
| Infeasible portfolio | Unattainable objective, all-SGOV restriction | `None` from engine; explicit stop in app | Finance and app tests |
| Baselines accidentally reweighted | Change app window/controls; inspect frozen comparison weights | Weights remain fixed; explicit working-mandate/scenario verdicts | `tests/test_app.py` |
| Point-in-time gate | Synthetic publication known answer; archived-date/header/checksum checks; missing source and shortfall probes | Future publications excluded; bad/missing evidence quarantined; shortfall triggers review | Tests, signal archive, data card |
| SEC supporting checks | Existing COST/JPM validator | Saved known-answer and missing-data propagation checks pass when recorded in verification | `outputs/sec-validation.txt` |
| AI report checking | Independent calculations and source transcription rather than prose agreement | Accepted formulas; qualified pilot/range; rejected adoption and unsupported historical-proof claims | This register / memo |
| Cold start | New project virtualenv, actual dependency download, pip check, tests, app launch | See recorded environment and health result; not a human stranger usability test | `outputs/verification.json` |

The stress cases are transparent engineering scenarios, not calibrated probability bounds or exhaustive robustness proof. The proposed paper range is 75–95% SGOV and complementary 25–5% VOO; not every weight in the interval has been independently approved. Failures remain visible. Annual rebalancing, turnover, taxes, and realized portfolio returns are not simulated.

## First failures and resolutions

- Audit found system Python 3.9.6 incompatible with Streamlit 1.66.0 (requires ≥3.11). Fresh environment uses CPython 3.14.7 and README requires 3.14.
- Initial sandbox package download failed DNS; authorized network retry installed dependencies successfully. Full resolved versions are in `requirements-lock.txt`.
- Full-history and bounded urllib ALFRED requests timed out. Bounded curl requests succeeded; downloader now uses curl. An intermediate Python-3.9 f-string compatibility error was fixed before successful source retrieval.
- Initial tests passed with a harmless unclosed test-file warning; file handling was corrected. Streamlit AppTest can emit its documented bare-mode `ScriptRunContext` warning; assertions inspect actual exceptions.
- The first HTTP health check failed because the sandbox prohibited binding localhost. Finance/app assertions and dependency checks passed in that run; an authorized local-server rerun is recorded separately in the verification output.
- The process's financial stability failure is **not fixed away**: the alternative-window shift exceeds five points, so adoption remains blocked.

## Named AI-use register

| Tool/model surface | Date | Material work | Independent check | Disposition / effect |
|---|---|---|---|---|
| OpenAI Codex, GPT-6 as identified by this session; exact model snapshot not exposed | 2026-11-16 | Audit; portfolio/app changes; validation code; draft docs | Analytic answer, separate NumPy grid/return calculations, retained-source comparison, fresh install, app tests | Accept tested calculations; qualify estimates and signal; pilot only |
| Same session | 2026-11-16 | Proposed signal monitor and scenario ranges | Inspect archived vintage; distinguish yield from total return; report actual scenario results | Proposed implementation policy, pending student/client review; no invented Lab 13 requirement |
| OpenAI Codex; same exposed model surface | 2026-11-17 | Post-run evidence preservation, arithmetic/hash checks, separate reconciliation | Original result retained byte-for-byte; all locked hashes matched precommit | Clarified relative changes; qualified untested loss range; no rerun or rewritten human reflection |
| Earlier repository AI use | Earlier dates/tools/versions not independently established | Existing portfolio, FRED, SEC exercises and memos | Existing source/probe files plus current tests | Historical AI-use metadata incomplete; student must supply only information actually available |

The SEC app's number-membership check can detect an unprinted number, but cannot verify metric/year/company association or a prose claim. Its previously documented fresh-browser comparison remains pending; this revision did not fabricate it. Passing an AI-output check is not proof of all statements or human authorship.

## Locked Changed-Input Record — evidence bundle completed

See the [completed record and reconciliation](locked-changed-input-reconciliation-2.md), [verbatim student reflection](locked-changed-input-reflection-2.md), and [unchanged execution result](../outputs/locked-allocation-result-2.json). The pre-run snapshot `878fee9` includes the user's verbatim prediction and expected decision effect and was pushed before the recorded November 17 execution. All ten input/code hashes in the result match that commit. [Integrity checks](../outputs/locked-record-integrity-2.json) record the original result hash and chronology checks.

The user self-attested AI-off authorship/unrun status before execution; the execution helper records an AI-off attestation. Those conditions were not independently observed. The agent did not run or rerun the designated experiment. Post-run arithmetic checking and reconciliation are explicitly AI-assisted. The earlier 75/25 proposal remains preserved with its overlap disclosure.

Both output directions matched the prediction; the student's actual decision is to retain 85/15 as the reference paper allocation. The relative volatility increase was 3.20 times the relative return increase. The student's 25–35% down-year loss illustration is not validated by this experiment; the simple return/volatility quotient is not a Sharpe ratio. Passing feasibility does not establish suitability or remove the window-stability adoption block. The original JSON's empty human-comment fields are preserved; the companion documents supply the later reflection and reconciliation.

## Remaining submission and review limitations

The student must review/own the final decision and opening statements, provide genuine videos/transcripts, freeze/push files, and verify access/submission. The manifest marks missing evidence honestly. The earlier 230.25/300 rubric estimate predates this completed evidence bundle and needs reassessment; the videos and other submission checks remain outstanding. This is not a submission-ready package.
