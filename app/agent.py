"""Root entry point for the PPAC Autonomous Reporting Agent application.

Delegates agent construction to app.integration.agent.
"""

from app.integration.agent import app, root_agent

__all__ = ["root_agent", "app"]
