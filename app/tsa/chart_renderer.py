"""Publication-grade chart generator for PPAC forecasts and reports."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

from app.canonical.models import ForecastResult, ProductType


class ForecastChartRenderer:
    """Renders high-resolution trend charts for document embedding."""

    def render_forecast_chart(
        self,
        historical_csv: Path,
        forecast: ForecastResult,
        output_path: Path,
        history_window_months: int = 24,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_hist = pd.read_csv(historical_csv)
        recent_df = df_hist.tail(history_window_months)

        target_col = "HSD_TMT" if forecast.product_type == ProductType.HSD else "MS_TMT"
        prod_title = "High-Speed Diesel (HSD)" if forecast.product_type == ProductType.HSD else "Motor Spirit (Petrol)"

        plt.figure(figsize=(10, 5), dpi=200)

        # Plot historical curve
        hist_x = list(recent_df["Month"])
        hist_y = list(recent_df[target_col])
        plt.plot(hist_x, hist_y, label="Historical Consumption (TMT)", color="#1F4E79", linewidth=2.2, marker="o", markersize=4)

        # Connect last historical point to forecast
        fc_x = [hist_x[-1]] + forecast.forecast_months
        fc_y = [hist_y[-1]] + forecast.point_forecast_tmt
        plt.plot(fc_x, fc_y, label=f"60-Day Forecast ({forecast.model_name})", color="#C00000", linewidth=2.5, linestyle="--", marker="s", markersize=5)

        # Shaded 95% confidence band
        lower_y = [hist_y[-1]] + forecast.lower_bound_95_tmt
        upper_y = [hist_y[-1]] + forecast.upper_bound_95_tmt
        plt.fill_between(fc_x, lower_y, upper_y, color="#C00000", alpha=0.15, label="95% Confidence Interval")

        plt.title(f"PPAC National Demand Trajectory: {prod_title} (Thousand Metric Tonnes)", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Month", fontsize=10, labelpad=8)
        plt.ylabel("Volume (TMT)", fontsize=10, labelpad=8)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.yticks(fontsize=8)
        plt.legend(loc="upper left", framealpha=0.9, fontsize=9)

        # Add MAPE annotation
        plt.annotate(
            f"Backtest MAPE: {forecast.mape_backtest_pct:.2f}%",
            xy=(0.78, 0.05),
            xycoords="axes fraction",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", fc="#F2F2F2", ec="#CCCCCC"),
        )

        plt.tight_layout()
        plt.savefig(output_path, format="png")
        plt.close()

        forecast.chart_artifact_path = str(output_path)
        return output_path
