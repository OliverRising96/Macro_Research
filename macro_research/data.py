"""Reproducible macroeconomic dataset.

Real macro research pulls series from providers such as FRED. To keep this
project self-contained and runnable offline (no API keys or network egress
required), :func:`load_macro_data` synthesizes a realistic monthly panel with a
deterministic random seed. The generator is intentionally simple but captures
the co-movements that the analysis module relies on:

- trending real GDP with business-cycle fluctuations,
- a gently rising price level (CPI),
- an unemployment rate that moves inversely with the output gap (Okun's law),
- a policy rate that reacts to inflation and unemployment (a Taylor-style rule).

Swap :func:`load_macro_data` for a real provider by returning a DataFrame with
the same columns and a monthly ``DatetimeIndex``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

INDICATORS = ["real_gdp", "cpi", "unemployment_rate", "policy_rate"]


def load_macro_data(
    start: str = "2000-01-01",
    periods: int = 300,
    seed: int = 42,
) -> pd.DataFrame:
    """Return a monthly panel of macroeconomic indicators.

    Parameters
    ----------
    start:
        First month of the sample (parsed by :func:`pandas.date_range`).
    periods:
        Number of monthly observations to generate.
    seed:
        Seed for the random generator, making the output fully reproducible.

    Returns
    -------
    pandas.DataFrame
        Indexed by month with the columns listed in :data:`INDICATORS`.
    """
    if periods <= 0:
        raise ValueError("periods must be a positive integer")

    rng = np.random.default_rng(seed)
    index = pd.date_range(start=start, periods=periods, freq="MS")
    t = np.arange(periods)

    # Real GDP: exponential trend + business cycle + small noise.
    trend = 100.0 * np.exp(0.0018 * t)
    cycle = 2.5 * np.sin(2 * np.pi * t / 84.0)
    gdp_noise = rng.normal(0.0, 0.4, size=periods).cumsum() * 0.15
    real_gdp = trend + cycle + gdp_noise

    # Output gap drives unemployment via an Okun's-law relationship.
    log_gdp = np.log(real_gdp)
    potential = np.polyval(np.polyfit(t, log_gdp, 1), t)
    output_gap = (log_gdp - potential) * 100.0
    unemployment = 5.5 - 0.5 * output_gap + rng.normal(0.0, 0.15, size=periods)
    unemployment = np.clip(unemployment, 2.5, 12.0)

    # CPI: cumulative inflation with a modest cyclical component.
    monthly_infl = 0.0018 + 0.0009 * np.sin(2 * np.pi * t / 60.0)
    monthly_infl += rng.normal(0.0, 0.0006, size=periods)
    cpi = 100.0 * np.exp(np.cumsum(monthly_infl))

    # Policy rate: Taylor-style reaction to inflation and unemployment.
    yoy_infl = np.zeros(periods)
    yoy_infl[12:] = (cpi[12:] / cpi[:-12] - 1.0) * 100.0
    policy_rate = 1.0 + 1.5 * yoy_infl - 0.5 * (unemployment - 5.5)
    policy_rate = np.clip(policy_rate + rng.normal(0.0, 0.1, size=periods), 0.0, 12.0)

    frame = pd.DataFrame(
        {
            "real_gdp": real_gdp,
            "cpi": cpi,
            "unemployment_rate": unemployment,
            "policy_rate": policy_rate,
        },
        index=index,
    )
    frame.index.name = "date"
    return frame
