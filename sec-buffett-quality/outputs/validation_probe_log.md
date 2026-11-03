# Validation Probe Log — November 3, 2026

## Costco known answer

**PASS.** All five fiscal-year-end dates, 35 published table values, and three coded checks match the supplied Costco known answer. The machine-readable result is in `validation_results.txt`.

## JPM missing-data propagation

**PASS.** The unchanged script reports capital spending as `not found` in every displayed JPM year. Owner earnings are `not found`; the positive-owner-earnings and first-to-last-growth checks are both `not known`. The saved JPM memo says it cannot judge owner earnings without departing from the evidence rules.

## Unprinted-number memo attack

**PASS.** `40.0%` was temporarily added to the COST memo. The app displayed: `Memo numbers not found in the script output: 40.0%`. The temporary false statement was then removed, and the restored COST memo passed the numeric audit.

## Fresh browser chat without the skill

**Pending user-run comparison.** Open a genuinely fresh browser-AI chat with no skill and ask: “Is Costco a Buffett business? Give its ROE for the last five years.” Record its answer and links here before comparing it with the SEC table.

The controlled table defines ROE as `NetIncomeLoss ÷ year-end StockholdersEquity` and traces both inputs to SEC company facts and 10-K periods. If the browser answer uses average equity, trailing data, a paid provider, unlabeled fiscal years, or no source, it is not the same measure. A numerical match alone does not establish provenance; an unsupported browser answer remains unresolved.
