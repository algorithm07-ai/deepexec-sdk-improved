"""Tests for the DeepExecAsyncClient."""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from src.core.async_client import DeepExecAsyncClient
from src.core.models import (
    ExecutionRequest, ExecutionResult,
    GenerationRequest, GenerationResult
)
from src.core.protocols.mcp import (
    PROTOCOL_VERSION,
    MCPRequestType,
    MCPResponseType,
    MCPStatus
)
from src.core.exceptions import (
    MCPAuthError, MCPConnectionError,
    MCPTimeoutError, MCPProtocolError, MCPExecutionError
)


class TestDeepExecAsyncClient:
    """Test the DeepExecAsyncClient."""

    @pytest.fixture
    async def client(self):
        """Create a client for testing."""
        client = DeepExecAsyncClient(
            endpoint="https://test.api.deepexec.com/v1",
            deepseek_key="test_deepseek_key",
            e2b_key="test_e2b_key"
        )
        await client.__aenter__()
        yield client
        await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test creating a session."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "protocol_version": PROTOCOL_VERSION,
            "type": "session_created",
            "session_id": "test_session",
            "status": "success"
        })
        
        # Mock the post method
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        session_id = await client.create_session("test_user")
        
        # Check the result
        assert session_id == "test_session"
        assert client.session_id == "test_session"
        
        # Check the request
        args, kwargs = client.session.post.call_args
        assert args[0] == "https://test.api.deepexec.com/v1/session"
        request_data = kwargs["json"]
        assert request_data["protocol_version"] == PROTOCOL_VERSION
        assert request_data["type"] == "create_session"
        assert request_data["input"]["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_execute_code(self, client):
        """Test executing code."""
        # Set up the client with a session
        client.session_id = "test_session"
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
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
        })
        
        # Mock the post method
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        result = await client.execute_code(
            code="print('Hello, world!')",
            language="python"
        )
        
        # Check the result
        assert isinstance(result, ExecutionResult)
        assert result.output == "Hello, world!\n"
        assert result.exit_code == 0
        assert result.execution_time == 100
        assert result.memory_usage == 10
        
        # Check the request
        args, kwargs = client.session.post.call_args
        assert args[0] == "https://test.api.deepexec.com/v1/execute"
        request_data = kwargs["json"]
        assert request_data["protocol_version"] == PROTOCOL_VERSION
        assert request_data["type"] == "code_execution"
        assert request_data["session_id"] == "test_session"
        assert request_data["input"]["code"] == "print('Hello, world!')"
        assert request_data["input"]["language"] == "python"

    @pytest.mark.asyncio
    async def test_execute_code_error(self, client):
        """Test executing code with an error."""
        # Set up the client with a session
        client.session_id = "test_session"
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "protocol_version": PROTOCOL_VERSION,
            "type": "code_execution_result",
            "session_id": "test_session",
            "status": "success",
            "output": {
                "execution_result": {
                    "output": "Traceback (most recent call last):\n  File \"/tmp/code.py\", line 1\n    print(undefined_variable)\nNameError: name 'undefined_variable' is not defined\n",
                    "exit_code": 1,
                    "execution_time": 50,
                    "memory_usage": 5
                }
            },
            "metadata": {}
        })
        
        # Mock the post method
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        result = await client.execute_code(
            code="print(undefined_variable)",
            language="python"
        )
        
        # Check the result
        assert isinstance(result, ExecutionResult)
        assert "NameError: name 'undefined_variable' is not defined" in result.output
        assert result.exit_code == 1

    @pytest.mark.asyncio
    async def test_generate_text(self, client):
        """Test generating text."""
        # Set up the client with a session
        client.session_id = "test_session"
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
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
        })
        
        # Mock the post method
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        result = await client.generate_text(
            prompt="Tell me about AI",
            model="deepseek-v3",
            max_tokens=1000,
            temperature=0.7
        )
        
        # Check the result
        assert isinstance(result, GenerationResult)
        assert result.text == "AI is a technology that..."
        assert result.model == "deepseek-v3"
        assert result.generation_time == 200
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 50
        assert result.usage.total_tokens == 60
        
        # Check the request
        args, kwargs = client.session.post.call_args
        assert args[0] == "https://test.api.deepexec.com/v1/generate"
        request_data = kwargs["json"]
        assert request_data["protocol_version"] == PROTOCOL_VERSION
        assert request_data["type"] == "text_generation"
        assert request_data["session_id"] == "test_session"
        assert request_data["input"]["prompt"] == "Tell me about AI"
        assert request_data["input"]["max_tokens"] == 1000
        assert request_data["input"]["temperature"] == 0.7
        assert request_data["metadata"]["model"] == "deepseek-v3"

    @pytest.mark.asyncio
    async def test_stream_generate_text(self, client):
        """Test streaming text generation."""
        # Set up the client with a session
        client.session_id = "test_session"
        
        # Mock the response content
        mock_content = MagicMock()
        mock_content.iter_lines = AsyncMock(return_value=[
            b'data: {"text": "AI", "done": false}',
            b'data: {"text": "AI is", "done": false}',
            b'data: {"text": "AI is a technology", "done": true}'
        ].__aiter__())
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = mock_content
        
        # Mock the post method
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Call the method and collect results
        chunks = []
        async for chunk in client.stream_generate_text(
            prompt="Tell me about AI",
            model="deepseek-v3"
        ):
            chunks.append(chunk)
        
        # Check the results
        assert len(chunks) == 3
        assert chunks[0]["text"] == "AI"
        assert chunks[0]["done"] is False
        assert chunks[1]["text"] == "AI is"
        assert chunks[1]["done"] is False
        assert chunks[2]["text"] == "AI is a technology"
        assert chunks[2]["done"] is True
        
        # Check the request
        args, kwargs = client.session.post.call_args
        assert args[0] == "https://test.api.deepexec.com/v1/generate/stream"
        request_data = kwargs["json"]
        assert request_data["protocol_version"] == PROTOCOL_VERSION
        assert request_data["type"] == "text_generation_stream"
        assert request_data["session_id"] == "test_session"

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling."""
        # Set up the client with a session
        client.session_id = "test_session"
        
        # Test authentication error
        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Invalid API key"
            }
        }))
        
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(MCPAuthError):
            await client.execute_code(
                code="print('Hello')",
                language="python"
            )
        
        # Test connection error
        client.session.post.side_effect = asyncio.TimeoutError()
        
        with pytest.raises(MCPTimeoutError):
            await client.execute_code(
                code="print('Hello')",
                language="python"
            )
        
        # Test protocol error
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Invalid request format"
            }
        }))
        client.session.post.side_effect = None
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(MCPProtocolError):
            await client.execute_code(
                code="print('Hello')",
                language="python"
            )

    @pytest.mark.asyncio
    async def test_retry_logic(self, client):
        """Test retry logic for failed requests."""
        # Set up the client with a session
        client.session_id = "test_session"
        client.max_retries = 2
        client.retry_delay = 0.01  # Short delay for testing
        
        # First attempt fails with a 500 error, second attempt succeeds
        mock_error_response = MagicMock()
        mock_error_response.status = 500
        mock_error_response.text = AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Internal server error"
            }
        }))
        
        mock_success_response = MagicMock()
        mock_success_response.status = 200
        mock_success_response.json = AsyncMock(return_value={
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
        })
        
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.side_effect = [
            mock_error_response,
            mock_success_response
        ]
        
        # Call the method
        result = await client.execute_code(
            code="print('Hello, world!')",
            language="python"
        )
        
        # Check that the request was retried
        assert client.session.post.call_count == 2
        assert isinstance(result, ExecutionResult)
        assert result.output == "Hello, world!\n"

    @pytest.mark.asyncio
    async def test_cancel_execution(self, client):
        """Test canceling execution."""
        # Set up the client with a session
        client.session_id = "test_session"
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "protocol_version": PROTOCOL_VERSION,
            "type": "execution_canceled",
            "session_id": "test_session",
            "status": "success"
        })
        
        # Mock the post method
        client.session = MagicMock()
        client.session.post = AsyncMock()
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        await client._cancel_execution("test_session")
        
        # Check the request
        args, kwargs = client.session.post.call_args
        assert args[0] == "https://test.api.deepexec.com/v1/cancel"
        request_data = kwargs["json"]
        assert request_data["protocol_version"] == PROTOCOL_VERSION
        assert request_data["type"] == "cancel_execution"
        assert request_data["session_id"] == "test_session"
