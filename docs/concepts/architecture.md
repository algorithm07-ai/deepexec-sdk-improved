# DeepExec SDK Architecture

## Overview

The DeepExec SDK is designed as a modular, extensible system that implements the Anthropic MCP (Message Creation Protocol) for code execution and text generation. It integrates with DeepSeek's large language models and E2B's code execution environment to provide a comprehensive solution for AI-powered code execution.

## Core Components

### Client Layer

The `DeepExecClient` class serves as the main entry point for applications using the SDK. It provides a high-level API for:

- Creating and managing sessions
- Executing code in various programming languages
- Generating text using DeepSeek models
- Streaming text generation results

### Configuration System

The configuration system (`ClientConfig`) provides a flexible way to configure the SDK from multiple sources:

- Constructor arguments (highest priority)
- Environment variables (with `DEEPEXEC_` prefix)
- Configuration file (`.deepexecrc`)
- Default values (lowest priority)

This layered approach allows for different configuration strategies depending on the deployment environment.

### Error Handling

A comprehensive error hierarchy starting with the base `MCPError` class enables precise error handling:

- `MCPConnectionError`: Network-level connection issues
- `MCPProtocolError`: Protocol violations or malformed messages
- `MCPTimeoutError`: Operation timeouts
- `MCPAuthError`: Authentication/authorization failures
- `MCPExecutionError`: Runtime execution errors
- `MCPConfigError`: Configuration errors
- `MCPResourceLimitError`: Resource limit exceeded

### MCP Protocol Implementation

The SDK implements the Anthropic MCP protocol (version 2024.1), which defines:

- Message formats for requests and responses
- Session management
- Tool calling conventions
- Error reporting

### Integration Layer

#### DeepSeek Integration

Connects to DeepSeek's API for:

- Text generation
- Code completion
- Code analysis

#### E2B Integration

Connects to E2B's sandboxed execution environment for:

- Secure code execution
- Environment management
- File system operations

## Data Flow

1. Application creates a `DeepExecClient` instance with appropriate configuration
2. Client creates a session via `createSession()`
3. Application sends requests (code execution or text generation)
4. SDK validates the request and performs security checks
5. Request is transformed into the appropriate MCP protocol message
6. Message is sent to the appropriate backend service (DeepSeek or E2B)
7. Response is received, validated, and transformed into the SDK's result format
8. Result is returned to the application

## Security Model

The SDK implements multiple layers of security:

1. Input validation for all API calls
2. Code scanning for blocked keywords
3. Language restrictions (configurable allowed languages)
4. Code length limits
5. Timeout controls
6. Sandboxed execution environment (via E2B)

See [security_model.md](./security_model.md) for more details.

## Extensibility

The SDK is designed to be extensible in several ways:

1. Custom configuration sources
2. Additional language support
3. Custom security rules
4. Extended MCP protocol features

Developers can extend the SDK by subclassing the core components or by implementing custom handlers for specific use cases.
