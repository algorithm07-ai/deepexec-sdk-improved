# -*- coding: utf-8 -*-
# Unicode test script with explicit encoding

import os
import sys
import io
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required modules
from unittest.mock import patch, MagicMock

# Print current encoding information
print(f"System default encoding: {sys.getdefaultencoding()}")

# Use unicode_escape for Chinese characters
chinese_test = "\u4e2d\u6587\u6d4b\u8bd5"  # "中文测试" in unicode escape
print(f"Unicode test: {chinese_test}")

# Create a test data file with explicit UTF-8 encoding
test_data = {
    "test_key": "test_value",
    "unicode_key": "\u4e2d\u6587\u6d4b\u8bd5"
}

# Write test data with explicit UTF-8 encoding
with open("test_data.json", "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=True)

# Read test data with explicit UTF-8 encoding
with open("test_data.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)

print(f"Loaded data: {loaded_data}")

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
    finally:
        # Clean up test file
        if os.path.exists("test_data.json"):
            os.remove("test_data.json")
