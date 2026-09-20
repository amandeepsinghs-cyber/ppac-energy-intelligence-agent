"""A2UI v0.9 component tree for Statutory Report Artifact Release Card.

Renders approved report metadata and sovereign GCS download paths in Gemini Enterprise.
"""

from typing import Any, Dict, List
from app.contracts import ReportArtifactSummary

ROOT_CARD_ID: str = "root"
ROOT_COLUMN_ID: str = "report-column"


def _text(component_id: str, text: str, variant: str = "body") -> Dict[str, Any]:
    return {
        "id": component_id,
        "component": "Text",
        "text": text,
        "variant": variant,
    }


def build_report_artifact_components(summary: ReportArtifactSummary) -> List[Dict[str, Any]]:
    """Build the A2UI component list for approved statutory report release."""
    children: List[str] = []
    components: List[Dict[str, Any]] = []

    def add(component: Dict[str, Any]) -> None:
        components.append(component)
        children.append(component["id"])

    # Title & Badge
    add(_text("rep-title", summary.title, "h3"))
    add(
        _text(
            "rep-subtitle",
            f"Period: {summary.period_id}  ·  Status: {summary.status}  ·  Published: {summary.generated_at}",
            "caption",
        )
    )
    add({"id": "rep-div-1", "component": "Divider"})

    # Executive Highlights
    add(_text("rep-hl-hdr", "Statutory Executive Findings (Section 0)", "h5"))
    for idx, point in enumerate(summary.executive_summary_points[:5]):
        add(_text(f"rep-point-{idx+1}", f"• {point}", "body"))

    add({"id": "rep-div-2", "component": "Divider"})

    # Download & Google Docs links
    add(_text("rep-dl-hdr", "Verified Statutory Artifacts & Sovereign Reports", "h5"))
    gdocs_url = summary.google_docs_url or "https://docs.google.com/document/d/1Ra0pXfO9qu5b8hvTfWJhSZlbR3bWBKRZNV-98MkS2Io/edit"
    html_url = summary.html_web_url or f"https://storage.cloud.google.com/og-sovereign-ppac-data/3_artifacts/{summary.period_id}/approved/PPAC_Executive_Report_{summary.period_id}_Approved.html"
    docx_url = summary.docx_web_url or f"https://storage.cloud.google.com/og-sovereign-ppac-data/3_artifacts/{summary.period_id}/approved/PPAC_Executive_Report_{summary.period_id}_Approved.docx"

    # Direct interactive web links
    add(_text("rep-dl-gdocs-link", f"📝 Open in Google Docs (Chromebook Native): {gdocs_url}", "body"))
    add(_text("rep-dl-html-link", f"🌐 Open HTML Executive Dashboard: {html_url}", "body"))
    add(_text("rep-dl-docx-link", f"📄 Download Word (.docx): {docx_url}", "caption"))
    add(_text("rep-dl-vault", f"🔒 Sovereign GCS Vault Archive: {summary.docx_gcs_uri}", "caption"))

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
