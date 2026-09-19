"""Script to render all 6 canonical sovereign charts for PPAC Ready Reckoner."""

import json
from pathlib import Path
from app.tsa.modern_chart_engine import ModernChartEngine

def render_charts(period_id="2026-08"):
    base_dir = Path(__file__).resolve().parent
    chart_engine = ModernChartEngine()

    dest_dirs = [
        base_dir / "data_lake" / "og_sovereign_ppac_data" / "3_artifacts" / period_id / "charts",
        base_dir / "data_lake" / "p40_planning_data" / "3_artifacts" / period_id / "charts",
    ]

    market_file = base_dir / "data_lake" / "og_sovereign_ppac_data" / "1_raw_inbox" / "live_market_api" / f"live_quotes_{period_id}.json"
    market_data = {}
    if market_file.exists():
        market_data = json.loads(market_file.read_text())

    for cdir in dest_dirs:
        cdir.mkdir(parents=True, exist_ok=True)
        chart_engine.render_crude_production_operator_pie(cdir / "crude_operator_pie.png")
        chart_engine.render_pol_production_vs_consumption(cdir / "pol_prod_cons_bar.png")
        chart_engine.render_lpg_marketing_pie(cdir / "lpg_marketing_pie.png")
        chart_engine.render_natural_gas_regime_pie(cdir / "natural_gas_regime_pie.png")
        chart_engine.render_price_buildup(cdir / "price_buildup.png")
        chart_engine.render_demand_projection(cdir / "hsd_demand_projection.png")
        if market_data:
            chart_engine.render_crude_spot_trend(market_data, cdir / "brent_wti_spot_trend.png")

        print(f"Rendered all 7 charts in: {cdir}")

if __name__ == "__main__":
    render_charts()
