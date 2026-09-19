"""Canonical Data Models tailored specifically to PPAC statutory publications."""

from datetime import datetime
from enum import Enum
from typing import Tuple, List, Optional
from pydantic import BaseModel, Field
import uuid


class DataStage(str, Enum):
    PROVISIONAL = "PROVISIONAL"    # Flash Report (1st-3rd of month)
    REVISED = "REVISED"            # Ready Reckoner (mid-month)
    FINAL_AUDITED = "FINAL_AUDITED"# Annual Statistics (audited)


class ProductType(str, Enum):
    MS = "MS"               # Motor Spirit (Petrol)
    HSD = "HSD"             # High-Speed Diesel
    LPG = "LPG"             # Liquefied Petroleum Gas
    ATF = "ATF"             # Aviation Turbine Fuel
    SKO = "SKO"             # Superior Kerosene Oil
    NAPHTHA = "NAPHTHA"     # Naphtha
    BITUMEN = "BITUMEN"     # Bitumen
    FO = "FO"               # Furnace Oil
    LDO = "LDO"             # Light Diesel Oil
    PETCOKE = "PETCOKE"     # Petroleum Coke
    OTHERS = "OTHERS"


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AnomalyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    VERIFIED = "VERIFIED"
    RESOLVED = "RESOLVED"


class MacroEconomicSnapshot(BaseModel):
    """Chapter 1 of PPAC Ready Reckoner: Key Macro Indicators."""
    period_id: str
    gdp_growth_rate_pct: float = 7.2
    iip_general_index: float = 142.5
    iip_manufacturing_growth_pct: float = 4.8
    cpi_inflation_pct: float = 4.3
    usd_inr_mean_exchange_rate: float = 83.95
    forex_reserves_usd_billion: float = 685.2


class HydrocarbonConsumptionRecord(BaseModel):
    """Chapter 5 of PPAC Ready Reckoner: Petroleum Product Consumption."""
    fact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period_id: str
    data_stage: DataStage = DataStage.PROVISIONAL
    entity_id: str  # IOCL, BPCL, HPCL, RIL, Nayara, Shell
    product_type: ProductType
    sector: str = "Total"  # Retail, Consumer, Rural, Industrial, Total
    volume_tmt: float
    source_file: str
    source_reference: str


class IndigenousCrudeProduction(BaseModel):
    """Chapter 2 of PPAC Ready Reckoner: Domestic Crude & Condensate Production."""
    period_id: str
    ongc_volume_mmt: float
    oil_volume_mmt: float
    psc_pvt_volume_mmt: float
    total_indigenous_mmt: float


class RefineryThroughputRecord(BaseModel):
    """Chapter 3 of PPAC Ready Reckoner: Refinery Runs and Utilization."""
    throughput_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period_id: str
    entity_id: str  # IOCL-Panipat, HPCL-Vizag, BPCL-Kochi, RIL-Jamnagar
    crude_type: str = "Blend"  # Sour, Sweet, Domestic
    volume_processed_tmt: float
    capacity_utilization_pct: float
    source_reference: str


class ImportDependencyBalance(BaseModel):
    """Key PPAC Metric: India's Petroleum Import Dependency."""
    period_id: str
    crude_imports_mmt: float
    crude_processing_mmt: float
    pol_exports_mmt: float
    pol_imports_mmt: float
    gross_import_bill_usd_billion: float
    gross_import_bill_inr_crores: float
    import_dependency_pct: float  # (Crude Imports - POL Exports) / Processing * 100


class PricingBenchmark(BaseModel):
    """Chapter 7 & 8 of PPAC Ready Reckoner: ICB and Natural Gas Benchmarks."""
    period_id: str
    brent_usd_bbl: float
    oman_dubai_usd_bbl: float
    weight_sour_pct: float = 75.6
    weight_sweet_pct: float = 24.4
    icb_composite_usd: float
    icb_composite_inr: float
    apm_natural_gas_usd_mmbtu: float
    hpht_deepwater_gas_usd_mmbtu: float = 9.87  # PPAC bi-annual ceiling for deepwater
    usd_inr_exchange_rate: float


class PriceBuildUpRecord(BaseModel):
    """Chapter 9 of PPAC Ready Reckoner: Delhi Retail Price Build-up."""
    product_name: str  # "Petrol (BS-VI)" or "Diesel (BS-VI)"
    base_price_inr_litre: float
    freight_inr_litre: float
    central_excise_duty_inr_litre: float
    dealer_commission_inr_litre: float
    state_vat_inr_litre: float
    retail_selling_price_inr_litre: float


class AuditAnomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: f"FLAG-{uuid.uuid4().hex[:6].upper()}")
    period_id: str
    entity_id: str
    severity: SeverityLevel
    field_name: str
    reported_value: float
    expected_range: Tuple[float, float]
    variance_pct: float
    source_reference: str
    status: AnomalyStatus = AnomalyStatus.ACTIVE
    resolution_notes: Optional[str] = None
    resolved_by_user: Optional[str] = None
    resolved_at: Optional[datetime] = None


class ForecastResult(BaseModel):
    product_type: ProductType
    forecast_months: List[str]
    point_forecast_tmt: List[float]
    lower_bound_95_tmt: List[float]
    upper_bound_95_tmt: List[float]
    model_name: str = "SARIMAX(1,1,0)(1,1,0)12"
    mape_backtest_pct: float
    chart_artifact_path: str
