import pytest
from unittest.mock import patch, MagicMock
from src.core.client import DeepExecClient


@pytest.fixture
def mock_client():
    """Create a mocked DeepExecClient for testing."""
    with patch('src.core.client.MCPConnection') as mock_conn:
        mock_conn.return_value.send_request.return_value = {
            "status": "success",
            "output": "mocked"
        }
        client = DeepExecClient(endpoint="mock://")
        client._conn = mock_conn.return_value  # Ensure the mock connection is accessible
        yield client


def test_execute_code(mock_client):
    """Test the execute_code method with mocked connection."""
    # Execute code with the mocked client
    result = mock_client.execute_code("print(1)")
    
    # Verify the result matches our mock
    assert result.output == "mocked"
    
    # Verify the connection's send_request method was called
    mock_client._conn.send_request.assert_called_once()


def test_generate_text(mock_client):
    """Test the generate_text method with mocked connection."""
    # Set up a different response for this test
    mock_client._conn.send_request.return_value = {
        "status": "success",
        "text": "generated text",
        "model": "test-model",
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 10,
            "total_tokens": 15
        }
    }
    
    # Generate text with the mocked client
    result = mock_client.generate_text("Test prompt")
    
    # Verify the result
    assert result.text == "generated text"
    assert result.model == "test-model"
    assert result.usage.total_tokens == 15
    
    # Verify the connection's send_request method was called
    mock_client._conn.send_request.assert_called_once()


def test_create_session(mock_client):
    """Test the create_session method with mocked connection."""
    # Set up response for session creation
    mock_client._conn.send_request.return_value = {
        "status": "success",
        "session_id": "test-session-123"
    }
    
    # Create a session
    session_id = mock_client.create_session("test-user")
    
    # Verify the session ID
    assert session_id == "test-session-123"
    assert mock_client.session_id == "test-session-123"
    
    # Verify the connection's send_request method was called
    mock_client._conn.send_request.assert_called_once()


def test_error_handling(mock_client):
    """Test error handling in the client."""
    # Set up an error response
    mock_client._conn.send_request.side_effect = Exception("Test error")
    
    # Attempt to execute code, which should raise an exception
    with pytest.raises(Exception) as exc_info:
        mock_client.execute_code("print(1)")
    
    # Verify the exception
    assert "Test error" in str(exc_info.value)


def test_with_different_parameters(mock_client):
    """Test execute_code with different parameters."""
    # Execute code with additional parameters
    mock_client.execute_code(
        code="print(1)",
        language="python",
        environment={"TEST_VAR": "test_value"},
        working_directory="/tmp"
    )
    
    # Get the call arguments
    args, kwargs = mock_client._conn.send_request.call_args
    
    # Verify the parameters were passed correctly
    request_data = kwargs.get("data", {})
    assert "code" in request_data
    assert request_data["code"] == "print(1)"
    assert request_data.get("language") == "python"
    assert request_data.get("environment", {}).get("TEST_VAR") == "test_value"
    assert request_data.get("working_directory") == "/tmp"
