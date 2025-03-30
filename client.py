import time
import requests
import json
import uuid
from typing import Dict, Any, Optional, List, Union, Generator

from .exceptions import (
    MCPError, MCPAuthError, MCPConnectionError, 
    MCPTimeoutError, MCPProtocolError, MCPExecutionError
)
from .models import (
    ExecutionRequest, ExecutionResult, 
    GenerationRequest, GenerationResult, 
    StreamGenerationChunk, TokenUsage,
    # MCP 模型导入
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


class DeepExecClient:
    """Synchronous client for interacting with the DeepExec service."""

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
        """Initialize the synchronous DeepExec client.

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
            
        # 创建会话
        self.session = requests.Session()
        self.session_id = str(uuid.uuid4())
    
    def __enter__(self):
        """Context manager entry point."""
        if self.session is None:
            self.session = requests.Session()
            self.session_id = str(uuid.uuid4())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        if self.session:
            self.session.close()
            self.session = None
    
    def _send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the DeepExec service.
        
        Args:
            endpoint: The API endpoint to call.
            data: The request data.
            
        Returns:
            The response data.
            
        Raises:
            MCPAuthError: If authentication fails.
            MCPConnectionError: If connection to the server fails.
            MCPTimeoutError: If the request times out.
            MCPProtocolError: If there's an issue with the protocol.
        """
        url = f"{self.endpoint}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    url,
                    json=data,
                    headers=self._headers,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
                
                if response.status_code == 401:
                    raise MCPAuthError("Authentication failed. Check your API keys.")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise MCPTimeoutError(f"Request timed out after {self.timeout} seconds")
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries - 1:
                    raise MCPConnectionError("Failed to connect to the server")
            except requests.exceptions.HTTPError as e:
                if attempt == self.max_retries - 1:
                    if e.response.status_code == 400:
                        raise MCPProtocolError(f"Protocol error: {e.response.text}")
                    elif e.response.status_code == 500:
                        raise MCPExecutionError(f"Server error: {e.response.text}")
                    else:
                        raise MCPError(f"HTTP error: {e.response.status_code}")
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise MCPError(f"Unexpected error: {str(e)}")
            
            # 指数退避重试
            time.sleep(self.retry_delay * (2 ** attempt))
    
    # MCP 协议具体操作方法
    
    def submit_job(self, 
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
        # Create and validate the request using Pydantic model
        request = MCPSubmitJobRequest(
            name=name,
            type=job_type,
            data=data,
            timeout=timeout,
            priority=priority,
            tags=tags or []
        )
        
        # Send the request
        response = self._send_request(
            "jobs",
            request.dict()
        )
        
        # Parse and return the response
        return MCPSubmitJobResponse(
            job_id=response.get("job_id"),
            status=MCPJobStatus(response.get("status")),
            created_at=response.get("created_at"),
            estimated_time=response.get("estimated_time")
        )
    
    def get_job_status(self, job_id: str) -> MCPJobStatusResponse:
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
        # Create and validate the request using Pydantic model
        request = MCPJobStatusRequest(job_id=job_id)
        
        # Send the request
        response = self._send_request(
            f"jobs/{job_id}/status",
            {}
        )
        
        # Parse and return the response
        return MCPJobStatusResponse(
            job_id=response.get("job_id"),
            status=MCPJobStatus(response.get("status")),
            progress=response.get("progress"),
            created_at=response.get("created_at"),
            started_at=response.get("started_at"),
            completed_at=response.get("completed_at"),
            result=response.get("result"),
            error=response.get("error")
        )
    
    def cancel_job(self, job_id: str, reason: Optional[str] = None) -> MCPCancelJobResponse:
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
        # Create and validate the request using Pydantic model
        request = MCPCancelJobRequest(job_id=job_id, reason=reason)
        
        # Send the request
        response = self._send_request(
            f"jobs/{job_id}/cancel",
            request.dict()
        )
        
        # Parse and return the response
        return MCPCancelJobResponse(
            job_id=response.get("job_id"),
            status=MCPJobStatus(response.get("status")),
            canceled_at=response.get("canceled_at")
        )
    
    def execute_code_job(self, 
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
        return self.submit_job(
            name=f"code_execution_{language}_{int(time.time())}",
            job_type="code_execution",
            data=code_request.dict(),
            timeout=timeout
        )
    
    def get_code_execution_result(self, job_id: str) -> MCPCodeExecutionResult:
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
        status_response = self.get_job_status(job_id)
        
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
    
    def execute_code_and_wait(self, 
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
        job_response = self.execute_code_job(
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
                return self.get_code_execution_result(job_id)
            except MCPExecutionError as e:
                # If job failed, re-raise the exception
                if "failed" in str(e):
                    raise
                # If job is still running, wait and retry
                time.sleep(poll_interval)
        
        # If we get here, the job timed out
        try:
            # Try to cancel the job
            self.cancel_job(job_id, reason="Client timeout")
        except Exception:
            # Ignore errors when canceling
            pass
        
        raise MCPTimeoutError(f"Code execution timed out after {max_wait_time} seconds")
    
    def generate_text_job(self,
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
        return self.submit_job(
            name=f"text_generation_{model}_{int(time.time())}",
            job_type="text_generation",
            data=text_request.dict(),
            timeout=timeout
        )
    
    def get_text_generation_result(self, job_id: str) -> MCPTextGenerationResult:
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
        status_response = self.get_job_status(job_id)
        
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
    
    def generate_text_and_wait(self,
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
        job_response = self.generate_text_job(
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
                return self.get_text_generation_result(job_id)
            except MCPExecutionError as e:
                # If job failed, re-raise the exception
                if "failed" in str(e):
                    raise
                # If job is still running, wait and retry
                time.sleep(poll_interval)
        
        # If we get here, the job timed out
        try:
            # Try to cancel the job
            self.cancel_job(job_id, reason="Client timeout")
        except Exception:
            # Ignore errors when canceling
            pass
        
        raise MCPTimeoutError(f"Text generation timed out after {max_wait_time} seconds")
    
    # 为了保持向后兼容性，我们保留原有的方法，但在内部使用新的实现
    
    def execute_code(self,
                   code: str,
                   language: str,
                   environment: Optional[Dict[str, str]] = None,
                   working_directory: Optional[str] = None,
                   timeout: Optional[float] = None) -> ExecutionResult:
        """Execute code synchronously.

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
            result = self.execute_code_and_wait(
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
                        self.cancel_job(getattr(e, "job_id"), reason="Client timeout")
                    except Exception:
                        # 忽略取消时的错误
                        pass
            raise
    
    def generate_text(self,
                     prompt: str,
                     model: str = "deepseek-v3",
                     max_tokens: int = 1000,
                     temperature: float = 0.7,
                     timeout: Optional[float] = None) -> GenerationResult:
        """Generate text synchronously.

        Args:
            prompt: The input prompt for text generation.
            model: The model to use for generation.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            timeout: Optional timeout for this specific generation.

        Returns:
            GenerationResult object containing the generated text and token usage.

        Raises:
            MCPProtocolError: If there's an issue with the protocol.
            MCPExecutionError: If text generation fails.
            MCPTimeoutError: If the generation times out.
            MCPConnectionError: If connection to the server fails.
        """
        # 使用新的实现
        try:
            result = self.generate_text_and_wait(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=int(timeout) if timeout else 60
            )
            
            # 转换为旧的结果格式
            return GenerationResult(
                text=result.text,
                model=result.model,
                usage=TokenUsage(**result.usage) if result.usage else TokenUsage(),
                generation_time=result.generation_time
            )
        except Exception as e:
            # 保持原有的异常处理逻辑
            if isinstance(e, MCPTimeoutError):
                # 尝试取消执行
                if hasattr(e, "job_id") and getattr(e, "job_id"):
                    try:
                        self.cancel_job(getattr(e, "job_id"), reason="Client timeout")
                    except Exception:
                        # 忽略取消时的错误
                        pass
            raise
    
    def close(self) -> None:
        """Close the client connection."""
        if self.session:
            self.session.close()
            self.session = None
