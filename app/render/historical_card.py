"""A2UI v0.9 component tree for Official PPAC Historical Demand Card.

Renders verified multi-year historical petroleum consumption data with interactive
VegaChart visualization and annual growth metrics in Gemini Enterprise chat.
"""

from typing import Any, Dict, List
from app.contracts import HistoricalDemandSummary
from app.render.historical_vega import HISTORICAL_SPEC_POINTER

ROOT_CARD_ID: str = "root"
ROOT_COLUMN_ID: str = "historical-column"


def _text(component_id: str, text: str, variant: str = "body") -> Dict[str, Any]:
    return {
        "id": component_id,
        "component": "Text",
        "text": text,
        "variant": variant,
    }


def build_historical_components(summary: HistoricalDemandSummary) -> List[Dict[str, Any]]:
    """Build the A2UI component list for official PPAC historical demand series."""
    children: List[str] = []
    components: List[Dict[str, Any]] = []

    def add(component: Dict[str, Any]) -> None:
        components.append(component)
        children.append(component["id"])

    # Header
    add(_text("hc-title", f"PPAC Official Historical Demand: {summary.product_name}", "h3"))
    add(
        _text(
            "hc-subtitle",
            f"Verified Ground-Truth · MoPNG PPAC Sovereign Series · {summary.start_period} to {summary.end_period}",
            "caption",
        )
    )
    # Live interactive VegaChart mounted at top of card with inlined spec
    from app.render.historical_vega import build_historical_vega_spec

    vega_spec = build_historical_vega_spec(summary)
    chart_component = {
        "id": "hc-chart-vega",
        "component": "VegaChart",
        "spec": vega_spec,
        "height": 290,
    }
    components.append(chart_component)
    children.append("hc-chart-vega")
    add({"id": "hc-div-chart", "component": "Divider"})

    # Key Multi-Year Quantitative Highlights
    annual_txt_lines = [f"• {fy}: {vol:,.0f} TMT" for fy, vol in summary.annual_summary.items()]
    annual_block = "\n".join(annual_txt_lines[:5])

    add(_text("hc-highlights-hdr", f"Multi-Year Consumption Trends ({summary.timeframe_years}-Year Window)", "h5"))
    add(
        _text(
            "hc-highlights-body",
            f"• Total Cumulative Volume: {summary.total_consumption_tmt:,.0f} TMT ({(summary.total_consumption_tmt/1000):,.1f} MMT)\n"
            f"• Monthly Consumption Average: {summary.average_monthly_tmt:,.0f} TMT / month\n"
            f"• Historical Peak Month: {summary.peak_month} ({summary.peak_volume_tmt:,.0f} TMT)\n"
            f"• Historical Trough Month: {summary.trough_month} ({summary.trough_volume_tmt:,.0f} TMT)\n"
            f"• Multi-Year CAGR: +{summary.cagr_pct:.1f}% Annualized",
            "body",
        )
    )

    # Interactive Digital Fiscal Year Data Grid
    table_lines = [
        "| Fiscal Year | Total Demand (TMT) | Equivalent (MMT) | Average / Month | Sovereign Validation Status |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ]
    for fy, vol in summary.annual_summary.items():
        mmt = vol / 1000.0
        avg_m = vol / 12.0
        table_lines.append(f"| **{fy}** | **{vol:,.1f} TMT** | {mmt:,.2f} MMT | {avg_m:,.1f} TMT | Verified MoPNG Series |")

    add({"id": "hc-div-grid", "component": "Divider"})
    add(_text("hc-grid-hdr", f"Verified Multi-Year Fiscal Matrix ({summary.timeframe_years}-Year Series)", "h5"))
    add(_text("hc-grid-table", "\n".join(table_lines), "body"))



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
