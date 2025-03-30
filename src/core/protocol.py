"""Protocol module for backward compatibility.

This module is maintained for backward compatibility and redirects to the new
implementation in protocols/mcp.py.
"""

from .protocols.mcp import (
    PROTOCOL_VERSION,
    SUPPORTED_VERSIONS,
    build_request_message,
    parse_response_message,
)


def validate_protocol_version(version: str) -> bool:
    """Validate that the protocol version is supported.

    Args:
        version: The protocol version to validate.

    Returns:
        True if the version is supported, False otherwise.
    """
    return version in SUPPORTED_VERSIONS


def validate_session_id(session_id: str) -> bool:
    """Validate that the session ID is properly formatted.

    Args:
        session_id: The session ID to validate.

    Returns:
        True if the session ID is valid, False otherwise.

    Raises:
        MCPProtocolError: If the session ID is invalid.
    """
    import re
    from .exceptions import MCPProtocolError
    
    # Session ID should be at least 8 characters and contain only alphanumeric characters,
    # underscores, and hyphens
    if not session_id or len(session_id) < 8:
        raise MCPProtocolError("Invalid session ID: too short")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise MCPProtocolError("Invalid session ID: contains invalid characters")
    
    return True
