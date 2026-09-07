# Macro_Research

A small, reproducible toolkit for macroeconomic time-series research. It ships a
deterministic macro dataset, a set of econometric diagnostics, a command-line
report generator, and an interactive [Streamlit](https://streamlit.io)
dashboard.

The dataset is synthesized with a fixed random seed, so the project runs fully
offline — no API keys or network access required. Swap
`macro_research.data.load_macro_data` for a real provider (e.g. FRED) to work
with live data while keeping the rest of the pipeline unchanged.

## Project layout

| Path | Purpose |
| --- | --- |
| `macro_research/data.py` | Reproducible monthly panel: real GDP, CPI, unemployment, policy rate. |
| `macro_research/analysis.py` | Derived series plus Okun's-law regression and Phillips-curve correlation. |
| `macro_research/cli.py` | `python -m macro_research.cli` — prints a report and can save a chart. |
| `macro_research/dashboard.py` | Streamlit dashboard for interactive exploration. |
| `tests/` | `pytest` suite covering the data and analysis modules. |

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the tests

```bash
pytest
```

### Generate a report and chart from the CLI

```bash
python -m macro_research.cli --output report.txt --chart overview.png
```

### Launch the dashboard

```bash
streamlit run macro_research/dashboard.py
```

Then open http://localhost:8501 in your browser.

## Cloud Agent environment

This repository is configured for Cursor Cloud Agents via
`.cursor/environment.json`:

- **install** creates a virtual environment and installs pinned dependencies.
- A **terminal** launches the Streamlit dashboard on port `8501`.
