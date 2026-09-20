"""Gate 5 Test: ADK Agent Tools, Callbacks, and A2UI v0.9 Component Validation."""

import json
import pytest
from unittest.mock import MagicMock
from google.genai import types

from app.contracts import (
    PpacLakeInventory,
    GcsObjectInfo,
    MarketBenchmarkSummary,
    HistoricalDemandSummary,
    ForecastResultSummary,
    ReportArtifactSummary,
    A2uiCatalogVersion,
)
from app.render.a2ui_envelope import (
    A2A_DATA_PART_OPEN_TAG,
    A2A_DATA_PART_CLOSE_TAG,
    wrap_a2ui_part,
)
from app.render.inventory_card import build_lake_inventory_components
from app.render.pricing_card import build_pricing_matrix_components
from app.render.forecast_card import build_forecast_components
from app.render.historical_card import build_historical_components
from app.render.report_card import build_report_artifact_components
from app.render.a2ui_emit import (
    build_inventory_surface,
    build_pricing_surface,
    build_historical_surface,
    build_forecast_surface,
    build_report_surface,
)
from app.integration.tools import (
    inspect_sovereign_lake,
    query_market_pricing,
    query_historical_demand,
    run_sarimax_forecast,
    compile_statutory_report,
    publish_report_to_google_docs,
    PENDING_INVENTORY_KEY,
    PENDING_PRICING_KEY,
    PENDING_HISTORICAL_KEY,
    PENDING_FORECAST_KEY,
    PENDING_REPORT_KEY,
)
from app.integration.agent import (
    root_agent,
    sanitize_llm_request_history,
    strip_fabricated_a2ui,
    emit_a2ui_surface,
)


def _validate_a2ui_tree(components: list[dict]):
    """Enforces critical A2UI v0.9 invariants."""
    assert len(components) > 0, "Components list cannot be empty"
    assert components[0]["id"] == "root", "First component must have id='root'"
    assert components[0]["component"] == "Card", "Root component must be a Card"
    assert "child" in components[0], "Root Card must specify 'child'"

    # Verify all referenced child IDs exist
    component_map = {c["id"]: c for c in components}
    for c in components:
        if "children" in c:
            for child_id in c["children"]:
                assert child_id in component_map, f"Missing child component: {child_id}"
        if "child" in c:
            child_id = c["child"]
            assert child_id in component_map, f"Missing child component: {child_id}"


def test_inventory_card_a2ui_structure():
    inv = PpacLakeInventory(
        bucket="og-sovereign-ppac-data",
        region="asia-south1",
        raw_psu_submissions=[GcsObjectInfo("1_raw_inbox/psu_submissions/iocl/test.xlsx", 1024)],
    )
    comps = build_lake_inventory_components(inv)
    _validate_a2ui_tree(comps)


def test_pricing_matrix_card_a2ui_structure():
    summary = MarketBenchmarkSummary(
        period_id="2026-08",
        icb_price_usd_bbl=90.19,
        brent_dated_usd_bbl=90.84,
        oman_dubai_sour_usd_bbl=89.98,
        apm_gas_usd_mmbtu=7.00,
        hpht_gas_ceiling_usd_mmbtu=8.90,
        rbi_exchange_rate_inr_usd=84.15,
        delhi_ms_petrol_inr_litre=102.12,
        delhi_hsd_diesel_inr_litre=95.20,
        delhi_lpg_domestic_inr_cylinder=942.00,
        pol_consumption_tmt=18606.0,
        hsd_consumption_tmt=7023.0,
        ms_consumption_tmt=3836.0,
        lpg_consumption_tmt=2347.0,
    )
    comps = build_pricing_matrix_components(summary)
    _validate_a2ui_tree(comps)
    # Check that Image plot component is mounted
    img_comps = [c for c in comps if c.get("component") == "Image"]
    assert len(img_comps) == 1
    assert img_comps[0]["id"] == "pm-chart-img"
    assert img_comps[0]["url"].startswith("data:image/png;base64,")


def test_focused_pricing_matrix_cards_a2ui():
    """Verify focused cards generate valid A2UI trees with dedicated plots."""
    for focus in ["consumption", "retail", "crude", "gas"]:
        summary = MarketBenchmarkSummary(
            period_id="2026-08",
            icb_price_usd_bbl=90.19,
            brent_dated_usd_bbl=90.84,
            oman_dubai_sour_usd_bbl=89.98,
            apm_gas_usd_mmbtu=7.00,
            hpht_gas_ceiling_usd_mmbtu=8.90,
            rbi_exchange_rate_inr_usd=84.15,
            delhi_ms_petrol_inr_litre=102.12,
            delhi_hsd_diesel_inr_litre=95.20,
            delhi_lpg_domestic_inr_cylinder=942.00,
            pol_consumption_tmt=18606.0,
            hsd_consumption_tmt=7023.0,
            ms_consumption_tmt=3836.0,
            lpg_consumption_tmt=2347.0,
            focus=focus,
        )
        comps = build_pricing_matrix_components(summary)
        _validate_a2ui_tree(comps)
        img_comps = [c for c in comps if c.get("component") == "Image"]
        assert len(img_comps) == 1
        assert img_comps[0]["id"] == "pm-chart-img"
        assert img_comps[0]["url"].startswith("data:image/png;base64,")


def test_forecast_card_a2ui_structure():
    summary = ForecastResultSummary(
        product_name="High Speed Diesel (HSD)",
        baseline_month="August 2026",
        baseline_tmt=7023.0,
        horizon_months=36,
        forecast_36m_end_tmt=8350.0,
        growth_cagr_pct=5.8,
        chart_image_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
        chart_title="36-Month HSD Forecast",
    )
    comps = build_forecast_components(summary)
    _validate_a2ui_tree(comps)


def test_report_artifact_card_a2ui_structure():
    summary = ReportArtifactSummary(
        period_id="2026-08",
        title="PPAC Hydrocarbon Executive Report",
        html_gcs_uri="gs://og-sovereign-ppac-data/3_artifacts/2026-08/approved/report.html",
        docx_gcs_uri="gs://og-sovereign-ppac-data/3_artifacts/2026-08/approved/report.docx",
        executive_summary_points=["Test point 1", "Test point 2"],
        generated_at="2026-09-19 04:00 IST",
    )
    comps = build_report_artifact_components(summary)
    _validate_a2ui_tree(comps)


def test_a2ui_envelope_wrapping():
    inv = PpacLakeInventory()
    parts = build_inventory_surface(inv, "surface-12345")
    assert len(parts) == 2  # createSurface + updateComponents
    for part in parts:
        assert isinstance(part, types.Part)
        assert part.inline_data is not None
        assert part.inline_data.mime_type == "text/plain"
        assert part.part_metadata == {"mimeType": "application/json+a2ui"}
        wire_text = part.inline_data.data.decode("utf-8")
        assert wire_text.startswith(A2A_DATA_PART_OPEN_TAG)
        assert wire_text.endswith(A2A_DATA_PART_CLOSE_TAG)
        payload = wire_text[len(A2A_DATA_PART_OPEN_TAG) : -len(A2A_DATA_PART_CLOSE_TAG)]
        data = json.loads(payload)
        assert data["kind"] == "data"
        assert data["metadata"]["mimeType"] == "application/json+a2ui"


def test_agent_tools_execution():
    mock_ctx = MagicMock()
    mock_ctx.state = {}

    # 1. Lake inspection
    res_lake = inspect_sovereign_lake(tool_context=mock_ctx)
    assert res_lake["ok"] is True
    assert PENDING_INVENTORY_KEY in mock_ctx.state

    # 2. Market pricing
    res_price = query_market_pricing(tool_context=mock_ctx)
    assert res_price["indian_crude_basket_usd_bbl"] == 90.19
    assert PENDING_PRICING_KEY in mock_ctx.state

    # 3. SARIMAX forecast
    res_fc = run_sarimax_forecast(horizon_months=36, tool_context=mock_ctx)
    assert res_fc["baseline_volume_tmt"] == 7023.0
    assert PENDING_FORECAST_KEY in mock_ctx.state

    # 4. Report synthesis
    res_rep = compile_statutory_report(tool_context=mock_ctx)
    assert res_rep["status"] == "APPROVED"
    assert PENDING_REPORT_KEY in mock_ctx.state

    # 5. Google Docs publishing
    res_docs = publish_report_to_google_docs(period_id="2026-08", tool_context=mock_ctx)
    assert res_docs["status"] == "PUBLISHED"
    assert "google_docs_url" in res_docs
    assert "https://docs.google.com" in res_docs["google_docs_url"]


def test_callback_scrubbing_and_emission():
    # Test strip_fabricated_a2ui
    bad_text = f"Here is the data {A2A_DATA_PART_OPEN_TAG}{{'fake':'payload'}}{A2A_DATA_PART_CLOSE_TAG} and more text."
    mock_resp = MagicMock()
    mock_resp.content.parts = [types.Part(text=bad_text)]
    cleaned = strip_fabricated_a2ui(mock_resp)
    assert A2A_DATA_PART_OPEN_TAG not in cleaned.content.parts[0].text
    assert "Here is the data" in cleaned.content.parts[0].text

    # Test emit_a2ui_surface with ADK State-like object (no .pop() method)
    class MockAdkState:
        def __init__(self, data):
            self._data = dict(data)
        def get(self, key, default=None):
            return self._data.get(key, default)
        def __getitem__(self, key):
            return self._data[key]
        def __setitem__(self, key, value):
            self._data[key] = value
        def __contains__(self, key):
            return key in self._data

    mock_ctx = MagicMock()
    mock_ctx.state = MockAdkState({
        PENDING_PRICING_KEY: MarketBenchmarkSummary(
            period_id="2026-08",
            icb_price_usd_bbl=90.19,
            brent_dated_usd_bbl=90.84,
            oman_dubai_sour_usd_bbl=89.98,
            apm_gas_usd_mmbtu=7.00,
            hpht_gas_ceiling_usd_mmbtu=8.90,
            rbi_exchange_rate_inr_usd=84.15,
            delhi_ms_petrol_inr_litre=102.12,
            delhi_hsd_diesel_inr_litre=95.20,
            delhi_lpg_domestic_inr_cylinder=942.00,
            pol_consumption_tmt=18606.0,
            hsd_consumption_tmt=7023.0,
            ms_consumption_tmt=3836.0,
            lpg_consumption_tmt=2347.0,
        )
    })
    surface_content = emit_a2ui_surface(callback_context=mock_ctx)
    assert surface_content is not None
    assert len(surface_content.parts) == 2  # createSurface + updateComponents
    assert mock_ctx.state.get(PENDING_PRICING_KEY) is None

    # Test emit_a2ui_surface for PENDING_INVENTORY_KEY with dict serialization
    inv_dict = {
        "bucket": "og-sovereign-ppac-data",
        "region": "asia-south1",
        "total_objects": 42,
        "raw_psu_submissions": [{"name": "iocl.xlsx", "size_bytes": 1024, "updated": "2026-08-01"}],
        "raw_official_pubs": [{"name": "ppac_rr.pdf", "size_bytes": 2048, "updated": "2026-08-01"}],
        "curated_datasets": [{"name": "consumption.csv", "size_bytes": 4096, "updated": "2026-08-01"}],
        "artifacts": [{"name": "report.html", "size_bytes": 8192, "updated": "2026-08-01"}],
        "quarantine": [],
        "ok": True,
        "error": None,
    }
    mock_ctx_inv = MagicMock()
    mock_ctx_inv.state = MockAdkState({PENDING_INVENTORY_KEY: inv_dict})
    inv_surface = emit_a2ui_surface(callback_context=mock_ctx_inv)
    assert inv_surface is not None
    assert len(inv_surface.parts) == 2
    assert mock_ctx_inv.state.get(PENDING_INVENTORY_KEY) is None


def test_historical_demand_tool_and_card_a2ui():
    mock_ctx = MagicMock()
    mock_ctx.state = {}

    res = query_historical_demand(product_name="HSD", years=5, tool_context=mock_ctx)
    assert res["product"] == "High Speed Diesel (HSD)"
    assert res["timeframe_years"] == 5
    assert res["chart_status"] == "RENDERED_INLINE"
    assert PENDING_HISTORICAL_KEY in mock_ctx.state

    summary_raw = mock_ctx.state[PENDING_HISTORICAL_KEY]
    summary = HistoricalDemandSummary(**summary_raw) if isinstance(summary_raw, dict) else summary_raw
    assert summary.product_name == "High Speed Diesel (HSD)"
    assert len(summary.months) == 60

    # Test components and A2UI surface
    components = build_historical_components(summary)
    _validate_a2ui_tree(components)
    img_nodes = [c for c in components if c.get("component") == "Image"]
    assert len(img_nodes) == 1
    assert img_nodes[0]["id"] == "hc-chart-img"
    assert "data:image/png;base64," in img_nodes[0]["url"]

    surface_parts = build_historical_surface(summary, "historical-demand-surface")
    assert len(surface_parts) == 3

