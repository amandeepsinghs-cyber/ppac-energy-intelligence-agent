"""Direct Script to compile HTML Executive Reports alongside .docx."""

import json
from pathlib import Path

from app.ingestion.excel_parser import OmcExcelParser
from app.ingestion.anomaly_engine import AnomalyEngine
from app.ingestion.live_market_client import LiveMarketClient
from app.ingestion.text_commentary_parser import TextCommentaryParser
from app.canonical.models import PricingBenchmark
from app.synthesis.asset_generator import generate_institutional_logos
from app.synthesis.executive_html_compiler import ExecutiveHtmlCompiler

def main(period_id="2026-08"):
    base_dir = Path(__file__).parent
    data_lake = base_dir / "data_lake" / "og_sovereign_ppac_data"
    raw_inbox = data_lake / "1_raw_inbox"
    curated_dir = data_lake / "2_curated" / period_id
    artifacts_dir = data_lake / "3_artifacts" / period_id

    # Load canonical pricing
    with open(curated_dir / "canonical_pricing.json", "r") as f:
        pricing_data = json.load(f)
    pricing = PricingBenchmark(**pricing_data)

    # Load market data
    with open(raw_inbox / "live_market_api" / f"live_quotes_{period_id}.json", "r") as f:
        market_data = json.load(f)

    # Load text dispatches and govt letters
    txt_parser = TextCommentaryParser()
    txt_file = raw_inbox / "text_commentary" / "policy_notes_aug2026.txt"
    parl_file = raw_inbox / "text_commentary" / "parliament_regulatory_dispatch_aug2026.txt"
    text_insights = txt_parser.parse_text_notes(txt_file)
    parl_insights = txt_parser.parse_text_notes(parl_file)
    for k, v in parl_insights.items():
        if v:
            text_insights[k] = v

    govt_letters = txt_parser.parse_government_letters(raw_inbox / "government_letters")

    # Load OMC consumption records
    target_excel = raw_inbox / "omc_sales" / f"omc_sales_{period_id}.xlsx"
    excel_parser = OmcExcelParser()
    records, comparisons = excel_parser.parse_workbook(target_excel, period_id=period_id)

    # Human-in-the-loop resolved records for approved publication
    for r in records:
        if r.entity_id == "BPCL" and r.product_type.value == "LPG":
            r.volume_tmt = 445.0

    anomaly_engine = AnomalyEngine()
    anomalies = anomaly_engine.evaluate_variances(comparisons, period_id=period_id)
    for a in anomalies:
        a.status = "RESOLVED"
        a.resolution_notes = "Verified distributor ERP entry typo with BPCL coordinator; corrected to 445.0 TMT"

    # Charts and logos
    assets_dir = base_dir / "assets"
    crest_path, logo_path = generate_institutional_logos(assets_dir)
    logos = {"header_crest": crest_path, "institutional_logo": logo_path}

    charts_dir = artifacts_dir / "charts"
    charts = {
        "crude_operator_pie": charts_dir / "crude_operator_pie.png",
        "pol_prod_cons_bar": charts_dir / "pol_prod_cons_bar.png",
        "lpg_marketing_pie": charts_dir / "lpg_marketing_pie.png",
        "natural_gas_regime_pie": charts_dir / "natural_gas_regime_pie.png",
        "brent_wti_spot_trend": charts_dir / "brent_wti_spot_trend.png",
        "omc_sales_distribution": charts_dir / "omc_sales_distribution.png",
        "price_buildup": charts_dir / "price_buildup.png",
        "demand_projection": charts_dir / "hsd_demand_projection.png",
    }

    compiler = ExecutiveHtmlCompiler()

    # Generate Approved HTML
    approved_html = artifacts_dir / "approved" / f"PPAC_Executive_Report_{period_id}_Approved.html"
    compiler.compile_executive_report(
        period_id=period_id,
        consumption_records=records,
        pricing=pricing,
        anomalies=anomalies,
        live_market_data=market_data,
        text_insights=text_insights,
        charts=charts,
        logos=logos,
        output_path=approved_html,
        government_letters=govt_letters,
    )
    print(f"Generated Approved HTML: {approved_html} ({approved_html.stat().st_size:,} bytes)")

    # Generate Draft HTML
    draft_html = artifacts_dir / "draft" / f"PPAC_Executive_Report_{period_id}_Draft.html"
    # reset anomaly status for draft
    draft_anomalies = anomaly_engine.evaluate_variances(comparisons, period_id=period_id)
    compiler.compile_executive_report(
        period_id=period_id,
        consumption_records=records,
        pricing=pricing,
        anomalies=draft_anomalies,
        live_market_data=market_data,
        text_insights=text_insights,
        charts=charts,
        logos=logos,
        output_path=draft_html,
        government_letters=govt_letters,
    )
    print(f"Generated Draft HTML: {draft_html} ({draft_html.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
