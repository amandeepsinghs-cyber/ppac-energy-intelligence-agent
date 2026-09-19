"""FastAPI server implementing A2A JSON-RPC 1.0 and REST endpoints for PPAC reporting."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.canonical.models import (
    AuditAnomaly,
    AnomalyStatus,
    SeverityLevel,
    PricingBenchmark,
    ProductType,
    MacroEconomicSnapshot,
    IndigenousCrudeProduction,
    ImportDependencyBalance,
)
from app.ingestion.excel_parser import OmcExcelParser
from app.ingestion.anomaly_engine import AnomalyEngine
from app.pricing.icb_calculator import IndianCrudeBasketCalculator
from app.pricing.gas_apm_engine import NaturalGasApmEngine
from app.tsa.sarimax_model import FuelDemandForecaster
from app.tsa.chart_renderer import ForecastChartRenderer
from app.synthesis.docx_compiler import PpacDocxCompiler
from app.integration.agent_card import get_agent_card


app = FastAPI(title="PPAC Autonomous Reporting Engine", version="1.0.0")

# In-memory operational store for pipeline state
PIPELINE_STORE: Dict[str, Dict[str, Any]] = {}


class TriggerRunPayload(BaseModel):
    period_id: str = "2026-08"
    template_mode: str = "FLASH_15_PAGE"


class ResolveFlagPayload(BaseModel):
    anomaly_id: str
    corrected_value: float
    resolution_rationale: str
    resolver_user: str


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = {}
    id: Optional[str | int] = 1


@app.get("/.well-known/agent-card.json")
@app.get("/a2a/ppac_report_synthesis/.well-known/agent-card.json")
def get_card():
    return get_agent_card()


@app.post("/api/v1/pipeline/trigger")
def trigger_pipeline(payload: TriggerRunPayload):
    period_id = payload.period_id
    base_dir = Path(__file__).parent.parent.parent
    fixtures_dir = base_dir / "fixtures"
    output_dir = base_dir / "output_artifacts" / period_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ingest Excel & Market Feed
    parser = OmcExcelParser()
    excel_path = fixtures_dir / "mock_omc_sales_aug2026.xlsx"
    records, comparisons = parser.parse_workbook(excel_path, period_id=period_id)

    # 2. Evaluate Anomalies
    anomaly_engine = AnomalyEngine()
    anomalies = anomaly_engine.evaluate_variances(comparisons, period_id=period_id)

    # 3. Ingest Market & Macroeconomics
    json_path = fixtures_dir / "mock_crude_fx_feed.json"
    with open(json_path) as f:
        mkt_data = json.load(f)

    icb_calc = IndianCrudeBasketCalculator()
    icb_res = icb_calc.calculate_icb(
        brent_usd=mkt_data["brent_usd_bbl"],
        oman_dubai_usd=mkt_data["oman_dubai_usd_bbl"],
        usd_inr_rate=mkt_data["usd_inr_exchange_rate"],
        weight_sour=mkt_data.get("weight_sour_pct", 75.6),
        weight_sweet=mkt_data.get("weight_sweet_pct", 24.4),
    )

    gas_engine = NaturalGasApmEngine()
    gas_res = gas_engine.calculate_apm_price(prior_month_icb_usd=mkt_data.get("prior_month_icb_usd", 82.00))

    pricing = PricingBenchmark(
        period_id=period_id,
        brent_usd_bbl=mkt_data["brent_usd_bbl"],
        oman_dubai_usd_bbl=mkt_data["oman_dubai_usd_bbl"],
        weight_sour_pct=icb_res["weight_sour_pct"],
        weight_sweet_pct=icb_res["weight_sweet_pct"],
        icb_composite_usd=icb_res["icb_usd_bbl"],
        icb_composite_inr=icb_res["icb_inr_bbl"],
        apm_natural_gas_usd_mmbtu=gas_res["effective_apm_usd_mmbtu"],
        hpht_deepwater_gas_usd_mmbtu=mkt_data.get("hpht_deepwater_gas_usd_mmbtu", 9.87),
        usd_inr_exchange_rate=mkt_data["usd_inr_exchange_rate"],
    )

    macro = MacroEconomicSnapshot(
        period_id=period_id,
        gdp_growth_rate_pct=mkt_data["macro"]["gdp_growth_rate_pct"],
        iip_general_index=mkt_data["macro"]["iip_general_index"],
        iip_manufacturing_growth_pct=mkt_data["macro"]["iip_manufacturing_growth_pct"],
        cpi_inflation_pct=mkt_data["macro"]["cpi_inflation_pct"],
        usd_inr_mean_exchange_rate=mkt_data["usd_inr_exchange_rate"],
        forex_reserves_usd_billion=mkt_data["macro"]["forex_reserves_usd_billion"],
    )

    indig_data = mkt_data.get("indigenous_crude", {})
    indigenous = IndigenousCrudeProduction(
        period_id=period_id,
        ongc_volume_mmt=indig_data.get("ongc_mmt", 1.62),
        oil_volume_mmt=indig_data.get("oil_mmt", 0.28),
        psc_pvt_volume_mmt=indig_data.get("psc_pvt_mmt", 0.52),
        total_indigenous_mmt=indig_data.get("total_mmt", 2.42),
    )

    tb = mkt_data.get("trade_balance", {})
    trade = ImportDependencyBalance(
        period_id=period_id,
        crude_imports_mmt=tb.get("crude_imports_mmt", 19.8),
        crude_processing_mmt=mkt_data.get("refinery_processing", {}).get("total_throughput_mmt", 22.5),
        pol_exports_mmt=tb.get("pol_exports_mmt", 5.1),
        pol_imports_mmt=tb.get("pol_imports_mmt", 3.8),
        gross_import_bill_usd_billion=tb.get("gross_import_bill_usd_billion", 12.4),
        gross_import_bill_inr_crores=tb.get("gross_import_bill_inr_crores", 104100.0),
        import_dependency_pct=tb.get("import_dependency_pct", 87.8),
    )

    # 4. Forecast & Chart
    csv_path = fixtures_dir / "mock_historical_consumption_2018_2026.csv"
    forecaster = FuelDemandForecaster()
    forecast = forecaster.fit_and_forecast(csv_path, product=ProductType.HSD, forecast_steps=2)

    chart_renderer = ForecastChartRenderer()
    chart_path = output_dir / f"HSD_Forecast_{period_id}.png"
    chart_renderer.render_forecast_chart(csv_path, forecast, chart_path)

    # 5. Compile Document
    compiler = PpacDocxCompiler()
    doc_path = output_dir / f"PPAC_Ready_Reckoner_{period_id}_Draft.docx"
    compiler.compile_flash_report(
        period_id=period_id,
        consumption_records=records,
        pricing=pricing,
        anomalies=anomalies,
        forecast=forecast,
        output_path=doc_path,
        chart_image_path=chart_path,
        macro=macro,
        indigenous=indigenous,
        trade=trade,
    )

    status_str = "DRAFT_NEEDS_REVIEW" if any(a.status != "RESOLVED" for a in anomalies) else "APPROVED_FOR_PUBLICATION"

    PIPELINE_STORE[period_id] = {
        "period_id": period_id,
        "status": status_str,
        "document_path": str(doc_path),
        "consumption_records": records,
        "pricing": pricing,
        "anomalies": anomalies,
        "forecast": forecast,
        "chart_path": str(chart_path),
        "output_dir": output_dir,
        "macro": macro,
        "indigenous": indigenous,
        "trade": trade,
    }

    return {
        "status": status_str,
        "period_id": period_id,
        "active_anomalies": [a.model_dump() for a in anomalies if a.status != "RESOLVED"],
        "document_uri": str(doc_path),
    }


@app.get("/api/v1/pipeline/status/{period_id}")
def get_status(period_id: str):
    if period_id not in PIPELINE_STORE:
        raise HTTPException(status_code=404, detail="Pipeline period not found")
    state = PIPELINE_STORE[period_id]
    return {
        "period_id": period_id,
        "status": state["status"],
        "document_uri": state["document_path"],
        "anomalies_count": len(state["anomalies"]),
        "active_anomalies": [a.model_dump() for a in state["anomalies"] if a.status != "RESOLVED"],
    }


@app.post("/api/v1/anomalies/resolve")
def resolve_anomaly(payload: ResolveFlagPayload):
    target_anomaly: Optional[AuditAnomaly] = None
    target_period = None

    for pid, state in PIPELINE_STORE.items():
        for a in state["anomalies"]:
            if a.anomaly_id == payload.anomaly_id:
                target_anomaly = a
                target_period = pid
                break
        if target_anomaly:
            break

    if not target_anomaly or not target_period:
        raise HTTPException(status_code=404, detail=f"Anomaly {payload.anomaly_id} not found")

    # Update anomaly
    target_anomaly.status = AnomalyStatus.RESOLVED
    target_anomaly.resolution_notes = payload.resolution_rationale
    target_anomaly.resolved_by_user = payload.resolver_user
    target_anomaly.resolved_at = datetime.utcnow()

    state = PIPELINE_STORE[target_period]

    # Update corresponding consumption record in state
    for rec in state["consumption_records"]:
        if rec.entity_id == target_anomaly.entity_id and target_anomaly.field_name.startswith(rec.sector):
            rec.volume_tmt = payload.corrected_value

    # Recompile document
    compiler = PpacDocxCompiler()
    doc_path = Path(state["document_path"])
    compiler.compile_flash_report(
        period_id=target_period,
        consumption_records=state["consumption_records"],
        pricing=state["pricing"],
        anomalies=state["anomalies"],
        forecast=state["forecast"],
        output_path=doc_path,
        chart_image_path=Path(state["chart_path"]),
        macro=state["macro"],
        indigenous=state["indigenous"],
        trade=state["trade"],
    )

    # Check if all critical flags resolved
    remaining_critical = [
        a for a in state["anomalies"] if a.status != AnomalyStatus.RESOLVED and a.severity == SeverityLevel.CRITICAL
    ]
    if not remaining_critical:
        state["status"] = "APPROVED_FOR_PUBLICATION"

    return {
        "anomaly_id": payload.anomaly_id,
        "status": "RESOLVED",
        "document_status": state["status"],
        "document_uri": str(doc_path),
        "remaining_active_flags": len([a for a in state["anomalies"] if a.status != AnomalyStatus.RESOLVED]),
    }


@app.post("/a2a/ppac_report_synthesis/jsonrpc")
def jsonrpc_handler(req: JsonRpcRequest):
    if req.method == "generate_report_draft":
        period_id = req.params.get("period_id", "2026-08")
        res = trigger_pipeline(TriggerRunPayload(period_id=period_id))
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {
                "document_uri": res["document_uri"],
                "active_anomalies_count": len(res["active_anomalies"]),
                "status": res["status"],
            },
        }
    elif req.method == "resolve_audit_anomaly":
        res = resolve_anomaly(ResolveFlagPayload(**req.params))
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": res,
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "error": {"code": -32601, "message": f"Method {req.method} not found"},
        }
