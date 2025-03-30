import os
import json
from typing import Dict, Any, List, Optional
from .exceptions import MCPConfigError
from .models import ExecutionResult, GenerationResult, TokenUsage


def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file.

    Args:
        file_path: Path to the configuration file.

    Returns:
        A dictionary containing the configuration.

    Raises:
        MCPConfigError: If the file contains invalid JSON.
    """
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise MCPConfigError(f"Invalid JSON in configuration file: {str(e)}")


def load_config_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables.

    Returns:
        A dictionary containing the configuration.
    """
    config = {}

    # Map environment variables to configuration keys
    env_mapping = {
        "DEEPEXEC_ENDPOINT": "endpoint",
        "DEEPEXEC_TIMEOUT": "timeout",
        "DEEPEXEC_MAX_RETRIES": "maxRetries",
        "DEEPEXEC_RETRY_DELAY": "retryDelay",
        "DEEPEXEC_VERIFY_SSL": "verifySSL",
        "DEEPEXEC_DEEPSEEK_KEY": "deepseekKey",
        "DEEPEXEC_E2B_KEY": "e2bKey",
    }

    # Security options mapping
    security_mapping = {
        "DEEPEXEC_MAX_CODE_LENGTH": "maxCodeLength",
        "DEEPEXEC_ALLOWED_LANGUAGES": "allowedLanguages",
        "DEEPEXEC_BLOCKED_KEYWORDS": "blockedKeywords",
    }

    # Process standard configuration options
    for env_var, config_key in env_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            
            # Convert types as needed
            if config_key in ["timeout", "retryDelay"]:
                config[config_key] = float(value)
            elif config_key in ["maxRetries"]:
                config[config_key] = int(value)
            elif config_key in ["verifySSL"]:
                config[config_key] = value.lower() == "true"
            else:
                config[config_key] = value

    # Process security options
    security_options = {}
    for env_var, option_key in security_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            
            # Convert types as needed
            if option_key == "maxCodeLength":
                security_options[option_key] = int(value)
            elif option_key in ["allowedLanguages", "blockedKeywords"]:
                security_options[option_key] = [item.strip() for item in value.split(',')]
            else:
                security_options[option_key] = value

    if security_options:
        config["securityOptions"] = security_options

    return config


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries.

    Args:
        *configs: Configuration dictionaries to merge, in order of increasing priority.

    Returns:
        A merged configuration dictionary.
    """
    merged = {}

    for config in configs:
        for key, value in config.items():
            # Special handling for nested dictionaries like securityOptions
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value

    return merged


def validate_language(language: str, allowed_languages: List[str]) -> bool:
    """Validate that the language is supported.

    Args:
        language: The programming language to validate.
        allowed_languages: List of allowed programming languages.

    Returns:
        True if the language is supported.

    Raises:
        ValueError: If the language is not supported.
    """
    if not allowed_languages or language.lower() in [lang.lower() for lang in allowed_languages]:
        return True
    
    raise ValueError(f"Unsupported language: {language}. Allowed languages: {', '.join(allowed_languages)}")


def validate_code(code: str, max_length: int, blocked_keywords: List[str]) -> bool:
    """Validate that the code meets security requirements.

    Args:
        code: The code to validate.
        max_length: Maximum allowed code length.
        blocked_keywords: List of blocked keywords.

    Returns:
        True if the code is valid.

    Raises:
        ValueError: If the code violates security requirements.
    """
    # Check code length
    if len(code) > max_length:
        raise ValueError(f"Code length ({len(code)}) exceeds maximum length ({max_length})")
    
    # Check for blocked keywords
    for keyword in blocked_keywords:
        if keyword.lower() in code.lower():
            raise ValueError(f"Code contains blocked keyword: {keyword}")
    
    return True


def format_execution_result(result: Dict[str, Any]) -> ExecutionResult:
    """Format execution result into a structured object.

    Args:
        result: Raw execution result data.

    Returns:
        An ExecutionResult object.
    """
    return ExecutionResult(
        output=result.get("output", ""),
        exit_code=result.get("exit_code", 1),
        execution_time=result.get("execution_time", 0),
        memory_usage=result.get("memory_usage", 0),
        metadata=result.get("metadata", {})
    )


def format_generation_result(result: Dict[str, Any]) -> GenerationResult:
    """Format text generation result into a structured object.

    Args:
        result: Raw text generation result data.

    Returns:
        A GenerationResult object.
    """
    usage_data = result.get("usage", {})
    usage = TokenUsage(
        promptTokens=usage_data.get("prompt_tokens", 0),
        completionTokens=usage_data.get("completion_tokens", 0),
        totalTokens=usage_data.get("total_tokens", 0)
    )
    
    return GenerationResult(
        text=result.get("text", ""),
        model=result.get("model", "unknown"),
        generationTime=result.get("generation_time", 0),
        usage=usage
    )
