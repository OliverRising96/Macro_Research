import math

import pytest

from macro_research.analysis import (
    add_derived_series,
    format_report,
    okuns_law,
    phillips_curve_correlation,
    summarize,
)
from macro_research.data import load_macro_data


def test_add_derived_series_columns():
    df = load_macro_data(periods=120)
    enriched = add_derived_series(df)
    for col in ("gdp_growth", "inflation", "unemployment_change"):
        assert col in enriched.columns
    # First 12 months of YoY series must be NaN.
    assert enriched["gdp_growth"].iloc[:12].isna().all()
    assert enriched["gdp_growth"].iloc[12:].notna().all()


def test_add_derived_series_missing_column():
    df = load_macro_data(periods=60).drop(columns=["cpi"])
    with pytest.raises(KeyError):
        add_derived_series(df)


def test_okuns_law_negative_slope():
    df = load_macro_data(periods=300)
    result = okuns_law(df)
    # Okun's law: faster growth -> lower unemployment (negative slope).
    assert result.slope < 0
    assert 0.0 <= result.r_squared <= 1.0
    assert result.n_obs > 100


def test_phillips_correlation_in_range():
    df = load_macro_data(periods=300)
    corr = phillips_curve_correlation(df)
    assert -1.0 <= corr <= 1.0


def test_summarize_and_format():
    df = load_macro_data(periods=300)
    report = summarize(df)
    assert not math.isnan(report.latest_gdp_growth)
    assert not math.isnan(report.latest_inflation)
    text = format_report(report)
    assert "Macro_Research summary" in text
    assert "Okun's law" in text
    assert "Phillips curve" in text
