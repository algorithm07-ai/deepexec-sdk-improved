Error Handling
=============

The DeepExec SDK implements a comprehensive error hierarchy to enable precise error handling. All errors extend from the base ``MCPError`` class.

Error Hierarchy
--------------

.. js:class:: MCPError

   Base error class for all SDK errors.

   .. js:constructor:: constructor(message)

      Creates a new MCPError instance.

      :param message: Error message
      :type message: string

   .. js:attribute:: message

      Error message.

      :type: string

   .. js:attribute:: name

      Error name (class name).

      :type: string

.. js:class:: MCPConnectionError
   :extends: MCPError

   Thrown when a connection to a required service fails.

   .. js:constructor:: constructor(message)

      Creates a new MCPConnectionError instance.

      :param message: Error message
      :type message: string

.. js:class:: MCPProtocolError
   :extends: MCPError

   Thrown when there are issues with the MCP protocol implementation or message format.

   .. js:constructor:: constructor(message)

      Creates a new MCPProtocolError instance.

      :param message: Error message
      :type message: string

.. js:class:: MCPTimeoutError
   :extends: MCPError

   Thrown when an operation exceeds its configured timeout.

   .. js:constructor:: constructor(message, timeoutSeconds)

      Creates a new MCPTimeoutError instance.

      :param message: Error message
      :type message: string
      :param timeoutSeconds: The timeout value that was exceeded
      :type timeoutSeconds: number

   .. js:attribute:: timeoutSeconds

      The timeout value that was exceeded.

      :type: number

.. js:class:: MCPAuthError
   :extends: MCPError

   Thrown when authentication or authorization fails.

   .. js:constructor:: constructor(message)

      Creates a new MCPAuthError instance.

      :param message: Error message
      :type message: string

.. js:class:: MCPExecutionError
   :extends: MCPError

   Thrown when code execution fails at runtime.

   .. js:constructor:: constructor(message, exitCode, logs)

      Creates a new MCPExecutionError instance.

      :param message: Error message
      :type message: string
      :param exitCode: Process exit code
      :type exitCode: number
      :param logs: Execution logs
      :type logs: string[]

   .. js:attribute:: exitCode

      Process exit code.

      :type: number

   .. js:attribute:: logs

      Execution logs.

      :type: string[]

.. js:class:: MCPConfigError
   :extends: MCPError

   Thrown when there are issues with the SDK configuration.

   .. js:constructor:: constructor(message)

      Creates a new MCPConfigError instance.

      :param message: Error message
      :type message: string

.. js:class:: MCPResourceLimitError
   :extends: MCPError

   Thrown when a resource limit is exceeded.

   .. js:constructor:: constructor(message, resourceType, limit, actual)

      Creates a new MCPResourceLimitError instance.

      :param message: Error message
      :type message: string
      :param resourceType: Type of resource that was limited
      :type resourceType: string
      :param limit: Resource limit value
      :type limit: number
      :param actual: Actual resource usage
      :type actual: number

   .. js:attribute:: resourceType

      Type of resource that was limited.

      :type: string

   .. js:attribute:: limit

      Resource limit value.

      :type: number

   .. js:attribute:: actual

      Actual resource usage.

      :type: number

Error Handling Examples
---------------------

Basic Error Handling
~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient, MCPError } from 'deepexec-sdk';

   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_..."
   });

   try {
     const result = await client.executeCode(code, 'python');
     console.log(result.output);
   } catch (error) {
     if (error instanceof MCPError) {
       console.error(`MCP error: ${error.message}`);
     } else {
       console.error(`Unexpected error: ${error}`);
     }
   }

Handling Specific Error Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { 
     DeepExecClient, 
     MCPExecutionError,
     MCPTimeoutError,
     MCPConnectionError,
     MCPError 
   } from 'deepexec-sdk';

   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_..."
   });

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
       console.error(`Please check your network connection and try again later`);
     } else if (error instanceof MCPError) {
       console.error(`MCP error: ${error.message}`);
     } else {
       console.error(`Unexpected error: ${error}`);
     }
   }

Implementing Retry Logic
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { 
     DeepExecClient, 
     MCPConnectionError,
     MCPTimeoutError 
   } from 'deepexec-sdk';

   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_..."
   });

   async function executeWithRetry(code, language, maxRetries = 3) {
     let retries = 0;
     while (true) {
       try {
         return await client.executeCode(code, language);
       } catch (error) {
         if (!(error instanceof MCPConnectionError || 
              error instanceof MCPTimeoutError) || 
             retries >= maxRetries) {
           throw error;
         }
         retries++;
         console.log(`Retry attempt ${retries}/${maxRetries}...`);
         await new Promise(resolve => setTimeout(resolve, 1000 * retries));
       }
     }
   }

   try {
     const result = await executeWithRetry(code, 'python');
     console.log(result.output);
   } catch (error) {
     console.error(`Failed after retries: ${error.message}`);
   }

Circuit Breaker Pattern
~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient, MCPError } from 'deepexec-sdk';

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

   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_..."
   });

   const breaker = new CircuitBreaker();

   try {
     const result = await breaker.execute(() => 
       client.executeCode(code, 'python')
     );
     console.log(result.output);
   } catch (error) {
     if (error.message === "Circuit is open, operation not attempted") {
       console.error("Service appears to be down, try again later");
     } else if (error instanceof MCPError) {
       console.error(`MCP error: ${error.message}`);
     } else {
       console.error(`Unexpected error: ${error}`);
     }
   }
