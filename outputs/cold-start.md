# Clean installation record — November 16, 2026

A new `.venv` was created in this repository with CPython 3.14.7; it did not reuse site packages from the older coursework environment. The available explicit Python 3.14 interpreter was used because the system `python3` is 3.9.6. README now specifies 3.14 and instructs the reader to install it if unavailable.

Initial command: `python -m pip install -r requirements.txt` in the new environment. Sandbox DNS restrictions prevented access to PyPI. Authorized retry with `--no-cache-dir` downloaded and installed Streamlit 1.66.0, NumPy 2.5.4, and dependencies. `requirements-lock.txt` records the resolved environment for the README installation. `pip check` found no broken requirements.

Finance tests, Streamlit AppTest, the SEC saved-output validator, and deterministic analysis regeneration ran inside this new environment. The first localhost health check was blocked by sandbox permissions even though the other checks passed; the authorized rerun is recorded in `verification.json`.

This establishes a fresh dependency installation and executable workflow on macOS arm64 / Python 3.14.7. It does not establish installation on every OS, a human stranger's usability review, GitHub access, or Brightspace submission. Network access is required only for installation or deliberate source refresh; the main app and routine analysis use retained evidence offline.
