import numpy as np
import pandas as pd
import pytest

from macro_research.data import INDICATORS, load_macro_data


def test_shape_and_columns():
    df = load_macro_data(periods=120)
    assert len(df) == 120
    assert list(df.columns) == INDICATORS
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "date"


def test_deterministic_with_seed():
    a = load_macro_data(periods=60, seed=7)
    b = load_macro_data(periods=60, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_different_seed_changes_output():
    a = load_macro_data(periods=60, seed=1)
    b = load_macro_data(periods=60, seed=2)
    assert not np.allclose(a["real_gdp"].to_numpy(), b["real_gdp"].to_numpy())


def test_ranges_are_plausible():
    df = load_macro_data(periods=300)
    assert df["unemployment_rate"].between(2.5, 12.0).all()
    assert df["policy_rate"].between(0.0, 12.0).all()
    assert (df["real_gdp"] > 0).all()
    assert (df["cpi"] > 0).all()


def test_invalid_periods():
    with pytest.raises(ValueError):
        load_macro_data(periods=0)
