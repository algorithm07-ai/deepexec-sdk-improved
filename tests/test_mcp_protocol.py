"""Tests for the MCP protocol implementation."""

import pytest
import json
from unittest.mock import patch, MagicMock

from src.core.protocols.mcp import (
    PROTOCOL_VERSION,
    build_request_message,
    parse_response_message,
    MCPRequestType,
    MCPResponseType,
    MCPStatus,
    MCPErrorCode,
    MCPBaseMessage,
    MCPRequestBase,
    MCPResponseBase,
    MCPErrorDetail,
    MCPErrorResponse,
    CreateSessionInput,
    CreateSessionRequest,
    SessionCreatedResponse,
    CodeExecutionInput,
    CodeExecutionRequest,
    ExecutionResultOutput,
    CodeExecutionOutput,
    CodeExecutionResultResponse,
    TextGenerationInput,
    TextGenerationMetadata,
    TextGenerationRequest,
    TextGenerationStreamRequest,
    TokenUsage,
    TextGenerationOutput,
    TextGenerationResultMetadata,
    TextGenerationResultResponse,
    TextGenerationStreamChunk,
    CancelExecutionRequest,
    ExecutionCanceledResponse
)
from src.core.exceptions import MCPProtocolError


class TestMCPProtocolModels:
    """Test the MCP protocol models."""

    def test_base_message(self):
        """Test the base message model."""
        message = MCPBaseMessage()
        assert message.protocol_version == PROTOCOL_VERSION

        # Test validation
        with pytest.raises(ValueError):
            MCPBaseMessage(protocol_version="invalid")

    def test_request_base(self):
        """Test the request base model."""
        request = MCPRequestBase(type="test")
        assert request.protocol_version == PROTOCOL_VERSION
        assert request.type == "test"
        assert request.session_id is None
        assert request.input == {}
        assert request.metadata == {}

    def test_response_base(self):
        """Test the response base model."""
        response = MCPResponseBase(type="test")
        assert response.protocol_version == PROTOCOL_VERSION
        assert response.type == "test"
        assert response.session_id is None
        assert response.status == MCPStatus.SUCCESS

    def test_error_response(self):
        """Test the error response model."""
        error_detail = MCPErrorDetail(message="Test error")
        response = MCPErrorResponse(error=error_detail)
        assert response.status == MCPStatus.ERROR
        assert response.error.code == MCPErrorCode.UNKNOWN_ERROR
        assert response.error.message == "Test error"

    def test_create_session_request(self):
        """Test the create session request model."""
        input_data = CreateSessionInput(user_id="test_user")
        request = CreateSessionRequest(input=input_data)
        assert request.type == MCPRequestType.CREATE_SESSION
        assert request.input.user_id == "test_user"

    def test_session_created_response(self):
        """Test the session created response model."""
        response = SessionCreatedResponse(session_id="test_session")
        assert response.type == MCPResponseType.SESSION_CREATED
        assert response.session_id == "test_session"

    def test_code_execution_request(self):
        """Test the code execution request model."""
        input_data = CodeExecutionInput(
            code="print('Hello, world!')",
            language="python"
        )
        request = CodeExecutionRequest(
            session_id="test_session",
            input=input_data
        )
        assert request.type == MCPRequestType.CODE_EXECUTION
        assert request.session_id == "test_session"
        assert request.input.code == "print('Hello, world!')"
        assert request.input.language == "python"

        # Test validation
        with pytest.raises(ValueError):
            CodeExecutionInput(code="", language="python")

        with pytest.raises(ValueError):
            CodeExecutionInput(code="print('Hello')", language="invalid")

    def test_code_execution_result_response(self):
        """Test the code execution result response model."""
        execution_result = ExecutionResultOutput(
            output="Hello, world!\n",
            exit_code=0,
            execution_time=100,
            memory_usage=10
        )
        output = CodeExecutionOutput(execution_result=execution_result)
        response = CodeExecutionResultResponse(
            session_id="test_session",
            output=output
        )
        assert response.type == MCPResponseType.CODE_EXECUTION_RESULT
        assert response.session_id == "test_session"
        assert response.output.execution_result.output == "Hello, world!\n"
        assert response.output.execution_result.exit_code == 0

    def test_text_generation_request(self):
        """Test the text generation request model."""
        input_data = TextGenerationInput(prompt="Generate text about AI")
        metadata = TextGenerationMetadata(model="deepseek-v3")
        request = TextGenerationRequest(
            session_id="test_session",
            input=input_data,
            metadata=metadata
        )
        assert request.type == MCPRequestType.TEXT_GENERATION
        assert request.session_id == "test_session"
        assert request.input.prompt == "Generate text about AI"
        assert request.metadata.model == "deepseek-v3"

        # Test validation
        with pytest.raises(ValueError):
            TextGenerationInput(prompt="")

        with pytest.raises(ValueError):
            TextGenerationInput(prompt="test", temperature=1.5)

        with pytest.raises(ValueError):
            TextGenerationInput(prompt="test", max_tokens=0)

    def test_text_generation_result_response(self):
        """Test the text generation result response model."""
        output = TextGenerationOutput(text="AI is a technology that...")
        usage = TokenUsage(prompt_tokens=10, completion_tokens=50, total_tokens=60)
        metadata = TextGenerationResultMetadata(
            model="deepseek-v3",
            generation_time=200,
            usage=usage
        )
        response = TextGenerationResultResponse(
            session_id="test_session",
            output=output,
            metadata=metadata
        )
        assert response.type == MCPResponseType.TEXT_GENERATION_RESULT
        assert response.session_id == "test_session"
        assert response.output.text == "AI is a technology that..."
        assert response.metadata.model == "deepseek-v3"
        assert response.metadata.usage.prompt_tokens == 10
        assert response.metadata.usage.completion_tokens == 50
        assert response.metadata.usage.total_tokens == 60

    def test_stream_generation_chunk(self):
        """Test the stream generation chunk model."""
        chunk = TextGenerationStreamChunk(text="AI", done=False)
        assert chunk.text == "AI"
        assert chunk.done is False

        final_chunk = TextGenerationStreamChunk(text="AI is a technology", done=True)
        assert final_chunk.text == "AI is a technology"
        assert final_chunk.done is True

    def test_cancel_execution_request(self):
        """Test the cancel execution request model."""
        request = CancelExecutionRequest(session_id="test_session")
        assert request.type == MCPRequestType.CANCEL_EXECUTION
        assert request.session_id == "test_session"

    def test_execution_canceled_response(self):
        """Test the execution canceled response model."""
        response = ExecutionCanceledResponse(session_id="test_session")
        assert response.type == MCPResponseType.EXECUTION_CANCELED
        assert response.session_id == "test_session"


class TestMCPProtocolFunctions:
    """Test the MCP protocol utility functions."""

    def test_build_request_message(self):
        """Test building a request message."""
        message = build_request_message(
            type="test_type",
            session_id="test_session",
            input={"key": "value"},
            metadata={"meta_key": "meta_value"}
        )
        assert message["protocol_version"] == PROTOCOL_VERSION
        assert message["type"] == "test_type"
        assert message["session_id"] == "test_session"
        assert message["input"] == {"key": "value"}
        assert message["metadata"] == {"meta_key": "meta_value"}

        # Test without session_id
        message = build_request_message(
            type="test_type",
            session_id=None,
            input={"key": "value"},
            metadata={"meta_key": "meta_value"}
        )
        assert "session_id" not in message

    def test_parse_response_message(self):
        """Test parsing a response message."""
        # Test session created response
        response = {
            "protocol_version": PROTOCOL_VERSION,
            "type": "session_created",
            "session_id": "test_session",
            "status": "success"
        }
        parsed = parse_response_message(response)
        assert parsed["session_id"] == "test_session"

        # Test code execution result response
        response = {
            "protocol_version": PROTOCOL_VERSION,
            "type": "code_execution_result",
            "session_id": "test_session",
            "status": "success",
            "output": {
                "execution_result": {
                    "output": "Hello, world!\n",
                    "exit_code": 0,
                    "execution_time": 100,
                    "memory_usage": 10
                }
            },
            "metadata": {}
        }
        parsed = parse_response_message(response)
        assert parsed["output"] == "Hello, world!\n"
        assert parsed["exitCode"] == 0
        assert parsed["executionTime"] == 100
        assert parsed["memoryUsage"] == 10

        # Test text generation result response
        response = {
            "protocol_version": PROTOCOL_VERSION,
            "type": "text_generation_result",
            "session_id": "test_session",
            "status": "success",
            "output": {
                "text": "AI is a technology that..."
            },
            "metadata": {
                "model": "deepseek-v3",
                "generation_time": 200,
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 50,
                    "total_tokens": 60
                }
            }
        }
        parsed = parse_response_message(response)
        assert parsed["text"] == "AI is a technology that..."
        assert parsed["model"] == "deepseek-v3"
        assert parsed["generationTime"] == 200
        assert parsed["usage"]["promptTokens"] == 10
        assert parsed["usage"]["completionTokens"] == 50
        assert parsed["usage"]["totalTokens"] == 60

        # Test error response
        response = {
            "protocol_version": PROTOCOL_VERSION,
            "status": "error",
            "error": {
                "code": "authentication_error",
                "message": "Invalid API key",
                "details": {}
            }
        }
        with pytest.raises(MCPProtocolError) as excinfo:
            parse_response_message(response)
        assert "Error (authentication_error): Invalid API key" in str(excinfo.value)

        # Test invalid protocol version
        response = {
            "protocol_version": "invalid",
            "type": "session_created",
            "session_id": "test_session",
            "status": "success"
        }
        with pytest.raises(MCPProtocolError) as excinfo:
            parse_response_message(response)
        assert "Unsupported protocol version" in str(excinfo.value)
