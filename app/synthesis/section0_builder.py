"""Section 0: AI Audit & Review Checklist Generator for Zero-to-Draft documents."""

from typing import List
from app.canonical.models import AuditAnomaly, SeverityLevel


class Section0AuditBuilder:
    """Formats tagged ingestion & calculation anomalies into an actionable executive audit checklist."""

    def build_markdown_checklist(self, anomalies: List[AuditAnomaly]) -> str:
        lines = []
        lines.append("=" * 80)
        lines.append("🔴 SECTION 0: AI AUDIT & REVIEW CHECKLIST (ACTION REQUIRED BEFORE PUBLISHING)")
        lines.append("=" * 80)

        active_flags = [a for a in anomalies if a.status != "RESOLVED"]
        critical_count = sum(1 for a in active_flags if a.severity == SeverityLevel.CRITICAL)
        warning_count = sum(1 for a in active_flags if a.severity == SeverityLevel.WARNING)

        lines.append(
            f"Instructions: Pipeline completed with {len(active_flags)} active anomalies "
            f"({critical_count} CRITICAL, {warning_count} WARNING). "
            f"Review and resolve each item below. Remove this section prior to statutory release.\n"
        )

        if not active_flags:
            lines.append(" [✔] ALL RECONCILIATION & ANOMALY CHECKS PASSED. DOCUMENT READY FOR SIGN-OFF.")
            lines.append("-" * 80)
            return "\n".join(lines)

        for a in active_flags:
            box = "[ ]"
            sev_tag = f"🔴 {a.severity.value}" if a.severity == SeverityLevel.CRITICAL else f"🟡 {a.severity.value}"
            lines.append(f" {box} {a.anomaly_id} | {sev_tag} | Entity: {a.entity_id} | Metric: {a.field_name}")
            lines.append(f"     • Issue: Ingested {a.reported_value:,.1f} TMT ({a.variance_pct:+.1f}% vs baseline). Expected: {a.expected_range[0]:,.1f} to {a.expected_range[1]:,.1f} TMT.")
            lines.append(f"     • Lineage: {a.source_reference}")
            lines.append(f"     • Action Required: Verify with {a.entity_id} coordinator; update cell or submit override via ResolveAuditFlag API.\n")

        lines.append("-" * 80)
        return "\n".join(lines)
