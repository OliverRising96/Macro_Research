"""Macro_Research: a small toolkit for macroeconomic time-series research.

The package provides three building blocks:

- :mod:`macro_research.data` produces a reproducible panel of macroeconomic
  indicators (real GDP, CPI, unemployment and the policy rate).
- :mod:`macro_research.analysis` derives standard research quantities such as
  year-over-year growth, an Okun's-law regression and a Phillips-curve
  correlation.
- :mod:`macro_research.dashboard` renders an interactive Streamlit dashboard on
  top of the two modules above.
"""

from macro_research.analysis import (
    AnalysisReport,
    add_derived_series,
    okuns_law,
    phillips_curve_correlation,
    summarize,
)
from macro_research.data import load_macro_data

__all__ = [
    "AnalysisReport",
    "add_derived_series",
    "load_macro_data",
    "okuns_law",
    "phillips_curve_correlation",
    "summarize",
]

__version__ = "0.1.0"
