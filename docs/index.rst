DeepExec SDK Documentation
==========================

Welcome to the DeepExec SDK documentation. This SDK provides a powerful interface for executing code and generating text using DeepSeek's AI models and E2B's secure execution environment.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   concepts/architecture
   concepts/mcp_protocol
   concepts/security_model
   concepts/error_handling
   api/index
   testing/index
   async/index
   logging/index

Getting Started
--------------

Installation
~~~~~~~~~~~

.. code-block:: bash

   npm install deepexec-sdk

Basic Usage
~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient } from 'deepexec-sdk';

   // Create a client
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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
