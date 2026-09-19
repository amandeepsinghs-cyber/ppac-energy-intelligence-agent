"""Agent card capabilities declaration for Gemini Enterprise and Agent Registry.

Declares ADK executor and A2UI v0.9 extension support.
"""

from typing import Dict, Any
from a2a.types import AgentCapabilities, AgentExtension

ADK_AGENT_EXECUTOR_EXTENSION_URI: str = (
    "https://google.github.io/adk-docs/a2a/a2a-extension/"
)
A2UI_V09_EXTENSION_URI: str = "https://a2ui.org/a2a-extension/a2ui/v0.9"
DEFAULT_GE_CATALOG_ID: str = (
    "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"
)


def build_agent_capabilities() -> AgentCapabilities:
    """Build the comprehensive A2A capabilities descriptor for the agent card."""
    from google.protobuf.struct_pb2 import Struct

    catalog_params = Struct()
    catalog_params.update({"supportedCatalogIds": [DEFAULT_GE_CATALOG_ID]})

    return AgentCapabilities(
        streaming=True,
        extensions=[
            AgentExtension(
                uri=ADK_AGENT_EXECUTOR_EXTENSION_URI,
                description="Ability to use the modern ADK agent executor implementation",
            ),
            AgentExtension(
                uri=A2UI_V09_EXTENSION_URI,
                description="Ability to render rich A2UI v0.9 interactive components (VegaChart, Canvas, Material 3)",
                params=catalog_params,
            ),
        ],
    )


def get_agent_card() -> Dict[str, Any]:
    """Compatibility agent card dictionary for JSON-RPC endpoints."""
    return {
        "id": "PPAC-REPORT-SYNTHESIS-AGENT",
        "name": "PPAC Autonomous Reporting & Econometric Forecasting Agent",
        "version": "1.0.0",
        "protocol": "a2a-jsonrpc-1.0",
        "description": "Autonomous Petroleum Planning & Analysis Cell Reporting Engine with SARIMAX Forecasting & Native Gemini Enterprise A2UI Surfaces",
        "publisher": {
            "organization": "Petroleum Planning & Analysis Cell (PPAC)",
            "ministry": "Ministry of Petroleum & Natural Gas (MoPNG), Govt of India",
        },
        "endpoints": {
            "jsonrpc": "/a2a/ppac_reporting_agent",
            "agent_card": "/a2a/ppac_reporting_agent/.well-known/agent-card.json",
        },
        "methods": [
            {
                "name": "generate_report_draft",
                "description": "Trigger scheduled or on-demand Zero-to-Draft publication pipeline.",
                "params": {
                    "period_id": {"type": "string", "example": "2026-08"},
                    "report_type": {"type": "string", "enum": ["FLASH_REPORT", "READY_RECKONER"]},
                },
                "result": {
                    "document_uri": "string",
                    "active_anomalies_count": "integer",
                    "a2ui_summary_surface": "object",
                },
            },
            {
                "name": "resolve_audit_anomaly",
                "description": "Resolve flagged line-item exceptions with an audit rationale.",
                "params": {
                    "anomaly_id": {"type": "string", "example": "FLAG-A1B2C3"},
                    "corrected_val": {"type": "number", "example": 445.0},
                    "rationale": {"type": "string"},
                },
                "result": {
                    "resolved": "boolean",
                    "document_status": "string",
                    "new_draft_uri": "string",
                },
            },
        ],
        "capabilities": {
            "streaming": True,
            "extensions": [
                ADK_AGENT_EXECUTOR_EXTENSION_URI,
                A2UI_V09_EXTENSION_URI,
            ],
        },
    }
