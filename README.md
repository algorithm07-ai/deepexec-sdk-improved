# DeepExec SDK

A Python SDK for interacting with the DeepExec service, providing secure code execution and AI text generation capabilities using the MCP (Model Communication Protocol).

## Features

- **Code Execution**: Execute code in various programming languages in a secure, sandboxed environment
- **Text Generation**: Generate text using DeepSeek's powerful AI models
- **Streaming Support**: Stream text generation results for real-time applications
- **MCP Protocol**: Full implementation of the Model Communication Protocol for standardized AI service interactions
- **Comprehensive Error Handling**: Detailed error hierarchy for precise error handling
- **Flexible Configuration**: Configure the SDK from multiple sources with clear priority order
- **Security-First Design**: Multiple layers of security controls to prevent abuse

## Installation

```bash
pip install deepexec-sdk
```

## Quick Start

### Asynchronous Client

```python
import asyncio
from deepexec_sdk import DeepExecAsyncClient

async def main():
    # Create client instance
    async with DeepExecAsyncClient(
        deepseek_key="sk-...",  # Your DeepSeek API key
        e2b_key="e2b_..."      # Your E2B API key
    ) as client:
        # Execute code
        try:
            result = await client.execute_code_and_wait(
                "print('Hello, World!')", 
                "python"
            )
            print(f"Output: {result.output}")
            print(f"Exit code: {result.exit_code}")
            print(f"Execution time: {result.execution_time} ms")
        except Exception as error:
            print(f"Execution failed: {error}")

        # Generate text
        try:
            result = await client.generate_text_and_wait(
                "Explain quantum computing in simple terms",
                model="deepseek-v3",
                max_tokens=500
            )
            print(f"Generated text: {result.text}")
            print(f"Model: {result.model}")
            print(f"Generation time: {result.generation_time} ms")
        except Exception as error:
            print(f"Text generation failed: {error}")

# Run the async function
asyncio.run(main())
```

### Synchronous Client

```python
from deepexec_sdk import DeepExecClient

# Create client instance
with DeepExecClient(
    deepseek_key="sk-...",  # Your DeepSeek API key
    e2b_key="e2b_..."      # Your E2B API key
) as client:
    # Execute code
    try:
        result = client.execute_code_and_wait(
            "print('Hello, World!')", 
            "python"
        )
        print(f"Output: {result.output}")
        print(f"Exit code: {result.exit_code}")
        print(f"Execution time: {result.execution_time} ms")
    except Exception as error:
        print(f"Execution failed: {error}")

    # Generate text
    try:
        result = client.generate_text_and_wait(
            "Explain quantum computing in simple terms",
            model="deepseek-v3",
            max_tokens=500
        )
        print(f"Generated text: {result.text}")
        print(f"Model: {result.model}")
        print(f"Generation time: {result.generation_time} ms")
    except Exception as error:
        print(f"Text generation failed: {error}")
```

## MCP Protocol Operations

The SDK provides specific methods for working with the MCP protocol:

### Job Management

```python
# Asynchronous example
async def job_management_example():
    async with DeepExecAsyncClient() as client:
        # Submit a job
        job_response = await client.submit_job(
            name="my_analysis_job",
            job_type="code_execution",
            data={
                "code": "print('Analyzing data...')",
                "language": "python"
            }
        )
        
        job_id = job_response.job_id
        print(f"Job submitted with ID: {job_id}")
        
        # Check job status
        status = await client.get_job_status(job_id)
        print(f"Job status: {status.status}")
        
        # Wait for job completion
        while status.status not in ["COMPLETED", "FAILED", "CANCELED"]:
            await asyncio.sleep(1)
            status = await client.get_job_status(job_id)
            print(f"Job status: {status.status}, Progress: {status.progress}%")
        
        # Get results if job completed successfully
        if status.status == "COMPLETED":
            print(f"Job result: {status.result}")
        else:
            print(f"Job failed: {status.error}")
            
        # Cancel a job (if needed)
        # cancel_response = await client.cancel_job(job_id, reason="No longer needed")
        # print(f"Job canceled at: {cancel_response.canceled_at}")
```

### Code Execution

```python
# Synchronous example
with DeepExecClient() as client:
    # Submit a code execution job
    job = client.execute_code_job(
        code="import time\nfor i in range(5):\n    print(f'Step {i}')\n    time.sleep(1)",
        language="python",
        environment={"DEBUG": "true"},
        timeout=30
    )
    
    print(f"Code execution job submitted with ID: {job.job_id}")
    
    # Get the result when ready
    result = client.get_code_execution_result(job.job_id)
    
    print(f"Output: {result.output}")
    print(f"Exit code: {result.exit_code}")
    print(f"Execution time: {result.execution_time} ms")
    print(f"Memory usage: {result.memory_usage} bytes")
    
    # Or use the convenience method that handles polling
    result = client.execute_code_and_wait(
        code="print('Hello, World!')",
        language="python"
    )
```

### Text Generation

```python
# Asynchronous example
async def text_generation_example():
    async with DeepExecAsyncClient() as client:
        # Submit a text generation job
        job = await client.generate_text_job(
            prompt="Write a short poem about artificial intelligence",
            model="deepseek-v3",
            max_tokens=200,
            temperature=0.8
        )
        
        print(f"Text generation job submitted with ID: {job.job_id}")
        
        # Get the result when ready
        result = await client.get_text_generation_result(job.job_id)
        
        print(f"Generated text: {result.text}")
        print(f"Model: {result.model}")
        print(f"Generation time: {result.generation_time} ms")
        print(f"Token usage: {result.usage}")
        
        # Or use the convenience method that handles polling
        result = await client.generate_text_and_wait(
            prompt="Explain how neural networks work",
            model="deepseek-v3"
        )
```

## Documentation

Comprehensive documentation is available in the `docs/` directory. To build the documentation:

```bash
cd docs
pip install -r requirements-docs.txt
sphinx-build -b html . _build/html
```

Then open `_build/html/index.html` in your browser.

### Key Documentation Sections

- **Concepts**: Architectural overview, MCP protocol details, security model, and error handling philosophy
- **API Reference**: Detailed documentation for all classes, methods, and interfaces
- **Examples**: Code samples for common use cases

## MCP Protocol

The SDK implements the Model Communication Protocol (MCP), a standardized protocol for communication between clients and AI model services. The protocol is documented in detail in [PROTOCOL.md](PROTOCOL.md).

### Key Components

- **Session Management**: Create and manage sessions for stateful interactions
- **Code Execution**: Execute code in various programming languages
- **Text Generation**: Generate text using AI models
- **Streaming**: Stream text generation results for real-time applications
- **Job Management**: Submit, monitor, and cancel jobs

### Protocol Structure

The MCP protocol uses JSON messages for communication:

```json
// Request
{
  "protocol_version": "2024.1",
  "type": "<request_type>",
  "session_id": "<session_id>",
  "input": { ... },
  "metadata": { ... }
}

// Response
{
  "protocol_version": "2024.1",
  "type": "<response_type>",
  "session_id": "<session_id>",
  "status": "success",
  "output": { ... },
  "metadata": { ... }
}
```

See [docs/mcp_protocol.md](docs/mcp_protocol.md) for more details on the implementation.

## Configuration

The SDK can be configured in multiple ways:

### Constructor Arguments

```python
client = DeepExecAsyncClient(
    endpoint="https://api.deepexec.com/v1",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
    deepseek_key="sk-...",
    e2b_key="e2b_...",
    verify_ssl=True
)
```

### Environment Variables

```bash
export DEEPEXEC_ENDPOINT="https://api.deepexec.com/v1"
export DEEPEXEC_TIMEOUT=30.0
export DEEPEXEC_MAX_RETRIES=3
export DEEPEXEC_RETRY_DELAY=1.0
export DEEPEXEC_DEEPSEEK_KEY="sk-..."
export DEEPEXEC_E2B_KEY="e2b_..."
export DEEPEXEC_VERIFY_SSL=true
```

## Error Handling

The SDK provides a comprehensive error hierarchy for precise error handling:

```python
from deepexec_sdk.exceptions import (
    MCPExecutionError, MCPTimeoutError, 
    MCPConnectionError, MCPAuthError, MCPProtocolError
)

try:
    result = await client.execute_code_and_wait(
        code="print('Hello, World!')", 
        language="python"
    )
    print(f"Output: {result.output}")
    print(f"Exit code: {result.exit_code}")
    print(f"Execution time: {result.execution_time} ms")
except MCPExecutionError as error:
    print(f"Execution failed with exit code {error.exit_code}")
    print(f"Output: {error.output}")
except MCPTimeoutError as error:
    print(f"Operation timed out after {error.timeout} seconds")
except MCPConnectionError as error:
    print(f"Connection error: {error}")
except MCPAuthError as error:
    print(f"Authentication error: {error}")
except MCPProtocolError as error:
    print(f"Protocol error: {error}")
except Exception as error:
    print(f"Unexpected error: {error}")
```

## Security

The SDK implements multiple layers of security:

1. **Input Validation**: All API calls are validated using Pydantic models
2. **Protocol Validation**: All messages are validated against the MCP protocol
3. **Language Restrictions**: Only allowed languages can be executed
4. **Code Length Limits**: Maximum code length is enforced
5. **Timeout Controls**: All operations have configurable timeouts
6. **Sandboxed Execution**: Code is executed in a secure, sandboxed environment

## Testing

The SDK includes comprehensive tests for all components:

```bash
pip install -r requirements-dev.txt
pytest
```

## License

MIT
