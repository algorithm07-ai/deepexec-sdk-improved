"""Basic usage example for the DeepExec SDK."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the DeepExecAsyncClient
from src.core.async_client import DeepExecAsyncClient

async def main():
    """Demonstrate basic usage of the DeepExec SDK."""
    # Create a client instance
    # You can provide API keys directly or via environment variables
    # DEEPEXEC_DEEPSEEK_KEY and DEEPEXEC_E2B_KEY
    async with DeepExecAsyncClient(
        endpoint="https://api.deepexec.com/v1",
        deepseek_key=os.getenv("DEEPSEEK_API_KEY"),
        e2b_key=os.getenv("E2B_API_KEY"),
        timeout=30.0,
        max_retries=3
    ) as client:
        # Create a session
        print("Creating session...")
        session_id = await client.create_session("example_user")
        print(f"Session created with ID: {session_id}")

        # Execute Python code
        print("\nExecuting Python code...")
        python_code = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
            
        result = fibonacci(10)
        print(f"Fibonacci(10) = {result}")
        """
        
        try:
            result = await client.execute_code(python_code, "python")
            print(f"Exit code: {result.exit_code}")
            print(f"Output:\n{result.output}")
            print(f"Execution time: {result.execution_time} ms")
            print(f"Memory usage: {result.memory_usage} MB")
        except Exception as e:
            print(f"Error executing Python code: {e}")

        # Execute JavaScript code
        print("\nExecuting JavaScript code...")
        js_code = """
        function calculateFactorial(n) {
            if (n === 0 || n === 1) {
                return 1;
            }
            return n * calculateFactorial(n - 1);
        }
        
        const result = calculateFactorial(5);
        console.log(`Factorial(5) = ${result}`);
        """
        
        try:
            result = await client.execute_code(js_code, "javascript")
            print(f"Exit code: {result.exit_code}")
            print(f"Output:\n{result.output}")
            print(f"Execution time: {result.execution_time} ms")
            print(f"Memory usage: {result.memory_usage} MB")
        except Exception as e:
            print(f"Error executing JavaScript code: {e}")

        # Generate text
        print("\nGenerating text...")
        try:
            result = await client.generate_text(
                prompt="Explain the concept of recursion in programming in 3 sentences.",
                model="deepseek-v3",
                max_tokens=100,
                temperature=0.7
            )
            print(f"Generated text:\n{result.text}")
            print(f"Model: {result.model}")
            print(f"Generation time: {result.generation_time} ms")
            print(f"Tokens: {result.usage.total_tokens} (prompt: {result.usage.prompt_tokens}, completion: {result.usage.completion_tokens})")
        except Exception as e:
            print(f"Error generating text: {e}")

        # Stream text generation
        print("\nStreaming text generation...")
        try:
            print("Generated text:")
            async for chunk in client.stream_generate_text(
                prompt="Write a short poem about coding.",
                model="deepseek-v3",
                max_tokens=150,
                temperature=0.8
            ):
                # Print without newline to simulate streaming
                print(chunk["text"], end="", flush=True)
                if chunk["done"]:
                    print("\n\nStream completed.")
        except Exception as e:
            print(f"\nError streaming text generation: {e}")

if __name__ == "__main__":
    asyncio.run(main())
