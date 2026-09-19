"""Vega-Lite v5 specification generator for PPAC pricing benchmarks.

Produces valid Vega-Lite specifications rendered by Gemini Enterprise's @safe_vega library.
"""

from typing import Any, Dict
from app.contracts import MarketBenchmarkSummary

SPEC_KEY: str = "spec"
SPEC_POINTER: str = f"/{SPEC_KEY}"


def build_pricing_vega_spec(summary: MarketBenchmarkSummary) -> Dict[str, Any]:
    """Build a Vega-Lite v5 horizontal bar chart for August 2026 crude oil benchmarks."""
    min_price = min(summary.brent_dated_usd_bbl, summary.icb_price_usd_bbl, summary.oman_dubai_sour_usd_bbl)
    domain_min = max(0.0, round(min_price - 10.0, 0))
    domain_max = round(max(summary.brent_dated_usd_bbl, summary.icb_price_usd_bbl) + 5.0, 0)

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": f"PPAC Hydrocarbon Benchmarks ({summary.period_id})",
        "width": 380,
        "height": 160,
        "data": {
            "values": [
                {
                    "benchmark": "Brent Dated (Sweet)",
                    "price": summary.brent_dated_usd_bbl,
                    "color": "#1A73E8",
                },
                {
                    "benchmark": "Indian Crude Basket",
                    "price": summary.icb_price_usd_bbl,
                    "color": "#0D904F",
                },
                {
                    "benchmark": "Oman & Dubai (Sour)",
                    "price": summary.oman_dubai_sour_usd_bbl,
                    "color": "#E37400",
                },
            ]
        },
        "layer": [
            {
                "mark": {"type": "bar", "cornerRadiusEnd": 4},
                "encoding": {
                    "y": {
                        "field": "benchmark",
                        "type": "nominal",
                        "axis": {"title": None, "labelFontSize": 12},
                        "sort": "-x",
                    },
                    "x": {
                        "field": "price",
                        "type": "quantitative",
                        "axis": {"title": "Price (USD / bbl)", "format": "$.2f", "grid": True},
                        "scale": {"domain": [domain_min, domain_max]},
                    },
                    "color": {
                        "field": "benchmark",
                        "type": "nominal",
                        "scale": {
                            "domain": [
                                "Brent Dated (Sweet)",
                                "Indian Crude Basket",
                                "Oman & Dubai (Sour)",
                            ],
                            "range": ["#1A73E8", "#0D904F", "#E37400"],
                        },
                        "legend": None,
                    },
                },
            },
            {
                "mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold"},
                "encoding": {
                    "y": {"field": "benchmark", "type": "nominal", "sort": "-x"},
                    "x": {"field": "price", "type": "quantitative"},
                    "text": {"field": "price", "type": "quantitative", "format": "$.2f"},
                },
            },
        ],
    }
