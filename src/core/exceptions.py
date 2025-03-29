from typing import Dict, Any, Optional


class MCPError(Exception):
    """Base exception class for all MCP-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class MCPConnectionError(MCPError):
    """Exception raised for connection-related errors."""
    pass


class MCPProtocolError(MCPError):
    """Exception raised for protocol-related errors."""
    pass


class MCPTimeoutError(MCPError):
    """Exception raised when a request times out."""
    pass


class MCPAuthError(MCPError):
    """Exception raised for authentication errors."""
    pass


class MCPExecutionError(MCPError):
    """Exception raised for code execution errors."""
    def __init__(self, message: str, exit_code: int = 1, output: str = "", details: Optional[Dict[str, Any]] = None):
        self.exit_code = exit_code
        self.output = output
        super().__init__(message, details)


class MCPConfigError(MCPError):
    """Exception raised for configuration errors."""
    pass
