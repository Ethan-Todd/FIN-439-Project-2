from copy import deepcopy

import streamlit as st

import portfolio as engine


st.set_page_config(page_title="Portfolio Risk Search", layout="wide")
st.title("Lowest-Risk Portfolio Search")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

objective_return = st.sidebar.number_input(
    "Objective return (%)", min_value=-100.0, max_value=100.0, value=6.5, step=0.1
) / 100.0
minimum_reserve = st.sidebar.number_input(
    "Minimum reserve-eligible weight (%)",
    min_value=0.0,
    max_value=100.0,
    value=3.0,
    step=1.0,
) / 100.0
uploaded_prices = st.sidebar.file_uploader("Upload prices.csv", type="csv")
use_last_36 = st.sidebar.toggle("Use only the last 36 monthly returns", value=False)

try:
    if uploaded_prices is None:
        source_label = "Meridian inputs"
        dataset_key = "meridian"
        baseline_sleeves = deepcopy(engine.SLEEVES)
        baseline_correlations = deepcopy(engine.CORRELATIONS)
        current_sleeves = deepcopy(baseline_sleeves)
        current_correlations = deepcopy(baseline_correlations)
        default_reserve = set(engine.RESERVE_ELIGIBLE)
    else:
        source_label = "Uploaded CSV"
        dataset_key = f"csv_{uploaded_prices.name}"
        baseline_sleeves, baseline_correlations = engine.estimate_from_price_csv(
            uploaded_prices, last_36=False
        )
        if use_last_36:
            current_sleeves, current_correlations = engine.estimate_from_price_csv(
                uploaded_prices, last_36=True
            )
        else:
            current_sleeves = deepcopy(baseline_sleeves)
            current_correlations = deepcopy(baseline_correlations)
        default_reserve = set()
except (UnicodeDecodeError, ValueError) as error:
    st.error(f"Could not load the inputs: {error}")
    st.stop()

st.sidebar.caption(f"Data source: {source_label}")

st.subheader("Expected-return assumptions")
return_columns = st.columns(min(3, len(current_sleeves)))
for index, (asset, values) in enumerate(current_sleeves.items()):
    with return_columns[index % len(return_columns)]:
        values["expected_return"] = st.number_input(
            f"{asset} expected return (%)",
            min_value=-100.0,
            max_value=100.0,
            value=float(values["expected_return"] * 100.0),
            step=0.1,
            key=f"return_{dataset_key}_{use_last_36}_{asset}",
        ) / 100.0

st.subheader("Reserve eligibility")
reserve_columns = st.columns(min(3, len(current_sleeves)))
reserve_eligible = set()
for index, asset in enumerate(current_sleeves):
    with reserve_columns[index % len(reserve_columns)]:
        if st.checkbox(
            asset,
            value=asset in default_reserve,
            key=f"reserve_{dataset_key}_{asset}",
        ):
            reserve_eligible.add(asset)


def search(sleeves, correlations):
    return engine.find_lowest_risk_mix(
        sleeves=sleeves,
        correlations=correlations,
        objective_return=objective_return,
        reserve_eligible=reserve_eligible,
        minimum_reserve=minimum_reserve,
        step_points=5,
    )


def show_result(title, result):
    st.markdown(f"### {title}")
    if result is None:
        st.warning("no mix meets the objective")
        return
    st.metric("Expected return", f"{result['expected_return']:.2%}")
    st.metric("Volatility", f"{result['volatility']:.2%}")
    st.metric(
        "Reserve-eligible weight", f"{result['reserve_eligible_weight']:.2%}"
    )
    st.table(
        [
            {"Asset": asset, "Weight": f"{weight:.2%}"}
            for asset, weight in result["weights"].items()
        ]
    )


try:
    current_result = search(current_sleeves, current_correlations)
    baseline_result = search(baseline_sleeves, baseline_correlations)
except ValueError as error:
    st.error(f"Cannot run the search: {error}")
    st.stop()

left, right = st.columns(2)
with left:
    show_result("Current controls", current_result)
with right:
    baseline_title = (
        "Inputs as loaded — Meridian"
        if uploaded_prices is None
        else "Inputs as loaded — CSV, all months"
    )
    show_result(baseline_title, baseline_result)

st.subheader("Largest weight change")
if current_result is None or baseline_result is None:
    st.write("Unavailable because one of the two searches has no feasible mix.")
else:
    changes = {
        asset: (
            current_result["weights"][asset] - baseline_result["weights"][asset]
        )
        * 100.0
        for asset in current_sleeves
    }
    largest_asset = max(changes, key=lambda asset: abs(changes[asset]))
    st.metric(largest_asset, f"{changes[largest_asset]:+.1f} percentage points")

st.caption(
    "Search method: every long-only portfolio in 5-percentage-point steps. "
    "CSV estimates use arithmetic monthly mean × 12, sample standard deviation × √12, "
    "and correlations from aligned monthly returns."
)
