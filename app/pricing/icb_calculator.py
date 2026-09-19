"""Indian Crude Basket (ICB) Pricing Calculator with dynamic weighting."""

from typing import Dict, Any


class IndianCrudeBasketCalculator:
    """Computes the composite Indian Crude Basket price according to PPAC methodology."""

    DEFAULT_SOUR_WEIGHT = 75.6  # Oman & Dubai average
    DEFAULT_SWEET_WEIGHT = 24.4  # Dated Brent

    def calculate_icb(
        self,
        brent_usd: float,
        oman_dubai_usd: float,
        usd_inr_rate: float,
        weight_sour: float = DEFAULT_SOUR_WEIGHT,
        weight_sweet: float = DEFAULT_SWEET_WEIGHT,
    ) -> Dict[str, Any]:
        """
        Calculates composite price in USD/bbl and INR/bbl.
        """
        total_weight = weight_sour + weight_sweet
        normalized_sour = weight_sour / total_weight
        normalized_sweet = weight_sweet / total_weight

        # Weighted calculation
        raw_icb_usd = (normalized_sour * oman_dubai_usd) + (normalized_sweet * brent_usd)
        icb_usd = round(raw_icb_usd, 2)
        icb_inr = round(icb_usd * usd_inr_rate, 2)

        return {
            "icb_usd_bbl": icb_usd,
            "icb_inr_bbl": icb_inr,
            "weight_sour_pct": weight_sour,
            "weight_sweet_pct": weight_sweet,
            "usd_inr_rate": usd_inr_rate,
        }
