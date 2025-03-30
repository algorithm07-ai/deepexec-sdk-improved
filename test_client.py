import pytest
import os
import json
from unittest.mock import patch, MagicMock
from src.DeepExecClient import DeepExecClient
from src.core.exceptions import (
    MCPError,
    MCPConnectionError,
    MCPProtocolError,
    MCPTimeoutError,
    MCPAuthError,
    MCPExecutionError,
    MCPConfigError
)


class TestDeepExecClient:
    """Unit tests for the DeepExecClient class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.client = DeepExecClient({
            "deepseekKey": "test_key",
            "e2bKey": "test_e2b_key"
        })

    def test_init_with_valid_config(self):
        """Test client initialization with valid configuration."""
        client = DeepExecClient({
            "deepseekKey": "test_key",
            "e2bKey": "test_e2b_key",
            "timeout": 60.0
        })
        assert client is not None
        assert client.config.getTimeout() == 60.0

    def test_init_with_invalid_config(self):
        """Test client initialization with invalid configuration."""
        with pytest.raises(MCPConfigError):
            DeepExecClient({
                "timeout": "invalid_timeout"  # Should be a number
            })

    def test_create_session(self):
        """Test session creation."""
        session_id = self.client.createSession("test_user")
        assert session_id is not None
        assert isinstance(session_id, str)
        assert self.client.sessionId == session_id

    @patch("src.DeepExecClient.DeepExecClient._send_request")
    def test_execute_code_success(self, mock_send_request):
        """Test successful code execution."""
        # Mock the response from the server
        mock_send_request.return_value = {
            "output": "Hello, World!\n",
            "exitCode": 0,
            "executionTime": 100,
            "memoryUsage": 10,
            "metadata": {"language": "python"}
        }

        # Create a session first
        self.client.createSession("test_user")

        # Execute code
        result = self.client.executeCode("print('Hello, World!')", "python")

        # Verify the result
        assert result.output == "Hello, World!\n"
        assert result.exitCode == 0
        assert result.executionTime == 100
        assert result.memoryUsage == 10
        assert result.metadata["language"] == "python"

    def test_execute_code_no_session(self):
        """Test code execution without an active session."""
        with pytest.raises(MCPProtocolError) as exc_info:
            self.client.executeCode("print('Hello, World!')", "python")
        assert "No active session" in str(exc_info.value)

    def test_execute_code_empty_code(self):
        """Test code execution with empty code."""
        # Create a session first
        self.client.createSession("test_user")

        with pytest.raises(MCPProtocolError) as exc_info:
            self.client.executeCode("", "python")
        assert "Code cannot be empty" in str(exc_info.value)

    def test_execute_code_invalid_language(self):
        """Test code execution with an invalid language."""
        # Create a session first
        self.client.createSession("test_user")

        # Set allowed languages in the config
        self.client.config.securityOptions = {
            "allowedLanguages": ["python", "javascript"]
        }

        with pytest.raises(MCPProtocolError) as exc_info:
            self.client.executeCode("print('Hello, World!')", "invalid_language")
        assert "not supported" in str(exc_info.value)

    def test_execute_code_blocked_keywords(self):
        """Test code execution with blocked keywords."""
        # Create a session first
        self.client.createSession("test_user")

        # Set blocked keywords in the config
        self.client.config.securityOptions = {
            "blockedKeywords": ["rm -rf", "os.system"]
        }

        with pytest.raises(MCPProtocolError) as exc_info:
            self.client.executeCode("import os; os.system('ls')", "python")
        assert "blocked keyword" in str(exc_info.value)

    @patch("src.DeepExecClient.DeepExecClient._send_request")
    def test_generate_text_success(self, mock_send_request):
        """Test successful text generation."""
        # Mock the response from the server
        mock_send_request.return_value = {
            "text": "Generated text response",
            "model": "deepseek-v3",
            "generationTime": 500,
            "usage": {
                "promptTokens": 10,
                "completionTokens": 50,
                "totalTokens": 60
            }
        }

        # Create a session first
        self.client.createSession("test_user")

        # Generate text
        result = self.client.generateText("Test prompt")

        # Verify the result
        assert result.text == "Generated text response"
        assert result.model == "deepseek-v3"
        assert result.generationTime == 500
        assert result.usage.promptTokens == 10
        assert result.usage.completionTokens == 50
        assert result.usage.totalTokens == 60

    def test_generate_text_no_session(self):
        """Test text generation without an active session."""
        with pytest.raises(MCPProtocolError) as exc_info:
            self.client.generateText("Test prompt")
        assert "No active session" in str(exc_info.value)

    def test_generate_text_empty_prompt(self):
        """Test text generation with an empty prompt."""
        # Create a session first
        self.client.createSession("test_user")

        with pytest.raises(MCPProtocolError) as exc_info:
            self.client.generateText("")
        assert "Prompt cannot be empty" in str(exc_info.value)

    @patch("src.DeepExecClient.DeepExecClient._send_request")
    def test_stream_generate_text(self, mock_send_request):
        """Test streaming text generation."""
        # This is a simplified test since we can't easily test generators in unit tests
        # Create a session first
        self.client.createSession("test_user")

        # Mock the generator function
        self.client.streamGenerateText = MagicMock(return_value=iter([
            {"text": "Hello", "done": False},
            {"text": " World", "done": True}
        ]))

        # Get the generator
        generator = self.client.streamGenerateText("Test prompt")

        # Consume the generator
        chunks = list(generator)

        # Verify the chunks
        assert len(chunks) == 2
        assert chunks[0]["text"] == "Hello"
        assert chunks[0]["done"] is False
        assert chunks[1]["text"] == " World"
        assert chunks[1]["done"] is True

    def test_close(self):
        """Test client closure."""
        # Create a session first
        self.client.createSession("test_user")
        assert self.client.sessionId is not None

        # Close the client
        self.client.close()
        assert self.client.sessionId is None
