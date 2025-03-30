import pytest
import asyncio
from src.core.async_client import DeepExecAsyncClient
from src.core.exceptions import MCPTimeoutError, MCPExecutionError


@pytest.mark.asyncio
async def test_code_execution_happy_path(mock_server):
    """Test successful code execution with the async client."""
    async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
        result = await client.execute_code("print('hello')", "python")
        assert result.output == "hello\n"
        assert result.exit_code == 0


@pytest.mark.asyncio
async def test_code_execution_timeout(mock_server):
    """Test code execution timeout with the async client."""
    mock_server.set_delay(10.0)  # Set server delay
    async with DeepExecAsyncClient(endpoint=mock_server.url, timeout=1.0) as client:
        with pytest.raises(MCPTimeoutError):
            await client.execute_code("import time; time.sleep(5)", "python")


@pytest.mark.asyncio
async def test_code_execution_error(mock_server):
    """Test code execution that results in an error."""
    # Configure the mock server to return an error
    mock_server.set_response("/v1/execute", {
        "protocol_version": "2024.1",
        "type": "code_execution_result",
        "session_id": "test_session",
        "request_id": "req_123",
        "status": "success",
        "output": {
            "execution_result": {
                "output": "Error: Division by zero",
                "exit_code": 1,
                "execution_time": 100,
                "memory_usage": 10
            }
        }
    })

    async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
        result = await client.execute_code("1/0", "python")
        assert result.exit_code == 1
        assert "Division by zero" in result.output


@pytest.mark.asyncio
async def test_multiple_concurrent_executions(mock_server):
    """Test running multiple code executions concurrently."""
    async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
        tasks = [
            client.execute_code(f"print({i})", "python")
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)

        # Verify all results
        for i, result in enumerate(results):
            assert result.exit_code == 0
            assert str(i) in result.output


@pytest.mark.asyncio
async def test_code_execution_with_different_languages(mock_server):
    """Test code execution with different programming languages."""
    async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
        # Python
        python_result = await client.execute_code("print('Python')", "python")
        assert python_result.exit_code == 0
        assert "Python" in python_result.output

        # JavaScript
        js_result = await client.execute_code("console.log('JavaScript')", "javascript")
        assert js_result.exit_code == 0
        assert "JavaScript" in js_result.output


@pytest.mark.asyncio
async def test_code_execution_with_environment_variables(mock_server):
    """Test code execution with custom environment variables."""
    async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
        result = await client.execute_code(
            "import os; print(os.environ.get('TEST_VAR', 'not set'))",
            "python",
            environment={"TEST_VAR": "test_value"}
        )
        assert result.exit_code == 0
        assert "test_value" in result.output


@pytest.mark.asyncio
async def test_code_execution_with_working_directory(mock_server):
    """Test code execution with a custom working directory."""
    async with DeepExecAsyncClient(endpoint=mock_server.url) as client:
        result = await client.execute_code(
            "import os; print(os.getcwd())",
            "python",
            working_directory="/custom/path"
        )
        assert result.exit_code == 0
        assert "/custom/path" in result.output
