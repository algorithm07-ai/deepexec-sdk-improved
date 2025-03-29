import pytest
import json
from unittest.mock import patch, MagicMock
from src.core.exceptions import (
    MCPError,
    MCPProtocolError
)


class TestMCPProtocol:
    """Unit tests for the MCP protocol implementation."""

    def test_request_format(self):
        """Test that request messages are correctly formatted."""
        from src.core.protocol import build_request_message

        # Test code execution request
        request = build_request_message(
            type="code_execution",
            session_id="test_session",
            input={"code": "print('hello')"},
            metadata={"language": "python"}
        )

        assert request["protocol_version"] == "2024.1"
        assert request["type"] == "code_execution"
        assert request["session_id"] == "test_session"
        assert request["input"]["code"] == "print('hello')"
        assert request["metadata"]["language"] == "python"

        # Test text generation request
        request = build_request_message(
            type="text_generation",
            session_id="test_session",
            input={"prompt": "Hello, world"},
            metadata={"model": "deepseek-v3"}
        )

        assert request["protocol_version"] == "2024.1"
        assert request["type"] == "text_generation"
        assert request["session_id"] == "test_session"
        assert request["input"]["prompt"] == "Hello, world"
        assert request["metadata"]["model"] == "deepseek-v3"

    def test_response_parsing(self):
        """Test that response messages are correctly parsed."""
        from src.core.protocol import parse_response_message

        # Test successful code execution response
        response = {
            "protocol_version": "2024.1",
            "type": "code_execution_result",
            "session_id": "test_session",
            "request_id": "req_123",
            "status": "success",
            "output": {
                "execution_result": {
                    "output": "hello\n",
                    "exit_code": 0,
                    "execution_time": 100,
                    "memory_usage": 10
                }
            }
        }

        result = parse_response_message(response)
        assert result["output"] == "hello\n"
        assert result["exitCode"] == 0
        assert result["executionTime"] == 100
        assert result["memoryUsage"] == 10

        # Test successful text generation response
        response = {
            "protocol_version": "2024.1",
            "type": "text_generation_result",
            "session_id": "test_session",
            "request_id": "req_123",
            "status": "success",
            "output": {
                "text": "Generated text"
            },
            "metadata": {
                "model": "deepseek-v3",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 50,
                    "total_tokens": 60
                }
            }
        }

        result = parse_response_message(response)
        assert result["text"] == "Generated text"
        assert result["model"] == "deepseek-v3"
        assert result["usage"]["promptTokens"] == 10
        assert result["usage"]["completionTokens"] == 50
        assert result["usage"]["totalTokens"] == 60

    def test_error_response_parsing(self):
        """Test that error responses are correctly parsed and raise appropriate exceptions."""
        from src.core.protocol import parse_response_message

        # Test error response
        response = {
            "protocol_version": "2024.1",
            "type": "error",
            "session_id": "test_session",
            "request_id": "req_123",
            "status": "error",
            "error": {
                "code": "execution_error",
                "message": "Execution failed",
                "details": {
                    "exit_code": 1,
                    "logs": ["Error: execution failed at line 1"]
                }
            }
        }

        with pytest.raises(MCPProtocolError) as exc_info:
            parse_response_message(response)
        assert "Execution failed" in str(exc_info.value)

    def test_invalid_protocol_version(self):
        """Test handling of invalid protocol versions."""
        from src.core.protocol import validate_protocol_version

        # Test valid version
        assert validate_protocol_version("2024.1") is True

        # Test invalid version
        with pytest.raises(MCPProtocolError) as exc_info:
            validate_protocol_version("1000.0")
        assert "Unsupported protocol version" in str(exc_info.value)

    def test_session_id_validation(self):
        """Test validation of session IDs."""
        from src.core.protocol import validate_session_id

        # Test valid session ID
        assert validate_session_id("session_12345") is True

        # Test invalid session ID (too short)
        with pytest.raises(MCPProtocolError) as exc_info:
            validate_session_id("s")
        assert "Invalid session ID" in str(exc_info.value)

        # Test invalid session ID (contains invalid characters)
        with pytest.raises(MCPProtocolError) as exc_info:
            validate_session_id("session;id")
        assert "Invalid session ID" in str(exc_info.value)
