"""User-run designated comparison. Do not execute before the prediction commit is pushed."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / 'outputs' / 'locked-allocation-result-2.json'
LOCKED_FILES = (
    'docs/locked-changed-input-prediction-2.md',
    'docs/locked-changed-input-decision-effect-2.md',
    'docs/locked-changed-input-provenance-2.md',
    'run_locked_allocation_test.py', 'analysis.py', 'portfolio.py',
    'signal_monitor.py', 'policy.json', 'prices.csv', 'requirements-lock.txt',
)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--precommit', required=True, help='full pushed commit containing prediction and decision effect')
    parser.add_argument('--attest-ai-off', action='store_true', help='use only when executing personally with AI tools closed')
    args = parser.parse_args()
    if not args.attest_ai_off:
        parser.error('Close AI tools before execution, then supply --attest-ai-off truthfully.')
    if RESULT.exists():
        parser.error('The result file already exists. Preserve it; this helper will not overwrite evidence.')
    commit = git('rev-parse', '--verify', args.precommit + '^{commit}').decode().strip()
    # This checks the locally recorded remote state; the preceding successful push is separate evidence.
    if subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'refs/remotes/origin/main'], cwd=ROOT).returncode:
        parser.error('Precommit is not in locally recorded origin/main. Confirm the push before execution.')
    hashes = {}
    for name in LOCKED_FILES:
        committed = git('show', f'{commit}:{name}')
        local = (ROOT / name).read_bytes()
        if local != committed:
            parser.error(f'{name} differs from the precommit. Do not run against altered inputs.')
        hashes[name] = hashlib.sha256(local).hexdigest()

    # Import and calculate only after the precommit checks, never during module loading.
    import analysis
    sleeves, correlations = analysis.load_prices()
    before = analysis.evaluate({'SGOV': .85, 'IEF': 0., 'LQD': 0., 'VOO': .15}, sleeves, correlations)
    after = analysis.evaluate({'SGOV': .10, 'IEF': 0., 'LQD': 0., 'VOO': .90}, sleeves, correlations)
    changes = {}
    for metric in ('net_estimated_return', 'volatility'):
        changes[metric] = {
            'difference_percentage_points': (after[metric] - before[metric]) * 100,
            'relative_change_percent': ((after[metric] / before[metric]) - 1) * 100 if before[metric] else None,
        }
    result = {
        'execution_timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'execution_ai_off': 'User asserted by supplying --attest-ai-off; not independently verified',
        'prediction_precommit': commit,
        'prediction_commit_url': f'https://github.com/Ethan-Todd/FIN-439-Project-2/commit/{commit}',
        'precommit_committer_timestamp': git('show', '-s', '--format=%cI', commit).decode().strip(),
        'execution_head': git('rev-parse', 'HEAD').decode().strip(),
        'python': platform.python_version(),
        'locked_file_sha256': hashes,
        'held_constant': {'sample': 'bundled 61 monthly prices / 60 returns', 'annual_cost': 0,
                          'return_objective': .05, 'minimum_sgov': .10,
                          'method': 'Fixed-weight comparison, not reoptimization; no realized-performance or annual-rebalancing simulation'},
        'asset_estimates': sleeves,
        'before': before, 'after': after, 'changes': changes,
        'actual_human_decision_effect': None,
        'human_prediction_reconciliation': None,
        'status': 'Measured outputs only; student actual decision and reconciliation still required',
    }
    RESULT.parent.mkdir(exist_ok=True)
    with RESULT.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps(result, indent=2, allow_nan=False))
    print(f'\nPreserved result: {RESULT}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
