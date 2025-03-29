DeepExecClient
==============

The ``DeepExecClient`` class is the main entry point for applications using the DeepExec SDK. It provides methods for session management, code execution, and text generation.

Class Definition
---------------

.. js:class:: DeepExecClient

   Main client class for interacting with the DeepExec service.

   .. js:constructor:: constructor(options)

      Creates a new DeepExec client instance.

      :param options: Configuration options
      :type options: ClientConfigOptions
      :throws: :js:class:`MCPConfigError` - For invalid configuration parameters

   .. js:method:: createSession(userId)

      Creates a new session.

      :param userId: User identifier for the session
      :type userId: string
      :returns: Session identifier
      :rtype: string
      :throws: :js:class:`MCPConnectionError` - If connection to the endpoint fails
      :throws: :js:class:`MCPAuthError` - If authentication fails

   .. js:method:: async executeCode(code, language, timeout)

      Execute code snippet in specified language runtime.

      :param code: Source code to execute
      :type code: string
      :param language: Programming language (default: "python")
      :type language: string
      :param timeout: Execution timeout in seconds (default: config timeout)
      :type timeout: number
      :returns: Execution result object
      :rtype: Promise<ExecutionResult>
      :throws: :js:class:`MCPRequestError` - For invalid requests
      :throws: :js:class:`MCPExecutionError` - For runtime errors during execution
      :throws: :js:class:`MCPTimeoutError` - If operation times out

   .. js:method:: async generateText(prompt, options)

      Generate text using the DeepSeek model.

      :param prompt: Text prompt
      :type prompt: string
      :param options: Generation options
      :type options: object
      :param options.maxTokens: Maximum number of tokens to generate
      :type options.maxTokens: number
      :param options.temperature: Sampling temperature (0.0-2.0)
      :type options.temperature: number
      :param options.topP: Top-p sampling parameter (0.0-1.0)
      :type options.topP: number
      :param options.model: Model name to use
      :type options.model: string
      :returns: Generated text result
      :rtype: Promise<TextGenerationResult>
      :throws: :js:class:`MCPRequestError` - For invalid requests
      :throws: :js:class:`MCPConnectionError` - If connection to the model service fails
      :throws: :js:class:`MCPTimeoutError` - If operation times out

   .. js:method:: async *streamGenerateText(prompt, options)

      Stream text generation results.

      :param prompt: Text prompt
      :type prompt: string
      :param options: Generation options
      :type options: object
      :param options.maxTokens: Maximum number of tokens to generate
      :type options.maxTokens: number
      :param options.temperature: Sampling temperature (0.0-2.0)
      :type options.temperature: number
      :param options.topP: Top-p sampling parameter (0.0-1.0)
      :type options.topP: number
      :param options.model: Model name to use
      :type options.model: string
      :returns: Async generator yielding text chunks
      :rtype: AsyncGenerator<{ text: string, done: boolean }>
      :throws: :js:class:`MCPRequestError` - For invalid requests
      :throws: :js:class:`MCPConnectionError` - If connection to the model service fails

   .. js:method:: async close()

      Close the client and release resources.

      :returns: Promise that resolves when cleanup is complete
      :rtype: Promise<void>

Interfaces
----------

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

   .. js:attribute:: metadata

      Additional metadata about the execution.

      :type: Record<string, any>

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

   .. js:attribute:: usage.promptTokens

      Number of tokens in the prompt.

      :type: number

   .. js:attribute:: usage.completionTokens

      Number of tokens in the completion.

      :type: number

   .. js:attribute:: usage.totalTokens

      Total number of tokens used.

      :type: number

Examples
--------

Basic Code Execution
~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient } from 'deepexec-sdk';

   // Create client instance
   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_..."
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

Text Generation
~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient } from 'deepexec-sdk';

   // Create client instance
   const client = new DeepExecClient({
     deepseekKey: "sk-..."
   });

   // Create a session
   const sessionId = client.createSession("user123");

   // Generate text
   try {
     const result = await client.generateText(
       "Explain quantum computing in simple terms",
       {
         maxTokens: 500,
         temperature: 0.7,
         model: "deepseek-v3"
       }
     );
     console.log(result.text);
   } catch (error) {
     console.error("Text generation failed:", error);
   }

Streaming Text Generation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient } from 'deepexec-sdk';

   // Create client instance
   const client = new DeepExecClient({
     deepseekKey: "sk-..."
   });

   // Create a session
   const sessionId = client.createSession("user123");

   // Stream text generation
   try {
     const stream = client.streamGenerateText(
       "Write a short story about a robot",
       {
         temperature: 0.8,
         model: "deepseek-v3"
       }
     );

     for await (const chunk of stream) {
       process.stdout.write(chunk.text);
       if (chunk.done) {
         process.stdout.write('\n');
       }
     }
   } catch (error) {
     console.error("Text streaming failed:", error);
   }
