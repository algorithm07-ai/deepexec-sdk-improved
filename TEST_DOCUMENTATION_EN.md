# DeepExec SDK - MCP Protocol Operations Testing

This document provides comprehensive testing instructions for the MCP (Model Communication Protocol) operations implemented in the DeepExec SDK. It covers both manual testing procedures and automated test scripts.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Manual Testing](#manual-testing)
3. [Automated Testing](#automated-testing)
4. [Test Cases](#test-cases)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

Before testing, ensure you have the following:

- DeepExec SDK installed (`pip install -e .` from the project root)
- Python 3.8 or higher
- Valid API keys:
  - DeepSeek API key
  - E2B API key
- Access to the DeepExec service endpoint

Set up environment variables for easier testing:

```bash
# Create a .env file in the project root
echo "DEEPEXEC_ENDPOINT=https://api.deepexec.com/v1" > .env
echo "DEEPEXEC_DEEPSEEK_KEY=sk-..." >> .env
echo "DEEPEXEC_E2B_KEY=e2b_..." >> .env
echo "DEEPEXEC_TIMEOUT=60.0" >> .env
echo "DEEPEXEC_MAX_RETRIES=3" >> .env
```

## Manual Testing

### 1. Basic Client Operations

Test the basic client initialization and connection:

```python
from deepexec_sdk import DeepExecClient, DeepExecAsyncClient

# Synchronous client
with DeepExecClient() as client:
    print("Synchronous client initialized successfully")

# Asynchronous client
import asyncio

async def test_async_client():
    async with DeepExecAsyncClient() as client:
        print("Asynchronous client initialized successfully")

asyncio.run(test_async_client())
```

### 2. Code Execution

Test code execution using both synchronous and asynchronous clients:

```python
# Synchronous code execution
with DeepExecClient() as client:
    result = client.execute_code_and_wait(
        code="print('Hello, World!')",
        language="python"
    )
    print(f"Output: {result.output}")
    print(f"Exit code: {result.exit_code}")

# Asynchronous code execution
async def test_async_code_execution():
    async with DeepExecAsyncClient() as client:
        result = await client.execute_code_and_wait(
            code="print('Hello, Async World!')",
            language="python"
        )
        print(f"Output: {result.output}")
        print(f"Exit code: {result.exit_code}")

asyncio.run(test_async_code_execution())
```

### 3. Text Generation

Test text generation using both clients:

```python
# Synchronous text generation
with DeepExecClient() as client:
    result = client.generate_text_and_wait(
        prompt="Explain quantum computing in simple terms",
        model="deepseek-v3",
        max_tokens=300
    )
    print(f"Generated text: {result.text}")

# Asynchronous text generation
async def test_async_text_generation():
    async with DeepExecAsyncClient() as client:
        result = await client.generate_text_and_wait(
            prompt="Write a short poem about AI",
            model="deepseek-v3",
            max_tokens=200,
            temperature=0.8
        )
        print(f"Generated text: {result.text}")

asyncio.run(test_async_text_generation())
```

### 4. Job Management

Test job submission, status checking, and cancellation:

```python
import asyncio
import time

async def test_job_management():
    async with DeepExecAsyncClient() as client:
        # Submit a job
        job_response = await client.submit_job(
            name="test_job",
            job_type="code_execution",
            data={
                "code": "import time\nfor i in range(5):\n    print(f'Step {i}')\n    time.sleep(1)\nprint('Done!')",
                "language": "python"
            },
            timeout=30
        )
        
        job_id = job_response.job_id
        print(f"Job submitted with ID: {job_id}")
        
        # Check status a few times
        for _ in range(3):
            status = await client.get_job_status(job_id)
            print(f"Status: {status.status}, Progress: {status.progress}%")
            await asyncio.sleep(2)
        
        # Cancel the job
        cancel_response = await client.cancel_job(job_id, reason="Testing cancellation")
        print(f"Job canceled at: {cancel_response.canceled_at}")
        
        # Verify cancellation
        final_status = await client.get_job_status(job_id)
        print(f"Final status: {final_status.status}")

asyncio.run(test_job_management())
```

## Automated Testing

The SDK includes automated tests for all MCP protocol operations. Run these tests to verify the implementation:

### 1. Unit Tests

Run the unit tests using pytest:

```bash
python -m pytest tests/test_mcp_operations.py -v
```

These tests use mocked responses to verify the client implementation without making actual API calls.

### 2. Integration Tests

Run the integration test script to test against the actual DeepExec service:

```bash
python examples/test_real_server.py
```

You can also specify API keys and endpoint directly:

```bash
python examples/test_real_server.py --endpoint "https://api.deepexec.com/v1" --deepseek-key "sk-..." --e2b-key "e2b_..."
```

### 3. Example Scripts

Run the example scripts to see the SDK in action:

```bash
python examples/mcp_operations_example.py
```

## Test Cases

The following test cases should be verified:

### Job Management

1. **Submit Job**
   - Submit jobs of different types (code_execution, text_generation)
   - Verify job ID is returned
   - Test with various parameters (timeout, priority)

2. **Get Job Status**
   - Check status of existing jobs
   - Verify status transitions (PENDING → RUNNING → COMPLETED)
   - Test with non-existent job IDs (should return appropriate error)

3. **Cancel Job**
   - Cancel running jobs
   - Verify status changes to CANCELED
   - Test canceling already completed jobs (should return appropriate error)

### Code Execution

1. **Execute Code**
   - Test with different programming languages (python, javascript, bash)
   - Verify output, exit code, execution time, and memory usage
   - Test with syntax errors (should return appropriate error)
   - Test with long-running code (should respect timeout)

2. **Code Execution Convenience Methods**
   - Test execute_code_job and get_code_execution_result separately
   - Test execute_code_and_wait for automatic polling

### Text Generation

1. **Generate Text**
   - Test with different prompts and models
   - Verify text output and token usage
   - Test with various parameters (temperature, max_tokens)

2. **Text Generation Convenience Methods**
   - Test generate_text_job and get_text_generation_result separately
   - Test generate_text_and_wait for automatic polling

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API keys are correct
   - Check environment variables are properly set

2. **Connection Errors**
   - Verify endpoint URL is correct
   - Check network connectivity
   - Increase timeout if necessary

3. **Protocol Errors**
   - Check request format (especially for custom job types)
   - Verify protocol version compatibility

4. **Execution Errors**
   - Check for syntax errors in code
   - Verify language is supported
   - Check for resource limitations (memory, execution time)

### Debugging

Enable debug logging for more detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then initialize the client
client = DeepExecClient()
```

Check the logs for request/response details and error messages.
