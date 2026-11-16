"""Deterministic routine analysis. This is NOT the human Locked Changed-Input exercise."""
import argparse
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import portfolio as p
from signal_monitor import signal_status

ROOT = Path(__file__).resolve().parent

def load_prices(source=None, last_36=False):
    source = source if source is not None else ROOT / 'prices.csv'
    text = p._csv_text(source)
    rows = list(csv.reader(io.StringIO(text)))
    nonblank = [r for r in rows[1:] if r and any(v.strip() for v in r)]
    if len(nonblank) != 61:
        raise ValueError('Project 2 requires exactly 61 consecutive monthly prices for its five-year sample')
    sleeves, correlations = p.estimate_from_price_csv(io.StringIO(text), last_36=last_36, required_returns=60)
    if set(sleeves) != set(p.UNIVERSE):
        raise ValueError('permitted universe is exactly SGOV, IEF, LQD, VOO')
    return sleeves, correlations

def evaluate(weights, sleeves, correlations, cost=0, objective=.05, minimum=.10):
    p.validate_inputs(sleeves, correlations)
    p.validate_weights(weights, sleeves)
    if not p.math.isfinite(cost) or cost < 0:
        raise ValueError('annual cost deduction must be finite and nonnegative')
    gross = p.portfolio_expected_return(weights, sleeves)
    net = gross - cost
    violations = []
    if net + 1e-12 < objective:
        violations.append(f'net estimated return below {objective:.2%}')
    if weights['SGOV'] + 1e-12 < minimum:
        violations.append(f'SGOV reserve below {minimum:.2%}')
    return {'weights': weights, 'gross_estimated_return': gross, 'annual_cost': cost,
            'net_estimated_return': net, 'volatility': p.portfolio_volatility(weights, p.build_covariance_matrix(sleeves, correlations)),
            'reserve_weight': weights['SGOV'], 'verdict': 'FAIL' if violations else 'PASS',
            'violated_rules': violations}

def optimize(sleeves, correlations, cost=0, objective=.05, minimum=.10):
    if not p.math.isfinite(cost) or cost < 0:
        raise ValueError('annual cost deduction must be finite and nonnegative')
    found = p.find_lowest_risk_mix(sleeves, correlations, objective + cost, {'SGOV'}, minimum)
    return None if found is None else evaluate(found['weights'], sleeves, correlations, cost, objective, minimum)

def fixed_baselines(sleeves):
    result = {'Equal weight': p.equal_weights(sleeves),
              'Inverse volatility (frozen full sample)': p.inverse_volatility_weights(sleeves)}
    policy = json.loads((ROOT / 'policy.json').read_text())
    if policy['benchmark'] is not None:
        result['Policy benchmark'] = p.benchmark_weights(sleeves, policy['benchmark'])
    return result

def scenarios():
    # Routine engineering choices, not precommitted human predictions or mandate amendments.
    return [
        {'name': 'Reference', 'dimension': 'reference'},
        {'name': 'All expected returns -1 percentage point', 'dimension': 'estimates', 'shift': -.01},
        {'name': 'All expected returns +1 percentage point', 'dimension': 'estimates', 'shift': .01},
        {'name': 'VOO volatility +25%', 'dimension': 'estimates', 'voo_vol_multiplier': 1.25},
        {'name': 'Last 36 returns', 'dimension': 'window', 'last_36': True},
        {'name': 'Annual cost 25 bp', 'dimension': 'costs', 'cost': .0025},
        {'name': 'Annual cost 100 bp', 'dimension': 'costs', 'cost': .01},
        {'name': 'SGOV minimum 25%', 'dimension': 'constraints', 'minimum': .25},
        {'name': 'SGOV minimum 100%', 'dimension': 'constraints', 'minimum': 1.0},
        {'name': 'Return target 6%', 'dimension': 'constraints', 'objective': .06},
    ]

def build_report(source=None):
    base, corr = load_prices(source)
    raw_text = p._csv_text(source if source is not None else ROOT / 'prices.csv')
    price_rows = [row for row in csv.reader(io.StringIO(raw_text)) if row and any(v.strip() for v in row)]
    candidate = optimize(base, corr)
    comparisons = {name: evaluate(w, base, corr) for name, w in fixed_baselines(base).items()}
    rows = []
    for spec in scenarios():
        sleeves, correlations = load_prices(source, spec.get('last_36', False))
        sleeves = deepcopy(sleeves)
        for values in sleeves.values():
            values['expected_return'] += spec.get('shift', 0)
        sleeves['VOO']['volatility'] *= spec.get('voo_vol_multiplier', 1)
        cost, target, reserve = spec.get('cost', 0), spec.get('objective', .05), spec.get('minimum', .10)
        result = optimize(sleeves, correlations, cost, target, reserve)
        change = None if result is None or candidate is None else max(abs(result['weights'][t] - candidate['weights'][t]) for t in p.UNIVERSE)
        held = None if candidate is None else evaluate(candidate['weights'], sleeves, correlations, cost, target, reserve)
        rows.append({'scenario': spec, 'candidate': result, 'reference_allocation_under_stress': held,
                     'maximum_weight_change': change,
                     'stop': result is None or (change is not None and change > .05 + 1e-12)})
    signal = signal_status(base['SGOV']['expected_return'])
    reasons = []
    window = next(row for row in rows if row['scenario']['dimension'] == 'window')
    if candidate is None:
        reasons.append('No mix meets the objective; halt allocation selection')
    if window['stop']:
        reasons.append('Alternative-window change exceeds the mandate five-percentage-point adoption limit')
    if signal['status'] in ('QUARANTINE', 'REVIEW'):
        reasons.append('Signal requires evidence or estimate review before adoption')
    policy = json.loads((ROOT / 'policy.json').read_text())
    if policy['benchmark'] is None:
        reasons.append('Client policy benchmark is not selected')
    weights = [row['candidate']['weights'] for row in rows if row['candidate'] is not None]
    return {'scope': 'Routine validation; not Locked Changed-Input evidence',
            'policy': policy, 'data': {'price_sha256': hashlib.sha256(raw_text.encode()).hexdigest(),
                                     'sample': '61 consecutive monthly adjusted-price observations / 60 returns',
                                     'price_period_labels': [price_rows[1][0], price_rows[-1][0]],
                                     'timing': 'Monthly labels are period labels, not availability timestamps; no historical backtest claim'},
            'assumptions': base, 'candidate': candidate, 'baselines': comparisons, 'sensitivity': rows,
            'signal': signal, 'decision': 'PILOT ONLY / NOT APPROVED FOR ADOPTION', 'adoption_blocks': reasons,
            'stress_allocation_envelope': {t: [min(w[t] for w in weights), max(w[t] for w in weights)] for t in p.UNIVERSE} if weights else {},
            'disclosures': ['Annual rebalancing is NOT simulated. No realized-performance backtest.',
                            'Costs are deterministic annual portfolio-level deductions, not estimated trading costs.',
                            'The 5% objective is tested after the stated cost deduction as a conservative sensitivity convention; the mandate did not specify costs.',
                            'Stress envelope is not a confidence interval, suitable allocation range, or trading permission.',
                            'Human evidence, approval, and submission materials remain incomplete.']}

def render_markdown(report):
    lines = ['# Visible Project 2 executed output', '', report['scope'], '',
             '**Decision: ' + report['decision'] + '**', '',
             'Policy: 5% estimated return; at least 10% SGOV; long-only, fully invested SGOV/IEF/LQD/VOO; 5-point search grid.', '',
             'Data period labels: ' + ' through '.join(report['data']['price_period_labels']) + '; 60 returns. Price SHA-256: `' + report['data']['price_sha256'] + '`. Signal cutoff: ' + report['signal']['cutoff'] + '.', '',
             '## Comparisons (historical estimates, not realized performance)', '',
             '| Portfolio | SGOV / IEF / LQD / VOO | Net return | Volatility | Verdict / violations |',
             '|---|---|---:|---:|---|']
    comparisons = dict(report['baselines'])
    comparisons['Constrained candidate'] = report['candidate']
    for name, row in comparisons.items():
        if row is None:
            lines.append(f'| {name} | unavailable | — | — | no mix meets the objective |')
        else:
            weights = ' / '.join(f'{row["weights"][t]:.2%}' for t in p.UNIVERSE)
            lines.append(f'| {name} | {weights} | {row["net_estimated_return"]:.4%} | {row["volatility"]:.4%} | {row["verdict"]}: {"; ".join(row["violated_rules"]) or "all coded rules"} |')
    lines += ['', '## Routine sensitivity', '', '| Scenario | Selected SGOV / IEF / LQD / VOO | Net return | Volatility | Largest change | Original allocation verdict |', '|---|---|---:|---:|---:|---|']
    for row in report['sensitivity']:
        result, held = row['candidate'], row['reference_allocation_under_stress']
        weights = ' / '.join(f'{result["weights"][t]:.0%}' for t in p.UNIVERSE) if result else 'INFEASIBLE'
        values = f'{result["net_estimated_return"]:.4%} | {result["volatility"]:.4%} | {row["maximum_weight_change"]:.1%}' if result and row['maximum_weight_change'] is not None else '— | — | —'
        lines.append(f'| {row["scenario"]["name"]} | {weights} | {values} | {held["verdict"] if held else "unavailable"} |')
    lines += ['', '## Point-in-time monitor', '', '```json', json.dumps(report['signal'], indent=2), '```', '', '## Adoption blocks', '']
    lines += ['- ' + x for x in report['adoption_blocks']]
    lines += ['', '## Limitations', ''] + ['- ' + x for x in report['disclosures']]
    return '\n'.join(lines) + '\n'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='save routine report to outputs/')
    args = parser.parse_args()
    report = build_report()
    if args.write:
        (ROOT / 'outputs').mkdir(exist_ok=True)
        (ROOT / 'outputs' / 'analysis.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        (ROOT / 'outputs' / 'analysis.md').write_text(render_markdown(report))
    print(render_markdown(report))

if __name__ == '__main__':
    main()
