"""Gate 0: Contract Verification & Synthetic Fixture Integrity Test."""

import json
from pathlib import Path
import pandas as pd
import pytest

from app.canonical.models import (
    HydrocarbonConsumptionRecord,
    ProductType,
    DataStage,
    PricingBenchmark,
    AuditAnomaly,
    SeverityLevel,
    MacroEconomicSnapshot,
    IndigenousCrudeProduction,
    ImportDependencyBalance,
    PriceBuildUpRecord,
)


def test_canonical_models_instantiation():
    record = HydrocarbonConsumptionRecord(
        period_id="2026-08",
        data_stage=DataStage.PROVISIONAL,
        entity_id="BPCL",
        product_type=ProductType.LPG,
        sector="Rural",
        volume_tmt=315.0,
        source_file="OMC_Sales_Aug2026.xlsx",
        source_reference="Sheet: LPG!C14",
    )
    assert record.volume_tmt == 315.0
    assert record.entity_id == "BPCL"
    assert record.product_type == ProductType.LPG

    pricing = PricingBenchmark(
        period_id="2026-08",
        brent_usd_bbl=82.10,
        oman_dubai_usd_bbl=78.50,
        weight_sour_pct=75.6,
        weight_sweet_pct=24.4,
        icb_composite_usd=79.38,
        icb_composite_inr=round(79.38 * 83.95, 2),
        apm_natural_gas_usd_mmbtu=6.50,
        usd_inr_exchange_rate=83.95,
    )
    assert pricing.icb_composite_usd == 79.38
    assert pricing.icb_composite_inr == 6663.95

    macro = MacroEconomicSnapshot(
        period_id="2026-08",
        gdp_growth_rate_pct=7.2,
        iip_general_index=142.5,
        iip_manufacturing_growth_pct=4.8,
        cpi_inflation_pct=4.3,
        usd_inr_mean_exchange_rate=83.95,
        forex_reserves_usd_billion=685.2,
    )
    assert macro.gdp_growth_rate_pct == 7.2

    crude_prod = IndigenousCrudeProduction(
        period_id="2026-08",
        ongc_volume_mmt=1.62,
        oil_volume_mmt=0.28,
        psc_pvt_volume_mmt=0.52,
        total_indigenous_mmt=2.42,
    )
    assert crude_prod.total_indigenous_mmt == 2.42

    trade_balance = ImportDependencyBalance(
        period_id="2026-08",
        crude_imports_mmt=19.8,
        crude_processing_mmt=22.5,
        pol_exports_mmt=5.1,
        pol_imports_mmt=3.8,
        gross_import_bill_usd_billion=12.4,
        gross_import_bill_inr_crores=104100.0,
        import_dependency_pct=87.8,
    )
    assert trade_balance.import_dependency_pct == 87.8

    price_buildup = PriceBuildUpRecord(
        product_name="Diesel (BS-VI)",
        base_price_inr_litre=55.60,
        freight_inr_litre=0.82,
        central_excise_duty_inr_litre=15.80,
        dealer_commission_inr_litre=2.60,
        state_vat_inr_litre=12.80,
        retail_selling_price_inr_litre=87.62,
    )
    assert price_buildup.retail_selling_price_inr_litre == 87.62

    anomaly = AuditAnomaly(
        period_id="2026-08",
        entity_id="BPCL",
        severity=SeverityLevel.CRITICAL,
        field_name="Rural LPG Sales",
        reported_value=315.0,
        expected_range=(420.0, 480.0),
        variance_pct=-30.0,
        source_reference="Sheet: LPG!C14",
    )
    assert anomaly.variance_pct == -30.0
    assert anomaly.anomaly_id.startswith("FLAG-")


def test_mock_fixtures_exist():
    fixtures_dir = Path(__file__).parent.parent / "fixtures"

    excel_file = fixtures_dir / "mock_omc_sales_aug2026.xlsx"
    assert excel_file.exists(), "Excel fixture missing"
    xl = pd.ExcelFile(excel_file)
    assert set(["MS", "HSD", "LPG"]).issubset(set(xl.sheet_names))

    json_file = fixtures_dir / "mock_crude_fx_feed.json"
    assert json_file.exists(), "JSON fixture missing"
    with open(json_file) as f:
        data = json.load(f)
    assert data["brent_usd_bbl"] == 82.10
    assert data["oman_dubai_usd_bbl"] == 78.50

    csv_file = fixtures_dir / "mock_historical_consumption_2018_2026.csv"
    assert csv_file.exists(), "Historical CSV missing"
    df = pd.read_csv(csv_file)
    assert len(df) >= 70
    assert "HSD_TMT" in df.columns
    assert "MS_TMT" in df.columns
