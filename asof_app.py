import csv
import io
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


SERIES_NAMES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}

DEFAULT_SERIES = list(SERIES_NAMES)
DEFAULT_START_DATE = date(2020, 1, 1)
FRED_SERIES_URL = "https://fred.stlouisfed.org/series/{}"


def _read_observations(url):
    request = Request(url, headers={"User-Agent": "FIN439-learning-app/1.0"})
    with urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8-sig")

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration as error:
        raise ValueError("the download was empty") from error
    if len(header) < 2 or header[0] not in {"observation_date", "DATE"}:
        raise ValueError("the download did not contain the expected FRED columns")

    observations = []
    for row_number, row in enumerate(reader, start=2):
        if len(row) < 2 or not row[0].strip():
            continue
        measured_on = date.fromisoformat(row[0].strip())
        raw_value = row[1].strip()
        if raw_value in {"", "."}:
            continue
        try:
            value = Decimal(raw_value)
        except InvalidOperation as error:
            raise ValueError(
                f"invalid value on downloaded row {row_number}: {raw_value}"
            ) from error
        observations.append((measured_on, value))

    if not observations:
        raise ValueError("the series contained no usable observations")
    return observations


@st.cache_data(show_spinner=False, ttl=3600)
def download_current_series(series_id):
    """Download today's FRED observations for one series."""
    query = urlencode({"id": series_id})
    return _read_observations(
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?{query}"
    )


@st.cache_data(show_spinner=False, ttl=3600)
def download_vintage_series(series_id, vintage_date):
    """Download ALFRED observations as known on one vintage date."""
    query = urlencode(
        {"id": series_id, "vintage_date": vintage_date.isoformat()}
    )
    return _read_observations(
        f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?{query}"
    )


def observations_from(observations, start_date):
    return [(measured_on, value) for measured_on, value in observations if measured_on >= start_date]


def compare_versions(current, vintage, start_date):
    current = observations_from(current, start_date)
    vintage = observations_from(vintage, start_date)
    if not current:
        raise ValueError("today's data has no values on or after the start date")

    latest_current_date, latest_current_value = current[-1]
    latest_vintage = vintage[-1] if vintage else None
    current_by_date = dict(current)
    vintage_by_date = dict(vintage)

    if latest_vintage is None:
        later_count = len(current)
    else:
        latest_vintage_date = latest_vintage[0]
        later_count = sum(
            measured_on > latest_vintage_date for measured_on in current_by_date
        )

    shared_dates = current_by_date.keys() & vintage_by_date.keys()
    revision_count = sum(
        current_by_date[measured_on] != vintage_by_date[measured_on]
        for measured_on in shared_dates
    )
    return {
        "current": current,
        "latest_vintage": latest_vintage,
        "latest_current": (latest_current_date, latest_current_value),
        "later_count": later_count,
        "revision_count": revision_count,
    }


def format_value(value):
    return format(value, "f")


def safe_series_id(value):
    series_id = value.strip().upper()
    if not series_id:
        return ""
    if not re.fullmatch(r"[A-Z0-9_-]+", series_id):
        raise ValueError("a FRED series ID may contain only letters, numbers, _ or -")
    return series_id


def display_name(series_id):
    name = SERIES_NAMES.get(series_id)
    return f"{series_id} — {name}" if name else series_id


def markdown_table(rows):
    lines = [
        "| Series | Last known then | Value then | Latest today | Value today | Newer values today | Revised shared dates |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        series_link = f"[{row['series']}]({FRED_SERIES_URL.format(row['series'])})"
        lines.append(
            "| "
            + " | ".join(
                [
                    series_link,
                    row["known_date"],
                    row["known_value"],
                    row["current_date"],
                    row["current_value"],
                    row["later_count"],
                    row["revision_count"],
                ]
            )
            + " |"
        )
    st.markdown("\n".join(lines))


def main():
    today = date.today()
    st.set_page_config(page_title="FRED As-Of Interest Rates", layout="wide")
    st.title("FRED Interest Rates: Today vs. As Known Then")
    st.caption(
        "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, "
        f"downloaded today ({today.isoformat()}); built with AI help, a learning "
        "demonstration, not investment advice."
    )

    selected_series = st.sidebar.multiselect(
        "FRED series",
        options=list(SERIES_NAMES),
        default=DEFAULT_SERIES,
        format_func=display_name,
    )
    custom_input = st.sidebar.text_input("Add another FRED series ID")
    start_date = st.sidebar.date_input(
        "Start date", value=DEFAULT_START_DATE, max_value=today
    )
    as_known_on = st.sidebar.date_input(
        '"As known on" date', value=today, max_value=today
    )

    try:
        custom_series = safe_series_id(custom_input)
    except ValueError as error:
        st.sidebar.error(str(error))
        custom_series = ""

    series_ids = list(selected_series)
    if custom_series and custom_series not in series_ids:
        series_ids.append(custom_series)

    if not series_ids:
        st.info("Select or enter at least one FRED series ID.")
        return

    table_rows = []
    for series_id in series_ids:
        st.subheader(display_name(series_id))
        try:
            with st.spinner(f"Downloading {series_id} from FRED and ALFRED..."):
                current = download_current_series(series_id)
                vintage = download_vintage_series(series_id, as_known_on)
            comparison = compare_versions(current, vintage, start_date)

            chart_data = {
                "Date": [measured_on for measured_on, _ in comparison["current"]],
                series_id: [float(value) for _, value in comparison["current"]],
            }
            st.line_chart(chart_data, x="Date", y=series_id)

            latest_vintage = comparison["latest_vintage"]
            if latest_vintage is None:
                st.caption(
                    f"No nonmissing observation on or after {start_date.isoformat()} "
                    f"was available as of {as_known_on.isoformat()}."
                )
                known_date = "unavailable"
                known_value = "unavailable"
            else:
                known_date = latest_vintage[0].isoformat()
                known_value = format_value(latest_vintage[1])
                st.caption(
                    f"Last observation known on {as_known_on.isoformat()}: "
                    f"{known_date} at {known_value}."
                )

            current_date, current_value = comparison["latest_current"]
            table_rows.append(
                {
                    "series": series_id,
                    "known_date": known_date,
                    "known_value": known_value,
                    "current_date": current_date.isoformat(),
                    "current_value": format_value(current_value),
                    "later_count": str(comparison["later_count"]),
                    "revision_count": str(comparison["revision_count"]),
                }
            )
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            st.error(f"Could not load {series_id}: {error}")
            table_rows.append(
                {
                    "series": series_id,
                    "known_date": "error",
                    "known_value": "error",
                    "current_date": "error",
                    "current_value": "error",
                    "later_count": "error",
                    "revision_count": "error",
                }
            )

    st.subheader("As-of comparison")
    markdown_table(table_rows)
    st.caption(
        "Newer values count nonmissing observations in today's download after the "
        "last date available in the selected vintage. Revisions count shared, "
        "nonmissing observation dates whose values differ."
    )


if __name__ == "__main__":
    main()
