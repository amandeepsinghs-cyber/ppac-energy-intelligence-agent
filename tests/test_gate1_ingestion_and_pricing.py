"""Gate 1: Ingestion, Anomaly Scoring & Statutory Pricing Math Test."""

from pathlib import Path
import pytest

from app.canonical.models import ProductType, SeverityLevel
from app.ingestion.excel_parser import OmcExcelParser
from app.ingestion.anomaly_engine import AnomalyEngine
from app.pricing.icb_calculator import IndianCrudeBasketCalculator
from app.pricing.gas_apm_engine import NaturalGasApmEngine


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent.parent / "fixtures"


def test_excel_ingestion_and_anomaly_detection(fixtures_dir):
    parser = OmcExcelParser()
    excel_path = fixtures_dir / "mock_omc_sales_aug2026.xlsx"
    records, comparisons = parser.parse_workbook(excel_path, period_id="2026-08")

    assert len(records) > 0
    products_found = set(r.product_type for r in records)
    assert ProductType.MS in products_found
    assert ProductType.HSD in products_found
    assert ProductType.LPG in products_found

    # Test Anomaly Detection
    anomaly_engine = AnomalyEngine(warning_threshold_pct=10.0, critical_threshold_pct=15.0)
    anomalies = anomaly_engine.evaluate_variances(comparisons, period_id="2026-08")

    assert len(anomalies) >= 1
    bpcl_lpg_anomalies = [a for a in anomalies if a.entity_id == "BPCL" and "LPG" in a.field_name]
    assert len(bpcl_lpg_anomalies) == 1
    flag = bpcl_lpg_anomalies[0]
    assert flag.severity == SeverityLevel.CRITICAL
    assert flag.reported_value == 1100.0
    assert flag.variance_pct > 15.0
    assert flag.anomaly_id.startswith("FLAG-")


def test_indian_crude_basket_calculation():
    calc = IndianCrudeBasketCalculator()
    # August 2026 test benchmark: Oman-Dubai 78.50, Brent 82.10, weights 75.6% : 24.4%, FX 83.95
    res = calc.calculate_icb(
        brent_usd=82.10,
        oman_dubai_usd=78.50,
        usd_inr_rate=83.95,
        weight_sour=75.6,
        weight_sweet=24.4,
    )

    # (0.756 * 78.50) + (0.244 * 82.10) = 59.346 + 20.0324 = 79.3784 -> 79.38
    assert res["icb_usd_bbl"] == 79.38
    assert res["icb_inr_bbl"] == round(79.38 * 83.95, 2)


def test_natural_gas_apm_kirit_parikh_formula():
    gas_engine = NaturalGasApmEngine()

    # Case 1: Prior ICB is $82.00 -> 10% is $8.20 -> Capped at ceiling $6.50
    res_high = gas_engine.calculate_apm_price(prior_month_icb_usd=82.00)
    assert res_high["raw_indexed_usd_mmbtu"] == 8.20
    assert res_high["effective_apm_usd_mmbtu"] == 6.50
    assert "APM_CEILING_ENFORCED" in res_high["status_notes"]

    # Case 2: Prior ICB is $35.00 -> 10% is $3.50 -> Bounded by floor $4.00
    res_low = gas_engine.calculate_apm_price(prior_month_icb_usd=35.00)
    assert res_low["raw_indexed_usd_mmbtu"] == 3.50
    assert res_low["effective_apm_usd_mmbtu"] == 4.00
    assert "APM_FLOOR_ENFORCED" in res_low["status_notes"]

    # Case 3: Prior ICB is $55.00 -> 10% is $5.50 -> Inside corridor [4.00, 6.50]
    res_mid = gas_engine.calculate_apm_price(prior_month_icb_usd=55.00)
    assert res_mid["effective_apm_usd_mmbtu"] == 5.50
    assert "APM_INDEXED_MARKET_RATE" in res_mid["status_notes"]
