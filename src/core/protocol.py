import re
import json
from typing import Dict, Any, Optional
from .exceptions import MCPProtocolError

# Current protocol version
PROTOCOL_VERSION = "2024.1"

# Supported protocol versions
SUPPORTED_VERSIONS = ["2024.1"]


def build_request_message(
    type: str,
    session_id: Optional[str],
    input: Dict[str, Any],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Build a request message according to the MCP protocol.

    Args:
        type: The request type (e.g., "code_execution", "text_generation").
        session_id: The session ID (can be None for session creation).
        input: The input data for the request.
        metadata: Additional metadata for the request.

    Returns:
        A dictionary containing the formatted request message.
    """
    message = {
        "protocol_version": PROTOCOL_VERSION,
        "type": type,
        "input": input,
        "metadata": metadata
    }

    # Add session_id if provided
    if session_id:
        message["session_id"] = session_id

    return message


def parse_response_message(response: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a response message according to the MCP protocol.

    Args:
        response: The response message from the server.

    Returns:
        A dictionary containing the parsed response data.

    Raises:
        MCPProtocolError: If the response contains an error or is invalid.
    """
    # Validate protocol version
    protocol_version = response.get("protocol_version")
    if not validate_protocol_version(protocol_version):
        raise MCPProtocolError(f"Unsupported protocol version: {protocol_version}")

    # Check for error response
    if response.get("status") == "error" or "error" in response:
        error = response.get("error", {})
        error_code = error.get("code", "unknown_error")
        error_message = error.get("message", "Unknown error occurred")
        error_details = error.get("details", {})
        
        raise MCPProtocolError(
            f"Error ({error_code}): {error_message}", 
            details=error_details
        )

    # Parse response based on type
    response_type = response.get("type")
    
    if response_type == "code_execution_result":
        output = response.get("output", {}).get("execution_result", {})
        return {
            "output": output.get("output", ""),
            "exitCode": output.get("exit_code", 1),
            "executionTime": output.get("execution_time", 0),
            "memoryUsage": output.get("memory_usage", 0),
            "metadata": response.get("metadata", {})
        }
    
    elif response_type == "text_generation_result":
        output = response.get("output", {})
        metadata = response.get("metadata", {})
        usage = metadata.get("usage", {})
        
        return {
            "text": output.get("text", ""),
            "model": metadata.get("model", "unknown"),
            "generationTime": metadata.get("generation_time", 0),
            "usage": {
                "promptTokens": usage.get("prompt_tokens", 0),
                "completionTokens": usage.get("completion_tokens", 0),
                "totalTokens": usage.get("total_tokens", 0)
            }
        }
    
    elif response_type == "session_created":
        return {
            "session_id": response.get("session_id", "")
        }
    
    else:
        # For other response types, return the raw response
        return response


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
    # Session ID should be at least 8 characters and contain only alphanumeric characters,
    # underscores, and hyphens
    if not session_id or len(session_id) < 8:
        raise MCPProtocolError("Invalid session ID: too short")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise MCPProtocolError("Invalid session ID: contains invalid characters")
    
    return True
