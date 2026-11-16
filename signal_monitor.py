"""DGS3MO monitoring only: a Treasury market yield is not SGOV total return."""
import csv
import hashlib
import io
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CUTOFF = '2026-10-31'

def parse_observations(text):
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    if len(header) != 2 or header[0] not in ('DATE', 'observation_date') or not header[1].startswith('DGS3MO'):
        raise ValueError('expected a two-column DGS3MO source CSV')
    rows = []
    for row in reader:
        if len(row) != 2:
            raise ValueError('invalid source row width')
        when = date.fromisoformat(row[0])
        if row[1] in ('', '.'):
            continue
        value = float(row[1])
        if not math.isfinite(value):
            raise ValueError('nonfinite source value')
        if rows and when <= rows[-1][0]:
            raise ValueError('source dates must increase without duplicates')
        rows.append((when, value))
    if not rows:
        raise ValueError('source has no usable values')
    return rows

def evaluate_monitor(value_percent, sgov_estimate):
    gap = value_percent / 100 - sgov_estimate
    return {'yield_percent': value_percent, 'sgov_historical_estimate': sgov_estimate,
            'gap_percentage_points': gap * 100,
            'status': 'REVIEW' if gap < -1e-12 else 'NO YIELD SHORTFALL FLAG',
            'action': 'Re-estimate SGOV and rerun feasibility before adoption; do not automatically trade.' if gap < -1e-12 else
                      'Continue monitoring; this flag does not authorize adoption or establish expected SGOV return.'}

def signal_status(sgov_estimate, cutoff=CUTOFF):
    folder = ROOT / 'signal_sources' / cutoff
    try:
        meta = json.loads((folder / 'metadata.json').read_text())
        if meta['cutoff'] != cutoff or meta['series'] != 'DGS3MO':
            raise ValueError('metadata series/cutoff mismatch')
        parsed = {}
        for label in ('vintage', 'current'):
            record = meta['downloads'][label]
            expected_url = (f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=DGS3MO&vintage_date={cutoff}&cosd={meta['start_date']}&coed={cutoff}"
                            if label == 'vintage' else f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3MO&cosd={meta['start_date']}")
            if record['url'] != expected_url:
                raise ValueError('source URL does not establish the requested vintage')
            raw = (folder / record['file']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != record['sha256']:
                raise ValueError('source checksum mismatch')
            text = raw.decode('utf-8-sig')
            if label == 'vintage' and next(csv.reader(io.StringIO(text)))[1] != 'DGS3MO_' + cutoff.replace('-', ''):
                raise ValueError('vintage column does not match requested cutoff')
            parsed[label] = dict(parse_observations(text))
        vintage, current = parsed['vintage'], parsed['current']
        latest = max(vintage)
        if latest > date.fromisoformat(cutoff):
            raise ValueError('observation after decision cutoff')
        result = evaluate_monitor(vintage[latest], sgov_estimate)
        result.update({'cutoff': cutoff, 'observation_date': str(latest), 'retrieved_at_utc': meta['downloads']['vintage']['retrieved_at_utc'],
                       'evidence': str(folder.relative_to(ROOT) / 'metadata.json'),
                       'revised_shared_dates': sum(vintage[d] != current[d] for d in vintage.keys() & current.keys()),
                       'later_observations': sum(d > latest for d in current),
                       'availability': 'Retrospectively retrieved ALFRED date vintage; not contemporaneous capture or intraday proof.'})
        return result
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'status': 'QUARANTINE', 'cutoff': cutoff, 'reason': str(error),
                'action': 'Do not use signal or adopt process until source evidence validates.'}
