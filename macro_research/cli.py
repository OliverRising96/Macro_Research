"""Command-line entry point for running the macro analysis.

Usage::

    python -m macro_research.cli --output report.txt --chart chart.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend for servers / CI
import matplotlib.pyplot as plt  # noqa: E402  (must follow backend selection)

from macro_research.analysis import add_derived_series, format_report, summarize
from macro_research.data import load_macro_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Macro_Research analysis.")
    parser.add_argument("--start", default="2000-01-01", help="First month (YYYY-MM-DD).")
    parser.add_argument("--periods", type=int, default=300, help="Number of monthly observations.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for the dataset.")
    parser.add_argument("--output", type=Path, default=None, help="Write the text report to this file.")
    parser.add_argument("--chart", type=Path, default=None, help="Save an overview chart to this path.")
    return parser


def save_chart(data, path: Path) -> None:
    enriched = add_derived_series(data)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    fig.suptitle("Macro_Research overview", fontsize=14)

    axes[0, 0].plot(enriched.index, enriched["real_gdp"], color="#1f77b4")
    axes[0, 0].set_title("Real GDP (index)")

    axes[0, 1].plot(enriched.index, enriched["inflation"], color="#d62728")
    axes[0, 1].set_title("CPI inflation (YoY %)")

    axes[1, 0].plot(enriched.index, enriched["unemployment_rate"], color="#2ca02c")
    axes[1, 0].set_title("Unemployment rate (%)")

    axes[1, 1].plot(enriched.index, enriched["policy_rate"], color="#9467bd")
    axes[1, 1].set_title("Policy rate (%)")

    for ax in axes.flat:
        ax.grid(True, alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data = load_macro_data(start=args.start, periods=args.periods, seed=args.seed)
    report = summarize(data)
    text = format_report(report)

    print(text)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"\nWrote report to {args.output}")

    if args.chart is not None:
        save_chart(data, args.chart)
        print(f"Wrote chart to {args.chart}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
