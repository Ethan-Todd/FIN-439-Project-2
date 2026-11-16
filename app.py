from copy import deepcopy
import json
from pathlib import Path
import streamlit as st
import analysis as a
import portfolio as p
from signal_monitor import signal_status

st.set_page_config(page_title='Project 2 Portfolio Review', layout='wide')
st.title('Project 2 — Portfolio Review')
st.caption('OpenAI Codex assisted with code, testing, and documentation. Student review and ownership of the final analysis and decision remain required.')
st.caption('Educational analysis, not investment advice.')
st.write('Working mandate: 5% estimated annual return, at least 10% SGOV, fully invested and long-only in SGOV/IEF/LQD/VOO.')
st.warning('Pilot only. Historical estimates are not realized performance. Annual rebalancing is NOT simulated.')

uploaded = st.sidebar.file_uploader('Optional replacement monthly adjusted prices (61 rows)', type='csv')
last_36 = st.sidebar.toggle('Use last 36 monthly returns', value=False)
objective = st.sidebar.number_input('Scenario return objective (%)', value=5.0, min_value=-100.0, max_value=100.0, step=.5) / 100
reserve = st.sidebar.number_input('Scenario minimum SGOV (%)', value=10.0, min_value=0.0, max_value=100.0, step=5.0) / 100
cost = st.sidebar.number_input('Annual cost deduction (basis points)', value=0, min_value=0, max_value=1000, step=25) / 10000
shift = st.sidebar.number_input('All expected returns shift (percentage points)', value=0.0, min_value=-50.0, max_value=50.0, step=.5) / 100
st.sidebar.caption('Scenario controls do not amend the mandate or change baseline weights. Costs are hypothetical annual deductions, not simulated trading costs.')

try:
    source = uploaded if uploaded is not None else a.ROOT / 'prices.csv'
    base, base_corr = a.load_prices(source)
    current, corr = a.load_prices(source, last_36)
    current = deepcopy(current)
    for values in current.values():
        values['expected_return'] += shift
    original = a.optimize(base, base_corr)
    candidate = a.optimize(current, corr, cost, objective, reserve)
    baselines = a.fixed_baselines(base)
except (ValueError, UnicodeDecodeError, OSError) as error:
    st.error(f'Inputs rejected: {error}')
    st.stop()

policy = json.loads((a.ROOT / 'policy.json').read_text())
if policy['benchmark'] is None:
    st.warning('Policy benchmark pending client choice. The two transparent comparisons below are not an invented Lab 13 benchmark.')
else:
    st.write('Current proposed fixed policy benchmark:', policy['benchmark'])
    st.caption(policy['benchmark_status'] + '. ' + policy['benchmark_rationale'])
st.subheader('Candidate and fixed baseline comparisons')
st.caption('All rows use the same current estimates and cost deduction. Baseline weights are frozen from the full input sample; window, costs, target, reserve, and return shifts do not reweight them.')
rows = []
portfolios = dict(baselines)
if candidate is not None:
    portfolios['Constrained portfolio'] = candidate['weights']
else:
    st.error('STOP: no mix meets the objective under the scenario controls.')
for name, weights in portfolios.items():
    scenario = a.evaluate(weights, current, corr, cost, objective, reserve)
    mandate = a.evaluate(weights, current, corr, cost)
    rows.append({'Portfolio': name, **{t: f'{weights[t]:.2%}' for t in p.UNIVERSE},
                 'Gross estimate': f'{scenario["gross_estimated_return"]:.2%}',
                 'Net estimate': f'{scenario["net_estimated_return"]:.2%}',
                 'Volatility': f'{scenario["volatility"]:.2%}',
                 'Working mandate': mandate['verdict'], 'Mandate violations': '; '.join(mandate['violated_rules']) or 'None',
                 'Scenario verdict': scenario['verdict'], 'Scenario violations': '; '.join(scenario['violated_rules']) or 'None'})
st.dataframe(rows, hide_index=True, width='stretch')
st.subheader('Process stopping conditions')
window_s, window_c = a.load_prices(source, True)
window_candidate = a.optimize(window_s, window_c)
change = None if original is None or window_candidate is None else max(abs(original['weights'][t] - window_candidate['weights'][t]) for t in p.UNIVERSE)
if change is None or change > .05 + 1e-12:
    st.error('DO NOT ADOPT: the reference versus 36-month window is infeasible or exceeds the mandate five-percentage-point stability limit.')
if change is not None:
    st.metric('Largest reference / 36-month allocation change', f'{change * 100:.1f} percentage points')
st.caption('Paper-pilot range: 75–95% SGOV and complementary 25–5% VOO, from saved routine stresses. This range describes sensitivity; it does not relax the five-point adoption limit. Adoption requires documented refreshed inputs and a reasonable alternative-window comparison with feasible portfolios and no asset-weight change above five points, plus resolved review flags and human authorization.')
st.write('Halt selection on invalid inputs or infeasibility. Do not adopt when the alternative-window stability test fails, the signal is quarantined or requires review, or the policy benchmark is unresolved. A stress failure requests review; stress settings are not new client constraints.')

st.subheader('Point-in-time reserve-yield monitor')
signal = signal_status(base['SGOV']['expected_return'])
st.json(signal)
st.caption('Proposed monitoring rule: if the vintage DGS3MO yield is below the full-sample SGOV estimate, review the reserve estimate before adoption. Yield is not SGOV total return. No automatic allocation change. The cutoff is a calendar-date vintage, not intraday proof.')

with st.expander('Estimates and limitations'):
    st.json(current)
    st.write('Monthly arithmetic mean × 12; sample standard deviation × √12; sample covariance; exhaustive five-point grid. Monthly labels do not establish availability. Adjusted-close history is a retained download, not a vintage backtest. Taxes, turnover, realized returns, and annual rebalancing are not simulated. No numerical volatility cap was supplied in the mandate.')
with st.expander('Reproducible saved routine sensitivity report'):
    report_path = a.ROOT / 'outputs' / 'analysis.md'
    if report_path.exists():
        st.caption('This frozen report uses bundled prices and default policy, not the current interactive scenario.')
        st.markdown(report_path.read_text())
    else:
        st.info('Run python analysis.py --write to generate the report.')
