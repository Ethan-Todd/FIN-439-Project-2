from datetime import date


# Editable inputs
DECISION_DATE = "2026-03-31"

ROWS = [
    {"row": 1, "ticker": "AAA", "month": "2026-01", "published": "2026-02-10", "price": 101.0},
    {"row": 2, "ticker": "AAA", "month": "2026-02", "published": "2026-03-10", "price": 104.0},
    {"row": 3, "ticker": "AAA", "month": "2026-03", "published": "2026-04-10", "price": 109.0},
    {"row": 4, "ticker": "AAA", "month": "2026-02", "published": "2026-03-25", "price": 103.0},
    {"row": 5, "ticker": "BBB", "month": "2026-01", "published": "2026-02-10", "price": 98.0},
    {"row": 6, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "price": 97.0},
    {"row": 7, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "price": 97.0},
    {"row": 8, "ticker": "BBB", "month": "2026-03", "published": "2026-04-10", "price": 92.0},
    {"row": 9, "ticker": "CCC", "month": "2026-01", "published": "2026-02-10", "price": 110.0},
    {"row": 10, "ticker": "CCC", "month": "2026-02", "published": "2026-04-05", "price": 112.0},
    {"row": 11, "ticker": "", "month": "2026-02", "published": "2026-03-10", "price": 99.0},
    {"row": 12, "ticker": "CCC", "month": "2026-02", "published": "2026-03-10", "price": 111.0},
]


def parse_date(value):
    return date.fromisoformat(value)


def exact_value_key(row):
    return row["ticker"], row["month"], row["published"], row["price"]


def apply_as_of_rules(rows, decision_date):
    remaining = [dict(row) for row in rows]
    funnel = []

    removed = [row for row in remaining if not row["ticker"].strip()]
    remaining = [row for row in remaining if row["ticker"].strip()]
    funnel.append(("Rule 1 — missing ticker (quarantine)", removed))

    seen = set()
    kept = []
    removed = []
    for row in remaining:
        key = exact_value_key(row)
        if key in seen:
            removed.append(row)
        else:
            seen.add(key)
            kept.append(row)
    remaining = kept
    funnel.append(("Rule 2 — exact duplicate", removed))

    removed = [
        row for row in remaining if parse_date(row["published"]) > decision_date
    ]
    remaining = [
        row for row in remaining if parse_date(row["published"]) <= decision_date
    ]
    funnel.append(("Rule 3 — published after decision date", removed))

    latest_by_series_month = {}
    for row in remaining:
        key = row["ticker"], row["month"]
        current = latest_by_series_month.get(key)
        if current is None or (
            parse_date(row["published"]), row["row"]
        ) > (parse_date(current["published"]), current["row"]):
            latest_by_series_month[key] = row
    kept_rows = {row["row"] for row in latest_by_series_month.values()}
    removed = [row for row in remaining if row["row"] not in kept_rows]
    remaining = [row for row in remaining if row["row"] in kept_rows]
    funnel.append(("Rule 4 — superseded publication", removed))

    return sorted(remaining, key=lambda row: row["row"]), funnel


def latest_publication_panel(rows):
    valid_rows = [row for row in rows if row["ticker"].strip()]
    latest = {}
    for row in valid_rows:
        key = row["ticker"], row["month"]
        current = latest.get(key)
        if current is None or (
            parse_date(row["published"]), row["row"]
        ) > (parse_date(current["published"]), current["row"]):
            latest[key] = row
    return list(latest.values())


def calculate_signals(panel):
    by_ticker = {}
    for row in panel:
        by_ticker.setdefault(row["ticker"], []).append(row)

    signals = []
    for ticker in sorted(by_ticker):
        observations = sorted(
            by_ticker[ticker], key=lambda row: (row["month"], row["published"])
        )
        if len(observations) < 2:
            signals.append((ticker, None, None, None))
            continue
        previous, latest = observations[-2:]
        change = latest["price"] / previous["price"] - 1.0
        signals.append((ticker, latest["month"], previous["month"], change))
    return signals


def row_numbers(rows):
    return ", ".join(str(row["row"]) for row in rows) if rows else "none"


def print_funnel(funnel):
    print("ROW FUNNEL")
    for label, removed in funnel:
        print(f"{label}: {len(removed)} row(s); row numbers: {row_numbers(removed)}")


def print_panel(panel):
    print("\nAS-OF PANEL")
    print(f"{'Row':>3}  {'Ticker':<6}  {'Month':<7}  {'Published':<10}  {'Price':>7}")
    for row in panel:
        print(
            f"{row['row']:>3}  {row['ticker']:<6}  {row['month']:<7}  "
            f"{row['published']:<10}  {row['price']:>7.1f}"
        )


def print_signals(title, signals):
    print(f"\n{title}")
    for ticker, latest_month, previous_month, change in signals:
        if change is None:
            print(f"{ticker}: unavailable — fewer than two months")
        else:
            print(
                f"{ticker}: {change:+.2%} for {latest_month} "
                f"(from {previous_month})"
            )


def main():
    decision_date = parse_date(DECISION_DATE)
    panel, funnel = apply_as_of_rules(ROWS, decision_date)
    naive_panel = latest_publication_panel(ROWS)

    print(f"Decision date: {decision_date.isoformat()}\n")
    print_funnel(funnel)
    print_panel(panel)
    print_signals("AS-OF SIGNALS", calculate_signals(panel))
    print_signals(
        "NAIVE SIGNALS — latest publications, ignoring publication date",
        calculate_signals(naive_panel),
    )


if __name__ == "__main__":
    main()
