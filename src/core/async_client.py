import asyncio
import aiohttp
import json
import time
import uuid
from typing import Dict, Any, Optional, AsyncGenerator, List

from .exceptions import (
    MCPError, MCPAuthError, MCPConnectionError, 
    MCPTimeoutError, MCPProtocolError, MCPExecutionError
)
from .models import (
    ExecutionRequest, ExecutionResult, 
    GenerationRequest, GenerationResult, 
    StreamGenerationChunk, TokenUsage
)
from .protocols.mcp import (
    build_request_message, parse_response_message,
    MCPRequestType, MCPResponseType,
    CreateSessionInput, CodeExecutionInput, TextGenerationInput,
    TextGenerationMetadata
)


class DeepExecAsyncClient:
    """Asynchronous client for interacting with the DeepExec service."""

    def __init__(
        self,
        endpoint: str = "https://api.deepexec.com/v1",
        deepseek_key: Optional[str] = None,
        e2b_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = True,
    ):
        """Initialize the asynchronous DeepExec client.

        Args:
            endpoint: The API endpoint URL.
            deepseek_key: The DeepSeek API key for authentication.
            e2b_key: The E2B API key for code execution.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            retry_delay: Base delay between retries in seconds.
            verify_ssl: Whether to verify SSL certificates.
        """
        self.endpoint = endpoint
        self.deepseek_key = deepseek_key
        self.e2b_key = e2b_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        
        self.session = None
        self.session_id = None
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if deepseek_key:
            self._headers["X-DeepSeek-Key"] = deepseek_key
        if e2b_key:
            self._headers["X-E2B-Key"] = e2b_key

    async def __aenter__(self):
        """Async context manager entry."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            self.session = None
        self.session_id = None

    async def create_session(self, user_id: str) -> str:
        """Create a new session with the DeepExec service.

        Args:
            user_id: Identifier for the user creating the session.

        Returns:
            The session ID.

        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
        """
        if not self.deepseek_key or not self.e2b_key:
            raise MCPAuthError("Both DeepSeek and E2B API keys are required")

        if self.session is None:
            await self.__aenter__()

        request_data = build_request_message(
            type=MCPRequestType.CREATE_SESSION,
            session_id=None,  # No session ID yet
            input=CreateSessionInput(user_id=user_id),
            metadata={}
        )

        response = await self._send_request(
            "sessions",
            request_data
        )

        self.session_id = response.get("session_id")
        if not self.session_id:
            raise MCPProtocolError("Failed to create session: No session ID returned")

        return self.session_id

    async def execute_code(
        self,
        code: str,
        language: str,
        environment: Optional[Dict[str, str]] = None,
        working_directory: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """Execute code asynchronously.

        Args:
            code: The code to execute.
            language: The programming language of the code.
            environment: Optional environment variables for the execution.
            working_directory: Optional working directory for the execution.
            timeout: Optional timeout for this specific execution.

        Returns:
            ExecutionResult object containing the execution results.

        Raises:
            MCPProtocolError: If there's an issue with the protocol.
            MCPExecutionError: If code execution fails.
            MCPTimeoutError: If the execution times out.
            MCPConnectionError: If connection to the server fails.
        """
        if not self.session_id:
            raise MCPProtocolError("No active session. Call create_session() first.")

        if not code.strip():
            raise MCPProtocolError("Code cannot be empty")

        # Validate the request using Pydantic model
        request = ExecutionRequest(
            code=code,
            language=language,
            environment=environment or {},
            working_directory=working_directory or "/home/user"
        )

        request_data = build_request_message(
            type=MCPRequestType.CODE_EXECUTION,
            session_id=self.session_id,
            input=CodeExecutionInput(
                code=request.code,
                language=request.language,
                environment=request.environment,
                working_directory=request.working_directory
            ),
            metadata={}
        )

        # Use the provided timeout if specified, otherwise use the client's default
        current_timeout = timeout or self.timeout

        try:
            response = await self._send_request(
                "execute",
                request_data,
                timeout=current_timeout
            )

            # Parse the execution result
            result = ExecutionResult(
                output=response.get("output", ""),
                exit_code=response.get("exitCode", 1),
                execution_time=response.get("executionTime", 0),
                memory_usage=response.get("memoryUsage", 0),
                metadata=response.get("metadata", {})
            )
            return result

        except MCPTimeoutError:
            # Attempt to cancel the execution if it timed out
            if self.session_id:
                try:
                    await self._cancel_execution(self.session_id)
                except Exception:
                    # Ignore errors when canceling, as we're already handling a timeout
                    pass
            raise

    async def generate_text(
        self,
        prompt: str,
        model: str = "deepseek-v3",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: Optional[float] = None
    ) -> GenerationResult:
        """Generate text asynchronously using the DeepSeek model.

        Args:
            prompt: The input prompt for text generation.
            model: The model to use for generation.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            timeout: Optional timeout for this specific generation.

        Returns:
            GenerationResult object containing the generated text and metadata.

        Raises:
            MCPProtocolError: If there's an issue with the protocol.
            MCPTimeoutError: If the generation times out.
            MCPConnectionError: If connection to the server fails.
        """
        if not self.session_id:
            raise MCPProtocolError("No active session. Call create_session() first.")

        if not prompt.strip():
            raise MCPProtocolError("Prompt cannot be empty")

        # Validate the request using Pydantic model
        request = GenerationRequest(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )

        request_data = build_request_message(
            type=MCPRequestType.TEXT_GENERATION,
            session_id=self.session_id,
            input=TextGenerationInput(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ),
            metadata=TextGenerationMetadata(model=request.model)
        )

        # Use the provided timeout if specified, otherwise use the client's default
        current_timeout = timeout or self.timeout

        response = await self._send_request(
            "generate",
            request_data,
            timeout=current_timeout
        )

        # Parse the generation result
        result = GenerationResult(
            text=response.get("text", ""),
            model=response.get("model", model),
            generation_time=response.get("generationTime", 0),
            usage=response.get("usage", {
                "promptTokens": 0,
                "completionTokens": 0,
                "totalTokens": 0
            })
        )
        return result

    async def stream_generate_text(
        self,
        prompt: str,
        model: str = "deepseek-v3",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate text with streaming response.

        Args:
            prompt: The input prompt for text generation.
            model: The model to use for generation.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0-1.0).

        Yields:
            Dictionary containing text chunks and completion status.

        Raises:
            MCPProtocolError: If there's an issue with the protocol.
            MCPConnectionError: If connection to the server fails.
        """
        if not self.session_id:
            raise MCPProtocolError("No active session. Call create_session() first.")

        if not prompt.strip():
            raise MCPProtocolError("Prompt cannot be empty")

        # Validate the request using Pydantic model
        request = GenerationRequest(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )

        request_data = build_request_message(
            type=MCPRequestType.TEXT_GENERATION_STREAM,
            session_id=self.session_id,
            input=TextGenerationInput(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ),
            metadata=TextGenerationMetadata(model=request.model)
        )

        if self.session is None:
            await self.__aenter__()

        url = f"{self.endpoint}/generate/stream"

        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self._handle_error_response(response.status, error_text)

                # Process the streaming response
                async for line in response.content.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            yield {
                                "text": data.get("text", ""),
                                "done": data.get("done", False)
                            }

        except asyncio.TimeoutError:
            raise MCPTimeoutError(f"Request timed out after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection error: {str(e)}")

    async def _send_request(
        self,
        endpoint_path: str,
        data: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Send a request to the DeepExec service with retry logic.

        Args:
            endpoint_path: The API endpoint path.
            data: The request data.
            timeout: Optional timeout for this specific request.

        Returns:
            The parsed response data.

        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        if self.session is None:
            await self.__aenter__()

        url = f"{self.endpoint}/{endpoint_path}"
        current_timeout = timeout or self.timeout

        # Add request ID if not present
        if "request_id" not in data:
            data["request_id"] = str(uuid.uuid4())

        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                # Set a timeout for this specific request
                timeout_obj = aiohttp.ClientTimeout(total=current_timeout)
                
                async with self.session.post(url, json=data, timeout=timeout_obj) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return parse_response_message(response_data)
                    else:
                        error_text = await response.text()
                        self._handle_error_response(response.status, error_text)

            except asyncio.TimeoutError:
                last_error = MCPTimeoutError(f"Request timed out after {current_timeout} seconds")
            except aiohttp.ClientError as e:
                last_error = MCPConnectionError(f"Connection error: {str(e)}")
            except MCPAuthError:
                # Don't retry auth errors
                raise
            except MCPError as e:
                last_error = e

            # Increment retry counter and delay before retrying
            retries += 1
            if retries <= self.max_retries:
                # Exponential backoff with jitter
                delay = self.retry_delay * (2 ** (retries - 1)) * (0.5 + 0.5 * (time.time() % 1))
                await asyncio.sleep(delay)

        # If we've exhausted all retries, raise the last error
        if last_error:
            raise last_error
        else:
            raise MCPConnectionError("Failed to connect to the server after multiple retries")

    def _handle_error_response(self, status_code: int, error_text: str) -> None:
        """Handle error responses from the server.

        Args:
            status_code: The HTTP status code.
            error_text: The error response text.

        Raises:
            MCPAuthError: If authentication fails (401, 403).
            MCPConnectionError: If there's a server error (5xx).
            MCPProtocolError: For other error responses.
        """
        error_data = {}
        try:
            error_data = json.loads(error_text)
        except json.JSONDecodeError:
            # If not JSON, use the raw text
            error_message = error_text
        else:
            error_message = error_data.get("error", {}).get("message", error_text)

        if status_code == 401 or status_code == 403:
            raise MCPAuthError(f"Authentication error: {error_message}")
        elif status_code == 429:
            raise MCPAuthError(f"Rate limit exceeded: {error_message}")
        elif 500 <= status_code < 600:
            raise MCPConnectionError(f"Server error ({status_code}): {error_message}")
        else:
            raise MCPProtocolError(f"Protocol error ({status_code}): {error_message}")

    async def _cancel_execution(self, session_id: str) -> None:
        """Attempt to cancel an ongoing execution.

        Args:
            session_id: The session ID of the execution to cancel.

        Raises:
            MCPConnectionError: If connection to the server fails.
            MCPProtocolError: If there's an issue with the protocol.
        """
        if self.session is None:
            await self.__aenter__()

        request_data = build_request_message(
            type=MCPRequestType.CANCEL_EXECUTION,
            session_id=session_id,
            input={},
            metadata={}
        )

        url = f"{self.endpoint}/cancel"

        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status != 200:
                    # Just log the error, don't raise
                    pass
        except Exception:
            # Ignore any errors when canceling
            pass

    async def close(self) -> None:
        """Close the client connection."""
        await self.__aexit__(None, None, None)
