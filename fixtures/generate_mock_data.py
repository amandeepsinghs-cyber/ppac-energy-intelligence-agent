"""Script generating comprehensive, authentic PPAC Ready Reckoner test fixtures."""

import json
from pathlib import Path
import numpy as np
import pandas as pd


def generate_fixtures(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Multi-tab OMC Sales Excel (August 2026) - Comprehensive PPAC Fuel Suite
    excel_path = output_dir / "mock_omc_sales_aug2026.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # MS (Motor Spirit / Petrol)
        df_ms = pd.DataFrame([
            {"Entity": "IOCL", "Sector": "Retail", "Volume_TMT": 1250.0, "Prior_Month_TMT": 1220.0},
            {"Entity": "BPCL", "Sector": "Retail", "Volume_TMT": 820.0, "Prior_Month_TMT": 810.0},
            {"Entity": "HPCL", "Sector": "Retail", "Volume_TMT": 780.0, "Prior_Month_TMT": 775.0},
            {"Entity": "RIL", "Sector": "Retail", "Volume_TMT": 220.0, "Prior_Month_TMT": 215.0},
            {"Entity": "Nayara", "Sector": "Retail", "Volume_TMT": 180.0, "Prior_Month_TMT": 178.0},
        ])
        df_ms.to_excel(writer, sheet_name="MS", index=False)

        # HSD (High Speed Diesel)
        df_hsd = pd.DataFrame([
            {"Entity": "IOCL", "Sector": "Retail", "Volume_TMT": 3450.0, "Prior_Month_TMT": 3480.0},
            {"Entity": "BPCL", "Sector": "Retail", "Volume_TMT": 2010.0, "Prior_Month_TMT": 2030.0},
            {"Entity": "HPCL", "Sector": "Retail", "Volume_TMT": 1920.0, "Prior_Month_TMT": 1940.0},
            {"Entity": "RIL", "Sector": "Retail", "Volume_TMT": 480.0, "Prior_Month_TMT": 475.0},
            {"Entity": "Nayara", "Sector": "Retail", "Volume_TMT": 360.0, "Prior_Month_TMT": 355.0},
        ])
        df_hsd.to_excel(writer, sheet_name="HSD", index=False)

        # LPG (Liquefied Petroleum Gas - with injected BPCL anomaly)
        df_lpg = pd.DataFrame([
            {"Entity": "IOCL", "Sector": "Total", "Volume_TMT": 1200.0, "Prior_Month_TMT": 1180.0},
            {"Entity": "BPCL", "Sector": "Rural", "Volume_TMT": 315.0, "Prior_Month_TMT": 450.0}, # -30% ANOMALY!
            {"Entity": "HPCL", "Sector": "Total", "Volume_TMT": 720.0, "Prior_Month_TMT": 710.0},
        ])
        df_lpg.to_excel(writer, sheet_name="LPG", index=False)

        # ATF (Aviation Turbine Fuel)
        df_atf = pd.DataFrame([
            {"Entity": "IOCL", "Sector": "Aviation", "Volume_TMT": 350.0, "Prior_Month_TMT": 340.0},
            {"Entity": "BPCL", "Sector": "Aviation", "Volume_TMT": 210.0, "Prior_Month_TMT": 205.0},
            {"Entity": "HPCL", "Sector": "Aviation", "Volume_TMT": 170.0, "Prior_Month_TMT": 168.0},
        ])
        df_atf.to_excel(writer, sheet_name="ATF", index=False)

        # Naphtha
        df_naphtha = pd.DataFrame([
            {"Entity": "Fertilizers", "Sector": "Industrial", "Volume_TMT": 480.0, "Prior_Month_TMT": 475.0},
            {"Entity": "Petrochemicals", "Sector": "Industrial", "Volume_TMT": 620.0, "Prior_Month_TMT": 615.0},
        ])
        df_naphtha.to_excel(writer, sheet_name="Naphtha", index=False)

        # Bitumen (Road construction)
        df_bitumen = pd.DataFrame([
            {"Entity": "NHAI & State PWDs", "Sector": "Infrastructure", "Volume_TMT": 540.0, "Prior_Month_TMT": 530.0},
        ])
        df_bitumen.to_excel(writer, sheet_name="Bitumen", index=False)

    print(f"Generated comprehensive multi-fuel Excel: {excel_path}")

    # 2. Comprehensive PPAC Energy Economics Feed (JSON)
    json_path = output_dir / "mock_crude_fx_feed.json"
    market_feed = {
        "period_id": "2026-08",
        # International Pricing
        "brent_usd_bbl": 82.10,
        "oman_dubai_usd_bbl": 78.50,
        "weight_sour_pct": 75.6,
        "weight_sweet_pct": 24.4,
        "usd_inr_exchange_rate": 83.95,
        "prior_month_icb_usd": 82.00,
        # Gas Benchmarks
        "statutory_gas_floor_usd": 4.00,
        "statutory_gas_ceiling_usd": 6.50,
        "hpht_deepwater_gas_usd_mmbtu": 9.87,
        # Macro Indicators (PPAC Chapter 1)
        "macro": {
            "gdp_growth_rate_pct": 7.2,
            "iip_general_index": 142.5,
            "iip_manufacturing_growth_pct": 4.8,
            "cpi_inflation_pct": 4.3,
            "forex_reserves_usd_billion": 685.2
        },
        # Indigenous Crude Production in MMT (PPAC Chapter 2)
        "indigenous_crude": {
            "ongc_mmt": 1.62,
            "oil_mmt": 0.28,
            "psc_pvt_mmt": 0.52,
            "total_mmt": 2.42
        },
        # Refinery Processing in MMT (PPAC Chapter 3)
        "refinery_processing": {
            "psu_refineries_mmt": 14.8,
            "private_jv_refineries_mmt": 7.7,
            "total_throughput_mmt": 22.5,
            "average_capacity_utilization_pct": 103.2
        },
        # Trade & Net Import Dependency (Key PPAC Sovereign Metric)
        "trade_balance": {
            "crude_imports_mmt": 19.8,
            "pol_exports_mmt": 5.1,
            "pol_imports_mmt": 3.8,
            "gross_import_bill_usd_billion": 12.4,
            "gross_import_bill_inr_crores": 104100.0,
            "import_dependency_pct": 87.8
        },
        # Delhi Retail Selling Price (RSP) Build-up (PPAC Chapter 9)
        "delhi_price_buildup": {
            "petrol": {
                "base_price": 55.40,
                "freight": 0.20,
                "central_excise": 19.90,
                "dealer_commission": 3.80,
                "state_vat": 15.42,
                "retail_selling_price": 94.72
            },
            "diesel": {
                "base_price": 56.20,
                "freight": 0.22,
                "central_excise": 15.80,
                "dealer_commission": 2.60,
                "state_vat": 12.80,
                "retail_selling_price": 87.62
            }
        }
    }
    with open(json_path, "w") as f:
        json.dump(market_feed, f, indent=2)
    print(f"Generated authentic PPAC economic feed: {json_path}")

    # 3. Monthly Historical Consumption (2018-01 to 2026-08) for TSA modeling
    csv_path = output_dir / "mock_historical_consumption_2018_2026.csv"
    dates = pd.date_range(start="2018-01-01", end="2026-08-01", freq="MS")
    n = len(dates)

    np.random.seed(42)
    time_trend = np.linspace(0, 10, n)
    month_of_year = dates.month
    seasonality = np.sin((month_of_year - 2) * (2 * np.pi / 12)) * 300.0
    monsoon_drop = np.where(month_of_year.isin([7, 8]), -400.0, 0.0)

    iip_index = 120.0 + time_trend * 3.5 + np.random.normal(0, 2, n)
    monsoon_departure = np.where(month_of_year.isin([6, 7, 8, 9]), np.random.normal(5, 10, n), 0.0)

    hsd_tmt = 6200.0 + time_trend * 180.0 + seasonality + monsoon_drop + np.random.normal(0, 80, n)
    ms_tmt = 2200.0 + time_trend * 130.0 + seasonality * 0.4 + np.random.normal(0, 40, n)

    df_hist = pd.DataFrame({
        "Month": dates.strftime("%Y-%m"),
        "HSD_TMT": np.round(hsd_tmt, 1),
        "MS_TMT": np.round(ms_tmt, 1),
        "IIP_Index": np.round(iip_index, 1),
        "Monsoon_Departure_Pct": np.round(monsoon_departure, 1),
    })
    df_hist.to_csv(csv_path, index=False)
    print(f"Generated Historical Time-Series fixture: {csv_path} ({n} months)")


if __name__ == "__main__":
    generate_fixtures(Path(__file__).parent)
