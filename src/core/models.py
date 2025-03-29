from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator


class ExecutionRequest(BaseModel):
    """Model for code execution requests."""
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
    """Model for code execution results."""
    output: str
    exit_code: int
    execution_time: int  # in milliseconds
    memory_usage: int  # in MB
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    """Model for token usage statistics."""
    prompt_tokens: int = Field(0, alias="promptTokens")
    completion_tokens: int = Field(0, alias="completionTokens")
    total_tokens: int = Field(0, alias="totalTokens")

    class Config:
        allow_population_by_field_name = True


class GenerationRequest(BaseModel):
    """Model for text generation requests."""
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
    """Model for text generation results."""
    text: str
    model: str
    generation_time: int = Field(0, alias="generationTime")  # in milliseconds
    usage: TokenUsage

    class Config:
        allow_population_by_field_name = True


class StreamGenerationChunk(BaseModel):
    """Model for streaming text generation chunks."""
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
