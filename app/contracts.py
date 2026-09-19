"""Data contracts and shared domain models for the PPAC Autonomous Reporting Engine.

Defines A2UI lifecycle contracts, sovereign lake inventory models,
market pricing benchmarks, econometric forecast summaries, and statutory report artifacts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ==============================================================================
# 1. A2UI Frontend Message Contracts (Gemini Enterprise)
# ==============================================================================

class A2uiCatalogVersion(str, Enum):
    """Gemini Enterprise A2UI catalog version."""
    V0_8 = "v0.8"   # Legacy Lit renderer
    V0_9 = "v0.9"   # Active Angular renderer (VegaChart, Canvas, Material 3)


ACTIVE_A2UI_CATALOG_VERSION: A2uiCatalogVersion = A2uiCatalogVersion.V0_9
A2UI_MIME_TYPE: str = "application/json+a2ui"
DEFAULT_GE_CATALOG_ID: str = (
    "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"
)


@dataclass(frozen=True)
class A2uiMessage:
    """A single protocol message emitted to the Gemini Enterprise A2UI surface.
    
    Each lifecycle message is serialized into an independent A2A DataPart envelope.
    """
    message_type: str                  # e.g. "createSurface", "updateComponents", "updateDataModel"
    surface_id: str                    # Unique surface identifier per conversation turn
    payload: Dict[str, Any]            # Version-specific message contents
    catalog_version: A2uiCatalogVersion = ACTIVE_A2UI_CATALOG_VERSION


# ==============================================================================
# 2. Sovereign GCS Lake Contracts
# ==============================================================================

@dataclass(frozen=True)
class GcsObjectInfo:
    """Metadata for a single object observed in the sovereign GCS bucket."""
    name: str
    size_bytes: int
    content_type: str = "application/octet-stream"
    updated: Optional[str] = None

    @property
    def size_kib(self) -> float:
        return self.size_bytes / 1024.0

    @property
    def basename(self) -> str:
        return self.name.rsplit("/", 1)[-1]


@dataclass(frozen=True)
class PpacLakeInventory:
    """Live audit inventory of gs://og-sovereign-ppac-data/ across the 4 Medallion tiers."""
    bucket: str = "og-sovereign-ppac-data"
    region: str = "asia-south1"
    raw_psu_submissions: List[GcsObjectInfo] = field(default_factory=list)
    raw_official_pubs: List[GcsObjectInfo] = field(default_factory=list)
    curated_datasets: List[GcsObjectInfo] = field(default_factory=list)
    artifacts: List[GcsObjectInfo] = field(default_factory=list)
    quarantine: List[GcsObjectInfo] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None

    @property
    def total_objects(self) -> int:
        return (
            len(self.raw_psu_submissions)
            + len(self.raw_official_pubs)
            + len(self.curated_datasets)
            + len(self.artifacts)
            + len(self.quarantine)
        )

    @property
    def total_bytes(self) -> int:
        all_objs = (
            self.raw_psu_submissions
            + self.raw_official_pubs
            + self.curated_datasets
            + self.artifacts
            + self.quarantine
        )
        return sum(o.size_bytes for o in all_objs)


# ==============================================================================
# 3. Domain Benchmark & Forecasting Contracts
# ==============================================================================

@dataclass(frozen=True)
class MarketBenchmarkSummary:
    """Verified official monthly benchmarks and retail price build-up."""
    period_id: str
    icb_price_usd_bbl: float
    brent_dated_usd_bbl: float
    oman_dubai_sour_usd_bbl: float
    apm_gas_usd_mmbtu: float
    hpht_gas_ceiling_usd_mmbtu: float
    rbi_exchange_rate_inr_usd: float
    delhi_ms_petrol_inr_litre: float
    delhi_hsd_diesel_inr_litre: float
    delhi_lpg_domestic_inr_cylinder: float
    pol_consumption_tmt: float
    hsd_consumption_tmt: float
    ms_consumption_tmt: float
    lpg_consumption_tmt: float
    focus: str = "overview"


@dataclass
class ForecastResultSummary:
    """SARIMAX econometric demand forecast summary."""
    product_name: str
    baseline_month: str
    baseline_tmt: float
    horizon_months: int
    forecast_36m_end_tmt: float
    growth_cagr_pct: float
    chart_image_base64: str            # PNG data uri or base64 string
    chart_title: str
    history_months: List[str] = field(default_factory=list)
    history_values: List[float] = field(default_factory=list)
    forecast_months: List[str] = field(default_factory=list)
    forecast_values: List[float] = field(default_factory=list)
    lower_bounds: List[float] = field(default_factory=list)
    upper_bounds: List[float] = field(default_factory=list)


@dataclass
class HistoricalDemandSummary:
    """Verified official historical multi-year fuel demand time series."""
    product_name: str
    timeframe_years: int
    start_period: str
    end_period: str
    total_consumption_tmt: float
    average_monthly_tmt: float
    peak_month: str
    peak_volume_tmt: float
    trough_month: str
    trough_volume_tmt: float
    cagr_pct: float
    months: List[str] = field(default_factory=list)
    monthly_values: List[float] = field(default_factory=list)
    annual_summary: Dict[str, float] = field(default_factory=dict)
    chart_image_base64: str = ""



@dataclass(frozen=True)
class ReportArtifactSummary:
    """Approved statutory report artifact release metadata."""
    period_id: str
    title: str
    html_gcs_uri: str
    docx_gcs_uri: str
    executive_summary_points: List[str]
    generated_at: str
    status: str = "APPROVED"
    html_web_url: str = ""
    docx_web_url: str = ""
    google_docs_url: str = ""
