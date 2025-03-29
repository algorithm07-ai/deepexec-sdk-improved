# MCP Protocol Details

## Introduction

The Message Creation Protocol (MCP) is a standardized protocol developed by Anthropic for communication between client applications and AI services. The DeepExec SDK implements version 2024.1 of this protocol, with extensions specific to code execution and DeepSeek model integration.

## Protocol Overview

The MCP protocol defines a structured message format for requests and responses, enabling consistent interaction with AI services. It supports various operation types, including text generation and code execution.

## Message Structure

### Request Format

```typescript
interface MCPRequest {
  protocol_version: string;        // e.g., "2024.1"
  type: "text_generation" | "code_execution" | string;
  session_id?: string;             // Session identifier
  input: {
    prompt?: string;              // For text generation
    code?: string;                // For code execution
    [key: string]: any;           // Other input parameters
  };
  metadata?: {
    language?: string;            // Programming language for code execution
    timeout?: number;             // Operation timeout in seconds
    [key: string]: any;           // Other metadata
  };
}
```

### Response Format

```typescript
interface MCPResponse {
  protocol_version: string;        // e.g., "2024.1"
  type: "text_generation_result" | "code_execution_result" | string;
  session_id?: string;             // Session identifier
  request_id: string;              // Unique request identifier
  status: "success" | "error";     // Operation status
  output: {
    text?: string;                // For text generation
    execution_result?: {          // For code execution
      output: string;             // Execution output
      exit_code: number;          // Process exit code
      execution_time: number;     // Execution time in milliseconds
      [key: string]: any;         // Other execution details
    };
    [key: string]: any;           // Other output parameters
  };
  error?: {
    code: string;                 // Error code
    message: string;              // Error message
    details?: any;                // Additional error details
  };
  metadata?: {
    model?: string;               // Model used for generation
    usage?: {                     // Token usage statistics
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
    [key: string]: any;           // Other metadata
  };
}
```

## Session Management

The MCP protocol uses sessions to maintain context across multiple requests. Sessions are identified by a unique `session_id` string, which should be included in all requests after session creation.

### Session Creation

Sessions are created by calling the `createSession` method on the client, which returns a session identifier. This identifier should be used in subsequent requests.

### Session Lifecycle

Sessions have the following lifecycle:

1. **Creation**: A new session is created with a unique identifier
2. **Active**: The session is used for one or more requests
3. **Termination**: The session is explicitly terminated or expires due to inactivity

## Operation Types

### Text Generation

Text generation operations use the `text_generation` type and require a `prompt` parameter in the input. The response includes generated text in the `output.text` field.

### Code Execution

Code execution operations use the `code_execution` type and require a `code` parameter in the input and a `language` parameter in the metadata. The response includes execution results in the `output.execution_result` field.

## Error Handling

Errors in the MCP protocol are represented by setting the `status` field to `"error"` and including an `error` object with the following fields:

- `code`: A string identifying the error type
- `message`: A human-readable error message
- `details`: Optional additional information about the error

Common error codes include:

- `invalid_request`: The request format is invalid
- `authentication_error`: Authentication failed
- `authorization_error`: The client is not authorized to perform the operation
- `rate_limit_exceeded`: The client has exceeded its rate limit
- `execution_error`: An error occurred during code execution
- `timeout`: The operation timed out
- `internal_error`: An internal server error occurred

## DeepExec Extensions

The DeepExec SDK extends the MCP protocol with the following features:

### Security Controls

Additional metadata fields for security controls:

- `security.max_code_length`: Maximum allowed code length
- `security.allowed_languages`: List of allowed programming languages
- `security.blocked_keywords`: List of blocked keywords

### DeepSeek Model Selection

The `metadata.model` field can be used to specify the DeepSeek model to use for text generation:

- `deepseek-v3`: Default model
- `deepseek-v3-mini`: Smaller, faster model
- `deepseek-coder`: Specialized for code generation

### Streaming Support

The protocol supports streaming responses for text generation by adding a `stream: true` field to the request metadata. Streaming responses are delivered as a series of partial response objects with the same structure as regular responses, but with incremental content.

## Protocol Versioning

The MCP protocol version is specified in the `protocol_version` field of both requests and responses. The DeepExec SDK currently supports version `"2024.1"` of the protocol.

Future versions of the protocol may introduce new features or change existing ones. The SDK will maintain backward compatibility with older protocol versions when possible.
