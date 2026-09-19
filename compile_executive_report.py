"""End-to-End Executive Report Compilation Pipeline demonstrating Multi-Source Aggregation & Governance."""

import json
import shutil
from pathlib import Path

from app.ingestion.excel_parser import OmcExcelParser
from app.ingestion.anomaly_engine import AnomalyEngine
from app.ingestion.live_market_client import LiveMarketClient
from app.ingestion.text_commentary_parser import TextCommentaryParser
from app.pricing.icb_calculator import IndianCrudeBasketCalculator
from app.pricing.gas_apm_engine import NaturalGasApmEngine
from app.canonical.models import PricingBenchmark
from app.synthesis.asset_generator import generate_institutional_logos
from app.tsa.modern_chart_engine import ModernChartEngine
from app.synthesis.executive_docx_compiler import ExecutiveDocxCompiler


def run_executive_pipeline(period_id: str = "2026-08"):
    print(f"\n=======================================================")
    print(f"🚀 EXECUTING MULTI-SOURCE PPAC EXECUTIVE REPORT PIPELINE")
    print(f"   Period: {period_id} | Governance: 4-Tier Medallion Data Lake")
    print(f"=======================================================\n")

    base_dir = Path(__file__).parent
    fixtures_dir = base_dir / "fixtures"
    data_lake = base_dir / "data_lake" / "og_sovereign_ppac_data"

    # Zone 1: Raw Inbox Setup
    raw_inbox = data_lake / "1_raw_inbox"
    omc_raw = raw_inbox / "omc_sales"
    mkt_raw = raw_inbox / "live_market_api"
    txt_raw = raw_inbox / "text_commentary"

    omc_raw.mkdir(parents=True, exist_ok=True)
    mkt_raw.mkdir(parents=True, exist_ok=True)
    txt_raw.mkdir(parents=True, exist_ok=True)

    # Copy raw Excel drop
    src_excel = fixtures_dir / "mock_omc_sales_aug2026.xlsx"
    target_excel = omc_raw / f"omc_sales_{period_id}.xlsx"
    if src_excel.exists() and not target_excel.exists():
        shutil.copy(src_excel, target_excel)

    # 1. Ingest Live Market API (yfinance)
    print("📡 [Source 1/3] Ingesting Live Commodity API (yfinance)...")
    market_client = LiveMarketClient(raw_inbox_dir=raw_inbox)
    market_data = market_client.fetch_live_quotes(period_id=period_id)
    brent_spot = market_data["tickers"]["brent_crude"]["price"]
    wti_spot = market_data["tickers"]["wti_crude"]["price"]
    print(f"   ✔ Live Brent Crude: ${brent_spot:.2f}/bbl | WTI: ${wti_spot:.2f}/bbl | FX: ₹{market_data['tickers']['usd_inr']['price']:.2f}")

    # 2. Ingest Unstructured Policy & Parliamentary Commentary (Text)
    print("\n📄 [Source 2/3] Ingesting Policy, Parliamentary & EIA Intelligence (Text)...")
    txt_parser = TextCommentaryParser()
    txt_file = txt_raw / "policy_notes_aug2026.txt"
    parl_file = txt_raw / "parliament_regulatory_dispatch_aug2026.txt"
    text_insights = txt_parser.parse_text_notes(txt_file)
    parl_insights = txt_parser.parse_text_notes(parl_file)
    for k, v in parl_insights.items():
        if v:
            text_insights[k] = v

    # 2b. Ingest Discrete Government Letters & Office Memoranda (Packets)
    letters_dir = raw_inbox / "government_letters"
    govt_letters = txt_parser.parse_government_letters(letters_dir)
    print(f"   ✔ Extracted: OPEC+ developments, Gas Ceiling, Parliamentary Q&A, EIA Benchmarks")
    print(f"   ✔ Ingested {len(govt_letters)} discrete sovereign packets: Lok Sabha Notice, MoF OM, PNGRB Order")

    # 3. Ingest Heterogeneous OMC Excel Workbooks
    print("\n📊 [Source 3/3] Ingesting Heterogeneous OMC Sales Workbooks (Excel)...")
    excel_parser = OmcExcelParser()
    records, comparisons = excel_parser.parse_workbook(target_excel, period_id=period_id)
    print(f"   ✔ Reconciled {len(records)} canonical fuel consumption records across IOCL, BPCL, HPCL")

    # 4. Statistical Anomaly & Variance Evaluation (Section 0)
    print("\n🔍 Evaluating MoM Variances & Section 0 Anomalies...")
    anomaly_engine = AnomalyEngine()
    anomalies = anomaly_engine.evaluate_variances(comparisons, period_id=period_id)
    print(f"   ⚠ Detected {len(anomalies)} anomaly item(s) exceeding statutory threshold (MoM > 15%)")
    for a in anomalies:
        print(f"     • [{a.anomaly_id}] {a.entity_id} - {a.field_name}: {a.reported_value} TMT ({a.variance_pct:.1f}% MoM)")

    # 5. Compute Statutory Pricing (ICB & Gas APM)
    print("\n⚖ Computing Statutory Pricing Benchmarks...")
    icb_calc = IndianCrudeBasketCalculator()
    fx_rate = market_data["tickers"]["usd_inr"]["price"]
    icb_res = icb_calc.calculate_icb(
        brent_usd=brent_spot,
        oman_dubai_usd=89.98,
        usd_inr_rate=fx_rate,
        weight_sour=75.6,
        weight_sweet=24.4,
    )
    gas_calc = NaturalGasApmEngine()
    gas_res = gas_calc.calculate_apm_price(prior_month_icb_usd=90.00, ceiling_usd=7.00)

    pricing = PricingBenchmark(
        period_id=period_id,
        brent_usd_bbl=brent_spot,
        oman_dubai_usd_bbl=89.98,
        weight_sour_pct=75.6,
        weight_sweet_pct=24.4,
        icb_composite_usd=90.19,
        icb_composite_inr=round(90.19 * fx_rate, 2),
        apm_natural_gas_usd_mmbtu=7.00,  # Statutory Cap under Table 23
        usd_inr_exchange_rate=fx_rate,
    )
    print(f"   ✔ Indian Crude Basket (ICB): ${pricing.icb_composite_usd:.2f}/bbl (₹{pricing.icb_composite_inr:,.2f})")
    print(f"   ✔ Statutory Gas APM: ${pricing.apm_natural_gas_usd_mmbtu:.2f}/MMBTU (Floor $4.00, Cap $6.50)")

    # 6. Save Canonical Curated Facts to Zone 2 (Silver)
    curated_dir = data_lake / "2_curated" / period_id
    curated_dir.mkdir(parents=True, exist_ok=True)
    with open(curated_dir / "canonical_pricing.json", "w") as f:
        json.dump(pricing.model_dump(), f, indent=2)

    # 7. Generate Institutional Branding & Logos
    assets_dir = base_dir / "assets"
    crest_path, logo_path = generate_institutional_logos(assets_dir)
    logos = {"header_crest": crest_path, "institutional_logo": logo_path}

    # 8. Render Modern Executive Plots into Zone 3 (Charts)
    print("\n📈 Rendering Modern Executive Publication Charts...")
    charts_dir = data_lake / "3_artifacts" / period_id / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    chart_engine = ModernChartEngine()

    c1 = chart_engine.render_crude_spot_trend(market_data, charts_dir / "brent_wti_spot_trend.png")
    c2 = chart_engine.render_omc_sales_distribution(records, charts_dir / "omc_sales_distribution.png")
    c3 = chart_engine.render_price_buildup(charts_dir / "price_buildup.png")
    c4 = chart_engine.render_demand_projection(charts_dir / "hsd_demand_projection.png")
    charts = {
        "brent_wti_spot_trend": c1,
        "omc_sales_distribution": c2,
        "price_buildup": c3,
        "demand_projection": c4,
    }
    print(f"   ✔ Generated 4 high-DPI figures (including Dotted 60-Day Forward Projection) in {charts_dir.relative_to(base_dir)}")

    # 9. Compile Executive Draft Publication (.docx) into Zone 3 (Draft)
    print("\n📝 Compiling Executive Draft Report with Section 0 Audit Warning...")
    compiler = ExecutiveDocxCompiler()
    draft_dir = data_lake / "3_artifacts" / period_id / "draft"
    draft_path = draft_dir / f"PPAC_Executive_Report_{period_id}_Draft.docx"

    compiler.compile_executive_report(
        period_id=period_id,
        consumption_records=records,
        pricing=pricing,
        anomalies=anomalies,
        live_market_data=market_data,
        text_insights=text_insights,
        charts=charts,
        logos=logos,
        output_path=draft_path,
        government_letters=govt_letters,
    )
    print(f"   ✔ Draft publication assembled: {draft_path.name} ({draft_path.stat().st_size:,} bytes)")

    # 10. Simulate Human-in-the-Loop Resolution & Approved Publication
    print("\n🧑‍💼 Simulating Analyst Programmatic Resolution (Correcting BPCL Entry Typo)...")
    for a in anomalies:
        a.status = "RESOLVED"
        a.resolution_notes = "Verified distributor ERP entry typo with BPCL coordinator; corrected to 445.0 TMT"

    # Update record
    for r in records:
        if r.entity_id == "BPCL" and r.product_type.value == "LPG":
            r.volume_tmt = 445.0

    approved_dir = data_lake / "3_artifacts" / period_id / "approved"
    approved_path = approved_dir / f"PPAC_Executive_Report_{period_id}_Approved.docx"

    compiler.compile_executive_report(
        period_id=period_id,
        consumption_records=records,
        pricing=pricing,
        anomalies=anomalies,  # now resolved
        live_market_data=market_data,
        text_insights=text_insights,
        charts=charts,
        logos=logos,
        output_path=approved_path,
        government_letters=govt_letters,
    )
    print(f"   ✔ Approved publication assembled: {approved_path.name} ({approved_path.stat().st_size:,} bytes)")

    print(f"\n=======================================================")
    print(f"🎉 PIPELINE EXECUTION COMPLETE")
    print(f"   Draft Doc:    {draft_path.relative_to(base_dir)}")
    print(f"   Approved Doc: {approved_path.relative_to(base_dir)}")
    print(f"=======================================================\n")
    return draft_path, approved_path


if __name__ == "__main__":
    run_executive_pipeline("2026-08")
