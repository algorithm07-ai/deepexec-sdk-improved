/**
 * Core exception classes for the DeepExec SDK.
 * 
 * This module provides a comprehensive hierarchy of exceptions
 * that can be thrown by the SDK, allowing for precise error handling.
 */

/**
 * Base exception for all MCP-related errors
 */
export class MCPError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'MCPError';
    Object.setPrototypeOf(this, MCPError.prototype);
  }
}

/**
 * Network-level connection failures
 */
export class MCPConnectionError extends MCPError {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'MCPConnectionError';
    Object.setPrototypeOf(this, MCPConnectionError.prototype);
  }
}

/**
 * Protocol violations or malformed messages
 */
export class MCPProtocolError extends MCPError {
  constructor(message: string, public readonly requestId?: string) {
    super(message);
    this.name = 'MCPProtocolError';
    Object.setPrototypeOf(this, MCPProtocolError.prototype);
  }
}

/**
 * Operation timed out
 */
export class MCPTimeoutError extends MCPError {
  constructor(message: string, public readonly operationId?: string) {
    super(message);
    this.name = 'MCPTimeoutError';
    Object.setPrototypeOf(this, MCPTimeoutError.prototype);
  }
}

/**
 * Authentication/authorization failures
 */
export class MCPAuthError extends MCPError {
  constructor(message: string) {
    super(message);
    this.name = 'MCPAuthError';
    Object.setPrototypeOf(this, MCPAuthError.prototype);
  }
}

/**
 * Runtime execution errors
 */
export class MCPExecutionError extends MCPError {
  /**
   * Creates a new execution error instance
   * 
   * @param message - Error message
   * @param exitCode - Process exit code (if applicable)
   * @param logs - Execution logs (if available)
   */
  constructor(
    message: string, 
    public readonly exitCode?: number, 
    public readonly logs?: string[]
  ) {
    super(message);
    this.name = 'MCPExecutionError';
    Object.setPrototypeOf(this, MCPExecutionError.prototype);
  }
}

/**
 * Configuration errors
 */
export class MCPConfigError extends MCPError {
  constructor(message: string) {
    super(message);
    this.name = 'MCPConfigError';
    Object.setPrototypeOf(this, MCPConfigError.prototype);
  }
}

/**
 * Resource limit exceeded
 */
export class MCPResourceLimitError extends MCPError {
  constructor(message: string, public readonly resourceType?: string) {
    super(message);
    this.name = 'MCPResourceLimitError';
    Object.setPrototypeOf(this, MCPResourceLimitError.prototype);
  }
}
