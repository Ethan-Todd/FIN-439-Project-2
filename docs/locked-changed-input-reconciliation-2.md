# Locked Changed-Input Record — completed evidence bundle

The student's prediction, expected decision effect, original execution output, and post-run reflection are preserved separately. This reconciliation is **AI-assisted post-run analysis**, not part of the human AI-off prediction. It does not replace or silently edit the student's words. Execution and authorship conditions remain self-attested, not independently observed.

## Evidence and chronology

| Evidence | Location / timing |
|---|---|
| Original active prediction | [Verbatim second prediction](locked-changed-input-prediction-2.md), first preserved in `885826a` |
| Expected decision effect | [Verbatim pre-run decision](locked-changed-input-decision-effect-2.md) |
| Complete pre-run snapshot | [878fee95eb32251880dc592b8801067025bcc6b7](https://github.com/Ethan-Todd/FIN-439-Project-2/commit/878fee95eb32251880dc592b8801067025bcc6b7), committed November 16, 2026 at 23:12:35 UTC; successful GitHub push was confirmed in this session before execution |
| Recorded execution | November 17, 2026 at 21:44:09.928386 UTC; execution head matches the pre-run commit |
| Original result | [Unmodified JSON](../outputs/locked-allocation-result-2.json), SHA-256 `4b1911128e4d35ac99d65c1f38ebfd98c63758d952df04e623a23d74c943eee0` |
| Student's post-run reflection and actual decision | [Verbatim reflection](locked-changed-input-reflection-2.md), supplied by the user after execution |
| Earlier superseded proposal | [First prediction](locked-changed-input-prediction.md) and [overlap disclosure](locked-changed-input-provenance.md); retained as history, not the active test |

The result's recorded SHA-256 values for all ten locked files match their bytes in the pre-run commit. Its recorded execution timestamp follows that commit. The agent read the existing JSON and checked arithmetic and hashes; **the designated experiment was not rerun**. The original JSON's null human-decision/reconciliation fields and its initial status are intentionally unchanged: the linked student reflection and this companion record supply those later events.

## Input change and controls

| Item | Before | After |
|---|---:|---:|
| SGOV weight | 85% | 10% |
| VOO weight | 15% | 90% |
| IEF / LQD weights | 0% / 0% | 0% / 0% |
| Estimated annual return | 5.2843% | 13.1303% |
| Annualized volatility | 2.4519% | 14.1078% |
| Estimated-return / volatility quotient | 2.1552 | 0.9307 |
| Coded feasibility verdict | PASS | PASS |

Held constant: the same 61 monthly adjusted-price observations / 60 returns, sample estimates and covariance, zero additional annual cost, 5% return objective, and 10% SGOV reserve minimum. This is a fixed-weight comparison, not reoptimization or realized performance. Annual rebalancing and down-market losses are not simulated.

## Prediction reconciliation and actual decision effect

| Student prediction / statement | Recorded evidence | Disposition |
|---|---|---|
| Estimated return increases | +7.8460 percentage points, or +148.48% relative to baseline | Direction matched |
| Volatility increases substantially toward VOO's volatility | +11.6559 percentage points, or +475.39%; changed portfolio 14.1078% versus VOO estimate 15.6667% | Direction matched; proximity is descriptive, not a pre-specified numerical tolerance |
| “Three times greater” risk increase | 475.39% / 148.48% = 3.2017 | Clarify as volatility's **relative percentage increase being about 3.20 times** return's relative percentage increase. Comparing percentage-point changes gives a different ratio; the two conventions must not be mixed |
| Return per unit of risk decreased | Simple estimated-return / volatility quotient falls from 2.1552 to 0.9307, a 56.82% decline | Supported for this descriptive quotient. It is not a Sharpe ratio: no risk-free rate is subtracted, and it is not a complete suitability measure |
| “Especially in down markets” | No conditional-down-market or drawdown test was executed | Not established by this experiment; the student correctly identifies this limitation |
| A 90%-stock portfolio could fall 25–35% in a down year | No source, calibrated loss model, or scenario calculation supports that numerical range in this record | Preserve the student's wording, but treat the range as an untested illustration, not a forecast or a result. Volatility is neither maximum loss nor drawdown |
| Retain 85% SGOV / 15% VOO | Student's post-run reflection explicitly retains it | Expected and actual decision agree. The decision did not change because the student judges the extra estimated return insufficient for the additional volatility under the capital-preservation objective |

PASS only establishes the coded checks on weights, universe, return and reserve; it does not establish suitability, minimum-risk optimality, or permission to adopt the process. The original portfolio remains the **reference paper-pilot allocation**. This result does not override the separate 60-versus-36-month stability failure or authorize client trading. The prior ten-point window shift remains above the five-point adoption limit.

## Completion boundary

The evidence bundle now contains the pre-run prediction, old/new values and units, expected direction and decision effect, preserved execution result, post-run student decision, and reconciliation with limitations. Human AI-off authorship/execution are supported by user attestations and the helper's execution flag, not independent observation. The record does not assert that no earlier internal optimizer grid calculation evaluated these weights. Institutional acceptance remains the instructor's judgment.

Videos, transcripts, final student ownership confirmation for the whole submission, access checks, and the final submission freeze remain outstanding. Completing this evidence bundle does not make the full project submission-ready.
