"""Interactive Streamlit dashboard for the Macro_Research panel.

Run locally with::

    streamlit run macro_research/dashboard.py

The dashboard lets you adjust the sample window and random seed, then explore
the indicator series and the headline econometric results.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from macro_research.analysis import add_derived_series, summarize
from macro_research.data import load_macro_data

st.set_page_config(page_title="Macro_Research", page_icon="📈", layout="wide")


@st.cache_data
def _cached_data(start: str, periods: int, seed: int) -> pd.DataFrame:
    return load_macro_data(start=start, periods=periods, seed=seed)


def main() -> None:
    st.title("📈 Macro_Research dashboard")
    st.caption(
        "A reproducible macroeconomic panel with Okun's-law and Phillips-curve "
        "diagnostics. Data is synthesized deterministically so the app runs "
        "fully offline."
    )

    with st.sidebar:
        st.header("Sample")
        start = st.text_input("Start month", value="2000-01-01")
        periods = st.slider("Months", min_value=60, max_value=480, value=300, step=12)
        seed = st.number_input("Random seed", min_value=0, max_value=9999, value=42, step=1)

    data = _cached_data(start, int(periods), int(seed))
    enriched = add_derived_series(data)
    report = summarize(data)

    st.subheader("Latest readings")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Real GDP growth (YoY)", f"{report.latest_gdp_growth:.2f}%")
    c2.metric("CPI inflation (YoY)", f"{report.latest_inflation:.2f}%")
    c3.metric("Unemployment", f"{report.latest_unemployment:.2f}%")
    c4.metric("Policy rate", f"{report.latest_policy_rate:.2f}%")

    st.subheader("Indicator series")
    left, right = st.columns(2)
    left.plotly_chart(
        px.line(enriched, y="real_gdp", title="Real GDP (index)"),
        use_container_width=True,
    )
    right.plotly_chart(
        px.line(enriched, y="inflation", title="CPI inflation (YoY %)"),
        use_container_width=True,
    )
    left.plotly_chart(
        px.line(enriched, y="unemployment_rate", title="Unemployment rate (%)"),
        use_container_width=True,
    )
    right.plotly_chart(
        px.line(enriched, y="policy_rate", title="Policy rate (%)"),
        use_container_width=True,
    )

    st.subheader("Econometric diagnostics")
    diag_left, diag_right = st.columns(2)

    with diag_left:
        st.markdown("**Okun's law** — Δ unemployment vs. GDP growth")
        okun_df = enriched[["gdp_growth", "unemployment_change"]].dropna()
        scatter = px.scatter(
            okun_df,
            x="gdp_growth",
            y="unemployment_change",
            opacity=0.6,
            labels={
                "gdp_growth": "GDP growth (YoY %)",
                "unemployment_change": "Δ unemployment (pp)",
            },
        )
        x_vals = okun_df["gdp_growth"]
        y_fit = report.okun.intercept + report.okun.slope * x_vals
        scatter.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_fit,
                mode="lines",
                name="OLS fit",
                line=dict(color="crimson"),
            )
        )
        st.plotly_chart(scatter, use_container_width=True)
        st.write(
            f"slope = **{report.okun.slope:+.4f}**, "
            f"R² = **{report.okun.r_squared:.3f}**, n = {report.okun.n_obs}"
        )

    with diag_right:
        st.markdown("**Phillips curve** — unemployment vs. inflation")
        phil_df = enriched[["unemployment_rate", "inflation"]].dropna()
        st.plotly_chart(
            px.scatter(
                phil_df,
                x="unemployment_rate",
                y="inflation",
                opacity=0.6,
                trendline="ols",
                labels={
                    "unemployment_rate": "Unemployment (%)",
                    "inflation": "Inflation (YoY %)",
                },
            ),
            use_container_width=True,
        )
        st.write(f"correlation = **{report.phillips_correlation:+.4f}**")

    with st.expander("Show raw data"):
        st.dataframe(enriched.tail(24))


if __name__ == "__main__":
    main()
else:
    # Streamlit executes the module top-to-bottom, so run immediately.
    main()
