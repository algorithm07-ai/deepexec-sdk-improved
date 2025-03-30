# MCP Protocol Documentation

## Overview

The MCP (Model Communication Protocol) is a standardized protocol for communication between clients and AI model services. This protocol is used by the DeepExec SDK to interact with the DeepExec service, enabling code execution and text generation capabilities.

## Protocol Version

Current version: `2024.1`

## Base URL Structure

```
https://api.deepexec.com/v1
```

## Authentication

The MCP protocol supports two authentication methods:

1. **DeepSeek API Key**: Used for text generation services
   - Header: `X-DeepSeek-Key: <your_deepseek_api_key>`

2. **E2B API Key**: Used for code execution services
   - Header: `X-E2B-Key: <your_e2b_api_key>`

Both keys can be provided simultaneously if both services are needed.

## Sessions

The MCP protocol uses sessions to maintain state between requests. A session must be created before making other requests.

### Creating a Session

- **Endpoint**: `/session`
- **Method**: POST
- **Request**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "create_session",
    "input": {
      "user_id": "<user_identifier>"
    },
    "metadata": {}
  }
  ```
- **Response**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "session_created",
    "session_id": "<session_id>",
    "status": "success"
  }
  ```

## Supported Operations

### Code Execution

- **Endpoint**: `/execute`
- **Method**: POST
- **Request**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "code_execution",
    "session_id": "<session_id>",
    "input": {
      "code": "<code_to_execute>",
      "language": "<programming_language>",
      "environment": {
        "<env_var_name>": "<env_var_value>"
      },
      "working_directory": "<working_directory>"
    },
    "metadata": {}
  }
  ```
- **Response**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "code_execution_result",
    "session_id": "<session_id>",
    "status": "success",
    "output": {
      "execution_result": {
        "output": "<execution_output>",
        "exit_code": 0,
        "execution_time": 123,
        "memory_usage": 10
      }
    },
    "metadata": {}
  }
  ```

### Text Generation

- **Endpoint**: `/generate`
- **Method**: POST
- **Request**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "text_generation",
    "session_id": "<session_id>",
    "input": {
      "prompt": "<generation_prompt>",
      "max_tokens": 1000,
      "temperature": 0.7
    },
    "metadata": {
      "model": "deepseek-v3"
    }
  }
  ```
- **Response**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "text_generation_result",
    "session_id": "<session_id>",
    "status": "success",
    "output": {
      "text": "<generated_text>"
    },
    "metadata": {
      "model": "deepseek-v3",
      "generation_time": 456,
      "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 100,
        "total_tokens": 110
      }
    }
  }
  ```

### Streaming Text Generation

- **Endpoint**: `/generate/stream`
- **Method**: POST
- **Request**: Same as text generation
- **Response**: Server-sent events (SSE) stream with each event having the format:
  ```
  data: {"text": "<chunk_of_text>", "done": false}
  ```
  The final event will have `"done": true`.

### Canceling Execution

- **Endpoint**: `/cancel`
- **Method**: POST
- **Request**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "cancel_execution",
    "session_id": "<session_id>",
    "input": {},
    "metadata": {}
  }
  ```
- **Response**:
  ```json
  {
    "protocol_version": "2024.1",
    "type": "execution_canceled",
    "session_id": "<session_id>",
    "status": "success"
  }
  ```

## Error Handling

Errors are returned with a status code and a JSON response body:

```json
{
  "protocol_version": "2024.1",
  "status": "error",
  "error": {
    "code": "<error_code>",
    "message": "<error_message>",
    "details": {}
  }
}
```

### Common Error Codes

- `invalid_request`: The request format is invalid
- `authentication_error`: Authentication failed
- `rate_limit_exceeded`: API rate limit exceeded
- `execution_error`: Error during code execution
- `generation_error`: Error during text generation
- `timeout_error`: Operation timed out
- `server_error`: Internal server error

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Insufficient permissions
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Best Practices

1. Always create a session before making other requests
2. Include appropriate API keys in the headers
3. Handle rate limits with exponential backoff and jitter
4. Implement proper error handling for all possible error codes
5. Close unused sessions to free up resources
