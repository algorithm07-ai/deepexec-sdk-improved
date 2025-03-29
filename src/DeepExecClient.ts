/**
 * Main client class for interacting with the DeepExec service.
 * 
 * Provides synchronous and asynchronous interfaces for executing
 * operations via the MCP protocol.
 * 
 * @example
 * ```typescript
 * import { DeepExecClient } from 'mcp-deepexec-sdk';
 * 
 * // Create client instance
 * const client = new DeepExecClient({
 *   deepseekKey: "sk-...",
 *   e2bKey: "e2b_..."
 * });
 * 
 * // Execute code
 * try {
 *   const result = await client.executeCode(
 *     "print('Hello, World!')", 
 *     "python"
 *   );
 *   console.log(result.output);
 * } catch (error) {
 *   console.error("Execution failed:", error);
 * }
 * ```
 */

import { ClientConfig, ClientConfigOptions } from './core/config';
import {
  MCPError,
  MCPConnectionError,
  MCPProtocolError,
  MCPTimeoutError,
  MCPAuthError,
  MCPExecutionError,
  MCPConfigError
} from './core/exceptions';

/**
 * Result of a code execution operation
 */
export interface ExecutionResult {
  /** Execution output (stdout/stderr combined) */
  output: string;
  
  /** Exit code of the process */
  exitCode: number;
  
  /** Execution time in milliseconds */
  executionTime: number;
  
  /** Memory usage in MB */
  memoryUsage?: number;
  
  /** Additional metadata about the execution */
  metadata?: Record<string, any>;
}

/**
 * Result of a text generation operation
 */
export interface TextGenerationResult {
  /** Generated text */
  text: string;
  
  /** Model used for generation */
  model: string;
  
  /** Generation time in milliseconds */
  generationTime: number;
  
  /** Token usage statistics */
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

/**
 * Main client class for interacting with the DeepExec service.
 * 
 * Provides synchronous and asynchronous interfaces for executing
 * operations via the MCP protocol.
 */
export class DeepExecClient {
  private config: ClientConfig;
  private sessionId: string | null = null;
  
  /**
   * Creates a new DeepExec client instance
   * 
   * @param options - Configuration options
   * @throws {MCPConfigError} For invalid configuration parameters
   */
  constructor(options: ClientConfigOptions = {}) {
    try {
      this.config = new ClientConfig(options);
    } catch (error) {
      if (error instanceof MCPConfigError) {
        throw error;
      }
      throw new MCPConfigError(`Failed to initialize client: ${(error as Error).message}`);
    }
  }
  
  /**
   * Creates a new session
   * 
   * @param userId - User identifier for the session
   * @returns Session identifier
   * @throws {MCPConnectionError} If connection to the endpoint fails
   * @throws {MCPAuthError} If authentication fails
   */
  createSession(userId: string): string {
    // Implementation would connect to the MCP service and create a session
    this.sessionId = `session_${Date.now()}_${userId}`;
    return this.sessionId;
  }
  
  /**
   * Execute code snippet in specified language runtime
   * 
   * @param code - Source code to execute
   * @param language - Programming language (default: "python")
   * @param timeout - Execution timeout in seconds (default: config timeout)
   * @returns Execution result object
   * @throws {MCPRequestError} For invalid requests
   * @throws {MCPExecutionError} For runtime errors during execution
   * @throws {MCPTimeoutError} If operation times out
   */
  async executeCode(code: string, language = "python", timeout?: number): Promise<ExecutionResult> {
    // Validate session
    if (!this.sessionId) {
      throw new MCPProtocolError("No active session, call createSession first");
    }
    
    // Validate code
    if (!code) {
      throw new MCPProtocolError("Code cannot be empty");
    }
    
    // Check code length
    if (code.length > this.config.securityOptions.maxCodeLength) {
      throw new MCPProtocolError(
        `Code exceeds maximum length of ${this.config.securityOptions.maxCodeLength} characters`
      );
    }
    
    // Check language
    if (!this.config.securityOptions.allowedLanguages.includes(language)) {
      throw new MCPProtocolError(
        `Language '${language}' is not supported. Allowed languages: ${this.config.securityOptions.allowedLanguages.join(', ')}`
      );
    }
    
    // Check for blocked keywords
    for (const keyword of this.config.securityOptions.blockedKeywords) {
      if (code.includes(keyword)) {
        throw new MCPProtocolError(`Code contains blocked keyword: ${keyword}`);
      }
    }
    
    // Implementation would send the request to the MCP service
    // This is a placeholder implementation
    try {
      // Simulate execution
      const executionTime = Math.random() * 1000;
      const exitCode = Math.random() > 0.8 ? 1 : 0;
      
      // Simulate failure
      if (exitCode !== 0) {
        throw new MCPExecutionError(
          `Execution failed with exit code ${exitCode}`,
          exitCode,
          [`Error: execution failed at line 1`, `Process exited with code ${exitCode}`]
        );
      }
      
      return {
        output: `Executed ${code.length} bytes of ${language} code successfully`,
        exitCode: 0,
        executionTime,
        memoryUsage: Math.random() * 100,
        metadata: {
          language,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      if (error instanceof MCPError) {
        throw error;
      }
      throw new MCPExecutionError(`Execution failed: ${(error as Error).message}`);
    }
  }
  
  /**
   * Generate text using the DeepSeek model
   * 
   * @param prompt - Text prompt
   * @param options - Generation options
   * @returns Generated text result
   * @throws {MCPRequestError} For invalid requests
   * @throws {MCPConnectionError} If connection to the model service fails
   * @throws {MCPTimeoutError} If operation times out
   */
  async generateText(
    prompt: string,
    options: {
      maxTokens?: number;
      temperature?: number;
      topP?: number;
      model?: string;
    } = {}
  ): Promise<TextGenerationResult> {
    // Validate session
    if (!this.sessionId) {
      throw new MCPProtocolError("No active session, call createSession first");
    }
    
    // Validate prompt
    if (!prompt) {
      throw new MCPProtocolError("Prompt cannot be empty");
    }
    
    // Implementation would send the request to the DeepSeek API
    // This is a placeholder implementation
    try {
      const generationTime = Math.random() * 2000;
      const model = options.model || "deepseek-v3";
      
      return {
        text: `Generated response for: ${prompt.substring(0, 20)}...`,
        model,
        generationTime,
        usage: {
          promptTokens: prompt.length / 4,
          completionTokens: 100,
          totalTokens: prompt.length / 4 + 100
        }
      };
    } catch (error) {
      if (error instanceof MCPError) {
        throw error;
      }
      throw new MCPConnectionError(`Text generation failed: ${(error as Error).message}`);
    }
  }
  
  /**
   * Stream text generation results
   * 
   * @param prompt - Text prompt
   * @param options - Generation options
   * @returns Async generator yielding text chunks
   * @throws {MCPRequestError} For invalid requests
   * @throws {MCPConnectionError} If connection to the model service fails
   */
  async *streamGenerateText(
    prompt: string,
    options: {
      maxTokens?: number;
      temperature?: number;
      topP?: number;
      model?: string;
    } = {}
  ): AsyncGenerator<{ text: string, done: boolean }> {
    // Validate session
    if (!this.sessionId) {
      throw new MCPProtocolError("No active session, call createSession first");
    }
    
    // Validate prompt
    if (!prompt) {
      throw new MCPProtocolError("Prompt cannot be empty");
    }
    
    // Implementation would stream responses from the DeepSeek API
    // This is a placeholder implementation
    try {
      const words = "This is a streaming response from the DeepSeek model. It demonstrates how text can be generated token by token.".split(' ');
      
      for (let i = 0; i < words.length; i++) {
        yield {
          text: words[i] + ' ',
          done: i === words.length - 1
        };
        
        // Simulate streaming delay
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    } catch (error) {
      if (error instanceof MCPError) {
        throw error;
      }
      throw new MCPConnectionError(`Text streaming failed: ${(error as Error).message}`);
    }
  }
  
  /**
   * Close the client and release resources
   * 
   * @returns Promise that resolves when cleanup is complete
   */
  async close(): Promise<void> {
    // Implementation would close connections and clean up resources
    this.sessionId = null;
  }
}
