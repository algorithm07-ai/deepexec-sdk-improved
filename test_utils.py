import pytest
import os
import tempfile
import json
from unittest.mock import patch, mock_open
from src.core.utils import (
    load_config_from_file,
    load_config_from_env,
    merge_configs,
    validate_language,
    validate_code,
    format_execution_result,
    format_generation_result
)
from src.core.exceptions import MCPConfigError


class TestConfigUtils:
    """Unit tests for configuration utility functions."""

    def test_load_config_from_file_exists(self):
        """Test loading configuration from an existing file."""
        config_data = {
            "endpoint": "https://test-api.deepexec.com/v1",
            "timeout": 60.0,
            "maxRetries": 5,
            "deepseekKey": "test_key",
            "e2bKey": "test_e2b_key"
        }

        # Create a mock file
        m = mock_open(read_data=json.dumps(config_data))
        with patch("builtins.open", m):
            with patch("os.path.exists", return_value=True):
                config = load_config_from_file("/path/to/config.json")

        assert config["endpoint"] == "https://test-api.deepexec.com/v1"
        assert config["timeout"] == 60.0
        assert config["maxRetries"] == 5
        assert config["deepseekKey"] == "test_key"
        assert config["e2bKey"] == "test_e2b_key"

    def test_load_config_from_file_not_exists(self):
        """Test loading configuration from a non-existent file."""
        with patch("os.path.exists", return_value=False):
            config = load_config_from_file("/path/to/nonexistent.json")

        assert config == {}

    def test_load_config_from_file_invalid_json(self):
        """Test loading configuration from a file with invalid JSON."""
        # Create a mock file with invalid JSON
        m = mock_open(read_data="{invalid json}")
        with patch("builtins.open", m):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(MCPConfigError) as exc_info:
                    load_config_from_file("/path/to/config.json")

        assert "Invalid JSON in configuration file" in str(exc_info.value)

    def test_load_config_from_env(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "DEEPEXEC_ENDPOINT": "https://env-api.deepexec.com/v1",
            "DEEPEXEC_TIMEOUT": "45.0",
            "DEEPEXEC_MAX_RETRIES": "3",
            "DEEPEXEC_DEEPSEEK_KEY": "env_key",
            "DEEPEXEC_E2B_KEY": "env_e2b_key",
            "DEEPEXEC_VERIFY_SSL": "false",
            "DEEPEXEC_MAX_CODE_LENGTH": "5000",
            "DEEPEXEC_ALLOWED_LANGUAGES": "python,javascript,typescript",
            "DEEPEXEC_BLOCKED_KEYWORDS": "rm -rf,os.system"
        }

        with patch.dict("os.environ", env_vars):
            config = load_config_from_env()

        assert config["endpoint"] == "https://env-api.deepexec.com/v1"
        assert config["timeout"] == 45.0
        assert config["maxRetries"] == 3
        assert config["deepseekKey"] == "env_key"
        assert config["e2bKey"] == "env_e2b_key"
        assert config["verifySSL"] is False
        assert config["securityOptions"]["maxCodeLength"] == 5000
        assert config["securityOptions"]["allowedLanguages"] == ["python", "javascript", "typescript"]
        assert config["securityOptions"]["blockedKeywords"] == ["rm -rf", "os.system"]

    def test_merge_configs(self):
        """Test merging multiple configurations with correct priority."""
        default_config = {
            "endpoint": "https://default-api.deepexec.com/v1",
            "timeout": 30.0,
            "maxRetries": 3,
            "verifySSL": True,
            "securityOptions": {
                "maxCodeLength": 10000,
                "allowedLanguages": ["python", "javascript"],
                "blockedKeywords": ["rm -rf"]
            }
        }

        file_config = {
            "endpoint": "https://file-api.deepexec.com/v1",
            "timeout": 60.0,
            "deepseekKey": "file_key",
            "securityOptions": {
                "maxCodeLength": 5000
            }
        }

        env_config = {
            "endpoint": "https://env-api.deepexec.com/v1",
            "deepseekKey": "env_key",
            "e2bKey": "env_e2b_key"
        }

        constructor_config = {
            "deepseekKey": "constructor_key"
        }

        # Merge configs in order of priority: constructor > env > file > default
        merged_config = merge_configs(
            default_config,
            file_config,
            env_config,
            constructor_config
        )

        # Check that values are taken from the highest priority source
        assert merged_config["endpoint"] == "https://env-api.deepexec.com/v1"  # From env
        assert merged_config["timeout"] == 60.0  # From file
        assert merged_config["maxRetries"] == 3  # From default
        assert merged_config["deepseekKey"] == "constructor_key"  # From constructor
        assert merged_config["e2bKey"] == "env_e2b_key"  # From env
        assert merged_config["verifySSL"] is True  # From default
        assert merged_config["securityOptions"]["maxCodeLength"] == 5000  # From file
        assert merged_config["securityOptions"]["allowedLanguages"] == ["python", "javascript"]  # From default
        assert merged_config["securityOptions"]["blockedKeywords"] == ["rm -rf"]  # From default


class TestValidationUtils:
    """Unit tests for validation utility functions."""

    def test_validate_language_valid(self):
        """Test validation of valid programming languages."""
        allowed_languages = ["python", "javascript", "typescript"]

        assert validate_language("python", allowed_languages) is True
        assert validate_language("javascript", allowed_languages) is True
        assert validate_language("typescript", allowed_languages) is True

    def test_validate_language_invalid(self):
        """Test validation of invalid programming languages."""
        allowed_languages = ["python", "javascript", "typescript"]

        with pytest.raises(ValueError) as exc_info:
            validate_language("ruby", allowed_languages)
        assert "Unsupported language" in str(exc_info.value)

    def test_validate_code_valid(self):
        """Test validation of valid code."""
        code = "print('Hello, World!')"
        max_length = 100
        blocked_keywords = ["rm -rf", "os.system"]

        assert validate_code(code, max_length, blocked_keywords) is True

    def test_validate_code_too_long(self):
        """Test validation of code that exceeds the maximum length."""
        code = "print('Hello, World!')" * 100  # Long code
        max_length = 100
        blocked_keywords = ["rm -rf", "os.system"]

        with pytest.raises(ValueError) as exc_info:
            validate_code(code, max_length, blocked_keywords)
        assert "exceeds maximum length" in str(exc_info.value)

    def test_validate_code_blocked_keywords(self):
        """Test validation of code containing blocked keywords."""
        code = "import os; os.system('ls')"
        max_length = 100
        blocked_keywords = ["rm -rf", "os.system"]

        with pytest.raises(ValueError) as exc_info:
            validate_code(code, max_length, blocked_keywords)
        assert "contains blocked keyword" in str(exc_info.value)


class TestFormattingUtils:
    """Unit tests for result formatting utility functions."""

    def test_format_execution_result(self):
        """Test formatting of execution results."""
        raw_result = {
            "output": "hello\n",
            "exit_code": 0,
            "execution_time": 100,
            "memory_usage": 10,
            "metadata": {"language": "python"}
        }

        formatted_result = format_execution_result(raw_result)

        assert formatted_result.output == "hello\n"
        assert formatted_result.exitCode == 0
        assert formatted_result.executionTime == 100
        assert formatted_result.memoryUsage == 10
        assert formatted_result.metadata["language"] == "python"

    def test_format_generation_result(self):
        """Test formatting of text generation results."""
        raw_result = {
            "text": "Generated text",
            "model": "deepseek-v3",
            "generation_time": 500,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "total_tokens": 60
            }
        }

        formatted_result = format_generation_result(raw_result)

        assert formatted_result.text == "Generated text"
        assert formatted_result.model == "deepseek-v3"
        assert formatted_result.generationTime == 500
        assert formatted_result.usage.promptTokens == 10
        assert formatted_result.usage.completionTokens == 50
        assert formatted_result.usage.totalTokens == 60
