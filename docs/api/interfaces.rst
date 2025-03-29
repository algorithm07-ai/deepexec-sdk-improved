Interfaces and Types
===================

This section documents the interfaces and type definitions used throughout the DeepExec SDK.

Execution Interfaces
------------------

.. js:class:: ExecutionResult

   Result of a code execution operation.

   .. js:attribute:: output

      Execution output (stdout/stderr combined).

      :type: string

   .. js:attribute:: exitCode

      Exit code of the process.

      :type: number

   .. js:attribute:: executionTime

      Execution time in milliseconds.

      :type: number

   .. js:attribute:: memoryUsage

      Memory usage in MB.

      :type: number
      :optional:

   .. js:attribute:: metadata

      Additional metadata about the execution.

      :type: Record<string, any>
      :optional:

.. js:class:: ExecutionOptions

   Options for code execution.

   .. js:attribute:: timeout

      Execution timeout in seconds.

      :type: number
      :optional:

   .. js:attribute:: language

      Programming language.

      :type: string
      :optional:

   .. js:attribute:: environment

      Environment variables to set for the execution.

      :type: Record<string, string>
      :optional:

   .. js:attribute:: workingDirectory

      Working directory for the execution.

      :type: string
      :optional:

Text Generation Interfaces
------------------------

.. js:class:: TextGenerationResult

   Result of a text generation operation.

   .. js:attribute:: text

      Generated text.

      :type: string

   .. js:attribute:: model

      Model used for generation.

      :type: string

   .. js:attribute:: generationTime

      Generation time in milliseconds.

      :type: number

   .. js:attribute:: usage

      Token usage statistics.

      :type: object
      :optional:

   .. js:attribute:: usage.promptTokens

      Number of tokens in the prompt.

      :type: number

   .. js:attribute:: usage.completionTokens

      Number of tokens in the completion.

      :type: number

   .. js:attribute:: usage.totalTokens

      Total number of tokens used.

      :type: number

.. js:class:: TextGenerationOptions

   Options for text generation.

   .. js:attribute:: maxTokens

      Maximum number of tokens to generate.

      :type: number
      :optional:

   .. js:attribute:: temperature

      Sampling temperature (0.0-2.0).

      :type: number
      :optional:

   .. js:attribute:: topP

      Top-p sampling parameter (0.0-1.0).

      :type: number
      :optional:

   .. js:attribute:: model

      Model name to use.

      :type: string
      :optional:

.. js:class:: TextStreamChunk

   Chunk of a streaming text generation response.

   .. js:attribute:: text

      Text chunk.

      :type: string

   .. js:attribute:: done

      Whether this is the final chunk.

      :type: boolean

Configuration Interfaces
----------------------

.. js:class:: ClientConfigOptions

   Configuration options for the DeepExec client.

   .. js:attribute:: endpoint

      API endpoint URL.

      :type: string
      :optional:

   .. js:attribute:: timeout

      Operation timeout in seconds.

      :type: number
      :optional:

   .. js:attribute:: maxRetries

      Maximum number of retry attempts for failed operations.

      :type: number
      :optional:

   .. js:attribute:: deepseekKey

      DeepSeek API key for authentication.

      :type: string
      :optional:

   .. js:attribute:: e2bKey

      E2B API key for code execution.

      :type: string
      :optional:

   .. js:attribute:: verifySSL

      Whether to verify SSL certificates.

      :type: boolean
      :optional:

   .. js:attribute:: securityOptions

      Advanced security configuration options.

      :type: SecurityOptions
      :optional:

.. js:class:: SecurityOptions

   Security configuration options.

   .. js:attribute:: maxCodeLength

      Maximum allowed code length in characters.

      :type: number
      :optional:

   .. js:attribute:: allowedLanguages

      List of allowed programming languages.

      :type: string[]
      :optional:

   .. js:attribute:: blockedKeywords

      List of blocked keywords that will trigger security errors.

      :type: string[]
      :optional:

Protocol Interfaces
-----------------

.. js:class:: MCPRequest

   MCP protocol request message.

   .. js:attribute:: protocol_version

      Protocol version (e.g., "2024.1").

      :type: string

   .. js:attribute:: type

      Request type (e.g., "text_generation", "code_execution").

      :type: string

   .. js:attribute:: session_id

      Session identifier.

      :type: string
      :optional:

   .. js:attribute:: input

      Request input parameters.

      :type: object

   .. js:attribute:: metadata

      Request metadata.

      :type: object
      :optional:

.. js:class:: MCPResponse

   MCP protocol response message.

   .. js:attribute:: protocol_version

      Protocol version (e.g., "2024.1").

      :type: string

   .. js:attribute:: type

      Response type (e.g., "text_generation_result", "code_execution_result").

      :type: string

   .. js:attribute:: session_id

      Session identifier.

      :type: string
      :optional:

   .. js:attribute:: request_id

      Unique request identifier.

      :type: string

   .. js:attribute:: status

      Operation status ("success" or "error").

      :type: string

   .. js:attribute:: output

      Response output data.

      :type: object

   .. js:attribute:: error

      Error information (only present if status is "error").

      :type: object
      :optional:

   .. js:attribute:: metadata

      Response metadata.

      :type: object
      :optional:
