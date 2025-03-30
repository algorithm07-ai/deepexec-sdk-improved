import pytest
import asyncio
from src.core.async_client import DeepExecAsyncClient
from src.core.exceptions import MCPAuthError


@pytest.mark.asyncio
async def test_successful_authentication(mock_server):
    """Test successful authentication with valid API keys."""
    async with DeepExecAsyncClient(
        endpoint=mock_server.url,
        deepseek_key="valid_key",
        e2b_key="valid_e2b_key"
    ) as client:
        # The connection should succeed
        session_id = await client.create_session("test_user")
        assert session_id is not None
        assert isinstance(session_id, str)


@pytest.mark.asyncio
async def test_invalid_deepseek_key(mock_server):
    """Test authentication failure with invalid DeepSeek API key."""
    # Configure the mock server to return an auth error for invalid keys
    mock_server.set_error_mode(True, 401, "Invalid authentication credentials")

    with pytest.raises(MCPAuthError) as exc_info:
        async with DeepExecAsyncClient(
            endpoint=mock_server.url,
            deepseek_key="invalid_key",
            e2b_key="valid_e2b_key"
        ) as client:
            await client.create_session("test_user")

    assert "Invalid authentication credentials" in str(exc_info.value)

    # Reset the mock server for other tests
    mock_server.set_error_mode(False)


@pytest.mark.asyncio
async def test_invalid_e2b_key(mock_server):
    """Test authentication failure with invalid E2B API key."""
    # Configure the mock server to return an auth error for invalid keys
    mock_server.set_error_mode(True, 401, "Invalid E2B API key")

    with pytest.raises(MCPAuthError) as exc_info:
        async with DeepExecAsyncClient(
            endpoint=mock_server.url,
            deepseek_key="valid_key",
            e2b_key="invalid_e2b_key"
        ) as client:
            await client.create_session("test_user")

    assert "Invalid E2B API key" in str(exc_info.value)

    # Reset the mock server for other tests
    mock_server.set_error_mode(False)


@pytest.mark.asyncio
async def test_missing_api_keys(mock_server):
    """Test authentication failure with missing API keys."""
    with pytest.raises(MCPAuthError) as exc_info:
        async with DeepExecAsyncClient(
            endpoint=mock_server.url
            # No API keys provided
        ) as client:
            await client.create_session("test_user")

    assert "API key" in str(exc_info.value)


@pytest.mark.asyncio
async def test_token_expiration_and_refresh(mock_server):
    """Test token expiration and automatic refresh."""
    # First request succeeds
    async with DeepExecAsyncClient(
        endpoint=mock_server.url,
        deepseek_key="valid_key",
        e2b_key="valid_e2b_key"
    ) as client:
        session_id = await client.create_session("test_user")
        assert session_id is not None

        # Configure the mock server to return a token expiration error
        mock_server.set_error_mode(True, 401, "Token expired")

        # This should trigger a token refresh and retry
        mock_server.set_error_mode(False)  # Reset for the retry
        result = await client.execute_code("print('hello')", "python")
        assert result.exit_code == 0
        assert "hello" in result.output


@pytest.mark.asyncio
async def test_rate_limiting(mock_server):
    """Test handling of rate limiting errors."""
    # Configure the mock server to return a rate limit error
    mock_server.set_error_mode(True, 429, "Rate limit exceeded")

    async with DeepExecAsyncClient(
        endpoint=mock_server.url,
        deepseek_key="valid_key",
        e2b_key="valid_e2b_key"
    ) as client:
        # This should implement retry with backoff
        with pytest.raises(MCPAuthError) as exc_info:
            await client.execute_code("print('hello')", "python")

        assert "Rate limit exceeded" in str(exc_info.value)

    # Reset the mock server for other tests
    mock_server.set_error_mode(False)
