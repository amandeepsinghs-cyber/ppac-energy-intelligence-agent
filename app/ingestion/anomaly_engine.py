"""Anomaly Detection & Scoring Engine for PPAC Reporting Pipeline."""

from typing import List, Dict, Any, Tuple
from app.canonical.models import AuditAnomaly, SeverityLevel


class AnomalyEngine:
    """Evaluates line-item consumption variances and flags exceptions for Section 0."""

    def __init__(self, warning_threshold_pct: float = 10.0, critical_threshold_pct: float = 15.0):
        self.warning_threshold = warning_threshold_pct
        self.critical_threshold = critical_threshold_pct

    def evaluate_variances(self, comparisons: List[Dict[str, Any]], period_id: str) -> List[AuditAnomaly]:
        anomalies: List[AuditAnomaly] = []

        for item in comparisons:
            cur_vol = item.get("current_volume")
            prior_vol = item.get("prior_volume")

            if prior_vol is None or prior_vol <= 0:
                continue

            delta_pct = ((cur_vol - prior_vol) / prior_vol) * 100.0

            if abs(delta_pct) >= self.warning_threshold:
                severity = (
                    SeverityLevel.CRITICAL
                    if abs(delta_pct) >= self.critical_threshold
                    else SeverityLevel.WARNING
                )
                product_name = getattr(item["product"], "value", str(item["product"]))
                field_desc = f"{item['sector']} {product_name} Sales"
                expected_min = round(prior_vol * 0.90, 1)
                expected_max = round(prior_vol * 1.10, 1)

                anomaly = AuditAnomaly(
                    period_id=period_id,
                    entity_id=item["entity"],
                    severity=severity,
                    field_name=field_desc,
                    reported_value=round(cur_vol, 1),
                    expected_range=(expected_min, expected_max),
                    variance_pct=round(delta_pct, 2),
                    source_reference=item["source_reference"],
                )
                anomalies.append(anomaly)

        return anomalies
