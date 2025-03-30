import asyncio
import aiohttp
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional, AsyncGenerator, List, Union

from .exceptions import (
    MCPError, MCPAuthError, MCPConnectionError, 
    MCPTimeoutError, MCPProtocolError, MCPExecutionError
)
from .models import (
    ExecutionRequest, ExecutionResult, 
    GenerationRequest, GenerationResult, 
    StreamGenerationChunk, TokenUsage,
    MCPSubmitJobRequest, MCPSubmitJobResponse,
    MCPJobStatusRequest, MCPJobStatusResponse,
    MCPCancelJobRequest, MCPCancelJobResponse,
    MCPCodeExecutionRequest, MCPCodeExecutionResult,
    MCPTextGenerationRequest, MCPTextGenerationResult,
    MCPStreamGenerationChunk, MCPJobStatus
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
            
        # 初始化日志记录器
        self.logger = logging.getLogger("deepexec.async_client")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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

        self.logger.debug("Creating new session with user ID %s", user_id)

        response = await self._send_request(
            "sessions",
            request_data
        )

        self.session_id = response.get("session_id")
        if not self.session_id:
            raise MCPProtocolError("Failed to create session: No session ID returned")

        self.logger.debug("Created new session with ID %s", self.session_id)

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

        self.logger.debug("Executing code with language %s and timeout %s", language, current_timeout)

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

        self.logger.debug("Generating text with model %s and timeout %s", model, current_timeout)

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
        if self.session:
            await self.session.close()
            self.session = None
            self.session_id = None

    # MCP 操作的高级方法
    async def submit_mcp_job(
        self, 
        name: str, 
        job_type: str, 
        data: Dict[str, Any], 
        timeout: Optional[int] = 60, 
        priority: Optional[int] = 0,
        tags: Optional[List[str]] = None
    ) -> MCPSubmitJobResponse:
        """Submit a job to the MCP.

        Args:
            name: The name of the job.
            job_type: The type of the job.
            data: The job data.
            timeout: The job timeout in seconds.
            priority: The job priority.
            tags: Optional tags for the job.

        Returns:
            The job submission response.

        Raises:
            MCPProtocolError: If job submission fails.
        """
        if not self.session_id:
            await self.create_session()

        request = MCPSubmitJobRequest(
            name=name,
            type=job_type,
            data=data,
            timeout=timeout,
            priority=priority,
            tags=tags or []
        )

        self.logger.debug("Submitting MCP job: %s (type: %s)", name, job_type)

        response = await self._send_request(
            "jobs",
            request
        )

        return MCPSubmitJobResponse(**response)

    async def get_mcp_job_status(self, job_id: str) -> MCPJobStatusResponse:
        """Get the status of an MCP job.

        Args:
            job_id: The ID of the job.

        Returns:
            The job status response.

        Raises:
            MCPProtocolError: If status retrieval fails.
        """
        if not self.session_id:
            await self.create_session()

        request = MCPJobStatusRequest(job_id=job_id)

        self.logger.debug("Getting status for MCP job: %s", job_id)

        response = await self._send_request(
            f"jobs/{job_id}/status",
            request
        )

        return MCPJobStatusResponse(**response)

    async def cancel_mcp_job(self, job_id: str, reason: Optional[str] = None) -> MCPCancelJobResponse:
        """Cancel an MCP job.

        Args:
            job_id: The ID of the job to cancel.
            reason: Optional reason for cancellation.

        Returns:
            The job cancellation response.

        Raises:
            MCPProtocolError: If job cancellation fails.
        """
        if not self.session_id:
            await self.create_session()

        request = MCPCancelJobRequest(
            job_id=job_id,
            reason=reason
        )

        self.logger.debug("Cancelling MCP job: %s (reason: %s)", job_id, reason or "Not specified")

        response = await self._send_request(
            f"jobs/{job_id}/cancel",
            request
        )

        return MCPCancelJobResponse(**response)

    async def wait_for_mcp_job_completion(
        self, 
        job_id: str, 
        poll_interval: float = 1.0, 
        max_wait_time: Optional[float] = None
    ) -> MCPJobStatusResponse:
        """Wait for an MCP job to complete.

        Args:
            job_id: The ID of the job to wait for.
            poll_interval: The interval between status checks in seconds.
            max_wait_time: The maximum time to wait in seconds. If None, wait indefinitely.

        Returns:
            The final job status response.

        Raises:
            MCPTimeoutError: If the job does not complete within the specified time.
            MCPProtocolError: If status retrieval fails.
        """
        start_time = time.time()
        self.logger.debug("Waiting for MCP job completion: %s", job_id)

        while True:
            status_response = await self.get_mcp_job_status(job_id)
            
            if status_response.status in [MCPJobStatus.COMPLETED, MCPJobStatus.FAILED, MCPJobStatus.CANCELED]:
                self.logger.debug("MCP job %s completed with status: %s", job_id, status_response.status)
                return status_response
            
            if max_wait_time and (time.time() - start_time) > max_wait_time:
                raise MCPTimeoutError(f"Job {job_id} did not complete within the specified time")
            
            await asyncio.sleep(poll_interval)

    # 更新现有方法以使用新的 MCP 高级方法
    async def submit_job(
        self, 
        name: str, 
        job_type: str, 
        data: Dict[str, Any], 
        timeout: Optional[int] = 60,
        priority: Optional[int] = 0,
        tags: Optional[List[str]] = None) -> MCPSubmitJobResponse:
        """Submit a job to the MCP service.
        
        Args:
            name: Name of the job.
            job_type: Type of the job (e.g., "code_execution", "text_generation").
            data: Job data, structure depends on the job type.
            timeout: Timeout for the job in seconds.
            priority: Priority of the job (higher values mean higher priority).
            tags: Optional tags for the job.
            
        Returns:
            MCPSubmitJobResponse object containing job details.
            
        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        return await self.submit_mcp_job(
            name=name,
            job_type=job_type,
            data=data,
            timeout=timeout,
            priority=priority,
            tags=tags
        )

    async def get_job_status(self, job_id: str) -> MCPJobStatusResponse:
        """Get the status of a job.
        
        Args:
            job_id: ID of the job to check.
            
        Returns:
            MCPJobStatusResponse object containing job status details.
            
        Raises:
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        return await self.get_mcp_job_status(job_id)

    async def cancel_job(self, job_id: str, reason: Optional[str] = None) -> MCPCancelJobResponse:
        """Cancel a job.
        
        Args:
            job_id: ID of the job to cancel.
            reason: Optional reason for cancellation.
            
        Returns:
            MCPCancelJobResponse object containing cancellation details.
            
        Raises:
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        return await self.cancel_mcp_job(job_id, reason)

    async def execute_code_job(self, 
                             code: str, 
                             language: str,
                             environment: Optional[Dict[str, str]] = None,
                             working_directory: Optional[str] = None,
                             timeout: Optional[int] = 30) -> MCPSubmitJobResponse:
        """Submit a code execution job.
        
        Args:
            code: The code to execute.
            language: The programming language of the code.
            environment: Optional environment variables for the execution.
            working_directory: Optional working directory for the execution.
            timeout: Optional timeout for this specific execution in seconds.
            
        Returns:
            MCPSubmitJobResponse object containing job details.
            
        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        # Create and validate the code execution request
        code_request = MCPCodeExecutionRequest(
            code=code,
            language=language,
            environment=environment or {},
            working_directory=working_directory or "/home/user",
            timeout=timeout
        )
        
        # Submit the job
        return await self.submit_mcp_job(
            name=f"code_execution_{language}_{int(time.time())}",
            job_type="code_execution",
            data=code_request.dict(),
            timeout=timeout
        )
    
    async def get_code_execution_result(self, job_id: str) -> MCPCodeExecutionResult:
        """Get the result of a code execution job.
        
        Args:
            job_id: ID of the code execution job.
            
        Returns:
            MCPCodeExecutionResult object containing execution results.
            
        Raises:
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
            MCPExecutionError: If the execution failed or is not complete.
        """
        # Get job status
        status_response = await self.get_mcp_job_status(job_id)
        
        # Check if job is completed
        if status_response.status != MCPJobStatus.COMPLETED:
            if status_response.status == MCPJobStatus.FAILED:
                error_details = status_response.error or {"message": "Unknown error"}
                raise MCPExecutionError(f"Code execution failed: {error_details.get('message')}")
            else:
                raise MCPExecutionError(f"Code execution is not complete. Current status: {status_response.status}")
        
        # Extract result
        result = status_response.result
        if not result:
            raise MCPProtocolError("No result data in completed job")
        
        # Parse and return the execution result
        return MCPCodeExecutionResult(
            output=result.get("output", ""),
            exit_code=result.get("exit_code", 1),
            execution_time=result.get("execution_time", 0),
            memory_usage=result.get("memory_usage", 0),
            metadata=result.get("metadata", {})
        )
    
    async def execute_code_and_wait(self, 
                                  code: str, 
                                  language: str,
                                  environment: Optional[Dict[str, str]] = None,
                                  working_directory: Optional[str] = None,
                                  timeout: Optional[int] = 30,
                                  poll_interval: float = 0.5) -> MCPCodeExecutionResult:
        """Execute code and wait for the result.
        
        This is a convenience method that submits a code execution job,
        polls for its completion, and returns the result.
        
        Args:
            code: The code to execute.
            language: The programming language of the code.
            environment: Optional environment variables for the execution.
            working_directory: Optional working directory for the execution.
            timeout: Optional timeout for this specific execution in seconds.
            poll_interval: Interval between status checks in seconds.
            
        Returns:
            MCPCodeExecutionResult object containing execution results.
            
        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the execution times out.
            MCPProtocolError: If there's an issue with the protocol.
            MCPExecutionError: If code execution fails.
        """
        # Submit the code execution job
        job_response = await self.execute_code_job(
            code=code,
            language=language,
            environment=environment,
            working_directory=working_directory,
            timeout=timeout
        )
        
        job_id = job_response.job_id
        start_time = time.time()
        max_wait_time = timeout or 30
        
        # Poll for job completion
        while time.time() - start_time < max_wait_time:
            try:
                # Try to get the result
                return await self.get_code_execution_result(job_id)
            except MCPExecutionError as e:
                # If job failed, re-raise the exception
                if "failed" in str(e):
                    raise
                # If job is still running, wait and retry
                await asyncio.sleep(poll_interval)
        
        # If we get here, the job timed out
        try:
            # Try to cancel the job
            await self.cancel_job(job_id, reason="Client timeout")
        except Exception:
            # Ignore errors when canceling
            pass
        
        raise MCPTimeoutError(f"Code execution timed out after {max_wait_time} seconds")
    
    async def generate_text_job(self,
                              prompt: str,
                              model: str = "deepseek-v3",
                              max_tokens: int = 1000,
                              temperature: float = 0.7,
                              timeout: Optional[int] = 60) -> MCPSubmitJobResponse:
        """Submit a text generation job.
        
        Args:
            prompt: The input prompt for text generation.
            model: The model to use for generation.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            timeout: Optional timeout for this specific generation in seconds.
            
        Returns:
            MCPSubmitJobResponse object containing job details.
            
        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        # Create and validate the text generation request
        text_request = MCPTextGenerationRequest(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Submit the job
        return await self.submit_mcp_job(
            name=f"text_generation_{model}_{int(time.time())}",
            job_type="text_generation",
            data=text_request.dict(),
            timeout=timeout
        )
    
    async def get_text_generation_result(self, job_id: str) -> MCPTextGenerationResult:
        """Get the result of a text generation job.
        
        Args:
            job_id: ID of the text generation job.
            
        Returns:
            MCPTextGenerationResult object containing generation results.
            
        Raises:
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
            MCPExecutionError: If the generation failed or is not complete.
        """
        # Get job status
        status_response = await self.get_mcp_job_status(job_id)
        
        # Check if job is completed
        if status_response.status != MCPJobStatus.COMPLETED:
            if status_response.status == MCPJobStatus.FAILED:
                error_details = status_response.error or {"message": "Unknown error"}
                raise MCPExecutionError(f"Text generation failed: {error_details.get('message')}")
            else:
                raise MCPExecutionError(f"Text generation is not complete. Current status: {status_response.status}")
        
        # Extract result
        result = status_response.result
        if not result:
            raise MCPProtocolError("No result data in completed job")
        
        # Parse and return the generation result
        return MCPTextGenerationResult(
            text=result.get("text", ""),
            model=result.get("model", "unknown"),
            generation_time=result.get("generation_time", 0),
            usage=result.get("usage", {})
        )
    
    async def generate_text_and_wait(self,
                                   prompt: str,
                                   model: str = "deepseek-v3",
                                   max_tokens: int = 1000,
                                   temperature: float = 0.7,
                                   timeout: Optional[int] = 60,
                                   poll_interval: float = 0.5) -> MCPTextGenerationResult:
        """Generate text and wait for the result.
        
        This is a convenience method that submits a text generation job,
        polls for its completion, and returns the result.
        
        Args:
            prompt: The input prompt for text generation.
            model: The model to use for generation.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            timeout: Optional timeout for this specific generation in seconds.
            poll_interval: Interval between status checks in seconds.
            
        Returns:
            MCPTextGenerationResult object containing generation results.
            
        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the generation times out.
            MCPProtocolError: If there's an issue with the protocol.
            MCPExecutionError: If text generation fails.
        """
        # Submit the text generation job
        job_response = await self.generate_text_job(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout
        )
        
        job_id = job_response.job_id
        start_time = time.time()
        max_wait_time = timeout or 60
        
        # Poll for job completion
        while time.time() - start_time < max_wait_time:
            try:
                # Try to get the result
                return await self.get_text_generation_result(job_id)
            except MCPExecutionError as e:
                # If job failed, re-raise the exception
                if "failed" in str(e):
                    raise
                # If job is still running, wait and retry
                await asyncio.sleep(poll_interval)
        
        # If we get here, the job timed out
        try:
            # Try to cancel the job
            await self.cancel_job(job_id, reason="Client timeout")
        except Exception:
            # Ignore errors when canceling
            pass
        
        raise MCPTimeoutError(f"Text generation timed out after {max_wait_time} seconds")
    
    async def execute_code(self,
                         code: str,
                         language: str,
                         environment: Optional[Dict[str, str]] = None,
                         working_directory: Optional[str] = None,
                         timeout: Optional[float] = None) -> ExecutionResult:
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
        # 使用新的实现
        try:
            result = await self.execute_code_and_wait(
                code=code,
                language=language,
                environment=environment,
                working_directory=working_directory,
                timeout=int(timeout) if timeout else 30
            )
            
            # 转换为旧的结果格式
            return ExecutionResult(
                output=result.output,
                exit_code=result.exit_code,
                execution_time=result.execution_time,
                memory_usage=result.memory_usage,
                metadata=result.metadata
            )
        except Exception as e:
            # 保持原有的异常处理逻辑
            if isinstance(e, MCPTimeoutError):
                # 尝试取消执行
                if hasattr(e, "job_id") and getattr(e, "job_id"):
                    try:
                        await self.cancel_job(getattr(e, "job_id"), reason="Client timeout")
                    except Exception:
                        # 忽略取消时的错误
                        pass
            raise
