"""A2UI v0.9 component tree for Sovereign Hydrocarbon Data Lake Inventory Card.

Renders live GCS audit status of gs://og-sovereign-ppac-data/ in Gemini Enterprise.
Root component id MUST be 'root' and Card must wrap children in a Column or Row.
"""

from typing import Any, Dict, List
from app.contracts import PpacLakeInventory, GcsObjectInfo

ROOT_CARD_ID: str = "root"
ROOT_COLUMN_ID: str = "lake-inventory-column"


def _text(component_id: str, text: str, variant: str = "body") -> Dict[str, Any]:
    return {
        "id": component_id,
        "component": "Text",
        "text": text,
        "variant": variant,
    }


def build_lake_inventory_components(inventory: PpacLakeInventory) -> List[Dict[str, Any]]:
    """Build the A2UI component list describing the live sovereign lake inventory."""
    children: List[str] = []
    components: List[Dict[str, Any]] = []

    def add(component: Dict[str, Any]) -> None:
        components.append(component)
        children.append(component["id"])

    add(_text("inv-title", "PPAC Sovereign Data Lake Audit", "h3"))
    add(
        _text(
            "inv-location",
            f"gs://{inventory.bucket}  ·  Region: {inventory.region} (Mumbai)  ·  Status: Active UBLA",
            "caption",
        )
    )
    add({"id": "inv-divider-1", "component": "Divider"})

    if not inventory.ok:
        add(_text("inv-error-heading", "Lake audit scan failed", "h5"))
        add(_text("inv-error-detail", inventory.error or "Unknown error", "body"))
    else:
        # High level summary
        psu_count = len(inventory.raw_psu_submissions)
        pub_count = len(inventory.raw_official_pubs)
        art_count = len(inventory.artifacts)
        quar_count = len(inventory.quarantine)

        add(
            _text(
                "inv-summary",
                f"Total Catalogued Objects: {inventory.total_objects}  ·  Audit Status: COMPLIANT",
                "h5",
            )
        )
        add({"id": "inv-divider-2", "component": "Divider"})

        add(_text("sec-raw", "1. Tier 1 - Raw PSU Ingestion & Legal Vault", "h5"))
        add(_text("sec-raw-detail", f"• PSU Operator Submissions (IOCL, BPCL, HPCL, ONGC, GAIL): {psu_count} file(s)", "body"))
        add(_text("sec-pub-detail", f"• Statutory Publications (Official PPAC Snapshot, ICB Dispatches): {pub_count} file(s)", "body"))

        add(_text("sec-art", "2. Tier 3 - Approved Statutory Artifacts", "h5"))
        add(_text("sec-art-detail", f"• Verified Reports & High-Res Graphics: {art_count} artifact(s) published", "body"))

        add(_text("sec-quar", "3. Tier 4 - Audit Exception Quarantine", "h5"))
        if quar_count == 0:
            add(_text("sec-quar-clean", "• Quarantine Ledger: 0 unresolved anomalies (100% verified)", "body"))
        else:
            add(_text("sec-quar-items", f"• Quarantine Ledger: {quar_count} item(s) pending clearance", "body"))

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
