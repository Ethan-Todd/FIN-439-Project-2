#!/usr/bin/env python3
"""Download five-year 10-K facts from SEC EDGAR and compute quality checks."""

import argparse
import json
import os
import sys
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
ANNUAL_MIN_DAYS = 300
ANNUAL_MAX_DAYS = 380
CATHIE_REVENUE_GROWTH_THRESHOLD = 0.15

METRICS = {
    "revenue": {
        "label": "Revenue",
        "tags": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
        ],
        "flow": True,
    },
    "net_income": {
        "label": "Net income",
        "tags": ["NetIncomeLoss"],
        "flow": True,
    },
    "operating_cash_flow": {
        "label": "Operating cash flow",
        "tags": ["NetCashProvidedByUsedInOperatingActivities"],
        "flow": True,
    },
    "capital_spending": {
        "label": "Capital spending",
        "tags": [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
        ],
        "flow": True,
    },
    "equity": {
        "label": "Equity",
        "tags": ["StockholdersEquity"],
        "flow": False,
    },
    "liabilities": {
        "label": "Liabilities",
        "tags": ["Liabilities"],
        "flow": False,
    },
    "research_and_development": {
        "label": "Research and development",
        "tags": ["ResearchAndDevelopmentExpense"],
        "flow": True,
    },
}


def parse_iso_date(value):
    return date.fromisoformat(value)


def fetch_json(url, user_agent):
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_company(ticker, user_agent):
    payload = fetch_json(TICKERS_URL, user_agent)
    ticker = ticker.upper()
    matches = [
        row
        for row in payload.values()
        if row.get("ticker", "").upper() == ticker
    ]
    if not matches:
        raise ValueError(f"ticker {ticker} was not found in the SEC ticker file")
    row = matches[0]
    return int(row["cik_str"]), row["title"]


def usd_records(companyfacts, tag):
    fact = companyfacts.get("facts", {}).get("us-gaap", {}).get(tag)
    if not fact:
        return []
    return fact.get("units", {}).get("USD", [])


def is_annual_record(record, flow):
    if (
        record.get("form") != "10-K"
        or not record.get("end")
        or record.get("val") is None
    ):
        return False
    if not flow:
        return True
    if not record.get("start"):
        return False
    days = (
        parse_iso_date(record["end"]) - parse_iso_date(record["start"])
    ).days
    return ANNUAL_MIN_DAYS <= days <= ANNUAL_MAX_DAYS


def latest_record(records):
    if not records:
        return None
    return max(
        records,
        key=lambda row: (
            parse_iso_date(row.get("filed", "1900-01-01")),
            row.get("accn", ""),
        ),
    )


def select_fact(companyfacts, tags, fiscal_end, flow):
    for tag in tags:
        candidates = [
            row
            for row in usd_records(companyfacts, tag)
            if is_annual_record(row, flow) and row["end"] == fiscal_end
        ]
        selected = latest_record(candidates)
        if selected:
            return {
                "value": selected["val"],
                "tag": tag,
                "filed": selected.get("filed"),
                "accession": selected.get("accn"),
                "start": selected.get("start"),
                "end": selected.get("end"),
            }
    return None


def fiscal_year_ends(companyfacts):
    spec = METRICS["revenue"]
    ends = set()
    for tag in spec["tags"]:
        for row in usd_records(companyfacts, tag):
            if is_annual_record(row, True):
                ends.add(row["end"])
    return sorted(ends)[-5:]


def derived_value(value, label, tag):
    return {"value": value, "label": label, "tag": tag}


def check_all(values, predicate):
    if not values or any(value is None for value in values):
        return "not known"
    return "PASS" if all(predicate(value) for value in values) else "FAIL"


def build_analysis(ticker, user_name, user_email):
    if not user_name.strip() or not user_email.strip() or "@" not in user_email:
        raise ValueError(
            "a real name and contact email are required for the SEC User-Agent"
        )
    user_agent = f"{user_name.strip()} {user_email.strip()}"
    cik, company_name = resolve_company(ticker, user_agent)
    time.sleep(0.12)
    facts_url = COMPANYFACTS_URL.format(cik=cik)
    companyfacts = fetch_json(facts_url, user_agent)
    ends = fiscal_year_ends(companyfacts)
    if not ends:
        raise ValueError("no qualifying annual revenue facts were found")

    years = []
    for fiscal_end in ends:
        facts = {}
        for key, spec in METRICS.items():
            facts[key] = select_fact(
                companyfacts, spec["tags"], fiscal_end, spec["flow"]
            )

        net_income = facts["net_income"]
        equity = facts["equity"]
        liabilities = facts["liabilities"]
        revenue = facts["revenue"]
        research_and_development = facts["research_and_development"]
        operating_cash_flow = facts["operating_cash_flow"]
        capital_spending = facts["capital_spending"]

        if net_income and equity and equity["value"] > 0:
            roe = derived_value(
                net_income["value"] / equity["value"],
                "ROE",
                f"{net_income['tag']} / {equity['tag']}",
            )
        else:
            roe = derived_value(None, "ROE", "not known")

        if operating_cash_flow and capital_spending:
            owner_earnings = derived_value(
                operating_cash_flow["value"] - capital_spending["value"],
                "Owner earnings",
                f"{operating_cash_flow['tag']} - {capital_spending['tag']}",
            )
        else:
            owner_earnings = derived_value(
                None, "Owner earnings", "not known"
            )

        if liabilities and equity and equity["value"] > 0:
            liabilities_to_equity = derived_value(
                liabilities["value"] / equity["value"],
                "Liabilities / equity",
                f"{liabilities['tag']} / {equity['tag']}",
            )
        else:
            liabilities_to_equity = derived_value(
                None, "Liabilities / equity", "not known"
            )

        if research_and_development and revenue and revenue["value"] != 0:
            research_and_development_to_revenue = derived_value(
                research_and_development["value"] / revenue["value"],
                "R&D / revenue",
                f"{research_and_development['tag']} / {revenue['tag']}",
            )
        else:
            research_and_development_to_revenue = derived_value(
                None, "R&D / revenue", "not known"
            )

        years.append(
            {
                "fiscal_year_end": fiscal_end,
                "facts": facts,
                "roe": roe,
                "owner_earnings": owner_earnings,
                "liabilities_to_equity": liabilities_to_equity,
                "research_and_development_to_revenue": (
                    research_and_development_to_revenue
                ),
            }
        )

    roe_values = [year["roe"]["value"] for year in years]
    owner_values = [year["owner_earnings"]["value"] for year in years]
    checks = {
        "roe_at_least_15_every_year": check_all(
            roe_values, lambda value: value >= 0.15
        ),
        "owner_earnings_positive_every_year": check_all(
            owner_values, lambda value: value > 0
        ),
        "owner_earnings_grew_first_to_last": (
            "not known"
            if not owner_values
            or owner_values[0] is None
            or owner_values[-1] is None
            else ("PASS" if owner_values[-1] > owner_values[0] else "FAIL")
        ),
    }

    revenue_values = [
        None if not year["facts"]["revenue"] else year["facts"]["revenue"]["value"]
        for year in years
    ]
    if (
        len(revenue_values) == 5
        and revenue_values[0] is not None
        and revenue_values[-1] is not None
        and revenue_values[0] > 0
        and revenue_values[-1] >= 0
    ):
        revenue_cagr = derived_value(
            (revenue_values[-1] / revenue_values[0]) ** (1 / 4) - 1,
            "Revenue growth, first year to last",
            "(last revenue / first revenue)^(1/4) - 1",
        )
    else:
        revenue_cagr = derived_value(
            None, "Revenue growth, first year to last", "not known"
        )

    latest_rd_ratio = years[-1]["research_and_development_to_revenue"]
    operating_cash_flow_covers_net_income = []
    for year in years:
        operating_cash_flow = year["facts"]["operating_cash_flow"]
        net_income = year["facts"]["net_income"]
        operating_cash_flow_covers_net_income.append(
            None
            if not operating_cash_flow or not net_income
            else operating_cash_flow["value"] >= net_income["value"]
        )

    investor_checks = {
        "Buffett": {
            "ROE at least 15% every year": checks[
                "roe_at_least_15_every_year"
            ],
            "Owner earnings positive every year": checks[
                "owner_earnings_positive_every_year"
            ],
            "Owner earnings grew, first year to last": checks[
                "owner_earnings_grew_first_to_last"
            ],
        },
        "Cathie Wood": {
            "Revenue grew at least "
            f"{CATHIE_REVENUE_GROWTH_THRESHOLD:.0%} a year": (
                "not known"
                if revenue_cagr["value"] is None
                else (
                    "PASS"
                    if revenue_cagr["value"]
                    >= CATHIE_REVENUE_GROWTH_THRESHOLD
                    else "FAIL"
                )
            ),
            "R&D at least 5% of revenue, latest year": (
                "not known"
                if latest_rd_ratio["value"] is None
                else ("PASS" if latest_rd_ratio["value"] >= 0.05 else "FAIL")
            ),
        },
        "Burry": {
            "Operating cash flow at least net income every year": check_all(
                operating_cash_flow_covers_net_income,
                lambda value: value,
            ),
            "Liabilities no more than twice equity, latest year": (
                "not known"
                if years[-1]["liabilities_to_equity"]["value"] is None
                else (
                    "PASS"
                    if years[-1]["liabilities_to_equity"]["value"] <= 2.0
                    else "FAIL"
                )
            ),
        },
    }

    analysis = {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "cik": f"{cik:010d}",
        "download_date": date.today().isoformat(),
        "sources": {
            "ticker_map": TICKERS_URL,
            "companyfacts": facts_url,
        },
        "units": "USD millions except ROE and liabilities/equity",
        "years": years,
        "checks": checks,
        "revenue_cagr": revenue_cagr,
        "investor_checks": investor_checks,
    }
    analysis["printed_report"] = render_report(analysis)
    return analysis


def money_text(fact):
    if fact is None or fact.get("value") is None:
        return "not found"
    return f"{fact['value'] / 1_000_000:,.1f}"


def percent_text(derived):
    if derived["value"] is None:
        return "not known"
    return f"{derived['value']:.2%}"


def ratio_text(derived):
    if derived["value"] is None:
        return "not known"
    return f"{derived['value']:.2f}x"


def tag_text(fact):
    return fact["tag"] if fact else "not found"


def render_report(analysis):
    lines = [
        f"Company: {analysis['company_name']}",
        f"Ticker: {analysis['ticker']}",
        f"CIK: {analysis['cik']}",
        f"Downloaded: {analysis['download_date']}",
        "Filings: 10-K only; last 5 fiscal years by fiscal-year-end date",
        f"Units: {analysis['units']}",
        f"Ticker source: {analysis['sources']['ticker_map']}",
        f"Facts source: {analysis['sources']['companyfacts']}",
        "",
        "FIVE-YEAR FACTS",
    ]
    ordered_metrics = [
        "revenue",
        "net_income",
        "operating_cash_flow",
        "capital_spending",
        "equity",
        "liabilities",
        "research_and_development",
    ]
    for year in analysis["years"]:
        lines.append(f"Fiscal year end: {year['fiscal_year_end']}")
        for key in ordered_metrics:
            fact = year["facts"][key]
            lines.append(
                f"  {METRICS[key]['label']}: {money_text(fact)} | "
                f"tag: {tag_text(fact)}"
            )
        lines.append(
            f"  ROE: {percent_text(year['roe'])} | tags: {year['roe']['tag']}"
        )
        lines.append(
            "  Owner earnings: "
            f"{money_text(year['owner_earnings'])} | "
            f"tags: {year['owner_earnings']['tag']}"
        )
        lines.append(
            "  Liabilities / equity: "
            f"{ratio_text(year['liabilities_to_equity'])} | tags: "
            f"{year['liabilities_to_equity']['tag']}"
        )
        lines.append(
            "  R&D / revenue: "
            f"{percent_text(year['research_and_development_to_revenue'])} | "
            f"tags: {year['research_and_development_to_revenue']['tag']}"
        )
    lines.extend(
        [
            "",
            "BUFFETT-STYLE CODED CHECKS",
            "  ROE of 15% or more every year: "
            + analysis["checks"]["roe_at_least_15_every_year"],
            "  Owner earnings positive every year: "
            + analysis["checks"]["owner_earnings_positive_every_year"],
            "  Owner earnings grew, first year to last: "
            + analysis["checks"]["owner_earnings_grew_first_to_last"],
            "",
            "REVENUE GROWTH",
            "  First year to last annual growth: "
            + percent_text(analysis["revenue_cagr"])
            + " | formula: "
            + analysis["revenue_cagr"]["tag"],
            "",
            "THREE-INVESTOR CODED CHECKS",
        ]
    )
    for investor, investor_checks in analysis["investor_checks"].items():
        lines.append(investor)
        for label, result in investor_checks.items():
            lines.append(f"  {label}: {result}")
    lines.extend(
        [
            "",
            "No price data used. This is a business-quality learning "
            "demonstration, not investment advice.",
        ]
    )
    return "\n".join(lines)


def save_outputs(analysis, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker = analysis["ticker"]
    json_path = output_dir / f"{ticker}_analysis.json"
    report_path = output_dir / f"{ticker}_script_output.txt"
    json_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    report_path.write_text(
        analysis["printed_report"] + "\n", encoding="utf-8"
    )
    return json_path, report_path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", help="SEC ticker symbol")
    parser.add_argument(
        "--name", default=os.environ.get("SEC_USER_AGENT_NAME", "Ethan Todd")
    )
    parser.add_argument(
        "--email", default=os.environ.get("SEC_USER_AGENT_EMAIL", "")
    )
    parser.add_argument("--output-dir", default="outputs")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        analysis = build_analysis(args.ticker, args.name, args.email)
        json_path, report_path = save_outputs(analysis, args.output_dir)
    except (
        HTTPError,
        URLError,
        TimeoutError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(analysis["printed_report"])
    print(f"\nSaved JSON: {json_path}")
    print(f"Saved report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
