"""Archive a requested ALFRED vintage and current comparison; never run on app startup."""
import argparse
import hashlib
import json
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
import subprocess
import tempfile
from signal_monitor import parse_observations

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cutoff', required=True, type=date.fromisoformat)
    args = parser.parse_args()
    if args.cutoff > date.today():
        parser.error('cutoff cannot be in the future')
    folder = ROOT / 'signal_sources' / args.cutoff.isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    records = {}
    start = args.cutoff - timedelta(days=30)
    for label, url in {
        'vintage': f'https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=DGS3MO&vintage_date={args.cutoff}&cosd={start}&coed={args.cutoff}',
        'current': f'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3MO&cosd={start}',
    }.items():
        # curl uses the platform TLS/network configuration; urllib timed out on this host.
        with tempfile.TemporaryDirectory() as temporary:
            headers_path = Path(temporary) / 'headers.txt'
            response = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                                       '--connect-timeout', '15', '--max-time', '45',
                                       '--dump-header', str(headers_path), url], capture_output=True, check=True)
            raw = response.stdout
            allowed_headers = {'date', 'last-modified', 'content-type', 'content-disposition', 'content-length'}
            headers = {line.split(':', 1)[0].lower(): line.split(':', 1)[1].strip()
                       for line in headers_path.read_text().splitlines()
                       if ':' in line and line.split(':', 1)[0].lower() in allowed_headers}
        observations = parse_observations(raw.decode('utf-8-sig'))
        if label == 'vintage' and any(d > args.cutoff for d, _ in observations):
            raise ValueError('vintage contains observation dates after cutoff; archive not admitted')
        filename = f'{label}.csv'
        (folder / filename).write_bytes(raw)
        records[label] = {'url': url, 'file': filename, 'sha256': hashlib.sha256(raw).hexdigest(),
                          'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                          'response_headers': headers, 'observations': len(observations)}
    metadata = {'start_date': str(start), 'series': 'DGS3MO', 'cutoff': str(args.cutoff), 'cutoff_precision': 'ALFRED calendar-date vintage; no intraday claim',
                'source': 'FRED/ALFRED; Board of Governors, H.15', 'downloads': records}
    (folder / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    main()
