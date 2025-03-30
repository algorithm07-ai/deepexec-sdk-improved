# -*- coding: utf-8 -*-
# Client test implementation - No Chinese characters

"""
This module demonstrates how to implement client method tests for DeepExec SDK
using unittest.mock. This approach is compatible with the planned Web deployment
using Next.js and Express.

Example usage:
    # Run this file directly
    python client_test_impl.py

Note: This implementation avoids any non-ASCII characters to prevent encoding issues.
"""

# Standard library imports
import unittest
from unittest.mock import patch, MagicMock

# Define a mock DeepExecClient for testing
class DeepExecClient:
    """Mock implementation of DeepExecClient for demonstration"""
    
    def __init__(self, endpoint="https://api.deepexec.com", api_key=None):
        """Initialize the client with endpoint and API key"""
        self.endpoint = endpoint
        self.api_key = api_key or "test_api_key"
        self.session_id = None
        self._conn = None  # This would be MCPConnection in the real implementation
    
    def create_session(self, user_id):
        """Create a new session"""
        # In a real implementation, this would call the API
        self.session_id = f"session_{user_id}_123"
        return self.session_id
    
    def execute_code(self, code, language="python"):
        """Execute code and return the result"""
        # In a real implementation, this would call the API
        if not code:
            raise ValueError("Code cannot be empty")
            
        # This would call self._conn.send_request in the real implementation
        result = self._send_request("/execute", {
            "code": code,
            "language": language
        })
        
        # Create a result object
        class ExecutionResult:
            def __init__(self, output, exit_code, execution_time, memory_usage):
                self.output = output
                self.exit_code = exit_code
                self.execution_time = execution_time
                self.memory_usage = memory_usage
        
        return ExecutionResult(
            output=result.get("output", ""),
            exit_code=result.get("exitCode", 1),
            execution_time=result.get("executionTime", 0),
            memory_usage=result.get("memoryUsage", 0)
        )
    
    def generate_text(self, prompt, model="default"):
        """Generate text based on a prompt"""
        # In a real implementation, this would call the API
        if not prompt:
            raise ValueError("Prompt cannot be empty")
            
        # This would call self._conn.send_request in the real implementation
        result = self._send_request("/generate", {
            "prompt": prompt,
            "model": model
        })
        
        # Create a result object
        class GenerationResult:
            def __init__(self, text, model, usage):
                self.text = text
                self.model = model
                self.usage = usage
        
        class TokenUsage:
            def __init__(self, prompt_tokens, completion_tokens, total_tokens):
                self.prompt_tokens = prompt_tokens
                self.completion_tokens = completion_tokens
                self.total_tokens = total_tokens
        
        usage_data = result.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("promptTokens", 0),
            completion_tokens=usage_data.get("completionTokens", 0),
            total_tokens=usage_data.get("totalTokens", 0)
        )
        
        return GenerationResult(
            text=result.get("text", ""),
            model=result.get("model", model),
            usage=usage
        )
    
    def _send_request(self, path, data):
        """Send a request to the API (mock implementation)"""
        # This is a mock implementation
        if path == "/execute":
            return {
                "output": "Hello, World!\n",
                "exitCode": 0,
                "executionTime": 100,
                "memoryUsage": 10
            }
        elif path == "/generate":
            return {
                "text": "This is a generated response.",
                "model": data.get("model", "default"),
                "usage": {
                    "promptTokens": 10,
                    "completionTokens": 50,
                    "totalTokens": 60
                }
            }
        else:
            return {}


# Test class for DeepExecClient
class TestDeepExecClient(unittest.TestCase):
    """Unit tests for DeepExecClient"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = DeepExecClient()
    
    def test_create_session(self):
        """Test session creation"""
        session_id = self.client.create_session("test_user")
        self.assertEqual(session_id, "session_test_user_123")
        self.assertEqual(self.client.session_id, session_id)
    
    def test_execute_code(self):
        """Test code execution"""
        # Mock the _send_request method
        self.client._send_request = MagicMock(return_value={
            "output": "mocked output",
            "exitCode": 0,
            "executionTime": 200,
            "memoryUsage": 20
        })
        
        result = self.client.execute_code("print('test')")
        
        # Verify the result
        self.assertEqual(result.output, "mocked output")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.execution_time, 200)
        self.assertEqual(result.memory_usage, 20)
        
        # Verify the method was called with correct arguments
        self.client._send_request.assert_called_once_with(
            "/execute", {"code": "print('test')", "language": "python"}
        )
    
    def test_generate_text(self):
        """Test text generation"""
        # Mock the _send_request method
        self.client._send_request = MagicMock(return_value={
            "text": "mocked text",
            "model": "test-model",
            "usage": {
                "promptTokens": 5,
                "completionTokens": 15,
                "totalTokens": 20
            }
        })
        
        result = self.client.generate_text("Test prompt", "test-model")
        
        # Verify the result
        self.assertEqual(result.text, "mocked text")
        self.assertEqual(result.model, "test-model")
        self.assertEqual(result.usage.prompt_tokens, 5)
        self.assertEqual(result.usage.completion_tokens, 15)
        self.assertEqual(result.usage.total_tokens, 20)
        
        # Verify the method was called with correct arguments
        self.client._send_request.assert_called_once_with(
            "/generate", {"prompt": "Test prompt", "model": "test-model"}
        )
    
    def test_execute_code_empty(self):
        """Test code execution with empty code"""
        with self.assertRaises(ValueError):
            self.client.execute_code("")
    
    def test_generate_text_empty(self):
        """Test text generation with empty prompt"""
        with self.assertRaises(ValueError):
            self.client.generate_text("")


# Function-based test approach (similar to your example)
def test_with_mock():
    """Demonstrate function-based testing with mocks"""
    # Create a mock for the MCPConnection
    with patch('__main__.DeepExecClient._send_request') as mock_send_request:
        # Configure the mock to return a specific response
        mock_send_request.return_value = {
            "output": "mocked output",
            "exitCode": 0
        }
        
        # Create the client
        client = DeepExecClient(endpoint="mock://")
        
        # Execute code
        result = client.execute_code("print(1)")
        
        # Verify the result
        assert result.output == "mocked output"
        assert result.exit_code == 0
        
        # Verify the mock was called
        mock_send_request.assert_called_once()


# Main function to run the tests
def main():
    """Run the tests"""
    print("Running class-based tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\nRunning function-based test...")
    test_with_mock()
    print("Function-based test passed!")


if __name__ == "__main__":
    main()
