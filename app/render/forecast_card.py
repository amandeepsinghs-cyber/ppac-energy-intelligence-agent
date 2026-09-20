"""A2UI v0.9 component tree for 36-Month SARIMAX Econometric Forecast Card.

Renders live fuel demand forecasting with confidence intervals and an inline
high-resolution chart image in Gemini Enterprise chat.
"""

from typing import Any, Dict, List
from app.contracts import ForecastResultSummary

ROOT_CARD_ID: str = "root"
ROOT_COLUMN_ID: str = "forecast-column"


def _text(component_id: str, text: str, variant: str = "body") -> Dict[str, Any]:
    return {
        "id": component_id,
        "component": "Text",
        "text": text,
        "variant": variant,
    }


def build_forecast_components(summary: ForecastResultSummary) -> List[Dict[str, Any]]:
    """Build the A2UI component list for live SARIMAX forecasting."""
    children: List[str] = []
    components: List[Dict[str, Any]] = []

    def add(component: Dict[str, Any]) -> None:
        components.append(component)
        children.append(component["id"])

    # Header
    h_label = f"{summary.horizon_months}-Month" if summary.horizon_months else "12-Month"
    add(_text("fc-title", f"SARIMAX {h_label} Econometric Forecast: {summary.product_name}", "h3"))
    add(
        _text(
            "fc-subtitle",
            f"Baseline: {summary.baseline_month} ({summary.baseline_tmt:,.0f} TMT)  ·  Model: Seasonal ARIMA (1,1,1)x(1,1,1)12",
            "caption",
        )
    )
    # Prominent high-resolution publication plot mounted at top of card
    if summary.chart_image_base64:
        data_uri = summary.chart_image_base64
        if not data_uri.startswith("data:image"):
            data_uri = f"data:image/png;base64,{data_uri}"

        chart_component = {
            "id": "fc-chart-img",
            "component": "Image",
            "url": data_uri,
            "description": summary.chart_title,
            "fit": "contain",
            "variant": "largeFeature",
        }
        components.append(chart_component)
        children.append("fc-chart-img")
        add({"id": "fc-div-chart", "component": "Divider"})

    # Key Quantitative Projections
    add(_text("fc-proj-hdr", "Econometric Projection & Growth Trajectory", "h5"))
    add(
        _text(
            "fc-proj-body",
            f"• {h_label} Projected Volume: {summary.forecast_36m_end_tmt:,.0f} TMT / month\n"
            f"• Seasonally Adjusted Annual Growth: +{summary.growth_cagr_pct:.1f}% YoY\n"
            f"• Confidence Intervals: 80% and 95% uncertainty bands modeled\n"
            f"• Seasonality: Accounting for pre-monsoon agricultural harvesting & Q3 festive surges",
            "body",
        )
    )

    root_card = {
        "id": ROOT_CARD_ID,
        "component": "Card",
        "child": ROOT_COLUMN_ID,
    }

    column_component = {
        "id": ROOT_COLUMN_ID,
        "component": "Column",
        "children": children,
    }

    return [root_card, column_component, *components]
