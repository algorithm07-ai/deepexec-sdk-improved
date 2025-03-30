"""Protocol implementations for the DeepExec SDK.

This package contains implementations of various protocols used by the SDK,
including the MCP (Model Communication Protocol) used for communication with
the DeepExec service.
"""

from . import mcp

__all__ = ["mcp"]
