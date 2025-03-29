# Error Handling Philosophy

## Overview

Effective error handling is a critical aspect of the DeepExec SDK design. This document outlines the error handling philosophy, the error hierarchy, and best practices for handling errors in applications using the SDK.

## Core Principles

The error handling system in the DeepExec SDK is built on these core principles:

1. **Specificity**: Errors should be as specific as possible to enable precise handling
2. **Hierarchy**: Errors form a logical hierarchy for flexible catch strategies
3. **Context**: Errors should provide sufficient context to understand and resolve the issue
4. **Consistency**: Error handling patterns should be consistent throughout the SDK
5. **Actionability**: Error messages should guide users toward resolution

## Error Hierarchy

The SDK implements a comprehensive error hierarchy starting with the base `MCPError` class:

```
MCPError (base class)
├── MCPConnectionError
├── MCPProtocolError
├── MCPTimeoutError
├── MCPAuthError
├── MCPExecutionError
├── MCPConfigError
└── MCPResourceLimitError
```

This hierarchy allows applications to handle errors at different levels of granularity:

```typescript
try {
  const result = await client.executeCode(code);
} catch (error) {
  if (error instanceof MCPExecutionError) {
    // Handle execution-specific errors
    console.error(`Execution failed with code ${error.exitCode}`);
    console.debug(`Execution logs: ${error.logs}`);
  } else if (error instanceof MCPTimeoutError) {
    // Handle timeout errors
    console.warn("Operation timed out, consider increasing the timeout");
  } else if (error instanceof MCPError) {
    // Handle any MCP-related error
    console.error(`MCP error: ${error.message}`);
  } else {
    // Handle unexpected errors
    console.error(`Unexpected error: ${error}`);
  }
}
```

## Error Types and Use Cases

### MCPConnectionError

Thrown when the SDK cannot establish a connection to the required services (DeepSeek API or E2B).

**Common causes**:
- Network connectivity issues
- Service outages
- Invalid endpoint URLs

**Handling strategies**:
- Implement retry logic with exponential backoff
- Check network connectivity
- Verify endpoint configuration

### MCPProtocolError

Thrown when there are issues with the MCP protocol implementation or message format.

**Common causes**:
- Invalid request format
- Unsupported protocol version
- Missing required fields

**Handling strategies**:
- Validate inputs before sending
- Check SDK version compatibility
- Review request construction

### MCPTimeoutError

Thrown when an operation exceeds its configured timeout.

**Common causes**:
- Long-running code execution
- Network latency
- Service overload

**Handling strategies**:
- Increase timeout for complex operations
- Optimize code for faster execution
- Implement asynchronous processing for long-running tasks

### MCPAuthError

Thrown when authentication or authorization fails.

**Common causes**:
- Invalid API keys
- Expired credentials
- Insufficient permissions

**Handling strategies**:
- Verify API key validity
- Implement credential refresh
- Check permission requirements

### MCPExecutionError

Thrown when code execution fails at runtime.

**Common causes**:
- Syntax errors in code
- Runtime exceptions
- Resource constraints

**Handling strategies**:
- Validate code before execution
- Provide meaningful feedback to users
- Check execution logs for details

### MCPConfigError

Thrown when there are issues with the SDK configuration.

**Common causes**:
- Missing required configuration
- Invalid configuration values
- Configuration conflicts

**Handling strategies**:
- Validate configuration at startup
- Provide sensible defaults
- Document configuration requirements

### MCPResourceLimitError

Thrown when a resource limit is exceeded.

**Common causes**:
- Code exceeds maximum length
- Too many concurrent requests
- Memory or CPU limits exceeded

**Handling strategies**:
- Implement resource usage monitoring
- Optimize resource usage
- Consider upgrading service tier

## Error Handling Best Practices

### Do's

1. **Catch Specific Errors First**: Start with the most specific error types and move to more general ones

   ```typescript
   try {
     // Operation
   } catch (error) {
     if (error instanceof MCPExecutionError) {
       // Specific handling
     } else if (error instanceof MCPError) {
       // General handling
     } else {
       // Unexpected errors
     }
   }
   ```

2. **Log Error Details**: Include relevant context in error logs

   ```typescript
   try {
     // Operation
   } catch (error) {
     logger.error(`Operation failed: ${error.message}`, {
       errorType: error.constructor.name,
       // Include relevant context
       operationType: 'executeCode',
       language: 'python',
     });
   }
   ```

3. **Provide User-Friendly Messages**: Transform technical errors into actionable messages

   ```typescript
   try {
     // Operation
   } catch (error) {
     if (error instanceof MCPAuthError) {
       showUserMessage("Authentication failed. Please check your API key.");
     } else {
       showUserMessage("An error occurred. Please try again later.");
     }
   }
   ```

4. **Implement Retry Logic**: For transient errors, implement appropriate retry strategies

   ```typescript
   async function executeWithRetry(code, language, maxRetries = 3) {
     let retries = 0;
     while (true) {
       try {
         return await client.executeCode(code, language);
       } catch (error) {
         if (!(error instanceof MCPConnectionError) || retries >= maxRetries) {
           throw error;
         }
         retries++;
         await new Promise(resolve => setTimeout(resolve, 1000 * retries));
       }
     }
   }
   ```

### Don'ts

1. **Don't Swallow Errors**: Avoid empty catch blocks

   ```typescript
   // BAD
   try {
     await client.executeCode(code);
   } catch (error) {
     // Silence the error - DON'T DO THIS
   }
   ```

2. **Don't Use Generic Catches for Specific Handling**: Be precise in error handling

   ```typescript
   // BAD
   try {
     await client.executeCode(code);
   } catch (error) {
     // Assuming it's always a timeout - DON'T DO THIS
     console.log("Operation timed out");
   }
   ```

3. **Don't Expose Raw Error Details to End Users**: Filter sensitive information

   ```typescript
   // BAD
   try {
     await client.executeCode(code);
   } catch (error) {
     // Exposing internal details - DON'T DO THIS
     userInterface.showError(`Internal error: ${error.stack}`);
   }
   ```

4. **Don't Ignore Error Context**: Use all available information

   ```typescript
   // BAD
   try {
     await client.executeCode(code);
   } catch (error) {
     if (error instanceof MCPExecutionError) {
       // Ignoring valuable context - DON'T DO THIS
       console.error("Execution failed");
       // Instead, use error.exitCode and error.logs
     }
   }
   ```

## Error Recovery Strategies

### Graceful Degradation

Implement fallback mechanisms when critical operations fail:

```typescript
async function generateTextWithFallback(prompt) {
  try {
    return await client.generateText(prompt);
  } catch (error) {
    // Fall back to a simpler model or cached responses
    return { text: "Sorry, text generation is currently unavailable." };
  }
}
```

### Circuit Breaker Pattern

Prevent cascading failures by temporarily disabling operations that consistently fail:

```typescript
class CircuitBreaker {
  private failures = 0;
  private lastFailure = 0;
  private threshold = 5;
  private resetTimeout = 30000; // 30 seconds

  async execute(operation) {
    if (this.isOpen()) {
      throw new Error("Circuit is open, operation not attempted");
    }

    try {
      const result = await operation();
      this.reset();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  private isOpen() {
    if (this.failures >= this.threshold) {
      const now = Date.now();
      if (now - this.lastFailure < this.resetTimeout) {
        return true;
      }
      this.reset();
    }
    return false;
  }

  private recordFailure() {
    this.failures++;
    this.lastFailure = Date.now();
  }

  private reset() {
    this.failures = 0;
  }
}
```

### Bulkhead Pattern

Isolate failures to prevent them from affecting the entire system:

```typescript
class Bulkhead {
  private executing = 0;
  private maxConcurrent;

  constructor(maxConcurrent = 10) {
    this.maxConcurrent = maxConcurrent;
  }

  async execute(operation) {
    if (this.executing >= this.maxConcurrent) {
      throw new Error("Bulkhead capacity reached");
    }

    this.executing++;
    try {
      return await operation();
    } finally {
      this.executing--;
    }
  }
}
```

## Conclusion

Effective error handling is essential for building robust applications with the DeepExec SDK. By following the principles and practices outlined in this document, developers can create applications that gracefully handle failures, provide meaningful feedback to users, and maintain system stability even when errors occur.
