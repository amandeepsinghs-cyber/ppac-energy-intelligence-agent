"""Vega-Lite v5 specification generator for PPAC pricing benchmarks.

Produces valid Vega-Lite specifications rendered by Gemini Enterprise's @safe_vega library.
"""

from typing import Any, Dict, List
from app.contracts import MarketBenchmarkSummary

SPEC_KEY: str = "spec"
SPEC_POINTER: str = f"/{SPEC_KEY}"


def build_pricing_vega_spec(summary: MarketBenchmarkSummary) -> Dict[str, Any]:
    """Build an interactive Vega-Lite v5 horizontal bar chart for PPAC pricing and market benchmarks."""
    focus = (getattr(summary, "focus", "overview") or "overview").lower()

    if any(k in focus for k in ["retail", "pump", "tax", "buildup", "vat", "delhi"]):
        # Retail build-up breakdown (Petrol MS vs Diesel HSD)
        plot_data = [
            {"component": "Base Price", "amount": 55.42, "fuel": "Petrol (MS) - ₹94.72/L"},
            {"component": "Central Excise", "amount": 19.90, "fuel": "Petrol (MS) - ₹94.72/L"},
            {"component": "Dealer Commission", "amount": 4.41, "fuel": "Petrol (MS) - ₹94.72/L"},
            {"component": "State VAT (Delhi)", "amount": 15.39, "fuel": "Petrol (MS) - ₹94.72/L"},
            {"component": "Base Price", "amount": 56.25, "fuel": "Diesel (HSD) - ₹87.62/L"},
            {"component": "Central Excise", "amount": 15.80, "fuel": "Diesel (HSD) - ₹87.62/L"},
            {"component": "Dealer Commission", "amount": 3.00, "fuel": "Diesel (HSD) - ₹87.62/L"},
            {"component": "State VAT (Delhi)", "amount": 12.57, "fuel": "Diesel (HSD) - ₹87.62/L"},
        ]
        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"Delhi Retail Fuel Price Build-Up ({summary.period_id})",
            "width": 420,
            "height": 200,
            "padding": {"left": 10, "right": 20, "top": 10, "bottom": 10},
            "data": {"values": plot_data},
            "mark": {"type": "bar", "cornerRadiusEnd": 3},
            "encoding": {
                "y": {"field": "fuel", "type": "nominal", "axis": {"title": None, "labelFontSize": 11}},
                "x": {"field": "amount", "type": "quantitative", "axis": {"title": "Price Build-Up (₹ / Litre)", "grid": True}},
                "color": {
                    "field": "component",
                    "type": "nominal",
                    "scale": {
                        "domain": ["Base Price", "Central Excise", "Dealer Commission", "State VAT (Delhi)"],
                        "range": ["#1B365D", "#DC2626", "#F59E0B", "#10B981"],
                    },
                    "legend": {"title": "Cost Component", "orient": "bottom"},
                },
                "tooltip": [
                    {"field": "fuel", "type": "nominal", "title": "Fuel"},
                    {"field": "component", "type": "nominal", "title": "Component"},
                    {"field": "amount", "type": "quantitative", "title": "Amount (₹/L)", "format": "₹.2f"},
                ],
            },
        }

    elif any(k in focus for k in ["gas", "apm", "hpht", "kirit"]):
        plot_data = [
            {"benchmark": "Domestic APM Natural Gas", "price": summary.apm_gas_usd_mmbtu, "color": "#8B5CF6"},
            {"benchmark": "Deepwater / HP-HT Gas", "price": summary.hpht_gas_ceiling_usd_mmbtu, "color": "#EC4899"},
        ]
        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"PPAC Natural Gas Ceilings ({summary.period_id})",
            "width": 420,
            "height": 160,
            "padding": {"left": 10, "right": 20, "top": 10, "bottom": 10},
            "data": {"values": plot_data},
            "layer": [
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 4},
                    "encoding": {
                        "y": {"field": "benchmark", "type": "nominal", "axis": {"title": None, "labelFontSize": 11}, "sort": "-x"},
                        "x": {"field": "price", "type": "quantitative", "axis": {"title": "Price ($ / MMBTU)", "grid": True}, "scale": {"domain": [0, 12], "zero": True, "nice": True}},
                        "color": {"field": "benchmark", "type": "nominal", "scale": {"domain": ["Domestic APM Natural Gas", "Deepwater / HP-HT Gas"], "range": ["#8B5CF6", "#EC4899"]}, "legend": None},
                    },
                },
                {
                    "mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold", "fontSize": 11},
                    "encoding": {
                        "y": {"field": "benchmark", "type": "nominal", "sort": "-x"},
                        "x": {"field": "price", "type": "quantitative"},
                        "text": {"field": "price", "type": "quantitative", "format": "$.2f"},
                    },
                },
            ],
        }

    elif any(k in focus for k in ["consumption", "demand", "pol"]):
        other_tmt = max(0.0, summary.pol_consumption_tmt - (summary.hsd_consumption_tmt + summary.ms_consumption_tmt + summary.lpg_consumption_tmt))
        plot_data = [
            {"product": "High Speed Diesel (HSD)", "volume": summary.hsd_consumption_tmt, "color": "#1B365D"},
            {"product": "Motor Spirit (Petrol)", "volume": summary.ms_consumption_tmt, "color": "#2563EB"},
            {"product": "Subsidized Domestic LPG", "volume": summary.lpg_consumption_tmt, "color": "#10B981"},
            {"product": "Other POL (ATF/Naphtha)", "volume": other_tmt, "color": "#64748B"},
        ]
        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"PPAC National POL Consumption ({summary.period_id})",
            "width": 420,
            "height": 190,
            "padding": {"left": 10, "right": 20, "top": 10, "bottom": 10},
            "data": {"values": plot_data},
            "layer": [
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 4},
                    "encoding": {
                        "y": {"field": "product", "type": "nominal", "axis": {"title": None, "labelFontSize": 11}, "sort": "-x"},
                        "x": {"field": "volume", "type": "quantitative", "axis": {"title": "Consumption Volume (TMT)", "grid": True}, "scale": {"zero": True, "nice": True}},
                        "color": {"field": "product", "type": "nominal", "scale": {"domain": [d["product"] for d in plot_data], "range": [d["color"] for d in plot_data]}, "legend": None},
                    },
                },
                {
                    "mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold", "fontSize": 10.5},
                    "encoding": {
                        "y": {"field": "product", "type": "nominal", "sort": "-x"},
                        "x": {"field": "volume", "type": "quantitative"},
                        "text": {"field": "volume", "type": "quantitative", "format": ",.0f"},
                    },
                },
            ],
        }

    else:
        # Default: Crude oil benchmarks ($/bbl)
        crude_pts = [
            {"benchmark": "Brent Dated (Sweet)", "price": summary.brent_dated_usd_bbl, "color": "#2563EB"},
            {"benchmark": "Indian Crude Basket (ICB)", "price": summary.icb_price_usd_bbl, "color": "#10B981"},
            {"benchmark": "Oman & Dubai (Sour)", "price": summary.oman_dubai_sour_usd_bbl, "color": "#F59E0B"},
        ]
        min_p = min(summary.brent_dated_usd_bbl, summary.icb_price_usd_bbl, summary.oman_dubai_sour_usd_bbl)
        max_p = max(summary.brent_dated_usd_bbl, summary.icb_price_usd_bbl, summary.oman_dubai_sour_usd_bbl)
        domain_min = max(0.0, float(int(min_p - 8)))
        domain_max = float(int(max_p + 8))

        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"PPAC Hydrocarbon Crude Benchmarks ({summary.period_id})",
            "width": 420,
            "height": 170,
            "padding": {"left": 10, "right": 20, "top": 10, "bottom": 10},
            "data": {"values": crude_pts},
            "layer": [
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 4},
                    "encoding": {
                        "y": {"field": "benchmark", "type": "nominal", "axis": {"title": None, "labelFontSize": 11.5}, "sort": "-x"},
                        "x": {
                            "field": "price",
                            "type": "quantitative",
                            "axis": {"title": "Price (USD / bbl)", "format": "$.2f", "grid": True},
                            "scale": {"domain": [domain_min, domain_max], "zero": False, "nice": True},
                        },
                        "color": {
                            "field": "benchmark",
                            "type": "nominal",
                            "scale": {
                                "domain": ["Brent Dated (Sweet)", "Indian Crude Basket (ICB)", "Oman & Dubai (Sour)"],
                                "range": ["#2563EB", "#10B981", "#F59E0B"],
                            },
                            "legend": None,
                        },
                    },
                },
                {
                    "mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold", "fontSize": 11},
                    "encoding": {
                        "y": {"field": "benchmark", "type": "nominal", "sort": "-x"},
                        "x": {"field": "price", "type": "quantitative"},
                        "text": {"field": "price", "type": "quantitative", "format": "$.2f"},
                    },
                },
            ],
        }
