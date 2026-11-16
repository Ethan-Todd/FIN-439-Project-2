# DGS3MO point-in-time monitoring data card

| Field | Record |
|---|---|
| Series and source | DGS3MO; FRED/ALFRED, Board of Governors H.15; [series page](https://fred.stlouisfed.org/series/DGS3MO) |
| Definition | Three-month constant-maturity Treasury market yield, investment basis; percent per annum; daily, not seasonally adjusted |
| Decision cutoff | 2026-10-31, calendar-date ALFRED vintage; no intraday cutoff claim |
| Requested evidence interval | 2026-10-01 onward; vintage bounded at cutoff |
| Archive retrieval | 2026-11-16 UTC; exact timestamps/URLs/checksums in [metadata](../signal_sources/2026-10-31/metadata.json) |
| Vintage result | Latest nonmissing observation 2026-10-29, 4.18% |
| Current comparison | 2026-11-13, 4.32%; 10 later observations; zero changed values on 20 shared nonmissing dates in this limited interval |
| Missing values | Empty or dot observations excluded; no forward fill |
| Revisions | Count only shared dates in this retained interval; zero here is not a claim that the series never revises |
| Admission | Historical calendar-date monitoring demonstration only; not proof of real-time use, intraday availability, or the original November 3 download |

Retained raw files: [ALFRED vintage](../signal_sources/2026-10-31/vintage.csv), [FRED current](../signal_sources/2026-10-31/current.csv). The vintage contains October 28 and 29 at 4.18%; the current file contains October 30 at 4.16%, which is absent from this vintage. This supports excluding October 30 for the October 31 cutoff. It does not by itself establish the exact later publication timestamp. The old root `asof_data_card.md` contains earlier narrative claims; those are not a substitute for this newly retained evidence.

## Proposed rule and portfolio connection

`signal_monitor.py` compares the latest eligible vintage yield with the full-sample SGOV historical return estimate. A lower yield triggers **REVIEW**: re-estimate the reserve sleeve and rerun feasibility before adoption. Otherwise the status is **NO YIELD SHORTFALL FLAG**, which never overrides the window-stability stop. Missing metadata, a changed checksum, wrong series/vintage header, mismatched URL, or an observation after the cutoff triggers **QUARANTINE** and blocks adoption.

The observed 4.18% exceeds the sample SGOV estimate of 3.7151% by 0.4649 percentage points. This is a monitoring comparison, not an equation between a quoted Treasury yield and an ETF's total return. The zero-gap threshold is an explicit implementation choice proposed during this revision, not a historical Lab 13 requirement. There is no automatic allocation adjustment.

## Limits and refresh

The portfolio uses a retained adjusted-price sample, not historical price vintages. No joint point-in-time backtest is claimed. The signal is frozen at October 31; a future decision needs a newly documented cutoff. The monitor does not estimate taxes, ETF expenses, duration changes, or a daily trading signal.

`python fetch_signal.py --cutoff 2026-10-31` retrieves the bounded source URLs using curl, retaining raw CSVs and selected non-sensitive HTTP headers. curl must be installed for refresh (not for offline use). Full-history Python network requests timed out during validation; the bounded curl request succeeded. Preserve a frozen submitted archive before deliberately refreshing it. Re-run `python analysis.py --write` after any refresh and inspect differences.
