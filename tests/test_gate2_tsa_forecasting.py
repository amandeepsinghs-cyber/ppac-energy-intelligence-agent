"""Gate 2: Time-Series Demand Forecasting & Chart Rendering Test."""

from pathlib import Path
import pytest

from app.canonical.models import ProductType
from app.tsa.sarimax_model import FuelDemandForecaster
from app.tsa.chart_renderer import ForecastChartRenderer


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def tmp_output_dir(tmp_path):
    return tmp_path / "charts"


def test_sarimax_demand_forecasting(fixtures_dir):
    forecaster = FuelDemandForecaster()
    csv_path = fixtures_dir / "mock_historical_consumption_2018_2026.csv"

    # Test HSD forecast
    hsd_result = forecaster.fit_and_forecast(
        historical_csv=csv_path,
        product=ProductType.HSD,
        forecast_steps=2,
    )

    assert len(hsd_result.point_forecast_tmt) == 2
    assert len(hsd_result.lower_bound_95_tmt) == 2
    assert len(hsd_result.upper_bound_95_tmt) == 2
    assert hsd_result.forecast_months == ["2026-09", "2026-10"]

    # Check bounds consistency
    for pt, low, up in zip(hsd_result.point_forecast_tmt, hsd_result.lower_bound_95_tmt, hsd_result.upper_bound_95_tmt):
        assert low < pt < up
        assert 6000.0 < pt < 10000.0  # HSD national volume range

    # Verify MAPE SLA
    assert hsd_result.mape_backtest_pct < 5.0, f"MAPE {hsd_result.mape_backtest_pct}% exceeded expectation"


def test_forecast_chart_rendering(fixtures_dir, tmp_output_dir):
    forecaster = FuelDemandForecaster()
    renderer = ForecastChartRenderer()
    csv_path = fixtures_dir / "mock_historical_consumption_2018_2026.csv"

    hsd_result = forecaster.fit_and_forecast(
        historical_csv=csv_path,
        product=ProductType.HSD,
        forecast_steps=2,
    )

    chart_file = tmp_output_dir / "HSD_Forecast_Aug2026.png"
    out_path = renderer.render_forecast_chart(
        historical_csv=csv_path,
        forecast=hsd_result,
        output_path=chart_file,
    )

    assert out_path.exists()
    assert out_path.stat().st_size > 10000  # Non-trivial high-res image
    assert hsd_result.chart_artifact_path == str(out_path)
