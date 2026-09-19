"""ADK Root Agent for Petroleum Planning & Analysis Cell (PPAC) Sovereign Reporting Engine.

Provides conversational intelligence, econometric forecasting, and native A2UI surfaces
for Gemini Enterprise chat.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from app.contracts import (
    PpacLakeInventory,
    MarketBenchmarkSummary,
    ForecastResultSummary,
    ReportArtifactSummary,
    HistoricalDemandSummary,
)
from app.integration.tools import (
    PENDING_FORECAST_KEY,
    PENDING_PRICING_KEY,
    PENDING_REPORT_KEY,
    PENDING_INVENTORY_KEY,
    PENDING_HISTORICAL_KEY,
    inspect_sovereign_lake,
    query_market_pricing,
    query_historical_demand,
    run_sarimax_forecast,
    compile_statutory_report,
    publish_report_to_google_docs,
)
from app.render.a2ui_envelope import (
    A2A_DATA_PART_CLOSE_TAG,
    A2A_DATA_PART_OPEN_TAG,
)
from app.render.a2ui_emit import (
    build_inventory_surface,
    build_pricing_surface,
    build_forecast_surface,
    build_report_surface,
    build_historical_surface,
)


logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _take_pending(callback_context: CallbackContext | None, key: str, target_cls: Any = None) -> Any | None:
    """Safely extract and reset a pending key from ADK State which does not support .pop()."""
    if callback_context is None:
        return None
    state = callback_context.state
    if state is None:
        return None
    val = state.get(key)
    if val is not None:
        try:
            state[key] = None
        except Exception:
            pass
    if val is not None and isinstance(val, dict) and target_cls is not None:
        try:
            if target_cls is PpacLakeInventory:
                data = dict(val)
                for field_name in ["raw_psu_submissions", "raw_official_pubs", "curated_datasets", "artifacts", "quarantine"]:
                    if field_name in data and isinstance(data[field_name], list):
                        data[field_name] = [
                            GcsObjectInfo(**item) if isinstance(item, dict) else item
                            for item in data[field_name]
                        ]
                return PpacLakeInventory(**data)
            return target_cls(**val)
        except Exception as exc:
            logger.warning("Failed to rehydrate %s for %s: %s", target_cls, key, exc)
            return val
    return val


def emit_a2ui_surface(
    callback_context: CallbackContext | None = None,
    **kwargs: Any,
) -> types.Content | None:
    """Attach the deterministic A2UI surface earned this turn to the model's reply."""
    surface_id = f"surface-{uuid.uuid4().hex[:8]}"

    if callback_context is None:
        return None

    pending_forecast = _take_pending(callback_context, PENDING_FORECAST_KEY, ForecastResultSummary)
    pending_historical = _take_pending(callback_context, PENDING_HISTORICAL_KEY, HistoricalDemandSummary)
    pending_pricing = _take_pending(callback_context, PENDING_PRICING_KEY, MarketBenchmarkSummary)
    pending_report = _take_pending(callback_context, PENDING_REPORT_KEY, ReportArtifactSummary)
    pending_inventory = _take_pending(callback_context, PENDING_INVENTORY_KEY, PpacLakeInventory)

    parts: list[types.Part] = []

    if pending_forecast:
        parts = build_forecast_surface(pending_forecast, surface_id)
    elif pending_historical:
        parts = build_historical_surface(pending_historical, surface_id)
    elif pending_pricing:
        parts = build_pricing_surface(pending_pricing, surface_id)
    elif pending_report:
        parts = build_report_surface(pending_report, surface_id)
    elif pending_inventory:
        parts = build_inventory_surface(pending_inventory, surface_id)
    else:
        return None


    if not parts:
        return None

    logger.info("emit_a2ui_surface: surface=%s parts=%d", surface_id, len(parts))
    return types.Content(role="model", parts=parts)


def strip_fabricated_a2ui(
    llm_response: LlmResponse | None = None,
    **kwargs: Any,
) -> LlmResponse | None:
    """Delete any A2UI payload the model wrote into its own prose."""
    if llm_response is None or llm_response.content is None:
        return None

    parts = llm_response.content.parts or []
    cleaned: list[types.Part] = []
    removed = 0

    for part in parts:
        text = getattr(part, "text", None)
        if not text or A2A_DATA_PART_OPEN_TAG not in text:
            cleaned.append(part)
            continue

        stripped = _remove_datapart_blobs(text)
        removed += 1
        if stripped.strip():
            cleaned.append(types.Part(text=stripped))

    if not removed:
        return None

    logger.warning("strip_fabricated_a2ui: removed A2UI payloads from %d text parts", removed)
    llm_response.content.parts = cleaned or [types.Part(text="")]
    return llm_response


def sanitize_llm_request_history(
    callback_context: CallbackContext | None = None,
    llm_request: LlmRequest | None = None,
    **kwargs: Any,
) -> LlmResponse | None:
    """Scrub A2UI tags and base64 payloads from history to prevent token exhaustion loops."""
    if llm_request is None or not getattr(llm_request, "contents", None):
        return None

    for content in llm_request.contents:
        if not getattr(content, "parts", None):
            continue
        cleaned_parts: list[types.Part] = []
        for part in content.parts:
            text = getattr(part, "text", None)
            if text and A2A_DATA_PART_OPEN_TAG in text:
                stripped = _remove_datapart_blobs(text)
                if stripped.strip():
                    cleaned_parts.append(types.Part(text=stripped))
            else:
                cleaned_parts.append(part)

        content.parts = cleaned_parts or [types.Part(text="")]

    if llm_request.config is None:
        llm_request.config = types.GenerateContentConfig(max_output_tokens=1024)
    elif (
        not getattr(llm_request.config, "max_output_tokens", None)
        or llm_request.config.max_output_tokens > 1024
    ):
        llm_request.config.max_output_tokens = 1024

    return None


def _remove_datapart_blobs(text: str) -> str:
    out: list[str] = []
    rest = text
    while True:
        start = rest.find(A2A_DATA_PART_OPEN_TAG)
        if start == -1:
            out.append(rest)
            return "".join(out)

        out.append(rest[:start])
        end = rest.find(A2A_DATA_PART_CLOSE_TAG, start)
        if end == -1:
            return "".join(out)
        rest = rest[end + len(A2A_DATA_PART_CLOSE_TAG):]


root_agent = Agent(
    name="ppac_reporting_agent",
    description="PPAC Autonomous Reporting & Econometric Forecasting Agent for Gemini Enterprise",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=1024,
    ),
    instruction=(
        "You are the Petroleum Planning & Analysis Cell (PPAC) Sovereign Reporting Agent. "
        "You provide real-time hydrocarbon intelligence, live SARIMAX econometric demand forecasts, "
        "and automated statutory executive reporting for the Ministry of Petroleum & Natural Gas (MoPNG).\n\n"
        "SOVEREIGN DATA PRINCIPLES:\n"
        "- All data is 100% verified August 2026 ground-truth from the official PPAC Ready Reckoner.\n"
        "- Total POL Consumption: 18,606 TMT (18.61 MMT).\n"
        "- HSD (Diesel): 7,023 TMT (+6.8% YoY).\n"
        "- MS (Petrol): 3,836 TMT (+8.2% YoY).\n"
        "- Indian Crude Basket (ICB): $90.19 / bbl (Oman/Dubai sour $89.98 @ 75.6%, Dated Brent $90.84 @ 24.4%).\n"
        "- Domestic APM Natural Gas: $7.00 / MMBTU ceiling (Kirit Parikh formula).\n"
        "- Deepwater HP-HT Ceiling: $8.90 / MMBTU.\n"
        "- RBI Reference Rate: ₹84.15 / USD.\n"
        "- Delhi Pump Prices: Petrol ₹102.12 / L, Diesel ₹95.20 / L, Domestic LPG ₹942.00 / cylinder.\n\n"
        "TOOLS:\n"
        "- inspect_sovereign_lake: Queries gs://og-sovereign-ppac-data to audit PSU submissions (IOCL, BPCL, HPCL, ONGC, GAIL) and quarantine ledger.\n"
        "- query_market_pricing: Queries official crude benchmarks, gas ceilings, consumption volumes, and Delhi retail fuel price build-up for a single period.\n"
        "  CRITICAL: When the user asks about an individual actual metric, ALWAYS call query_market_pricing with the appropriate focus:\n"
        "    * focus='consumption' for POL demand, HSD/diesel consumption, MS/petrol consumption, or LPG volume.\n"
        "    * focus='retail' for Delhi retail pump price structure, dealer margins, or state VAT.\n"
        "    * focus='crude' for Indian Crude Basket (ICB), Oman/Dubai sour blend, or Dated Brent.\n"
        "    * focus='gas' for domestic APM gas ceiling or HP-HT ceiling.\n"
        "    * focus='overview' for broad pricing benchmarks.\n"
        "- query_historical_demand: Queries official PPAC multi-year historical petroleum consumption time series (2020–2026, past 5 years) for HSD, MS, LPG, ATF, or Total POL. ALWAYS call query_historical_demand when the user asks for historical consumption, past demand trends, multi-year comparisons, or past 5 years data.\n"
        "- run_sarimax_forecast: Generates live 12-month econometric demand forecasts with confidence intervals and interactive VegaChart visualization.\n"
        "- compile_statutory_report: Compiles and signs off on the official 15-page HTML and executive Word DOCX in the sovereign lake.\n"
        "- publish_report_to_google_docs: Publishes the verified statutory DOCX report directly to Google Docs with a clickable viewing URL.\n\n"
        "SURFACES & DISPLAY:\n"
        "Interactive A2UI surfaces, charts, and KPI cards are attached automatically to your response. "
        "Confirm in one or two clear sentences that the interactive card or focused visual plot is displayed below. "
        "NEVER emit raw <a2a_datapart_json> tags or JSON markup in your reply. Your text output is prose only."
    ),
    tools=[
        inspect_sovereign_lake,
        query_market_pricing,
        query_historical_demand,
        run_sarimax_forecast,
        compile_statutory_report,
        publish_report_to_google_docs,
    ],
    before_model_callback=sanitize_llm_request_history,
    after_model_callback=strip_fabricated_a2ui,
    after_agent_callback=emit_a2ui_surface,
)


app = App(
    root_agent=root_agent,
    name="ppac_reporting_agent",
)
