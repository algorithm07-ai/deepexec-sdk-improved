Configuration System
===================

The configuration system in the DeepExec SDK provides a flexible way to configure the client from multiple sources, with a clear priority order.

Class Definition
---------------

.. js:class:: ClientConfig

   Manages configuration settings for the DeepExec client.

   .. js:constructor:: constructor(options)

      Creates a new configuration instance.

      :param options: Configuration options
      :type options: ClientConfigOptions
      :throws: :js:class:`MCPConfigError` - For invalid configuration values

   .. js:method:: getEndpoint()

      Gets the configured API endpoint.

      :returns: API endpoint URL
      :rtype: string

   .. js:method:: getTimeout()

      Gets the configured timeout value.

      :returns: Timeout in seconds
      :rtype: number

   .. js:method:: getMaxRetries()

      Gets the configured maximum retry count.

      :returns: Maximum number of retries
      :rtype: number

   .. js:method:: getAuthToken()

      Gets the configured authentication token.

      :returns: Authentication token
      :rtype: string

   .. js:method:: getSecurityOptions()

      Gets the configured security options.

      :returns: Security options object
      :rtype: SecurityOptions

Interfaces
----------

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

Configuration Sources
--------------------

The configuration system loads settings from multiple sources in the following order of precedence (highest to lowest):

1. **Constructor Arguments**: Values passed directly to the `ClientConfig` constructor
2. **Environment Variables**: Variables with the `DEEPEXEC_` prefix
3. **Configuration File**: Settings in `.deepexecrc` file
4. **Default Values**: Built-in defaults

Environment Variables
~~~~~~~~~~~~~~~~~~~~

The following environment variables are supported:

- `DEEPEXEC_ENDPOINT`: API endpoint URL
- `DEEPEXEC_TIMEOUT`: Operation timeout in seconds
- `DEEPEXEC_MAX_RETRIES`: Maximum retry attempts
- `DEEPEXEC_DEEPSEEK_KEY`: DeepSeek API key
- `DEEPEXEC_E2B_KEY`: E2B API key
- `DEEPEXEC_VERIFY_SSL`: Whether to verify SSL certificates ("true" or "false")
- `DEEPEXEC_MAX_CODE_LENGTH`: Maximum allowed code length
- `DEEPEXEC_ALLOWED_LANGUAGES`: Comma-separated list of allowed languages
- `DEEPEXEC_BLOCKED_KEYWORDS`: Comma-separated list of blocked keywords

Configuration File
~~~~~~~~~~~~~~~~

The SDK looks for a `.deepexecrc` file in the following locations (in order):

1. Current working directory
2. User's home directory

The configuration file should be in JSON format:

.. code-block:: json

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

Default Values
~~~~~~~~~~~~

If a configuration value is not specified in any of the above sources, the following defaults are used:

- `endpoint`: "https://api.deepexec.com/v1"
- `timeout`: 30.0 seconds
- `maxRetries`: 3
- `verifySSL`: true
- `securityOptions.maxCodeLength`: 10000
- `securityOptions.allowedLanguages`: ["python", "javascript", "typescript", "bash", "ruby"]
- `securityOptions.blockedKeywords`: ["rm -rf", "System.exit", "os.system", "exec", "eval"]

Examples
--------

Basic Configuration
~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient } from 'deepexec-sdk';

   // Create client with basic configuration
   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_...",
     timeout: 60.0  // 60 second timeout
   });

Advanced Security Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import { DeepExecClient } from 'deepexec-sdk';

   // Create client with advanced security configuration
   const client = new DeepExecClient({
     deepseekKey: "sk-...",
     e2bKey: "e2b_...",
     securityOptions: {
       maxCodeLength: 5000,
       allowedLanguages: ['python', 'javascript'],
       blockedKeywords: [
         'rm -rf', 
         'System.exit', 
         'os.system',
         'subprocess',
         'exec',
         'eval'
       ]
     }
   });

Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

   // Set environment variables before importing
   process.env.DEEPEXEC_DEEPSEEK_KEY = "sk-...";
   process.env.DEEPEXEC_E2B_KEY = "e2b_...";
   process.env.DEEPEXEC_TIMEOUT = "45.0";
   process.env.DEEPEXEC_ALLOWED_LANGUAGES = "python,javascript";

   import { DeepExecClient } from 'deepexec-sdk';

   // Create client with no explicit configuration
   // It will use the environment variables
   const client = new DeepExecClient();
