# DeepExec SDK

A TypeScript SDK for interacting with the DeepExec service, providing secure code execution and AI text generation capabilities.

## Features

- **Code Execution**: Execute code in various programming languages in a secure, sandboxed environment
- **Text Generation**: Generate text using DeepSeek's powerful AI models
- **Streaming Support**: Stream text generation results for real-time applications
- **Comprehensive Error Handling**: Detailed error hierarchy for precise error handling
- **Flexible Configuration**: Configure the SDK from multiple sources with clear priority order
- **Security-First Design**: Multiple layers of security controls to prevent abuse

## Installation

```bash
npm install deepexec-sdk
```

## Quick Start

```typescript
import { DeepExecClient } from 'deepexec-sdk';

// Create client instance
const client = new DeepExecClient({
  deepseekKey: "sk-...",  // Your DeepSeek API key
  e2bKey: "e2b_..."      // Your E2B API key
});

// Create a session
const sessionId = client.createSession("user123");

// Execute code
try {
  const result = await client.executeCode(
    "print('Hello, World!')", 
    "python"
  );
  console.log(result.output);
} catch (error) {
  console.error("Execution failed:", error);
}

// Generate text
try {
  const result = await client.generateText(
    "Explain quantum computing in simple terms"
  );
  console.log(result.text);
} catch (error) {
  console.error("Text generation failed:", error);
}

// Close the client
await client.close();
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

## Configuration

The SDK can be configured in multiple ways:

### Constructor Arguments

```typescript
const client = new DeepExecClient({
  endpoint: "https://api.deepexec.com/v1",
  timeout: 30.0,
  maxRetries: 3,
  deepseekKey: "sk-...",
  e2bKey: "e2b_...",
  verifySSL: true,
  securityOptions: {
    maxCodeLength: 10000,
    allowedLanguages: ["python", "javascript", "typescript"],
    blockedKeywords: ["rm -rf", "System.exit", "os.system"]
  }
});
```

### Environment Variables

```bash
export DEEPEXEC_ENDPOINT="https://api.deepexec.com/v1"
export DEEPEXEC_TIMEOUT=30.0
export DEEPEXEC_MAX_RETRIES=3
export DEEPEXEC_DEEPSEEK_KEY="sk-..."
export DEEPEXEC_E2B_KEY="e2b_..."
export DEEPEXEC_VERIFY_SSL=true
export DEEPEXEC_MAX_CODE_LENGTH=10000
export DEEPEXEC_ALLOWED_LANGUAGES="python,javascript,typescript"
export DEEPEXEC_BLOCKED_KEYWORDS="rm -rf,System.exit,os.system"
```

### Configuration File

Create a `.deepexecrc` file in your project directory or home directory:

```json
{
  "endpoint": "https://api.deepexec.com/v1",
  "timeout": 30.0,
  "maxRetries": 3,
  "deepseekKey": "sk-...",
  "e2bKey": "e2b_...",
  "verifySSL": true,
  "securityOptions": {
    "maxCodeLength": 10000,
    "allowedLanguages": ["python", "javascript", "typescript"],
    "blockedKeywords": ["rm -rf", "System.exit", "os.system"]
  }
}
```

## Error Handling

The SDK provides a comprehensive error hierarchy for precise error handling:

```typescript
try {
  const result = await client.executeCode(code, 'python');
  console.log(result.output);
} catch (error) {
  if (error instanceof MCPExecutionError) {
    console.error(`Execution failed with exit code ${error.exitCode}`);
    console.error(`Logs: ${error.logs.join('\n')}`);
  } else if (error instanceof MCPTimeoutError) {
    console.error(`Operation timed out after ${error.timeoutSeconds} seconds`);
  } else if (error instanceof MCPConnectionError) {
    console.error(`Connection error: ${error.message}`);
  } else if (error instanceof MCPError) {
    console.error(`MCP error: ${error.message}`);
  } else {
    console.error(`Unexpected error: ${error}`);
  }
}
```

## Security

The SDK implements multiple layers of security:

1. **Input Validation**: All API calls are validated
2. **Code Scanning**: Code is scanned for blocked keywords
3. **Language Restrictions**: Only allowed languages can be executed
4. **Code Length Limits**: Maximum code length is enforced
5. **Timeout Controls**: All operations have configurable timeouts
6. **Sandboxed Execution**: Code is executed in a secure, sandboxed environment

See the [security model documentation](docs/concepts/security_model.md) for more details.

## License

MIT
