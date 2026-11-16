"""Run routine checks and a local HTTP health check; never a human locked experiment."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'

def run(command, filename):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (OUT / filename).write_text(result.stdout + result.stderr)
    return {'command': command[1:], 'exit_code': result.returncode, 'evidence': f'outputs/{filename}'}

def main():
    OUT.mkdir(exist_ok=True)
    records = []
    records.append(run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], 'test-results.txt'))
    records.append(run([sys.executable, '-m', 'pip', 'check'], 'dependency-check.txt'))
    records.append(run([sys.executable, 'sec-buffett-quality/scripts/validate_known_answer.py', '--outputs', 'sec-buffett-quality/outputs'], 'sec-validation.txt'))
    records.append(run([sys.executable, 'analysis.py', '--write'], 'analysis-run.txt'))
    # Verify regeneration produces byte-identical artifacts.
    paths = [OUT / 'analysis.json', OUT / 'analysis.md']
    before = [p.read_bytes() for p in paths]
    repeat = subprocess.run([sys.executable, 'analysis.py', '--write'], cwd=ROOT, capture_output=True)
    deterministic = repeat.returncode == 0 and before == [p.read_bytes() for p in paths]
    health = {'status': 'FAIL'}
    process = None
    try:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        with (OUT / 'server.log').open('w') as log:
            process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.address', '127.0.0.1',
                                        '--server.port', str(port), '--server.headless', 'true', '--browser.gatherUsageStats', 'false'],
                                       cwd=ROOT, stdout=log, stderr=log)
            for _ in range(40):
                if process.poll() is not None:
                    break
                try:
                    with urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=1) as response:
                        body = response.read().decode()
                        if response.status == 200 and body == 'ok':
                            health = {'status': 'PASS', 'http_code': response.status, 'body': body,
                                      'note': 'HTTP health plus Streamlit AppTest; not a human usability review'}
                            break
                except OSError:
                    time.sleep(.25)
    except OSError as error:
        health['error'] = str(error)
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    import streamlit, numpy
    source_paths = sorted(list(ROOT.glob('*.py')) + list((ROOT/'tests').glob('*.py')) + list((ROOT/'docs').glob('*.md')) +
                          [ROOT/'README.md', ROOT/'policy.json', ROOT/'requirements-lock.txt', ROOT/'prices.csv'])
    result = {'scope': 'Routine AI-assisted verification, not designated Locked Changed-Input execution',
              'executed_at_utc': datetime.now(timezone.utc).isoformat(),
              'python': platform.python_version(), 'platform': platform.platform(),
              'streamlit': streamlit.__version__, 'numpy': numpy.__version__,
              'base_git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'submission_freeze': 'Not committed or pushed by this verification',
              'checks': records, 'deterministic_analysis': deterministic, 'server_health': health,
              'source_sha256': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}}
    result['passed'] = all(r['exit_code']==0 for r in records) and deterministic and health['status']=='PASS'
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
