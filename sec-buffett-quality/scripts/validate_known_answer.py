#!/usr/bin/env python3
"""Validate saved COST known answers and the JPM missing-data probe."""

import argparse
import json
from pathlib import Path


COST_EXPECTED = {
    "2022-08-28": [226954, 5844, 7392, 3891, 20642, 28.3, 3501],
    "2023-09-03": [242290, 6292, 11068, 4323, 25058, 25.1, 6745],
    "2024-09-01": [254453, 7367, 11339, 4710, 23622, 31.2, 6629],
    "2025-08-31": [275235, 8099, 13335, 5498, 29164, 27.8, 7837],
    "2026-08-30": [303154, 9226, 15817, 6435, 35803, 25.8, 9382],
}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def millions(item):
    return item["value"] / 1_000_000


def validate_cost(analysis):
    failures = []
    years = {year["fiscal_year_end"]: year for year in analysis["years"]}
    if set(years) != set(COST_EXPECTED):
        failures.append("COST fiscal-year-end dates differ from the known answer")
    for fiscal_end, expected in COST_EXPECTED.items():
        if fiscal_end not in years:
            continue
        year = years[fiscal_end]
        actual = [
            millions(year["facts"]["revenue"]),
            millions(year["facts"]["net_income"]),
            millions(year["facts"]["operating_cash_flow"]),
            millions(year["facts"]["capital_spending"]),
            millions(year["facts"]["equity"]),
            round(year["roe"]["value"] * 100, 1),
            millions(year["owner_earnings"]),
        ]
        if actual != expected:
            failures.append(f"COST {fiscal_end}: expected {expected}, got {actual}")
    expected_checks = {
        "roe_at_least_15_every_year": "PASS",
        "owner_earnings_positive_every_year": "PASS",
        "owner_earnings_grew_first_to_last": "PASS",
    }
    if analysis["checks"] != expected_checks:
        failures.append(
            f"COST checks: expected {expected_checks}, got {analysis['checks']}"
        )
    return failures


def validate_jpm(analysis):
    failures = []
    for year in analysis["years"]:
        if year["facts"]["capital_spending"] is not None:
            failures.append(
                f"JPM {year['fiscal_year_end']} capital spending was not missing"
            )
        if year["owner_earnings"]["value"] is not None:
            failures.append(
                f"JPM {year['fiscal_year_end']} owner earnings was not missing"
            )
    for key in (
        "owner_earnings_positive_every_year",
        "owner_earnings_grew_first_to_last",
    ):
        if analysis["checks"][key] != "not known":
            failures.append(f"JPM {key} was not 'not known'")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", default="outputs")
    parser.add_argument("--save")
    args = parser.parse_args()
    output_dir = Path(args.outputs)
    failures = []
    failures.extend(validate_cost(load(output_dir / "COST_analysis.json")))
    failures.extend(validate_jpm(load(output_dir / "JPM_analysis.json")))
    lines = [
        "COST known-answer values and checks: "
        + ("PASS" if not validate_cost(load(output_dir / "COST_analysis.json")) else "FAIL"),
        "JPM missing-capex propagation probe: "
        + ("PASS" if not validate_jpm(load(output_dir / "JPM_analysis.json")) else "FAIL"),
    ]
    if failures:
        lines.extend(f"FAIL: {failure}" for failure in failures)
    else:
        lines.append("Every expected value and missing-data result matches.")
    report = "\n".join(lines) + "\n"
    print(report, end="")
    if args.save:
        Path(args.save).write_text(report, encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
