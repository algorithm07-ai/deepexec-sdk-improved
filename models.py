from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


# MCP 协议基础模型
class MCPProtocolVersion(str, Enum):
    """MCP 协议版本"""
    V2024_1 = "2024.1"


class MCPJobStatus(str, Enum):
    """MCP 作业状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMEOUT = "timeout"


# 具体 MCP 请求模型
class MCPSubmitJobRequest(BaseModel):
    """提交 MCP 作业请求模型"""
    name: str
    type: str  # 作业类型: code_execution, text_generation 等
    data: Dict[str, Any]  # 作业数据，根据类型不同而变化
    timeout: Optional[int] = 60  # 超时时间（秒）
    priority: Optional[int] = 0  # 作业优先级
    tags: Optional[List[str]] = Field(default_factory=list)  # 作业标签
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Job name cannot be empty')
        return v
    
    @validator('type')
    def type_must_be_valid(cls, v):
        valid_types = ["code_execution", "text_generation", "text_generation_stream"]
        if v not in valid_types:
            raise ValueError(f"Invalid job type: {v}. Valid types: {', '.join(valid_types)}")
        return v


class MCPSubmitJobResponse(BaseModel):
    """提交 MCP 作业响应模型"""
    job_id: str
    status: MCPJobStatus
    created_at: str  # ISO 格式时间戳
    estimated_time: Optional[int] = None  # 预计完成时间（秒）


class MCPJobStatusRequest(BaseModel):
    """查询 MCP 作业状态请求模型"""
    job_id: str


class MCPJobStatusResponse(BaseModel):
    """查询 MCP 作业状态响应模型"""
    job_id: str
    status: MCPJobStatus
    progress: Optional[float] = None  # 进度百分比 (0-100)
    created_at: str  # ISO 格式时间戳
    started_at: Optional[str] = None  # ISO 格式时间戳
    completed_at: Optional[str] = None  # ISO 格式时间戳
    result: Optional[Dict[str, Any]] = None  # 作业结果，仅当状态为 COMPLETED 时存在
    error: Optional[Dict[str, Any]] = None  # 错误信息，仅当状态为 FAILED 时存在


class MCPCancelJobRequest(BaseModel):
    """取消 MCP 作业请求模型"""
    job_id: str
    reason: Optional[str] = None


class MCPCancelJobResponse(BaseModel):
    """取消 MCP 作业响应模型"""
    job_id: str
    status: MCPJobStatus  # 应为 CANCELED
    canceled_at: str  # ISO 格式时间戳


class MCPErrorDetail(BaseModel):
    """MCP 错误详情模型"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# 代码执行特定模型
class MCPCodeExecutionRequest(BaseModel):
    """代码执行请求模型"""
    code: str
    language: str
    environment: Dict[str, str] = Field(default_factory=dict)
    working_directory: str = "/home/user"
    timeout: Optional[int] = 30
    
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


class MCPCodeExecutionResult(BaseModel):
    """代码执行结果模型"""
    output: str
    exit_code: int
    execution_time: int  # 毫秒
    memory_usage: int  # MB
    metadata: Dict[str, Any] = Field(default_factory=dict)


# 文本生成特定模型
class MCPTextGenerationRequest(BaseModel):
    """文本生成请求模型"""
    prompt: str
    model: str = "deepseek-v3"
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


class MCPTokenUsage(BaseModel):
    """Token 使用统计模型"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class MCPTextGenerationResult(BaseModel):
    """文本生成结果模型"""
    text: str
    model: str
    generation_time: int = 0  # 毫秒
    usage: MCPTokenUsage = Field(default_factory=MCPTokenUsage)


class MCPStreamGenerationChunk(BaseModel):
    """流式文本生成块模型"""
    text: str
    done: bool = False


# 保留原有模型，但标记为兼容性用途
class ExecutionRequest(BaseModel):
    """Model for code execution requests (Legacy)."""
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
        # This is a basic validation that can be extended with a list of supported languages
        valid_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", "csharp", 
            "go", "rust", "ruby", "php", "bash", "powershell"
        ]
        if v.lower() not in valid_languages:
            raise ValueError(f"Unsupported language: {v}. Supported languages: {', '.join(valid_languages)}")
        return v.lower()


class ExecutionResult(BaseModel):
    """Model for code execution results (Legacy)."""
    output: str
    exit_code: int
    execution_time: int  # in milliseconds
    memory_usage: int  # in MB
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    """Model for token usage statistics (Legacy)."""
    prompt_tokens: int = Field(0, alias="promptTokens")
    completion_tokens: int = Field(0, alias="completionTokens")
    total_tokens: int = Field(0, alias="totalTokens")

    class Config:
        allow_population_by_field_name = True


class GenerationRequest(BaseModel):
    """Model for text generation requests (Legacy)."""
    prompt: str
    model: str = "deepseek-v3"
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


class GenerationResult(BaseModel):
    """Model for text generation results (Legacy)."""
    text: str
    model: str
    generation_time: int = Field(0, alias="generationTime")  # in milliseconds
    usage: TokenUsage

    class Config:
        allow_population_by_field_name = True


class StreamGenerationChunk(BaseModel):
    """Model for streaming text generation chunks (Legacy)."""
    text: str
    done: bool


class SecurityOptions(BaseModel):
    """Model for security configuration options."""
    max_code_length: int = Field(10000, alias="maxCodeLength")
    allowed_languages: List[str] = Field(default_factory=list, alias="allowedLanguages")
    blocked_keywords: List[str] = Field(default_factory=list, alias="blockedKeywords")

    class Config:
        allow_population_by_field_name = True


class ClientConfig(BaseModel):
    """Model for client configuration."""
    endpoint: str = "https://api.deepexec.com/v1"
    timeout: float = 30.0
    max_retries: int = Field(3, alias="maxRetries")
    retry_delay: float = Field(1.0, alias="retryDelay")
    verify_ssl: bool = Field(True, alias="verifySSL")
    deepseek_key: Optional[str] = Field(None, alias="deepseekKey")
    e2b_key: Optional[str] = Field(None, alias="e2bKey")
    security_options: SecurityOptions = Field(default_factory=SecurityOptions, alias="securityOptions")

    class Config:
        allow_population_by_field_name = True
