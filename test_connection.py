import pytest
import asyncio
import aiohttp
from src.core.async_client import DeepExecAsyncClient
from src.core.exceptions import MCPConnectionError, MCPTimeoutError


@pytest.mark.asyncio
async def test_connection_retry(mock_server):
    """Test connection retry mechanism when server is temporarily unavailable."""
    # Configure the mock server to be temporarily unavailable
    mock_server.set_error_mode(True, 503, "Service Unavailable")

    # Set the client to retry a few times
    async with DeepExecAsyncClient(
        endpoint=mock_server.url,
        max_retries=3,
        retry_delay=0.1  # Short delay for testing
    ) as client:
        # This should fail after retrying
        with pytest.raises(MCPConnectionError) as exc_info:
            await client.create_session("test_user")

        assert "Service Unavailable" in str(exc_info.value)

    # Reset the mock server for other tests
    mock_server.set_error_mode(False)


@pytest.mark.asyncio
async def test_connection_recovery(mock_server):
    """Test connection recovery after temporary failure."""
    # Configure the mock server to fail once then recover
    mock_server.set_error_mode(True, 503, "Service Unavailable", fail_count=1)

    # Set the client to retry
    async with DeepExecAsyncClient(
        endpoint=mock_server.url,
        max_retries=3,
        retry_delay=0.1  # Short delay for testing
    ) as client:
        # This should succeed after one retry
        session_id = await client.create_session("test_user")
        assert session_id is not None


@pytest.mark.asyncio
async def test_connection_timeout(mock_server):
    """Test connection timeout handling."""
    # Configure the mock server to delay responses
    mock_server.set_delay(5.0)  # 5 second delay

    # Set a short timeout
    async with DeepExecAsyncClient(
        endpoint=mock_server.url,
        timeout=0.5  # 0.5 second timeout
    ) as client:
        with pytest.raises(MCPTimeoutError) as exc_info:
            await client.create_session("test_user")

        assert "timed out" in str(exc_info.value).lower()

    # Reset the mock server for other tests
    mock_server.set_delay(0)


@pytest.mark.asyncio
async def test_concurrent_connections(mock_server):
    """Test multiple concurrent connections to the server."""
    async def create_and_use_client(user_id):
        async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
            session_id = await client.create_session(f"user_{user_id}")
            assert session_id is not None
            result = await client.execute_code(f"print('Hello from user {user_id}')", "python")
            assert result.exit_code == 0
            assert f"Hello from user {user_id}" in result.output
            return user_id

    # Create multiple concurrent clients
    tasks = [create_and_use_client(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all clients completed successfully
    assert sorted(results) == list(range(5))


@pytest.mark.asyncio
async def test_connection_with_invalid_endpoint(mock_server):
    """Test connection to an invalid endpoint."""
    # Use a non-existent endpoint
    async with DeepExecAsyncClient(endpoint="http://non-existent-endpoint:12345") as client:
        with pytest.raises(MCPConnectionError) as exc_info:
            await client.create_session("test_user")

        # Check that the error message contains information about the connection failure
        assert "connection" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_graceful_shutdown(mock_server):
    """Test graceful shutdown of the client connection."""
    client = DeepExecAsyncClient(endpoint=mock_server.url)
    
    # Open the connection
    await client.__aenter__()
    session_id = await client.create_session("test_user")
    assert session_id is not None
    
    # Execute a command
    result = await client.execute_code("print('hello')", "python")
    assert result.exit_code == 0
    
    # Close the connection gracefully
    await client.__aexit__(None, None, None)
    
    # Verify the client is closed by attempting to use it (should fail)
    with pytest.raises(MCPConnectionError) as exc_info:
        await client.execute_code("print('should fail')", "python")
    
    assert "no active session" in str(exc_info.value).lower()
