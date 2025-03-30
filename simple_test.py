import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.conftest import MockServer
from src.core.async_client import DeepExecAsyncClient


async def test_execute_code_with_mock_server():
    """Test code execution with MockServer"""
    # Start mock server
    server = MockServer()
    await server.start()
    print(f"MockServer started at: {server.url}")
    
    try:
        # Create client connected to mock server
        client = DeepExecAsyncClient(
            endpoint=server.url,
            deepseek_key="test_deepseek_key",
            e2b_key="test_e2b_key"
        )
        
        async with client:
            # 1. Test session creation
            print("\nTesting session creation...")
            session_id = await client.create_session("test_user")
            print(f"Session created successfully, ID: {session_id}")
            
            # View requests received by server
            requests = server.get_requests()
            print(f"Number of requests received: {len(requests)}")
            print(f"Request path: {requests[0]['path']}")
            
            # Clear request history
            server.clear_requests()
            
            # 2. Test code execution
            print("\nTesting code execution...")
            python_code = """print('Hello, DeepExec!')
result = 42 * 2
print(f'The answer is {result}')"""
            
            result = await client.execute_code(
                code=python_code,
                language="python"
            )
            
            print(f"Execution result:\n{result.output}")
            print(f"Exit code: {result.exit_code}")
            print(f"Execution time: {result.execution_time}ms")
            
            # View requests received by server
            requests = server.get_requests()
            print(f"Number of requests received: {len(requests)}")
            print(f"Request path: {requests[0]['path']}")
            
            # Clear request history
            server.clear_requests()
            
            # 3. Test text generation
            print("\nTesting text generation...")
            prompt = "Explain what is artificial intelligence"
            
            # Set custom response
            server.set_response("/v1/generate", {
                "protocol_version": "2024.1",
                "type": "text_generation_result",
                "session_id": session_id,
                "request_id": "custom_req_id",
                "status": "success",
                "output": {
                    "text": "Artificial Intelligence (AI) is a branch of computer science focused on creating systems that can perform tasks that typically require human intelligence."
                },
                "metadata": {
                    "model": "deepseek-v3",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 100,
                        "total_tokens": 110
                    }
                }
            })
            
            result = await client.generate_text(
                prompt=prompt,
                model="deepseek-v3"
            )
            
            print(f"Generated text:\n{result.text}")
            print(f"Model: {result.model}")
            print(f"Token usage: {result.usage.total_tokens}")
            
            # View requests received by server
            requests = server.get_requests()
            print(f"Number of requests received: {len(requests)}")
            print(f"Request path: {requests[0]['path']}")
            
            # 4. Test error handling
            print("\nTesting error handling...")
            server.set_error_mode(True, 401, "Invalid API key")
            
            try:
                await client.execute_code(
                    code="print('This should fail')",
                    language="python"
                )
            except Exception as e:
                print(f"Successfully caught expected error: {type(e).__name__}: {str(e)}")
            
            # Restore normal mode
            server.set_error_mode(False)
            
            # 5. Test delayed response
            print("\nTesting delayed response...")
            server.set_delay(1.0)  # Set 1 second delay
            
            start_time = asyncio.get_event_loop().time()
            await client.execute_code(
                code="print('Testing delayed response')",
                language="python"
            )
            end_time = asyncio.get_event_loop().time()
            
            print(f"Delayed response took: {end_time - start_time:.2f} seconds")
            
            # Reset delay
            server.set_delay(0.0)
            
            print("\nAll tests completed!")
    
    finally:
        # Stop mock server
        await server.stop()
        print("MockServer stopped")


async def main():
    await test_execute_code_with_mock_server()


if __name__ == "__main__":
    asyncio.run(main())
