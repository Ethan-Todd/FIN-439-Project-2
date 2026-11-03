HOLDINGS = {
    "Cash": {
        "issuer": "none",
        "business_days_to_redeem": 0,
        "reserve_eligible": True,
    },
    "Treasury bills": {
        "issuer": "U.S. Treasury",
        "business_days_to_redeem": 1,
        "reserve_eligible": True,
    },
    "Treasury 10-year note": {
        "issuer": "U.S. Treasury",
        "business_days_to_redeem": 1,
        "reserve_eligible": True,
    },
    "Global equity index fund": {
        "issuer": "diversified fund",
        "business_days_to_redeem": 2,
        "reserve_eligible": False,
    },
    "Investment-grade bond fund": {
        "issuer": "diversified fund",
        "business_days_to_redeem": 3,
        "reserve_eligible": False,
    },
    "Private real estate fund": {
        "issuer": "diversified fund",
        "business_days_to_redeem": 90,
        "reserve_eligible": False,
    },
    "Acme Corp bonds": {
        "issuer": "Acme Corp",
        "business_days_to_redeem": 4,
        "reserve_eligible": False,
    },
    "Acme Corp stock": {
        "issuer": "Acme Corp",
        "business_days_to_redeem": 1,
        "reserve_eligible": False,
    },
}

CANDIDATES = {
    "A": {
        "Cash": 2,
        "Treasury bills": 2,
        "Treasury 10-year note": 10,
        "Global equity index fund": 60,
        "Investment-grade bond fund": 26,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1,
        "Treasury bills": 0,
        "Treasury 10-year note": 0,
        "Global equity index fund": 55,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 15,
        "Acme Corp bonds": 5,
        "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1,
        "Treasury bills": 1,
        "Treasury 10-year note": 0,
        "Global equity index fund": 70,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 8,
    },
    "D": {
        "Cash": 3,
        "Treasury bills": 0,
        "Treasury 10-year note": 89,
        "Global equity index fund": 0,
        "Investment-grade bond fund": 0,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 8,
    },
    "E": {
        "Cash": 0,
        "Treasury bills": 0,
        "Treasury 10-year note": 0,
        "Global equity index fund": 60,
        "Investment-grade bond fund": 40,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
}

RESERVE_SIZE = 100.0  # USD millions
QUARTERLY_DISTRIBUTION = 0.75  # USD millions
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5  # business days
MINIMUM_LIQUID_SHARE = 90.0  # percent
ISSUER_LIMIT = 8.0  # percent
ISSUER_LIMIT_EXEMPTIONS = {"none", "U.S. Treasury", "diversified fund"}


def print_check(label, value, passed):
    status = "pass" if passed else "FAIL"
    print(f"{label}: {value:.1f}% — {status}")


reserve_minimum = (
    QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100.0
)
print(f"Reserve minimum: {reserve_minimum:.1f}%")

for candidate_name, weights in CANDIDATES.items():
    print(f"\nCandidate {candidate_name}")
    failures = 0

    weights_sum = sum(weights.values())
    weights_sum_passes = abs(weights_sum - 100.0) < 0.000001
    print_check("Weights sum", weights_sum, weights_sum_passes)
    failures += not weights_sum_passes

    lowest_weight = min(weights.values())
    long_only_passes = lowest_weight >= 0.0
    print_check("Lowest weight", lowest_weight, long_only_passes)
    failures += not long_only_passes

    reserve_eligible_weight = sum(
        weight
        for holding, weight in weights.items()
        if HOLDINGS[holding]["reserve_eligible"]
    )
    reserve_passes = reserve_eligible_weight >= reserve_minimum
    print_check("Reserve-eligible weight", reserve_eligible_weight, reserve_passes)
    failures += not reserve_passes

    liquid_weight = sum(
        weight
        for holding, weight in weights.items()
        if HOLDINGS[holding]["business_days_to_redeem"] <= LIQUIDITY_WINDOW
    )
    liquidity_passes = liquid_weight >= MINIMUM_LIQUID_SHARE
    print_check("Weight redeemable within window", liquid_weight, liquidity_passes)
    failures += not liquidity_passes

    company_weights = {}
    for holding, weight in weights.items():
        issuer = HOLDINGS[holding]["issuer"]
        if issuer not in ISSUER_LIMIT_EXEMPTIONS:
            company_weights[issuer] = company_weights.get(issuer, 0.0) + weight
    largest_company_weight = max(company_weights.values(), default=0.0)
    issuer_passes = largest_company_weight <= ISSUER_LIMIT
    print_check("Largest single company", largest_company_weight, issuer_passes)
    failures += not issuer_passes

    print("Calendar-year loss rule: requires CIO clarification")
    if failures == 0:
        print("Verdict: passes every checkable rule")
    else:
        print(f"Verdict: fails {failures} rule(s)")
