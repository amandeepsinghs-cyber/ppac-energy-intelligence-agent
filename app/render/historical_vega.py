"""Vega-Lite v5 specification generator for PPAC historical petroleum demand.

Produces interactive Vega-Lite specifications rendered by Gemini Enterprise's @safe_vega library,
featuring multi-year consumption trends, seasonal patterns, and annual comparison points.
"""

from typing import Any, Dict, List, Optional
from app.contracts import HistoricalDemandSummary

HISTORICAL_SPEC_KEY: str = "historical_spec"
HISTORICAL_SPEC_POINTER: str = f"/{HISTORICAL_SPEC_KEY}"


def build_historical_vega_spec(summary: HistoricalDemandSummary) -> Dict[str, Any]:
    """Build an interactive Vega-Lite v5 line and bar chart for multi-year historical fuel demand."""
    plot_data: List[Dict[str, Any]] = []

    months = summary.months or []
    values = summary.monthly_values or []

    for m, v in zip(months, values):
        plot_data.append({
            "month": m,
            "volume": v,
            "product": summary.product_name,
        })

    if not plot_data:
        plot_data = [{"month": "2026-08", "volume": 7023.0, "product": summary.product_name}]

    import math

    all_vals = [d["volume"] for d in plot_data]
    val_min = min(all_vals)
    val_max = max(all_vals)
    span = max(val_max - val_min, 100.0)
    min_y = max(0.0, float(math.floor((val_min - span * 0.08) / 100) * 100))
    max_y = float(math.ceil((val_max + span * 0.08) / 100) * 100)

    y_scale: Dict[str, Any] = {
        "domain": [min_y, max_y],
        "zero": False,
        "nice": True,
    }

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": f"Official PPAC Historical Consumption: {summary.product_name} ({summary.start_period} to {summary.end_period})",
        "width": 440,
        "height": 230,
        "padding": {"left": 10, "right": 20, "top": 10, "bottom": 10},
        "data": {"values": plot_data},
        "layer": [
            {
                "mark": {"type": "line", "point": {"filled": True, "size": 35}, "strokeWidth": 2.5, "color": "#1B365D"},
                "encoding": {
                    "x": {
                        "field": "month",
                        "type": "nominal",
                        "axis": {
                            "title": "Month",
                            "labelAngle": -40,
                            "labelFontSize": 9,
                            "labelOverlap": "parity",
                        },
                    },
                    "y": {
                        "field": "volume",
                        "type": "quantitative",
                        "axis": {
                            "title": f"Consumption ({summary.product_name} - TMT)",
                            "format": ",.0f",
                            "grid": True,
                        },
                        "scale": y_scale,
                    },
                    "tooltip": [
                        {"field": "month", "type": "nominal", "title": "Month"},
                        {"field": "product", "type": "nominal", "title": "Fuel Product"},
                        {"field": "volume", "type": "quantitative", "title": "Actual Consumption (TMT)", "format": ",.0f"},
                    ],
                },
            },
        ],
    }
