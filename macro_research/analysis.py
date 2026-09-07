"""Econometric analysis built on top of the macro panel.

The functions here are deliberately small and composable so they can be unit
tested and reused from both the CLI and the Streamlit dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass
class RegressionResult:
    """Container for a simple ordinary-least-squares fit."""

    slope: float
    intercept: float
    r_squared: float
    n_obs: int


@dataclass
class AnalysisReport:
    """Aggregated results produced by :func:`summarize`."""

    okun: RegressionResult
    phillips_correlation: float
    latest_gdp_growth: float
    latest_inflation: float
    latest_unemployment: float
    latest_policy_rate: float


def add_derived_series(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``data`` with year-over-year growth columns added.

    Adds ``gdp_growth`` and ``inflation`` (both in percent, year over year) and
    ``unemployment_change`` (percentage-point change year over year).
    """
    required = {"real_gdp", "cpi", "unemployment_rate"}
    missing = required - set(data.columns)
    if missing:
        raise KeyError(f"missing required columns: {sorted(missing)}")

    enriched = data.copy()
    enriched["gdp_growth"] = enriched["real_gdp"].pct_change(12) * 100.0
    enriched["inflation"] = enriched["cpi"].pct_change(12) * 100.0
    enriched["unemployment_change"] = enriched["unemployment_rate"].diff(12)
    return enriched


def _ols(y: pd.Series, x: pd.Series) -> RegressionResult:
    frame = pd.concat([y, x], axis=1).dropna()
    if len(frame) < 3:
        raise ValueError("not enough overlapping observations for a regression")

    endog = frame.iloc[:, 0].to_numpy()
    exog = sm.add_constant(frame.iloc[:, 1].to_numpy())
    model = sm.OLS(endog, exog).fit()
    return RegressionResult(
        slope=float(model.params[1]),
        intercept=float(model.params[0]),
        r_squared=float(model.rsquared),
        n_obs=int(model.nobs),
    )


def okuns_law(data: pd.DataFrame) -> RegressionResult:
    """Estimate Okun's law: change in unemployment vs. GDP growth.

    A negative slope is the expected sign: faster growth lowers unemployment.
    """
    enriched = add_derived_series(data)
    return _ols(enriched["unemployment_change"], enriched["gdp_growth"])


def phillips_curve_correlation(data: pd.DataFrame) -> float:
    """Return the correlation between unemployment and inflation.

    The classic Phillips curve predicts a negative relationship.
    """
    enriched = add_derived_series(data)
    frame = enriched[["unemployment_rate", "inflation"]].dropna()
    if len(frame) < 3:
        raise ValueError("not enough overlapping observations for a correlation")
    return float(frame["unemployment_rate"].corr(frame["inflation"]))


def _latest_valid(series: pd.Series) -> float:
    valid = series.dropna()
    if valid.empty:
        return float("nan")
    return float(valid.iloc[-1])


def summarize(data: pd.DataFrame) -> AnalysisReport:
    """Compute the full :class:`AnalysisReport` for the given panel."""
    enriched = add_derived_series(data)
    return AnalysisReport(
        okun=okuns_law(data),
        phillips_correlation=phillips_curve_correlation(data),
        latest_gdp_growth=_latest_valid(enriched["gdp_growth"]),
        latest_inflation=_latest_valid(enriched["inflation"]),
        latest_unemployment=_latest_valid(enriched["unemployment_rate"]),
        latest_policy_rate=_latest_valid(enriched["policy_rate"]),
    )


def format_report(report: AnalysisReport) -> str:
    """Render an :class:`AnalysisReport` as a human-readable text block."""
    lines = [
        "Macro_Research summary",
        "======================",
        "",
        "Latest readings (year-over-year where applicable):",
        f"  Real GDP growth   : {report.latest_gdp_growth:6.2f} %",
        f"  CPI inflation      : {report.latest_inflation:6.2f} %",
        f"  Unemployment rate  : {report.latest_unemployment:6.2f} %",
        f"  Policy rate        : {report.latest_policy_rate:6.2f} %",
        "",
        "Okun's law (Δ unemployment ~ GDP growth):",
        f"  slope     : {report.okun.slope:+.4f} (expected negative)",
        f"  intercept : {report.okun.intercept:+.4f}",
        f"  R-squared : {report.okun.r_squared:.4f}",
        f"  n         : {report.okun.n_obs}",
        "",
        "Phillips curve (unemployment vs. inflation):",
        f"  correlation : {report.phillips_correlation:+.4f}",
    ]
    return "\n".join(lines)
