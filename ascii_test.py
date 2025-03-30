# -*- coding: utf-8 -*-
# ASCII-only test script

import os
import sys
import io

# Force standard streams to use UTF-8
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set environment variables
os.environ["PYTHONUTF8"] = "1"  # Python 3.7+
os.environ["PYTHONIOENCODING"] = "utf-8"

# Add project root to Python path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required modules
from unittest.mock import patch, MagicMock

# Print current encoding information
print(f"System default encoding: {sys.getdefaultencoding()}")
print(f"Standard input encoding: {sys.stdin.encoding}")
print(f"Standard output encoding: {sys.stdout.encoding}")
print(f"Standard error encoding: {sys.stderr.encoding}")
print(f"File system encoding: {sys.getfilesystemencoding()}")

# Test ASCII output
print("\nTesting ASCII output: This is a test text")

# Mock client test
print("\nStarting mock client test...")

# Mock DeepExecClient class
class MockDeepExecClient:
    def __init__(self, endpoint="mock://"):
        self.endpoint = endpoint
        self.session_id = None
        print(f"Initializing client: {endpoint}")
    
    def create_session(self, user_id):
        self.session_id = f"session_{user_id}_{id(self)}"
        print(f"Session created: {self.session_id}")
        return self.session_id
    
    def execute_code(self, code, language="python"):
        print(f"Executing code: {language}\n{code}")
        # Mock execution result
        class Result:
            def __init__(self):
                self.output = "Mock output result\nCode executed successfully"
                self.exit_code = 0
                self.execution_time = 100
                self.memory_usage = 10
            
            def __str__(self):
                return f"Result(output='{self.output}', exit_code={self.exit_code})"
        
        return Result()
    
    def generate_text(self, prompt, model="test-model"):
        print(f"Generating text: {prompt}")
        # Mock generation result
        class Result:
            def __init__(self):
                self.text = "This is a generated text response"
                self.model = model
                self.usage = type('Usage', (), {
                    'prompt_tokens': 10,
                    'completion_tokens': 50,
                    'total_tokens': 60,
                    '__str__': lambda self: f"Usage(total_tokens={self.total_tokens})"
                })()
            
            def __str__(self):
                return f"Result(text='{self.text}', model='{self.model}')"
        
        return Result()


def test_client_methods():
    """Test client methods"""
    # Create mock client
    client = MockDeepExecClient(endpoint="mock://test")
    
    # Test session creation
    session_id = client.create_session("test_user")
    print(f"Session ID: {session_id}")
    
    # Test code execution
    code = "print('Hello, World!')\nresult = 42 * 2\nprint(f'The answer is {result}')"
    result = client.execute_code(code, "python")
    print(f"Execution result: {result}")
    
    # Test text generation
    prompt = "Explain what is artificial intelligence"
    result = client.generate_text(prompt, "test-model")
    print(f"Generation result: {result}")
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    try:
        test_client_methods()
    except Exception as e:
        print(f"Error during test: {type(e).__name__}: {str(e)}")
