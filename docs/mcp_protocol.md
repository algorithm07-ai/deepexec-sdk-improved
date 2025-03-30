# MCP Protocol Implementation

## Overview

The MCP (Model Communication Protocol) is a standardized protocol for communication between clients and AI model services. This document provides details on how the MCP protocol is implemented in the DeepExec SDK.

## Protocol Structure

The MCP protocol uses JSON messages for communication between clients and servers. Each message has a specific structure depending on whether it's a request or a response.

### Request Structure

```json
{
  "protocol_version": "2024.1",
  "type": "<request_type>",
  "session_id": "<session_id>",
  "input": { ... },
  "metadata": { ... }
}
```

### Response Structure

```json
{
  "protocol_version": "2024.1",
  "type": "<response_type>",
  "session_id": "<session_id>",
  "status": "success",
  "output": { ... },
  "metadata": { ... }
}
```

## Implementation Details

### Pydantic Models

The MCP protocol is implemented using Pydantic models for request and response validation. The models are defined in `src/core/protocols/mcp.py`.

#### Base Models

- `MCPBaseMessage`: Base model for all MCP messages
- `MCPRequestBase`: Base model for all MCP requests
- `MCPResponseBase`: Base model for all MCP responses
- `MCPErrorResponse`: Model for error responses

#### Request Models

- `CreateSessionRequest`: Request model for session creation
- `CodeExecutionRequest`: Request model for code execution
- `TextGenerationRequest`: Request model for text generation
- `TextGenerationStreamRequest`: Request model for streaming text generation
- `CancelExecutionRequest`: Request model for canceling execution

#### Response Models

- `SessionCreatedResponse`: Response model for session creation
- `CodeExecutionResultResponse`: Response model for code execution
- `TextGenerationResultResponse`: Response model for text generation
- `ExecutionCanceledResponse`: Response model for execution cancellation

### Utility Functions

- `build_request_message`: Builds a request message according to the MCP protocol
- `parse_response_message`: Parses a response message according to the MCP protocol

## Using the MCP Protocol

### Creating a Session

```python
from src.core.protocols.mcp import (
    MCPRequestType,
    CreateSessionInput,
    build_request_message
)

# Build a session creation request
request_data = build_request_message(
    type=MCPRequestType.CREATE_SESSION,
    session_id=None,  # No session ID yet
    input=CreateSessionInput(user_id="user123"),
    metadata={}
)

# Send the request to the server
# ...
```

### Executing Code

```python
from src.core.protocols.mcp import (
    MCPRequestType,
    CodeExecutionInput,
    build_request_message
)

# Build a code execution request
request_data = build_request_message(
    type=MCPRequestType.CODE_EXECUTION,
    session_id="session123",
    input=CodeExecutionInput(
        code="print('Hello, world!')",
        language="python"
    ),
    metadata={}
)

# Send the request to the server
# ...
```

### Generating Text

```python
from src.core.protocols.mcp import (
    MCPRequestType,
    TextGenerationInput,
    TextGenerationMetadata,
    build_request_message
)

# Build a text generation request
request_data = build_request_message(
    type=MCPRequestType.TEXT_GENERATION,
    session_id="session123",
    input=TextGenerationInput(
        prompt="Tell me about AI",
        max_tokens=1000,
        temperature=0.7
    ),
    metadata=TextGenerationMetadata(model="deepseek-v3")
)

# Send the request to the server
# ...
```

### Parsing Responses

```python
from src.core.protocols.mcp import parse_response_message

# Parse a response from the server
response_data = {...}  # Response from the server
parsed_response = parse_response_message(response_data)

# Use the parsed response
# ...
```

## Error Handling

The MCP protocol defines several error types that can be returned by the server. These errors are mapped to specific exception classes in the SDK:

- `MCPAuthError`: Authentication errors (401, 403)
- `MCPConnectionError`: Connection errors (5xx)
- `MCPTimeoutError`: Timeout errors
- `MCPProtocolError`: Protocol errors (4xx)
- `MCPExecutionError`: Execution errors

```python
from src.core.exceptions import (
    MCPAuthError,
    MCPConnectionError,
    MCPTimeoutError,
    MCPProtocolError,
    MCPExecutionError
)

try:
    # Send a request to the server
    # ...
except MCPAuthError as e:
    print(f"Authentication error: {e}")
except MCPConnectionError as e:
    print(f"Connection error: {e}")
except MCPTimeoutError as e:
    print(f"Timeout error: {e}")
except MCPProtocolError as e:
    print(f"Protocol error: {e}")
except MCPExecutionError as e:
    print(f"Execution error: {e}")
```

## Best Practices

1. Always create a session before making other requests
2. Include appropriate API keys in the headers
3. Handle rate limits with exponential backoff and jitter
4. Implement proper error handling for all possible error codes
5. Close unused sessions to free up resources

## References

- [PROTOCOL.md](../PROTOCOL.md): Detailed documentation of the MCP protocol
- [src/core/protocols/mcp.py](../src/core/protocols/mcp.py): Implementation of the MCP protocol
- [src/core/async_client.py](../src/core/async_client.py): Asynchronous client implementation
