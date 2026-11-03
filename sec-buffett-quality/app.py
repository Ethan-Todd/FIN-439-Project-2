import json
import os
import re
import sys
from pathlib import Path

import streamlit as st


SKILL_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_facts import build_analysis, save_outputs  # noqa: E402


OUTPUT_DIR = SKILL_DIR / "outputs"
NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])[-+]?\$?\d[\d,]*(?:\.\d+)?%?")


def canonical_number(token):
    return token.replace("$", "").replace(",", "").lstrip("+")


def numbers_in(text):
    return {canonical_number(token) for token in NUMBER_PATTERN.findall(text)}


def unprinted_memo_numbers(memo, report):
    return sorted(numbers_in(memo) - numbers_in(report))


def load_analysis(ticker):
    path = OUTPUT_DIR / f"{ticker}_analysis.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def money_cell(fact):
    if not fact or fact.get("value") is None:
        return "not found"
    return f"{fact['value'] / 1_000_000:,.1f}"


def derived_money_cell(item):
    if item.get("value") is None:
        return "not known"
    return f"{item['value'] / 1_000_000:,.1f}"


def display_analysis(analysis):
    st.markdown(
        f"**{analysis['company_name']} ({analysis['ticker']})** — fiscal years "
        "are labelled by fiscal-year-end date; money is USD millions."
    )
    chart_rows = []
    table_rows = []
    for year in analysis["years"]:
        net_income = year["facts"]["net_income"]
        owner_earnings = year["owner_earnings"]
        chart_rows.append(
            {
                "Fiscal year end": year["fiscal_year_end"],
                "Net income": (
                    None if not net_income else net_income["value"] / 1_000_000
                ),
                "Owner earnings": (
                    None
                    if owner_earnings["value"] is None
                    else owner_earnings["value"] / 1_000_000
                ),
            }
        )
        row = {"Fiscal year end": year["fiscal_year_end"]}
        for key, label in [
            ("revenue", "Revenue"),
            ("net_income", "Net income"),
            ("operating_cash_flow", "Operating cash flow"),
            ("capital_spending", "Capital spending"),
            ("equity", "Equity"),
        ]:
            fact = year["facts"][key]
            row[label] = money_cell(fact)
            row[f"{label} tag"] = fact["tag"] if fact else "not found"
        row["ROE"] = (
            "not known"
            if year["roe"]["value"] is None
            else f"{year['roe']['value']:.2%}"
        )
        row["ROE tags"] = year["roe"]["tag"]
        row["Owner earnings"] = derived_money_cell(owner_earnings)
        row["Owner earnings tags"] = owner_earnings["tag"]
        table_rows.append(row)

    st.subheader("Owner earnings and net income")
    st.line_chart(
        chart_rows,
        x="Fiscal year end",
        y=["Owner earnings", "Net income"],
    )

    st.subheader("Five-year 10-K facts and tags")
    st.dataframe(table_rows, width="stretch", hide_index=True)

    st.subheader("Three coded checks")
    st.table(
        [
            {
                "Check": "ROE of 15% or more every year",
                "Result": analysis["checks"]["roe_at_least_15_every_year"],
            },
            {
                "Check": "Owner earnings positive every year",
                "Result": analysis["checks"][
                    "owner_earnings_positive_every_year"
                ],
            },
            {
                "Check": "Owner earnings grew, first year to last",
                "Result": analysis["checks"][
                    "owner_earnings_grew_first_to_last"
                ],
            },
        ]
    )

    st.markdown(
        f"Sources: [SEC ticker map]({analysis['sources']['ticker_map']}) · "
        f"[SEC company facts]({analysis['sources']['companyfacts']})"
    )

    st.subheader("Buffett-style business-quality memo")
    memo_path = OUTPUT_DIR / f"{analysis['ticker']}_buffett_memo.md"
    if not memo_path.exists():
        st.warning(f"Memo not found: {memo_path.name}")
        return
    memo = memo_path.read_text(encoding="utf-8")
    st.markdown(memo)
    flagged = unprinted_memo_numbers(memo, analysis["printed_report"])
    if flagged:
        st.error(
            "Memo numbers not found in the script output: "
            + ", ".join(flagged)
        )
    else:
        st.success(
            "Numeric audit passed: every number in the memo was printed by "
            "the script."
        )


def main():
    st.set_page_config(page_title="SEC Buffett Quality", layout="wide")
    st.title("SEC 10-K Buffett-Style Business Quality")
    st.caption(
        "Data from SEC EDGAR; built with AI help, a learning demonstration, "
        "not investment advice."
    )
    ticker = st.sidebar.text_input("Ticker", value="COST").strip().upper()
    user_name = st.sidebar.text_input(
        "SEC User-Agent name",
        value=os.environ.get("SEC_USER_AGENT_NAME", "Ethan Todd"),
    )
    user_email = st.sidebar.text_input(
        "SEC User-Agent email", value=os.environ.get("SEC_USER_AGENT_EMAIL", "")
    )
    if st.sidebar.button("Download or refresh SEC facts"):
        try:
            with st.spinner(f"Downloading {ticker} from SEC EDGAR..."):
                analysis = build_analysis(ticker, user_name, user_email)
                save_outputs(analysis, OUTPUT_DIR)
            st.success("SEC facts refreshed.")
        except Exception as error:
            st.error(f"Could not refresh {ticker}: {error}")

    analysis = load_analysis(ticker)
    if analysis is None:
        st.info(
            "No saved analysis for this ticker. Enter the SEC contact email "
            "and select Download or refresh SEC facts."
        )
    else:
        display_analysis(analysis)


if __name__ == "__main__":
    main()
