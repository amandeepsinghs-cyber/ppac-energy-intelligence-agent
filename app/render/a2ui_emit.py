"""A2UI surface emitter for PPAC Reporting Engine.

Constructs paired 'createSurface' and 'updateComponents' ADK Parts for Gemini Enterprise.
"""

from typing import List
from google.genai import types

from app.contracts import (
    PpacLakeInventory,
    MarketBenchmarkSummary,
    ForecastResultSummary,
    ReportArtifactSummary,
    HistoricalDemandSummary,
)
from app.render.a2ui_envelope import wrap_a2ui_part
from app.render.a2ui_lifecycle import (
    build_create_surface,
    build_update_components,
    build_update_data_model,
)
from app.render.inventory_card import build_lake_inventory_components
from app.render.pricing_card import build_pricing_matrix_components
from app.render.pricing_vega import SPEC_KEY, build_pricing_vega_spec
from app.render.forecast_card import build_forecast_components
from app.render.forecast_vega import FORECAST_SPEC_KEY, build_forecast_vega_spec
from app.render.report_card import build_report_artifact_components
from app.render.historical_card import build_historical_components
from app.render.historical_vega import HISTORICAL_SPEC_KEY, build_historical_vega_spec



def build_inventory_surface(inventory: PpacLakeInventory, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for sovereign lake inventory."""
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(
            build_update_components(
                surface_id=surface_id,
                components=build_lake_inventory_components(inventory),
            )
        ),
    ]


def build_pricing_surface(summary: MarketBenchmarkSummary, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateDataModel (Vega spec) + updateComponents for market benchmarks and pricing with plot."""
    spec = build_pricing_vega_spec(summary)
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_data_model(surface_id=surface_id, value={SPEC_KEY: spec})),
        wrap_a2ui_part(
            build_update_components(
                surface_id=surface_id,
                components=build_pricing_matrix_components(summary),
            )
        ),
    ]


def build_forecast_surface(summary: ForecastResultSummary, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateDataModel (Vega spec) + updateComponents for SARIMAX forecast with interactive chart."""
    spec = build_forecast_vega_spec(summary)
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_data_model(surface_id=surface_id, value={FORECAST_SPEC_KEY: spec})),
        wrap_a2ui_part(
            build_update_components(
                surface_id=surface_id,
                components=build_forecast_components(summary),
            )
        ),
    ]


def build_report_surface(summary: ReportArtifactSummary, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for statutory report release."""
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(
            build_update_components(
                surface_id=surface_id,
                components=build_report_artifact_components(summary),
            )
        ),
    ]


def build_historical_surface(summary: HistoricalDemandSummary, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateDataModel (Vega spec) + updateComponents for official PPAC historical demand series."""
    spec = build_historical_vega_spec(summary)
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_data_model(surface_id=surface_id, value={HISTORICAL_SPEC_KEY: spec})),
        wrap_a2ui_part(
            build_update_components(
                surface_id=surface_id,
                components=build_historical_components(summary),
            )
        ),
    ]

