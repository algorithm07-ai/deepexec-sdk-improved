# MCP Protocol Operations

This document provides detailed information about the Model Communication Protocol (MCP) operations available in the DeepExec SDK. These operations allow for direct control over job submission, status checking, cancellation, and completion monitoring.

## Table of Contents

1. [Introduction](#introduction)
2. [High-Level MCP Methods](#high-level-mcp-methods)
   - [submit_mcp_job](#submit_mcp_job)
   - [get_mcp_job_status](#get_mcp_job_status)
   - [cancel_mcp_job](#cancel_mcp_job)
   - [wait_for_mcp_job_completion](#wait_for_mcp_job_completion)
3. [Usage Examples](#usage-examples)
4. [Error Handling](#error-handling)
5. [Best Practices](#best-practices)

## Introduction

The Model Communication Protocol (MCP) is a standardized protocol for interacting with AI model execution services. The DeepExec SDK provides high-level methods for working with the MCP, making it easier to submit jobs, check their status, and manage their lifecycle.

While the SDK provides convenience methods like `execute_code_and_wait` and `generate_text_and_wait`, the high-level MCP methods offer more direct control over the job execution process, allowing for more advanced use cases and custom workflows.

## High-Level MCP Methods

### submit_mcp_job

**Description**: Submits a job to the MCP service with the specified parameters.

**Parameters**:

- `name` (str): A descriptive name for the job.
- `job_type` (str): The type of job to execute (e.g., "code_execution", "text_generation").
- `data` (Dict[str, Any]): Job-specific data required for execution.
- `timeout` (Optional[int]): Maximum execution time in seconds (default: 60).
- `priority` (Optional[int]): Job priority level (default: 0).
- `tags` (Optional[List[str]]): List of tags to associate with the job.

**Returns**: An `MCPJobResponse` object containing the job ID and initial status.

**Example**:

```python
# Synchronous client
with DeepExecClient() as client:
    response = client.submit_mcp_job(
        name="python_execution",
        job_type="code_execution",
        data={
            "code": "print('Hello, World!')",
            "language": "python"
        },
        timeout=30,
        tags=["example", "python"]
    )
    print(f"Job submitted with ID: {response.job_id}")

# Asynchronous client
async with DeepExecAsyncClient() as client:
    response = await client.submit_mcp_job(
        name="text_generation",
        job_type="text_generation",
        data={
            "prompt": "Explain quantum computing",
            "model": "deepseek-v3",
            "max_tokens": 300
        }
    )
    print(f"Job submitted with ID: {response.job_id}")
```

### get_mcp_job_status

**Description**: Retrieves the current status of a job by its ID.

**Parameters**:

- `job_id` (str): The ID of the job to check.

**Returns**: An `MCPJobStatusResponse` object containing the job's current status, progress, result (if completed), and error (if failed).

**Example**:

```python
# Synchronous client
with DeepExecClient() as client:
    status = client.get_mcp_job_status("job_12345")
    print(f"Status: {status.status}, Progress: {status.progress}%")
    if status.status == "COMPLETED":
        print(f"Result: {status.result}")

# Asynchronous client
async with DeepExecAsyncClient() as client:
    status = await client.get_mcp_job_status("job_12345")
    print(f"Status: {status.status}, Progress: {status.progress}%")
```

### cancel_mcp_job

**Description**: Cancels a running job by its ID.

**Parameters**:

- `job_id` (str): The ID of the job to cancel.
- `reason` (Optional[str]): A reason for cancellation (for logging purposes).

**Returns**: An `MCPCancelJobResponse` object containing the cancellation timestamp.

**Example**:

```python
# Synchronous client
with DeepExecClient() as client:
    try:
        cancel_response = client.cancel_mcp_job(
            job_id="job_12345",
            reason="User requested cancellation"
        )
        print(f"Job canceled at: {cancel_response.canceled_at}")
    except Exception as e:
        print(f"Cancellation failed: {e}")

# Asynchronous client
async with DeepExecAsyncClient() as client:
    try:
        cancel_response = await client.cancel_mcp_job("job_12345")
        print(f"Job canceled at: {cancel_response.canceled_at}")
    except Exception as e:
        print(f"Cancellation failed: {e}")
```

### wait_for_mcp_job_completion

**Description**: Waits for a job to complete by polling its status at regular intervals.

**Parameters**:

- `job_id` (str): The ID of the job to wait for.
- `poll_interval` (float): Time in seconds between status checks (default: 1.0).
- `max_wait_time` (Optional[float]): Maximum time to wait in seconds (default: None, wait indefinitely).

**Returns**: An `MCPJobStatusResponse` object containing the final job status and result.

**Example**:

```python
# Synchronous client
with DeepExecClient() as client:
    try:
        final_status = client.wait_for_mcp_job_completion(
            job_id="job_12345",
            poll_interval=0.5,  # Check every 0.5 seconds
            max_wait_time=30.0  # Wait up to 30 seconds
        )
        print(f"Final status: {final_status.status}")
        if final_status.result:
            print(f"Result: {final_status.result}")
    except TimeoutError:
        print("Job did not complete within the specified time")

# Asynchronous client
async with DeepExecAsyncClient() as client:
    try:
        final_status = await client.wait_for_mcp_job_completion(
            job_id="job_12345",
            poll_interval=0.5,
            max_wait_time=30.0
        )
        print(f"Final status: {final_status.status}")
    except TimeoutError:
        print("Job did not complete within the specified time")
```

## Usage Examples

### Basic Job Submission and Monitoring

```python
import asyncio
from deepexec_sdk import DeepExecAsyncClient

async def run_job():
    async with DeepExecAsyncClient() as client:
        # Submit a job
        job_response = await client.submit_mcp_job(
            name="example_job",
            job_type="code_execution",
            data={
                "code": "import time\nfor i in range(5):\n    print(f'Step {i}')\n    time.sleep(1)\nprint('Done!')",
                "language": "python"
            }
        )
        
        job_id = job_response.job_id
        print(f"Job submitted with ID: {job_id}")
        
        # Wait for completion with progress updates
        print("Waiting for job completion...")
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await client.get_mcp_job_status(job_id)
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"Status: {status.status}, Progress: {status.progress or 0}%, Elapsed: {elapsed:.1f}s")
            
            if status.status in ["COMPLETED", "FAILED", "CANCELED"]:
                break
                
            await asyncio.sleep(1.0)
        
        if status.status == "COMPLETED":
            print(f"Job completed successfully!")
            print(f"Result: {status.result}")
        elif status.status == "FAILED":
            print(f"Job failed: {status.error}")
        else:
            print("Job was canceled")

asyncio.run(run_job())
```

### Job Cancellation Example

```python
import asyncio
from deepexec_sdk import DeepExecAsyncClient

async def cancel_after_delay():
    async with DeepExecAsyncClient() as client:
        # Submit a long-running job
        job_response = await client.submit_mcp_job(
            name="long_running_job",
            job_type="code_execution",
            data={
                "code": "import time\nfor i in range(60):\n    print(f'Step {i}')\n    time.sleep(1)\nprint('Done!')",
                "language": "python"
            },
            timeout=120  # 2 minutes timeout
        )
        
        job_id = job_response.job_id
        print(f"Long-running job submitted with ID: {job_id}")
        
        # Wait for 5 seconds
        print("Waiting 5 seconds before cancellation...")
        await asyncio.sleep(5)
        
        # Cancel the job
        print("Canceling job...")
        cancel_response = await client.cancel_mcp_job(
            job_id=job_id,
            reason="Demonstration of cancellation"
        )
        
        print(f"Job canceled at: {cancel_response.canceled_at}")
        
        # Verify final status
        final_status = await client.get_mcp_job_status(job_id)
        print(f"Final status: {final_status.status}")

asyncio.run(cancel_after_delay())
```

### Using wait_for_mcp_job_completion

```python
import asyncio
from deepexec_sdk import DeepExecAsyncClient

async def wait_with_timeout():
    async with DeepExecAsyncClient() as client:
        # Submit a job
        job_response = await client.submit_mcp_job(
            name="quick_job",
            job_type="code_execution",
            data={
                "code": "print('This is a quick job')",
                "language": "python"
            }
        )
        
        job_id = job_response.job_id
        print(f"Job submitted with ID: {job_id}")
        
        try:
            # Wait for completion with a timeout
            print("Waiting for job completion (max 10 seconds)...")
            final_status = await client.wait_for_mcp_job_completion(
                job_id=job_id,
                poll_interval=0.5,  # Check every 0.5 seconds
                max_wait_time=10.0  # Wait up to 10 seconds
            )
            
            print(f"Job completed with status: {final_status.status}")
            if final_status.result:
                print(f"Result: {final_status.result}")
        except TimeoutError:
            print("Job did not complete within the specified time")
            
            # We can still check the status
            current_status = await client.get_mcp_job_status(job_id)
            print(f"Current status: {current_status.status}, Progress: {current_status.progress or 0}%")

asyncio.run(wait_with_timeout())
```

## Error Handling

The MCP operations can raise various exceptions that should be handled appropriately:

1. **MCPAuthenticationError**: Raised when there are authentication issues with the MCP service.
2. **MCPConnectionError**: Raised when there are network connectivity issues.
3. **MCPTimeoutError**: Raised when an operation times out.
4. **MCPProtocolError**: Raised when there are issues with the MCP protocol format or version.
5. **MCPExecutionError**: Raised when there are issues with job execution.
6. **TimeoutError**: Raised by `wait_for_mcp_job_completion` when the maximum wait time is exceeded.

Example error handling:

```python
from deepexec_sdk import (
    DeepExecClient, 
    MCPAuthenticationError, 
    MCPConnectionError,
    MCPTimeoutError,
    MCPProtocolError,
    MCPExecutionError
)

try:
    with DeepExecClient() as client:
        response = client.submit_mcp_job(
            name="error_handling_example",
            job_type="code_execution",
            data={
                "code": "print('Testing error handling')",
                "language": "python"
            }
        )
        
        # Try to get status
        status = client.get_mcp_job_status(response.job_id)
        
        # Try to cancel
        client.cancel_mcp_job(response.job_id)
        
        # Try to wait for completion
        client.wait_for_mcp_job_completion(response.job_id, max_wait_time=10.0)
        
except MCPAuthenticationError as e:
    print(f"Authentication error: {e}")
    # Handle authentication issues (e.g., refresh API keys)
    
except MCPConnectionError as e:
    print(f"Connection error: {e}")
    # Handle connectivity issues (e.g., retry with backoff)
    
except MCPTimeoutError as e:
    print(f"Timeout error: {e}")
    # Handle timeout issues (e.g., increase timeout or check status later)
    
except MCPProtocolError as e:
    print(f"Protocol error: {e}")
    # Handle protocol issues (e.g., check SDK version compatibility)
    
except MCPExecutionError as e:
    print(f"Execution error: {e}")
    # Handle execution issues (e.g., check job parameters)
    
except TimeoutError as e:
    print(f"Wait timeout: {e}")
    # Handle wait timeout (e.g., continue polling manually)
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other unexpected errors
```

## Best Practices

1. **Job Naming**: Use descriptive job names to make it easier to identify jobs in logs and monitoring tools.

2. **Timeout Management**: Set appropriate timeouts based on the expected execution time of your jobs. For long-running jobs, consider using a longer timeout or implementing a custom polling mechanism.

3. **Error Handling**: Always implement proper error handling to gracefully handle failures and provide meaningful feedback to users.

4. **Resource Cleanup**: Always cancel jobs that are no longer needed to free up resources on the MCP service.

5. **Polling Interval**: When using `wait_for_mcp_job_completion`, choose an appropriate polling interval. Too frequent polling can increase load on the MCP service, while too infrequent polling can delay detecting job completion.

6. **Asynchronous Operations**: For applications that need to handle multiple jobs concurrently, use the asynchronous client (`DeepExecAsyncClient`) to avoid blocking the main thread.

7. **Job Tagging**: Use tags to categorize jobs for easier filtering and management, especially in production environments.

8. **Progress Monitoring**: Regularly check job progress for long-running jobs to provide feedback to users and detect stalled jobs.

9. **Logging**: Implement logging for all MCP operations to help with debugging and monitoring.

10. **Retry Logic**: Implement retry logic with exponential backoff for transient errors, especially for network-related issues.
