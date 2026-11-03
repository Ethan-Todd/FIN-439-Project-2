import csv
import datetime
import io
import math
import statistics
import sys


# Editable inputs
SLEEVES = {
    "Treasury bills": {"expected_return": 0.035, "volatility": 0.005},
    "Treasury 10-year note": {"expected_return": 0.043, "volatility": 0.070},
    "Investment-grade bond fund": {"expected_return": 0.050, "volatility": 0.060},
    "Global equity index fund": {"expected_return": 0.080, "volatility": 0.160},
}

CORRELATIONS = {
    "Treasury bills": {
        "Treasury bills": 1.00,
        "Treasury 10-year note": 0.10,
        "Investment-grade bond fund": 0.05,
        "Global equity index fund": 0.00,
    },
    "Treasury 10-year note": {
        "Treasury bills": 0.10,
        "Treasury 10-year note": 1.00,
        "Investment-grade bond fund": 0.80,
        "Global equity index fund": -0.10,
    },
    "Investment-grade bond fund": {
        "Treasury bills": 0.05,
        "Treasury 10-year note": 0.80,
        "Investment-grade bond fund": 1.00,
        "Global equity index fund": 0.25,
    },
    "Global equity index fund": {
        "Treasury bills": 0.00,
        "Treasury 10-year note": -0.10,
        "Investment-grade bond fund": 0.25,
        "Global equity index fund": 1.00,
    },
}

OBJECTIVE_RETURN = 0.065
MINIMUM_RESERVE = 0.03
RESERVE_ELIGIBLE = {"Treasury bills", "Treasury 10-year note"}


def validate_inputs(sleeves, correlations):
    names = list(sleeves)
    if set(correlations) != set(names):
        raise ValueError("correlation table rows must match the sleeve names")

    for name in names:
        if set(correlations[name]) != set(names):
            raise ValueError(f"correlation table columns for {name} must match the sleeve names")
        if sleeves[name]["volatility"] <= 0.0:
            raise ValueError(f"volatility for {name} must be greater than zero")

    for row_name in names:
        for column_name in names:
            correlation = correlations[row_name][column_name]
            if correlation < -1.0 or correlation > 1.0:
                raise ValueError(
                    f"correlation for {row_name} and {column_name} must be between -1 and 1"
                )
            reverse = correlations[column_name][row_name]
            if not math.isclose(correlation, reverse, abs_tol=1e-12):
                raise ValueError(
                    f"correlation table is not symmetric for {row_name} and {column_name}"
                )


def build_covariance_matrix(sleeves, correlations):
    names = list(sleeves)
    return {
        row_name: {
            column_name: (
                correlations[row_name][column_name]
                * sleeves[row_name]["volatility"]
                * sleeves[column_name]["volatility"]
            )
            for column_name in names
        }
        for row_name in names
    }


def benchmark_weights(sleeves):
    return {
        name: (
            0.40
            if name == "Investment-grade bond fund"
            else 0.60
            if name == "Global equity index fund"
            else 0.0
        )
        for name in sleeves
    }


def equal_weights(sleeves):
    weight = 1.0 / len(sleeves)
    return {name: weight for name in sleeves}


def inverse_volatility_weights(sleeves):
    inverse_volatilities = {
        name: 1.0 / values["volatility"] for name, values in sleeves.items()
    }
    total = sum(inverse_volatilities.values())
    return {name: value / total for name, value in inverse_volatilities.items()}


def portfolio_expected_return(weights, sleeves):
    return sum(weights[name] * sleeves[name]["expected_return"] for name in sleeves)


def portfolio_volatility(weights, covariance_matrix):
    variance = sum(
        weights[row_name]
        * weights[column_name]
        * covariance_matrix[row_name][column_name]
        for row_name in weights
        for column_name in weights
    )
    return math.sqrt(max(0.0, variance))


def reserve_eligible_weight(weights, reserve_eligible):
    return sum(weights[name] for name in reserve_eligible)


def meets_objective(expected_return, objective_return):
    return expected_return >= objective_return


def _weight_combinations(asset_count, units_remaining, prefix=()):
    if asset_count == 1:
        yield prefix + (units_remaining,)
        return
    for units in range(units_remaining + 1):
        yield from _weight_combinations(
            asset_count - 1, units_remaining - units, prefix + (units,)
        )


def find_lowest_risk_mix(
    sleeves,
    correlations,
    objective_return,
    reserve_eligible,
    minimum_reserve,
    step_points=5,
):
    """Return the lowest-volatility feasible long-only mix, or None."""
    if step_points <= 0 or 100 % step_points != 0:
        raise ValueError("step_points must be a positive divisor of 100")
    if minimum_reserve < 0.0 or minimum_reserve > 1.0:
        raise ValueError("minimum reserve must be between 0 and 1")

    validate_inputs(sleeves, correlations)
    unknown_reserve_assets = set(reserve_eligible) - set(sleeves)
    if unknown_reserve_assets:
        raise ValueError("reserve-eligible assets must exist in the sleeve table")

    names = list(sleeves)
    covariance_matrix = build_covariance_matrix(sleeves, correlations)
    total_units = 100 // step_points
    best = None

    for units in _weight_combinations(len(names), total_units):
        weights = {
            name: units[index] / total_units for index, name in enumerate(names)
        }
        expected_return = portfolio_expected_return(weights, sleeves)
        reserve_weight = reserve_eligible_weight(weights, reserve_eligible)
        if expected_return < objective_return or reserve_weight < minimum_reserve:
            continue
        volatility = portfolio_volatility(weights, covariance_matrix)
        if best is None or volatility < best["volatility"]:
            best = {
                "weights": weights,
                "expected_return": expected_return,
                "volatility": volatility,
                "reserve_eligible_weight": reserve_weight,
            }
    return best


def _parse_date(value):
    value = value.strip()
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        for date_format in ("%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
            try:
                return datetime.datetime.strptime(value, date_format).date()
            except ValueError:
                pass
    raise ValueError(f"unrecognized date: {value}")


def _csv_text(source):
    if hasattr(source, "read"):
        if hasattr(source, "seek"):
            source.seek(0)
        contents = source.read()
        if isinstance(contents, bytes):
            contents = contents.decode("utf-8-sig")
        return contents
    with open(source, "r", encoding="utf-8-sig", newline="") as csv_file:
        return csv_file.read()


def estimate_from_price_csv(source, last_36=False):
    """Estimate annual return, volatility, and correlations from monthly prices."""
    reader = csv.reader(io.StringIO(_csv_text(source)))
    try:
        header = next(reader)
    except StopIteration as error:
        raise ValueError("price CSV is empty") from error

    tickers = [name.strip() for name in header[1:]]
    if not header or not header[0].strip() or not tickers:
        raise ValueError("price CSV must have a date column followed by ticker columns")
    if any(not ticker for ticker in tickers) or len(set(tickers)) != len(tickers):
        raise ValueError("ticker names must be present and unique")

    dates = []
    prices = {ticker: [] for ticker in tickers}
    for row_number, row in enumerate(reader, start=2):
        if not row or all(not value.strip() for value in row):
            continue
        if len(row) != len(header):
            raise ValueError(f"row {row_number} does not match the header width")
        date = _parse_date(row[0])
        if dates and date <= dates[-1]:
            raise ValueError("price dates must be oldest first with no duplicates")
        dates.append(date)
        for ticker, value in zip(tickers, row[1:]):
            try:
                price = float(value)
            except ValueError as error:
                raise ValueError(
                    f"invalid price for {ticker} on row {row_number}"
                ) from error
            if price <= 0.0:
                raise ValueError(f"price for {ticker} must be greater than zero")
            prices[ticker].append(price)

    if len(dates) < 3:
        raise ValueError("price CSV needs at least three monthly price rows")

    returns = {
        ticker: [
            current / previous - 1.0
            for previous, current in zip(values, values[1:])
        ]
        for ticker, values in prices.items()
    }
    if last_36:
        returns = {ticker: values[-36:] for ticker, values in returns.items()}

    observations = len(next(iter(returns.values())))
    if observations < 2:
        raise ValueError("at least two monthly returns are required")

    monthly_means = {
        ticker: statistics.fmean(values) for ticker, values in returns.items()
    }
    monthly_volatilities = {
        ticker: statistics.stdev(values) for ticker, values in returns.items()
    }
    for ticker, volatility in monthly_volatilities.items():
        if volatility == 0.0:
            raise ValueError(f"{ticker} has zero monthly volatility")

    sleeves = {
        ticker: {
            "expected_return": monthly_means[ticker] * 12.0,
            "volatility": monthly_volatilities[ticker] * math.sqrt(12.0),
        }
        for ticker in tickers
    }
    correlations = {ticker: {} for ticker in tickers}
    for row_ticker in tickers:
        for column_ticker in tickers:
            covariance = sum(
                (row_value - monthly_means[row_ticker])
                * (column_value - monthly_means[column_ticker])
                for row_value, column_value in zip(
                    returns[row_ticker], returns[column_ticker]
                )
            ) / (observations - 1)
            correlation = covariance / (
                monthly_volatilities[row_ticker]
                * monthly_volatilities[column_ticker]
            )
            correlations[row_ticker][column_ticker] = max(
                -1.0, min(1.0, correlation)
            )

    validate_inputs(sleeves, correlations)
    return sleeves, correlations


def build_portfolios(
    sleeves,
    correlations=None,
    objective_return=OBJECTIVE_RETURN,
    reserve_eligible=RESERVE_ELIGIBLE,
    minimum_reserve=MINIMUM_RESERVE,
    step_points=5,
):
    portfolios = {
        "Benchmark": benchmark_weights(sleeves),
        "Equal weight": equal_weights(sleeves),
        "Inverse volatility": inverse_volatility_weights(sleeves),
    }
    if correlations is not None:
        candidate = find_lowest_risk_mix(
            sleeves,
            correlations,
            objective_return,
            reserve_eligible,
            minimum_reserve,
            step_points=step_points,
        )
        if candidate is not None:
            portfolios["Candidate (lowest risk)"] = candidate["weights"]
    return portfolios


def print_portfolio(
    name,
    weights,
    sleeves,
    covariance_matrix,
    objective_return,
    reserve_eligible,
    minimum_reserve=MINIMUM_RESERVE,
):
    expected_return = portfolio_expected_return(weights, sleeves)
    volatility = portfolio_volatility(weights, covariance_matrix)
    reserve_weight = reserve_eligible_weight(weights, reserve_eligible)

    print(f"\n{name}")
    for sleeve_name, weight in weights.items():
        print(f"  {sleeve_name}: {weight:.1%}")
    print(f"  Expected return: {expected_return:.2%}")
    print(f"  Volatility: {volatility:.2%}")
    print(f"  Reserve-eligible weight: {reserve_weight:.2%}")
    print(
        "  Meets objective: "
        + ("yes" if meets_objective(expected_return, objective_return) else "no")
    )
    print(
        "  Meets reserve: "
        + ("yes" if reserve_weight >= minimum_reserve else "no")
    )


def main():
    try:
        validate_inputs(SLEEVES, CORRELATIONS)
        covariance_matrix = build_covariance_matrix(SLEEVES, CORRELATIONS)
        portfolios = build_portfolios(
            SLEEVES,
            CORRELATIONS,
            OBJECTIVE_RETURN,
            RESERVE_ELIGIBLE,
            MINIMUM_RESERVE,
        )
        print(f"Objective return: {OBJECTIVE_RETURN:.2%}")
        print(f"Reserve minimum: {MINIMUM_RESERVE:.2%}")
        for name, weights in portfolios.items():
            print_portfolio(
                name,
                weights,
                SLEEVES,
                covariance_matrix,
                OBJECTIVE_RETURN,
                RESERVE_ELIGIBLE,
                MINIMUM_RESERVE,
            )
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
