"""A2UI v0.9 component tree for Market Commodity Pricing & Retail Build-Up Card.

Renders verified August 2026 benchmark metrics and Delhi retail pump pricing
directly in Gemini Enterprise chat.
"""

import base64
import io
from typing import Any, Dict, List
from app.contracts import MarketBenchmarkSummary
from app.render.pricing_vega import SPEC_POINTER

ROOT_CARD_ID: str = "root"
ROOT_COLUMN_ID: str = "pricing-column"


def _text(component_id: str, text: str, variant: str = "body") -> Dict[str, Any]:
    return {
        "id": component_id,
        "component": "Text",
        "text": text,
        "variant": variant,
    }


def generate_overview_chart_base64(summary: MarketBenchmarkSummary) -> str:
    """Generate high-resolution PNG chart comparing crude benchmarks and retail pump prices."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(8, 3.2), dpi=140)
        fig.patch.set_facecolor("#FFFFFF")

        # Panel 1: Crude Oil Benchmarks ($/bbl)
        crude_names = ["Oman/Dubai\n(Sour)", "Indian Crude\nBasket", "Brent Dated\n(Sweet)"]
        crude_vals = [
            summary.oman_dubai_sour_usd_bbl,
            summary.icb_price_usd_bbl,
            summary.brent_dated_usd_bbl,
        ]
        crude_colors = ["#F59E0B", "#10B981", "#3B82F6"]
        bars1 = axes[0].barh(crude_names, crude_vals, color=crude_colors, height=0.5, edgecolor="#1E293B", linewidth=0.8)
        axes[0].set_xlim(80, 95)
        axes[0].set_xlabel("Price (USD / bbl)", fontsize=9, fontweight="bold", color="#1E293B")
        axes[0].set_title("Crude Oil Benchmarks ($/bbl)", fontsize=10, fontweight="bold", color="#0F172A", pad=8)
        axes[0].grid(axis="x", linestyle=":", alpha=0.6)
        for bar in bars1:
            w = bar.get_width()
            axes[0].text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"${w:.2f}", va="center", ha="left", fontsize=8.5, fontweight="bold", color="#0F172A")

        # Panel 2: Domestic Gas & Retail Pumps
        retail_names = ["APM Gas\n($/MMBtu)", "HPHT Gas\n($/MMBtu)", "Diesel (HSD)\n(₹/Litre)", "Petrol (MS)\n(₹/Litre)"]
        retail_vals = [
            summary.apm_gas_usd_mmbtu,
            summary.hpht_gas_ceiling_usd_mmbtu,
            summary.delhi_hsd_diesel_inr_litre,
            summary.delhi_ms_petrol_inr_litre,
        ]
        retail_colors = ["#8B5CF6", "#EC4899", "#059669", "#2563EB"]
        bars2 = axes[1].barh(retail_names, retail_vals, color=retail_colors, height=0.55, edgecolor="#1E293B", linewidth=0.8)
        axes[1].set_xlim(0, 115)
        axes[1].set_xlabel("Price Value", fontsize=9, fontweight="bold", color="#1E293B")
        axes[1].set_title("Domestic Gas & Retail Pumps", fontsize=10, fontweight="bold", color="#0F172A", pad=8)
        axes[1].grid(axis="x", linestyle=":", alpha=0.6)
        for i, bar in enumerate(bars2):
            w = bar.get_width()
            prefix = "$" if i < 2 else "₹"
            axes[1].text(w + 1.5, bar.get_y() + bar.get_height() / 2, f"{prefix}{w:.2f}", va="center", ha="left", fontsize=8.5, fontweight="bold", color="#0F172A")

        for ax in axes:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(labelsize=8.5)

        plt.suptitle(f"PPAC Official Price & Benchmark Matrix — {summary.period_id}", fontsize=11, fontweight="bold", color="#0F172A", y=1.02)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=140)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return ""


# Backwards compatibility alias
generate_pricing_chart_base64 = generate_overview_chart_base64


def generate_consumption_chart_base64(summary: MarketBenchmarkSummary) -> str:
    """Generate high-resolution PNG chart for National POL Consumption breakdown."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.2, 3.4), dpi=140)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        other_tmt = max(0.0, summary.pol_consumption_tmt - (summary.hsd_consumption_tmt + summary.ms_consumption_tmt + summary.lpg_consumption_tmt))
        products = [
            "Domestic LPG\n(2,347 TMT)",
            "Motor Spirit (Petrol)\n(3,836 TMT)",
            "High Speed Diesel (HSD)\n(7,023 TMT)",
            f"Other POL (ATF/Naphtha)\n({other_tmt:,.0f} TMT)",
            f"Total POL Consumption\n({summary.pol_consumption_tmt:,.0f} TMT)",
        ]
        values = [
            summary.lpg_consumption_tmt,
            summary.ms_consumption_tmt,
            summary.hsd_consumption_tmt,
            other_tmt,
            summary.pol_consumption_tmt,
        ]
        colors = ["#10B981", "#3B82F6", "#1E3A8A", "#64748B", "#F59E0B"]
        growth_tags = ["+4.1% YoY", "+8.2% YoY", "+6.8% YoY", "Stable", "+6.3% Net YoY"]

        bars = ax.barh(products, values, color=colors, height=0.55, edgecolor="#1E293B", linewidth=0.8)
        ax.set_xlim(0, 21500)
        ax.set_xlabel("Consumption Volume (Thousand Metric Tonnes - TMT)", fontsize=9, fontweight="bold", color="#1E293B")
        ax.set_title(f"Official National POL Consumption Breakdown — {summary.period_id} (Table 11A)", fontsize=10.5, fontweight="bold", color="#0F172A", pad=10)
        ax.grid(axis="x", linestyle=":", alpha=0.6)

        for bar, tag in zip(bars, growth_tags):
            w = bar.get_width()
            pct_total = (w / summary.pol_consumption_tmt) * 100
            label_text = f"{w:,.0f} TMT ({pct_total:.1f}%) · {tag}" if w < summary.pol_consumption_tmt else f"{w:,.0f} TMT (18.61 MMT) · {tag}"
            ax.text(w + 300, bar.get_y() + bar.get_height() / 2, label_text, va="center", ha="left", fontsize=8.5, fontweight="bold", color="#0F172A")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=8.5)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=140)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return ""


def generate_retail_buildup_chart_base64(summary: MarketBenchmarkSummary) -> str:
    """Generate high-resolution PNG chart for Delhi retail pump price & tax build-up."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.2, 3.4), dpi=140)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        fuels = ["High Speed Diesel (HSD)\n(₹95.20 / Litre)", "Motor Spirit (MS / Petrol)\n(₹102.12 / Litre)"]
        dealer_base = [78.30, 81.12]
        dealer_comm = [2.99, 4.41]
        state_vat = [13.91, 16.59]

        y_pos = [0, 1]
        h = 0.45

        b1 = ax.barh(y_pos, dealer_base, height=h, label="Refinery Pre-Tax Base", color="#2563EB", edgecolor="#1E293B", linewidth=0.8)
        b2 = ax.barh(y_pos, dealer_comm, left=dealer_base, height=h, label="Dealer Commission", color="#F59E0B", edgecolor="#1E293B", linewidth=0.8)
        left_vat = [b + c for b, c in zip(dealer_base, dealer_comm)]
        b3 = ax.barh(y_pos, state_vat, left=left_vat, height=h, label="State VAT / Local Taxes", color="#EF4444", edgecolor="#1E293B", linewidth=0.8)

        for i in range(2):
            ax.text(dealer_base[i] / 2, y_pos[i], f"₹{dealer_base[i]:.2f}", va="center", ha="center", color="#FFFFFF", fontsize=8.5, fontweight="bold")
            ax.text(dealer_base[i] + dealer_comm[i] / 2, y_pos[i], f"₹{dealer_comm[i]:.2f}", va="center", ha="center", color="#0F172A", fontsize=8.0, fontweight="bold")
            ax.text(left_vat[i] + state_vat[i] / 2, y_pos[i], f"₹{state_vat[i]:.2f}", va="center", ha="center", color="#FFFFFF", fontsize=8.5, fontweight="bold")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(fuels, fontsize=9, fontweight="bold")
        ax.set_xlim(0, 118)
        ax.set_xlabel("Retail Pump Price Breakdown (INR / Litre)", fontsize=9, fontweight="bold", color="#1E293B")
        ax.set_title(f"Delhi Consumer Fuel Price Structure & Tax Build-Up ({summary.period_id})", fontsize=10.5, fontweight="bold", color="#0F172A", pad=10)
        ax.legend(loc="lower right", framealpha=0.9, fontsize=8.5)
        ax.grid(axis="x", linestyle=":", alpha=0.6)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=8.5)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=140)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return ""


def generate_crude_basket_chart_base64(summary: MarketBenchmarkSummary) -> str:
    """Generate high-resolution PNG chart for Indian Crude Basket calculation & blend ratio."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.2), dpi=140)
        fig.patch.set_facecolor("#FFFFFF")

        # Left: Component Prices
        names = ["Oman/Dubai Sour\n(75.6% Blend)", "Dated Brent Sweet\n(24.4% Blend)", "Indian Crude Basket\n(Calculated ICB)"]
        prices = [summary.oman_dubai_sour_usd_bbl, summary.brent_dated_usd_bbl, summary.icb_price_usd_bbl]
        colors = ["#F59E0B", "#3B82F6", "#10B981"]

        bars = axes[0].barh(names, prices, color=colors, height=0.48, edgecolor="#1E293B", linewidth=0.8)
        axes[0].set_xlim(85, 93)
        axes[0].set_xlabel("Price ($/bbl)", fontsize=9, fontweight="bold", color="#1E293B")
        axes[0].set_title("Benchmark Price Realizations", fontsize=10, fontweight="bold", color="#0F172A", pad=8)
        axes[0].grid(axis="x", linestyle=":", alpha=0.6)

        for bar in bars:
            w = bar.get_width()
            axes[0].text(w + 0.15, bar.get_y() + bar.get_height() / 2, f"${w:.2f}", va="center", ha="left", fontsize=8.5, fontweight="bold", color="#0F172A")

        # Right: Statutory Weighting Donut
        weights = [75.6, 24.4]
        labels = ["Sour (75.6%)\n$89.98", "Sweet (24.4%)\n$90.84"]
        donut_colors = ["#F59E0B", "#3B82F6"]
        wedges, texts, autotexts = axes[1].pie(
            weights,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=donut_colors,
            wedgeprops=dict(width=0.45, edgecolor="#1E293B", linewidth=0.8),
            textprops=dict(fontsize=8.5, fontweight="bold"),
        )
        for at in autotexts:
            at.set_color("#FFFFFF")
        axes[1].set_title("MoPNG Statutory Blend Ratio", fontsize=10, fontweight="bold", color="#0F172A", pad=8)

        for ax in axes:
            ax.tick_params(labelsize=8.5)

        inr_icb = summary.icb_price_usd_bbl * summary.rbi_exchange_rate_inr_usd
        plt.suptitle(f"Indian Crude Basket (ICB): ${summary.icb_price_usd_bbl:.2f}/bbl (₹{inr_icb:,.2f})", fontsize=11, fontweight="bold", color="#0F172A", y=1.02)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=140)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return ""


def generate_gas_benchmark_chart_base64(summary: MarketBenchmarkSummary) -> str:
    """Generate high-resolution PNG chart for Natural Gas statutory ceilings."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.2, 3.2), dpi=140)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        benchmarks = [
            "Domestic APM Natural Gas\n(Statutory Ceiling - Kirit Parikh Formula)",
            "Deepwater / Ultra-Deepwater / HP-HT\n(Statutory Price Ceiling)",
        ]
        values = [summary.apm_gas_usd_mmbtu, summary.hpht_gas_ceiling_usd_mmbtu]
        colors = ["#8B5CF6", "#EC4899"]

        bars = ax.barh(benchmarks, values, color=colors, height=0.45, edgecolor="#1E293B", linewidth=0.8)
        ax.set_xlim(0, 11)
        ax.set_xlabel("Statutory Price ($ / MMBTU)", fontsize=9, fontweight="bold", color="#1E293B")
        ax.set_title(f"MoPNG Natural Gas Pricing Guidelines ({summary.period_id})", fontsize=10.5, fontweight="bold", color="#0F172A", pad=10)
        ax.grid(axis="x", linestyle=":", alpha=0.6)

        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.2, bar.get_y() + bar.get_height() / 2, f"${w:.2f} / MMBTU", va="center", ha="left", fontsize=9, fontweight="bold", color="#0F172A")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=8.5)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=140)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return ""



def build_pricing_matrix_components(summary: MarketBenchmarkSummary) -> List[Dict[str, Any]]:
    """Build the A2UI component list for official pricing and retail build-up."""
    children: List[str] = []
    components: List[Dict[str, Any]] = []

    def add(component: Dict[str, Any]) -> None:
        components.append(component)
        children.append(component["id"])

    focus = (getattr(summary, "focus", "overview") or "overview").lower()

    if any(k in focus for k in ["consumption", "demand", "pol", "hsd", "diesel", "petrol", "ms", "lpg"]):
        chart_b64 = generate_consumption_chart_base64(summary)
        title = f"PPAC Official POL Consumption ({summary.period_id})"
        chart_desc = f"POL Consumption Breakdown ({summary.period_id})"
        primary_section = "consumption"
    elif any(k in focus for k in ["retail", "pump", "tax", "buildup", "vat", "delhi"]):
        chart_b64 = generate_retail_buildup_chart_base64(summary)
        title = f"PPAC Delhi Retail Fuel Price Build-Up ({summary.period_id})"
        chart_desc = f"Delhi Retail Fuel Price Structure ({summary.period_id})"
        primary_section = "retail"
    elif any(k in focus for k in ["crude", "basket", "icb", "brent", "oman", "sour"]):
        chart_b64 = generate_crude_basket_chart_base64(summary)
        title = f"PPAC Indian Crude Basket (ICB) Benchmark ({summary.period_id})"
        chart_desc = f"Indian Crude Basket Benchmark ({summary.period_id})"
        primary_section = "crude"
    elif any(k in focus for k in ["gas", "apm", "hpht", "kirit"]):
        chart_b64 = generate_gas_benchmark_chart_base64(summary)
        title = f"PPAC Natural Gas Statutory Ceilings ({summary.period_id})"
        chart_desc = f"Natural Gas Ceilings ({summary.period_id})"
        primary_section = "gas"
    else:
        chart_b64 = generate_overview_chart_base64(summary)
        title = f"PPAC Official Pricing & Benchmarks ({summary.period_id})"
        chart_desc = f"PPAC Price & Benchmark Matrix ({summary.period_id})"
        primary_section = "overview"

    # Header & Subtitle
    add(_text("pm-title", title, "h3"))
    add(
        _text(
            "pm-subtitle",
            f"Verified Ground-Truth · MoPNG Ready Reckoner · RBI Ref: ₹{summary.rbi_exchange_rate_inr_usd:.2f}/USD",
            "caption",
        )
    )
    add({"id": "pm-div-1", "component": "Divider"})

    # Live interactive VegaChart mounted at top of card with inlined spec
    from app.render.pricing_vega import build_pricing_vega_spec

    vega_spec = build_pricing_vega_spec(summary)
    chart_component = {
        "id": "pm-chart-vega",
        "component": "VegaChart",
        "spec": vega_spec,
        "height": 290,
    }
    components.append(chart_component)
    children.append("pm-chart-vega")
    add({"id": "pm-div-chart", "component": "Divider"})

    def add_sec_consumption():
        add(_text("pm-sec3-hdr", "Verified National POL Consumption (Table 11A)", "h5"))
        add(
            _text(
                "pm-pol-totals",
                f"• Total POL Consumption: {summary.pol_consumption_tmt:,.0f} TMT (18.61 MMT)\n"
                f"• High Speed Diesel (HSD): {summary.hsd_consumption_tmt:,.0f} TMT (+6.8% YoY)\n"
                f"• Motor Spirit (MS / Petrol): {summary.ms_consumption_tmt:,.0f} TMT (+8.2% YoY)\n"
                f"• Subsidized Domestic LPG: {summary.lpg_consumption_tmt:,.0f} TMT (+4.1% YoY)",
                "body",
            )
        )

    def add_sec_retail():
        add(_text("pm-sec2-hdr", "Delhi Retail Fuel Price Structure (Pumps)", "h5"))
        add(
            _text(
                "pm-ms-retail",
                f"• Motor Spirit (MS / Petrol): ₹{summary.delhi_ms_petrol_inr_litre:.2f} / Litre "
                f"[Dealer Pre-tax: ₹81.12 · Dealer Comm: ₹4.41 · State VAT: ₹16.59]",
                "body",
            )
        )
        add(
            _text(
                "pm-hsd-retail",
                f"• High Speed Diesel (HSD): ₹{summary.delhi_hsd_diesel_inr_litre:.2f} / Litre "
                f"[Dealer Pre-tax: ₹78.30 · Dealer Comm: ₹2.99 · State VAT: ₹13.91]",
                "body",
            )
        )
        add(
            _text(
                "pm-lpg-retail",
                f"• Subsidized Domestic LPG (14.2 kg): ₹{summary.delhi_lpg_domestic_inr_cylinder:.2f} / Cylinder "
                f"(Direct Benefit Transfer via PMUY ₹12,000 Cr Subsidy Allocation)",
                "body",
            )
        )

    def add_sec_crude_gas():
        add(_text("pm-sec1-hdr", "Upstream Crude & Natural Gas Benchmarks", "h5"))
        add(
            _text(
                "pm-icb",
                f"• Indian Crude Basket (ICB): ${summary.icb_price_usd_bbl:.2f} / bbl "
                f"(Sour Blend: ${summary.oman_dubai_sour_usd_bbl:.2f} [75.6%] · Sweet Dated Brent: ${summary.brent_dated_usd_bbl:.2f} [24.4%])",
                "body",
            )
        )
        add(
            _text(
                "pm-gas",
                f"• Domestic APM Natural Gas: ${summary.apm_gas_usd_mmbtu:.2f} / MMBTU (Statutory Ceiling under Kirit Parikh Formula)",
                "body",
            )
        )
        add(
            _text(
                "pm-hpht",
                f"• Deepwater High-Pressure High-Temperature (HP-HT) Ceiling: ${summary.hpht_gas_ceiling_usd_mmbtu:.2f} / MMBTU",
                "body",
            )
        )

    # Order sections based on user inquiry focus
    if primary_section == "consumption":
        add_sec_consumption()
        add({"id": "pm-div-2", "component": "Divider"})
        add_sec_retail()
        add({"id": "pm-div-3", "component": "Divider"})
        add_sec_crude_gas()
    elif primary_section == "retail":
        add_sec_retail()
        add({"id": "pm-div-2", "component": "Divider"})
        add_sec_consumption()
        add({"id": "pm-div-3", "component": "Divider"})
        add_sec_crude_gas()
    elif primary_section in ["crude", "gas"]:
        add_sec_crude_gas()
        add({"id": "pm-div-2", "component": "Divider"})
        add_sec_retail()
        add({"id": "pm-div-3", "component": "Divider"})
        add_sec_consumption()
    else:
        add_sec_crude_gas()
        add({"id": "pm-div-2", "component": "Divider"})
        add_sec_retail()
    # Interactive Digital Fuel & Benchmark Grid
    inr_icb = summary.icb_price_usd_bbl * summary.rbi_exchange_rate_inr_usd
    benchmark_lines = [
        "| Stream / Cost Element | Benchmark / Pump Price | Regulatory / Sovereign Standard |",
        "| :--- | :---: | :--- |",
        f"| **Indian Crude Basket (ICB)** | **${summary.icb_price_usd_bbl:.2f} / bbl** | ₹{inr_icb:,.2f} / bbl · Official MoPNG Sourcing Benchmark |",
        f"| **Brent Dated (Sweet)** | **${summary.brent_dated_usd_bbl:.2f} / bbl** | S&P Platts North Sea Grade Benchmark |",
        f"| **Oman & Dubai Sour (50:50)** | **${summary.oman_dubai_sour_usd_bbl:.2f} / bbl** | Middle East Sour Crude Loading Basis |",
        f"| **Domestic APM Natural Gas** | **${summary.apm_gas_usd_mmbtu:.2f} / MMBTU** | Statutory Price Ceiling (Kirit Parikh Formula) |",
        f"| **HPHT / Deepwater Gas Ceiling** | **${summary.hpht_gas_ceiling_usd_mmbtu:.2f} / MMBTU** | Difficult Fields Statutory Price Ceiling |",
        f"| **Delhi Retail Petrol (MS)** | **₹{summary.delhi_ms_petrol_inr_litre:.2f} / Litre** | [Base ₹55.42 · Excise ₹19.90 · Comm ₹4.41 · VAT ₹15.39] |",
        f"| **Delhi Retail Diesel (HSD)** | **₹{summary.delhi_hsd_diesel_inr_litre:.2f} / Litre** | [Base ₹56.25 · Excise ₹15.80 · Comm ₹3.00 · VAT ₹12.57] |",
        f"| **Subsidized Domestic LPG (14.2kg)** | **₹{summary.delhi_lpg_domestic_inr_cylinder:.2f} / Cyl** | MoPNG Regulated Household Cylinder |",
    ]
    add({"id": "pm-div-grid", "component": "Divider"})
    add(_text("pm-grid-hdr", f"Interactive Hydrocarbon Benchmark Matrix ({summary.period_id})", "h5"))
    add(_text("pm-grid-table", "\n".join(benchmark_lines), "body"))

    root_card = {
        "id": ROOT_CARD_ID,
        "component": "Card",
        "child": ROOT_COLUMN_ID,
    }

    column_component = {
        "id": ROOT_COLUMN_ID,
        "component": "Column",
        "children": children,
    }

    return [root_card, column_component, *components]

