/**
 * Configuration management for the DeepExec SDK.
 * 
 * This module provides a flexible configuration system that supports
 * multiple sources (constructor arguments, environment variables, config files)
 * with sensible defaults and validation.
 */

import { MCPConfigError } from './exceptions';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Configuration options for the DeepExec client
 */
export interface ClientConfigOptions {
  /** MCP service endpoint URL */
  endpoint?: string;
  
  /** Request timeout in seconds */
  timeout?: number;
  
  /** Maximum number of retry attempts */
  maxRetries?: number;
  
  /** Authentication token */
  authToken?: string;
  
  /** Whether to verify SSL certificates */
  verifySSL?: boolean;
  
  /** DeepSeek API key */
  deepseekKey?: string;
  
  /** E2B API key */
  e2bKey?: string;
  
  /** DeepSeek API URL */
  deepseekApiUrl?: string;
  
  /** Security options */
  securityOptions?: {
    /** Maximum code length in characters */
    maxCodeLength?: number;
    
    /** List of allowed programming languages */
    allowedLanguages?: string[];
    
    /** List of blocked keywords */
    blockedKeywords?: string[];
  };
}

/**
 * Default configuration values
 */
const DEFAULT_CONFIG: Required<ClientConfigOptions> = {
  endpoint: 'wss://api.deepexec.ai/v1',
  timeout: 30.0,
  maxRetries: 3,
  authToken: '',
  verifySSL: true,
  deepseekKey: '',
  e2bKey: '',
  deepseekApiUrl: 'https://api.deepseek.com/v1',
  securityOptions: {
    maxCodeLength: 10000,
    allowedLanguages: ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c', 'cpp'],
    blockedKeywords: ['rm -rf', 'System.exit', 'os.system'],
  },
};

/**
 * Environment variable prefix for all config options
 */
const ENV_PREFIX = 'DEEPEXEC_';

/**
 * Default config file name
 */
const CONFIG_FILE = '.deepexecrc';

/**
 * Client configuration class
 */
export class ClientConfig {
  endpoint: string;
  timeout: number;
  maxRetries: number;
  authToken: string;
  verifySSL: boolean;
  deepseekKey: string;
  e2bKey: string;
  deepseekApiUrl: string;
  securityOptions: {
    maxCodeLength: number;
    allowedLanguages: string[];
    blockedKeywords: string[];
  };

  /**
   * Creates a new client configuration instance
   * 
   * Configuration is loaded from multiple sources in the following order of precedence:
   * 1. Constructor arguments
   * 2. Environment variables
   * 3. Configuration file
   * 4. Default values
   * 
   * @param options - Configuration options
   */
  constructor(options: ClientConfigOptions = {}) {
    // Start with default values
    const config = { ...DEFAULT_CONFIG };
    
    // Load from config file if it exists
    this.loadFromFile(config);
    
    // Load from environment variables
    this.loadFromEnv(config);
    
    // Override with constructor arguments
    this.mergeOptions(config, options);
    
    // Validate and assign final configuration
    this.validate(config);
    this.assignConfig(config);
  }

  /**
   * Loads configuration from file if it exists
   */
  private loadFromFile(config: Required<ClientConfigOptions>): void {
    const homeDir = process.env.HOME || process.env.USERPROFILE || '';
    const configPaths = [
      path.join(process.cwd(), CONFIG_FILE),
      path.join(homeDir, CONFIG_FILE),
    ];

    for (const configPath of configPaths) {
      if (fs.existsSync(configPath)) {
        try {
          const content = fs.readFileSync(configPath, 'utf8');
          const lines = content.split('\n');
          
          for (const line of lines) {
            const [key, value] = line.split('=').map(s => s.trim());
            if (key && value) {
              this.setNestedProperty(config, key, this.parseValue(value));
            }
          }
          
          break; // Stop after first found config file
        } catch (error) {
          // Silently ignore file reading errors
        }
      }
    }
  }

  /**
   * Loads configuration from environment variables
   */
  private loadFromEnv(config: Required<ClientConfigOptions>): void {
    for (const key in process.env) {
      if (key.startsWith(ENV_PREFIX)) {
        const configKey = key.substring(ENV_PREFIX.length).toLowerCase();
        const value = process.env[key];
        
        if (value) {
          this.setNestedProperty(config, configKey, this.parseValue(value));
        }
      }
    }
  }

  /**
   * Merges provided options with existing configuration
   */
  private mergeOptions(config: Required<ClientConfigOptions>, options: ClientConfigOptions): void {
    for (const [key, value] of Object.entries(options)) {
      if (value !== undefined) {
        if (key === 'securityOptions' && options.securityOptions) {
          config.securityOptions = {
            ...config.securityOptions,
            ...options.securityOptions,
          };
        } else {
          (config as any)[key] = value;
        }
      }
    }
  }

  /**
   * Validates the configuration
   */
  private validate(config: Required<ClientConfigOptions>): void {
    // Validate endpoint
    if (!config.endpoint) {
      throw new MCPConfigError('Endpoint URL is required');
    }
    
    // Validate timeout
    if (config.timeout <= 0) {
      throw new MCPConfigError('Timeout must be positive');
    }
    
    // Validate maxRetries
    if (config.maxRetries < 0) {
      throw new MCPConfigError('Max retries cannot be negative');
    }
    
    // Validate API keys
    if (!config.deepseekKey) {
      throw new MCPConfigError('DeepSeek API key is required');
    }
    
    if (!config.e2bKey) {
      throw new MCPConfigError('E2B API key is required');
    }
  }

  /**
   * Assigns the final validated configuration
   */
  private assignConfig(config: Required<ClientConfigOptions>): void {
    this.endpoint = config.endpoint;
    this.timeout = config.timeout;
    this.maxRetries = config.maxRetries;
    this.authToken = config.authToken;
    this.verifySSL = config.verifySSL;
    this.deepseekKey = config.deepseekKey;
    this.e2bKey = config.e2bKey;
    this.deepseekApiUrl = config.deepseekApiUrl;
    this.securityOptions = { ...config.securityOptions };
  }

  /**
   * Sets a nested property in the configuration object
   */
  private setNestedProperty(obj: any, key: string, value: any): void {
    const parts = key.split('_');
    let current = obj;
    
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part];
    }
    
    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  /**
   * Parses string values into appropriate types
   */
  private parseValue(value: string): any {
    // Try parsing as number
    if (/^\d+$/.test(value)) {
      return parseInt(value, 10);
    }
    if (/^\d+\.\d+$/.test(value)) {
      return parseFloat(value);
    }
    
    // Try parsing as boolean
    if (value.toLowerCase() === 'true') return true;
    if (value.toLowerCase() === 'false') return false;
    
    // Try parsing as array
    if (value.startsWith('[') && value.endsWith(']')) {
      try {
        return JSON.parse(value);
      } catch {
        // If parsing fails, return as string
      }
    }
    
    // Return as string
    return value;
  }
}
