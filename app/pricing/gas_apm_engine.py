"""Statutory Natural Gas Administered Price Mechanism (APM) Calculator (Kirit Parikh Formula)."""

from typing import Dict, Any


class NaturalGasApmEngine:
    """
    Computes statutory domestic natural gas APM price under MoPNG / Kirit Parikh guidelines.
    Formula: 10% of monthly average Indian Crude Basket price of preceding month,
    subject to statutory floor and ceiling constraints with annual escalator.
    """

    DEFAULT_FLOOR_USD = 4.00     # USD / MMBTU
    DEFAULT_CEILING_USD = 6.50   # USD / MMBTU
    INDEXATION_RATIO = 0.10      # 10% of ICB

    def calculate_apm_price(
        self,
        prior_month_icb_usd: float,
        floor_usd: float = DEFAULT_FLOOR_USD,
        ceiling_usd: float = DEFAULT_CEILING_USD,
        escalator_usd: float = 0.0,
    ) -> Dict[str, Any]:
        raw_price = prior_month_icb_usd * self.INDEXATION_RATIO
        effective_ceiling = ceiling_usd + escalator_usd
        effective_floor = floor_usd

        status_notes = []
        if raw_price > effective_ceiling:
            constrained_price = effective_ceiling
            status_notes.append("APM_CEILING_ENFORCED")
        elif raw_price < effective_floor:
            constrained_price = effective_floor
            status_notes.append("APM_FLOOR_ENFORCED")
        else:
            constrained_price = raw_price
            status_notes.append("APM_INDEXED_MARKET_RATE")

        return {
            "raw_indexed_usd_mmbtu": round(raw_price, 2),
            "effective_apm_usd_mmbtu": round(constrained_price, 2),
            "floor_usd": effective_floor,
            "ceiling_usd": effective_ceiling,
            "escalator_usd": escalator_usd,
            "status_notes": status_notes,
        }
