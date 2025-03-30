"""MCP (Model Communication Protocol) implementation.

This module contains the implementation of the MCP protocol, including
Pydantic models for requests and responses, and utility functions for
working with the protocol.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator

# Protocol version constants
PROTOCOL_VERSION = "2024.1"
SUPPORTED_VERSIONS = ["2024.1"]


class MCPRequestType(str, Enum):
    """Enum for MCP request types."""
    CREATE_SESSION = "create_session"
    CODE_EXECUTION = "code_execution"
    TEXT_GENERATION = "text_generation"
    TEXT_GENERATION_STREAM = "text_generation_stream"
    CANCEL_EXECUTION = "cancel_execution"


class MCPResponseType(str, Enum):
    """Enum for MCP response types."""
    SESSION_CREATED = "session_created"
    CODE_EXECUTION_RESULT = "code_execution_result"
    TEXT_GENERATION_RESULT = "text_generation_result"
    EXECUTION_CANCELED = "execution_canceled"


class MCPStatus(str, Enum):
    """Enum for MCP response status."""
    SUCCESS = "success"
    ERROR = "error"


class MCPErrorCode(str, Enum):
    """Enum for MCP error codes."""
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    EXECUTION_ERROR = "execution_error"
    GENERATION_ERROR = "generation_error"
    TIMEOUT_ERROR = "timeout_error"
    SERVER_ERROR = "server_error"
    UNKNOWN_ERROR = "unknown_error"


# Base models for requests and responses
class MCPBaseMessage(BaseModel):
    """Base model for all MCP messages."""
    protocol_version: str = PROTOCOL_VERSION

    @validator('protocol_version')
    def validate_protocol_version(cls, v):
        """Validate that the protocol version is supported."""
        if v not in SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported protocol version: {v}")
        return v


class MCPRequestBase(MCPBaseMessage):
    """Base model for all MCP requests."""
    type: str
    session_id: Optional[str] = None
    input: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None


class MCPResponseBase(MCPBaseMessage):
    """Base model for all MCP responses."""
    type: str
    session_id: Optional[str] = None
    status: MCPStatus = MCPStatus.SUCCESS


class MCPErrorDetail(BaseModel):
    """Model for MCP error details."""
    code: MCPErrorCode = MCPErrorCode.UNKNOWN_ERROR
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class MCPErrorResponse(MCPResponseBase):
    """Model for MCP error responses."""
    status: MCPStatus = MCPStatus.ERROR
    error: MCPErrorDetail


# Session models
class CreateSessionInput(BaseModel):
    """Input model for session creation."""
    user_id: str


class CreateSessionRequest(MCPRequestBase):
    """Request model for session creation."""
    type: str = MCPRequestType.CREATE_SESSION
    input: CreateSessionInput


class SessionCreatedResponse(MCPResponseBase):
    """Response model for session creation."""
    type: str = MCPResponseType.SESSION_CREATED
    session_id: str


# Code execution models
class CodeExecutionInput(BaseModel):
    """Input model for code execution."""
    code: str
    language: str
    environment: Dict[str, str] = Field(default_factory=dict)
    working_directory: str = "/home/user"

    @validator('code')
    def code_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v

    @validator('language')
    def language_must_be_valid(cls, v):
        valid_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", "csharp", 
            "go", "rust", "ruby", "php", "bash", "powershell"
        ]
        if v.lower() not in valid_languages:
            raise ValueError(f"Unsupported language: {v}. Supported languages: {', '.join(valid_languages)}")
        return v.lower()


class CodeExecutionRequest(MCPRequestBase):
    """Request model for code execution."""
    type: str = MCPRequestType.CODE_EXECUTION
    session_id: str
    input: CodeExecutionInput


class ExecutionResultOutput(BaseModel):
    """Model for execution result output."""
    output: str
    exit_code: int = 0
    execution_time: int = 0  # in milliseconds
    memory_usage: int = 0  # in MB


class CodeExecutionOutput(BaseModel):
    """Output model for code execution."""
    execution_result: ExecutionResultOutput


class CodeExecutionResultResponse(MCPResponseBase):
    """Response model for code execution."""
    type: str = MCPResponseType.CODE_EXECUTION_RESULT
    session_id: str
    output: CodeExecutionOutput


# Text generation models
class TextGenerationInput(BaseModel):
    """Input model for text generation."""
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7

    @validator('prompt')
    def prompt_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v

    @validator('temperature')
    def temperature_must_be_valid(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperature must be between 0.0 and 1.0')
        return v

    @validator('max_tokens')
    def max_tokens_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('max_tokens must be positive')
        return v


class TextGenerationMetadata(BaseModel):
    """Metadata model for text generation."""
    model: str = "deepseek-v3"


class TextGenerationRequest(MCPRequestBase):
    """Request model for text generation."""
    type: str = MCPRequestType.TEXT_GENERATION
    session_id: str
    input: TextGenerationInput
    metadata: TextGenerationMetadata


class TextGenerationStreamRequest(MCPRequestBase):
    """Request model for streaming text generation."""
    type: str = MCPRequestType.TEXT_GENERATION_STREAM
    session_id: str
    input: TextGenerationInput
    metadata: TextGenerationMetadata


class TokenUsage(BaseModel):
    """Model for token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class TextGenerationOutput(BaseModel):
    """Output model for text generation."""
    text: str


class TextGenerationResultMetadata(BaseModel):
    """Metadata model for text generation result."""
    model: str
    generation_time: int = 0  # in milliseconds
    usage: TokenUsage


class TextGenerationResultResponse(MCPResponseBase):
    """Response model for text generation."""
    type: str = MCPResponseType.TEXT_GENERATION_RESULT
    session_id: str
    output: TextGenerationOutput
    metadata: TextGenerationResultMetadata


class TextGenerationStreamChunk(BaseModel):
    """Model for streaming text generation chunks."""
    text: str
    done: bool = False


# Cancel execution models
class CancelExecutionRequest(MCPRequestBase):
    """Request model for canceling execution."""
    type: str = MCPRequestType.CANCEL_EXECUTION
    session_id: str


class ExecutionCanceledResponse(MCPResponseBase):
    """Response model for execution cancellation."""
    type: str = MCPResponseType.EXECUTION_CANCELED
    session_id: str


# Utility functions for working with the protocol
def build_request_message(type: str, session_id: Optional[str], input: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Build a request message according to the MCP protocol.

    Args:
        type: The request type (e.g., "code_execution", "text_generation").
        session_id: The session ID (can be None for session creation).
        input: The input data for the request.
        metadata: Additional metadata for the request.

    Returns:
        A dictionary containing the formatted request message.
    """
    message = {
        "protocol_version": PROTOCOL_VERSION,
        "type": type,
        "input": input,
        "metadata": metadata
    }

    # Add session_id if provided
    if session_id:
        message["session_id"] = session_id

    return message


def parse_response_message(response: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a response message according to the MCP protocol.

    Args:
        response: The response message from the server.

    Returns:
        A dictionary containing the parsed response data.

    Raises:
        MCPProtocolError: If the response contains an error or is invalid.
    """
    from ..exceptions import MCPProtocolError
    
    # Validate protocol version
    protocol_version = response.get("protocol_version")
    if protocol_version not in SUPPORTED_VERSIONS:
        raise MCPProtocolError(f"Unsupported protocol version: {protocol_version}")

    # Check for error response
    if response.get("status") == "error" or "error" in response:
        error = response.get("error", {})
        error_code = error.get("code", "unknown_error")
        error_message = error.get("message", "Unknown error occurred")
        error_details = error.get("details", {})
        
        raise MCPProtocolError(
            f"Error ({error_code}): {error_message}", 
            details=error_details
        )

    # Parse response based on type
    response_type = response.get("type")
    
    if response_type == MCPResponseType.CODE_EXECUTION_RESULT:
        output = response.get("output", {}).get("execution_result", {})
        return {
            "output": output.get("output", ""),
            "exitCode": output.get("exit_code", 1),
            "executionTime": output.get("execution_time", 0),
            "memoryUsage": output.get("memory_usage", 0),
            "metadata": response.get("metadata", {})
        }
    
    elif response_type == MCPResponseType.TEXT_GENERATION_RESULT:
        output = response.get("output", {})
        metadata = response.get("metadata", {})
        usage = metadata.get("usage", {})
        
        return {
            "text": output.get("text", ""),
            "model": metadata.get("model", "unknown"),
            "generationTime": metadata.get("generation_time", 0),
            "usage": {
                "promptTokens": usage.get("prompt_tokens", 0),
                "completionTokens": usage.get("completion_tokens", 0),
                "totalTokens": usage.get("total_tokens", 0)
            }
        }
    
    elif response_type == MCPResponseType.SESSION_CREATED:
        return {
            "session_id": response.get("session_id", "")
        }
    
    else:
        # For other response types, return the raw response
        return response
