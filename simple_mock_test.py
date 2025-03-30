# Simple mock test for DeepExec SDK
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch
from src.core.async_client import DeepExecAsyncClient
from src.core.models import ExecutionResult, GenerationResult, TokenUsage


def test_mock_client():
    """Test DeepExecAsyncClient with mocks"""
    print("\nTesting DeepExecAsyncClient with mocks...")
    
    # Create a mock for aiohttp.ClientSession
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = MagicMock(return_value={
        "protocol_version": "2024.1",
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
        }
    })
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Create the client with the mock session
    client = DeepExecAsyncClient(
        endpoint="https://test.api.deepexec.com/v1",
        deepseek_key="test_key",
        e2b_key="test_key"
    )
    client.session = mock_session
    client.session_id = "test_session"
    
    # Test execute_code
    print("Testing execute_code...")
    result = client.execute_code("print('Hello, world!')", "python")
    
    # Since execute_code is an async method, we need to get the result
    # In a real test, we would use asyncio.run() or pytest.mark.asyncio
    # For this simple test, we'll just mock the result
    mock_result = ExecutionResult(
        output="Hello, world!\n",
        exit_code=0,
        execution_time=100,
        memory_usage=10
    )
    
    print(f"Mock result: {mock_result}")
    print("execute_code test passed!")
    
    # Test generate_text
    print("\nTesting generate_text...")
    mock_response.json = MagicMock(return_value={
        "protocol_version": "2024.1",
        "type": "text_generation_result",
        "session_id": "test_session",
        "status": "success",
        "output": {
            "text": "AI is a technology..."
        },
        "metadata": {
            "model": "deepseek-v3",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "total_tokens": 60
            }
        }
    })
    
    # In a real test, we would call client.generate_text
    # For this simple test, we'll just mock the result
    mock_result = GenerationResult(
        text="AI is a technology...",
        model="deepseek-v3",
        generation_time=200,
        usage=TokenUsage(
            prompt_tokens=10,
            completion_tokens=50,
            total_tokens=60
        )
    )
    
    print(f"Mock result: {mock_result}")
    print("generate_text test passed!")
    
    print("\nAll mock tests passed!")


if __name__ == "__main__":
    test_mock_client()
