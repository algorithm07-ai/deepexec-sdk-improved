import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime

from deepexec_sdk import DeepExecClient, DeepExecAsyncClient
from deepexec_sdk.core.models import (
    MCPSubmitJobRequest, MCPSubmitJobResponse,
    MCPJobStatusRequest, MCPJobStatusResponse,
    MCPCancelJobRequest, MCPCancelJobResponse,
    MCPCodeExecutionRequest, MCPCodeExecutionResult,
    MCPTextGenerationRequest, MCPTextGenerationResult
)
from deepexec_sdk.core.protocols.mcp import MCPRequestType, MCPResponseType

# 测试数据
TEST_JOB_ID = "job-123456789"
TEST_SESSION_ID = "session-987654321"
TEST_CODE = "print('Hello, World!')"
TEST_LANGUAGE = "python"
TEST_PROMPT = "Explain quantum computing"
TEST_MODEL = "deepseek-v3"

# 模拟响应数据
def mock_submit_job_response():
    return {
        "protocol_version": "2024.1",
        "type": MCPResponseType.SUBMIT_JOB,
        "status": "success",
        "output": {
            "job_id": TEST_JOB_ID,
            "status": "PENDING",
            "created_at": datetime.now().isoformat()
        },
        "metadata": {
            "request_id": "req-123"
        }
    }

def mock_job_status_response(status="COMPLETED", progress=100):
    response = {
        "protocol_version": "2024.1",
        "type": MCPResponseType.JOB_STATUS,
        "status": "success",
        "output": {
            "job_id": TEST_JOB_ID,
            "status": status,
            "progress": progress,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        "metadata": {
            "request_id": "req-456"
        }
    }
    
    if status == "COMPLETED":
        response["output"]["result"] = {"message": "Job completed successfully"}
    elif status == "FAILED":
        response["output"]["error"] = {"message": "Job execution failed", "code": "EXECUTION_ERROR"}
    
    return response

def mock_cancel_job_response():
    return {
        "protocol_version": "2024.1",
        "type": MCPResponseType.CANCEL_JOB,
        "status": "success",
        "output": {
            "job_id": TEST_JOB_ID,
            "status": "CANCELED",
            "canceled_at": datetime.now().isoformat()
        },
        "metadata": {
            "request_id": "req-789"
        }
    }

def mock_code_execution_response():
    return {
        "protocol_version": "2024.1",
        "type": MCPResponseType.CODE_EXECUTION,
        "status": "success",
        "output": {
            "output": "Hello, World!\n",
            "exit_code": 0,
            "execution_time": 123,
            "memory_usage": 1024
        },
        "metadata": {
            "request_id": "req-abc"
        }
    }

def mock_text_generation_response():
    return {
        "protocol_version": "2024.1",
        "type": MCPResponseType.TEXT_GENERATION,
        "status": "success",
        "output": {
            "text": "Quantum computing is a type of computing that uses quantum-mechanical phenomena...",
            "model": TEST_MODEL,
            "generation_time": 456,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "total_tokens": 60
            }
        },
        "metadata": {
            "request_id": "req-def"
        }
    }

# 同步客户端测试
class TestDeepExecClient:
    @pytest.fixture
    def client(self):
        with DeepExecClient(endpoint="https://test-api.example.com") as client:
            yield client
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_submit_job(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_submit_job_response()
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.submit_job(
            name="test_job",
            job_type="code_execution",
            data={"code": TEST_CODE, "language": TEST_LANGUAGE}
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "PENDING"
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert json_data["type"] == MCPRequestType.SUBMIT_JOB
        assert json_data["input"]["name"] == "test_job"
        assert json_data["input"]["type"] == "code_execution"
        assert json_data["input"]["data"]["code"] == TEST_CODE
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_get_job_status(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_job_status_response()
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.get_job_status(TEST_JOB_ID)
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "COMPLETED"
        assert response.progress == 100
        assert "message" in response.result
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert json_data["type"] == MCPRequestType.JOB_STATUS
        assert json_data["input"]["job_id"] == TEST_JOB_ID
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_cancel_job(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_cancel_job_response()
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.cancel_job(TEST_JOB_ID, reason="Testing cancellation")
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "CANCELED"
        assert response.canceled_at is not None
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert json_data["type"] == MCPRequestType.CANCEL_JOB
        assert json_data["input"]["job_id"] == TEST_JOB_ID
        assert json_data["input"]["reason"] == "Testing cancellation"
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_execute_code_job(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_submit_job_response()
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.execute_code_job(
            code=TEST_CODE,
            language=TEST_LANGUAGE,
            timeout=30
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert json_data["type"] == MCPRequestType.SUBMIT_JOB
        assert json_data["input"]["type"] == "code_execution"
        assert json_data["input"]["data"]["code"] == TEST_CODE
        assert json_data["input"]["data"]["language"] == TEST_LANGUAGE
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_get_code_execution_result(self, mock_post, client):
        # 设置模拟响应 - 首先模拟作业状态
        mock_response1 = MagicMock()
        mock_response1.json.return_value = mock_job_status_response()
        
        # 然后模拟代码执行结果
        mock_response2 = MagicMock()
        mock_response2.json.return_value = mock_code_execution_response()
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        # 调用方法
        result = client.get_code_execution_result(TEST_JOB_ID)
        
        # 验证结果
        assert result.output == "Hello, World!\n"
        assert result.exit_code == 0
        assert result.execution_time == 123
        assert result.memory_usage == 1024
        
        # 验证请求
        assert mock_post.call_count == 2
    
    @patch("deepexec_sdk.core.client.DeepExecClient.get_job_status")
    @patch("deepexec_sdk.core.client.DeepExecClient.execute_code_job")
    @patch("deepexec_sdk.core.client.DeepExecClient.get_code_execution_result")
    def test_execute_code_and_wait(self, mock_get_result, mock_execute, mock_status, client):
        # 设置模拟响应
        mock_execute.return_value = MCPSubmitJobResponse(
            job_id=TEST_JOB_ID,
            status="PENDING",
            created_at=datetime.now().isoformat()
        )
        
        mock_status.return_value = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="COMPLETED",
            progress=100,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            result={"message": "Job completed successfully"}
        )
        
        mock_get_result.return_value = MCPCodeExecutionResult(
            output="Hello, World!\n",
            exit_code=0,
            execution_time=123,
            memory_usage=1024
        )
        
        # 调用方法
        result = client.execute_code_and_wait(TEST_CODE, TEST_LANGUAGE)
        
        # 验证结果
        assert result.output == "Hello, World!\n"
        assert result.exit_code == 0
        
        # 验证调用
        mock_execute.assert_called_once_with(
            code=TEST_CODE,
            language=TEST_LANGUAGE,
            environment=None,
            timeout=60
        )
        mock_status.assert_called()
        mock_get_result.assert_called_once_with(TEST_JOB_ID)

# 异步客户端测试
class TestDeepExecAsyncClient:
    @pytest.fixture
    async def client(self):
        async with DeepExecAsyncClient(endpoint="https://test-api.example.com") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_submit_job(self, client):
        # 模拟 send_request 方法
        client.send_request = MagicMock()
        client.send_request.return_value = mock_submit_job_response()
        
        # 调用方法
        response = await client.submit_job(
            name="test_job",
            job_type="code_execution",
            data={"code": TEST_CODE, "language": TEST_LANGUAGE}
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "PENDING"
        
        # 验证请求
        client.send_request.assert_called_once()
        args, _ = client.send_request.call_args
        assert args[0] == MCPRequestType.SUBMIT_JOB
        assert args[1]["name"] == "test_job"
        assert args[1]["type"] == "code_execution"
    
    @pytest.mark.asyncio
    async def test_get_job_status(self, client):
        # 模拟 send_request 方法
        client.send_request = MagicMock()
        client.send_request.return_value = mock_job_status_response()
        
        # 调用方法
        response = await client.get_job_status(TEST_JOB_ID)
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "COMPLETED"
        
        # 验证请求
        client.send_request.assert_called_once()
        args, _ = client.send_request.call_args
        assert args[0] == MCPRequestType.JOB_STATUS
        assert args[1]["job_id"] == TEST_JOB_ID
    
    @pytest.mark.asyncio
    async def test_cancel_job(self, client):
        # 模拟 send_request 方法
        client.send_request = MagicMock()
        client.send_request.return_value = mock_cancel_job_response()
        
        # 调用方法
        response = await client.cancel_job(TEST_JOB_ID, reason="Testing cancellation")
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "CANCELED"
        
        # 验证请求
        client.send_request.assert_called_once()
        args, _ = client.send_request.call_args
        assert args[0] == MCPRequestType.CANCEL_JOB
        assert args[1]["job_id"] == TEST_JOB_ID
        assert args[1]["reason"] == "Testing cancellation"
    
    @pytest.mark.asyncio
    async def test_execute_code_job(self, client):
        # 模拟 send_request 方法
        client.send_request = MagicMock()
        client.send_request.return_value = mock_submit_job_response()
        
        # 调用方法
        response = await client.execute_code_job(
            code=TEST_CODE,
            language=TEST_LANGUAGE
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        
        # 验证请求
        client.send_request.assert_called_once()
        args, _ = client.send_request.call_args
        assert args[0] == MCPRequestType.SUBMIT_JOB
        assert args[1]["type"] == "code_execution"
        assert args[1]["data"]["code"] == TEST_CODE
        assert args[1]["data"]["language"] == TEST_LANGUAGE
    
    @pytest.mark.asyncio
    async def test_generate_text_job(self, client):
        # 模拟 send_request 方法
        client.send_request = MagicMock()
        client.send_request.return_value = mock_submit_job_response()
        
        # 调用方法
        response = await client.generate_text_job(
            prompt=TEST_PROMPT,
            model=TEST_MODEL
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        
        # 验证请求
        client.send_request.assert_called_once()
        args, _ = client.send_request.call_args
        assert args[0] == MCPRequestType.SUBMIT_JOB
        assert args[1]["type"] == "text_generation"
        assert args[1]["data"]["prompt"] == TEST_PROMPT
        assert args[1]["data"]["model"] == TEST_MODEL
    
    @pytest.mark.asyncio
    async def test_execute_code_and_wait(self, client):
        # 模拟方法
        client.execute_code_job = MagicMock()
        client.execute_code_job.return_value = MCPSubmitJobResponse(
            job_id=TEST_JOB_ID,
            status="PENDING",
            created_at=datetime.now().isoformat()
        )
        
        client.get_job_status = MagicMock()
        client.get_job_status.return_value = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="COMPLETED",
            progress=100,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            result={"message": "Job completed successfully"}
        )
        
        client.get_code_execution_result = MagicMock()
        client.get_code_execution_result.return_value = MCPCodeExecutionResult(
            output="Hello, World!\n",
            exit_code=0,
            execution_time=123,
            memory_usage=1024
        )
        
        # 调用方法
        result = await client.execute_code_and_wait(TEST_CODE, TEST_LANGUAGE)
        
        # 验证结果
        assert result.output == "Hello, World!\n"
        assert result.exit_code == 0
        
        # 验证调用
        client.execute_code_job.assert_called_once_with(
            code=TEST_CODE,
            language=TEST_LANGUAGE,
            environment=None,
            timeout=60
        )
        client.get_job_status.assert_called()
        client.get_code_execution_result.assert_called_once_with(TEST_JOB_ID)
    
    @pytest.mark.asyncio
    async def test_generate_text_and_wait(self, client):
        # 模拟方法
        client.generate_text_job = MagicMock()
        client.generate_text_job.return_value = MCPSubmitJobResponse(
            job_id=TEST_JOB_ID,
            status="PENDING",
            created_at=datetime.now().isoformat()
        )
        
        client.get_job_status = MagicMock()
        client.get_job_status.return_value = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="COMPLETED",
            progress=100,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            result={"message": "Job completed successfully"}
        )
        
        client.get_text_generation_result = MagicMock()
        client.get_text_generation_result.return_value = MCPTextGenerationResult(
            text="Quantum computing is a type of computing that uses quantum-mechanical phenomena...",
            model=TEST_MODEL,
            generation_time=456,
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "total_tokens": 60
            }
        )
        
        # 调用方法
        result = await client.generate_text_and_wait(TEST_PROMPT, model=TEST_MODEL)
        
        # 验证结果
        assert "Quantum computing" in result.text
        assert result.model == TEST_MODEL
        
        # 验证调用
        client.generate_text_job.assert_called_once_with(
            prompt=TEST_PROMPT,
            model=TEST_MODEL,
            max_tokens=None,
            temperature=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None,
            timeout=60
        )
        client.get_job_status.assert_called()
        client.get_text_generation_result.assert_called_once_with(TEST_JOB_ID)

    # 测试新添加的 MCP 高级方法
    @pytest.mark.asyncio
    async def test_submit_mcp_job(self, client):
        # 模拟 _send_request 方法
        client._send_request = MagicMock()
        client._send_request.return_value = mock_submit_job_response()["output"]
        
        # 调用方法
        response = await client.submit_mcp_job(
            name="test_mcp_job",
            job_type="code_execution",
            data={"code": TEST_CODE, "language": TEST_LANGUAGE},
            timeout=120,
            priority=5,
            tags=["test", "mcp"]
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "PENDING"
        
        # 验证请求
        client._send_request.assert_called_once()
        args, kwargs = client._send_request.call_args
        assert args[0] == "jobs"
        assert "name" in args[1]
        assert args[1]["name"] == "test_mcp_job"
        assert args[1]["type"] == "code_execution"
        assert args[1]["timeout"] == 120
        assert args[1]["priority"] == 5
        assert "test" in args[1]["tags"]
        assert "mcp" in args[1]["tags"]
    
    @pytest.mark.asyncio
    async def test_get_mcp_job_status(self, client):
        # 模拟 _send_request 方法
        client._send_request = MagicMock()
        client._send_request.return_value = mock_job_status_response()["output"]
        
        # 调用方法
        response = await client.get_mcp_job_status(TEST_JOB_ID)
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "COMPLETED"
        assert response.progress == 100
        assert "message" in response.result
        
        # 验证请求
        client._send_request.assert_called_once()
        args, kwargs = client._send_request.call_args
        assert args[0] == f"jobs/{TEST_JOB_ID}/status"
        assert "job_id" in args[1]
        assert args[1]["job_id"] == TEST_JOB_ID
    
    @pytest.mark.asyncio
    async def test_cancel_mcp_job(self, client):
        # 模拟 _send_request 方法
        client._send_request = MagicMock()
        client._send_request.return_value = mock_cancel_job_response()["output"]
        
        # 调用方法
        response = await client.cancel_mcp_job(TEST_JOB_ID, reason="Testing MCP cancellation")
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "CANCELED"
        assert response.canceled_at is not None
        
        # 验证请求
        client._send_request.assert_called_once()
        args, kwargs = client._send_request.call_args
        assert args[0] == f"jobs/{TEST_JOB_ID}/cancel"
        assert "job_id" in args[1]
        assert args[1]["job_id"] == TEST_JOB_ID
        assert args[1]["reason"] == "Testing MCP cancellation"
    
    @pytest.mark.asyncio
    async def test_wait_for_mcp_job_completion(self, client):
        # 模拟 get_mcp_job_status 方法
        # 首先返回进行中的状态，然后返回已完成的状态
        client.get_mcp_job_status = MagicMock()
        in_progress_response = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="IN_PROGRESS",
            progress=50,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        completed_response = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="COMPLETED",
            progress=100,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            result={"message": "Job completed successfully"}
        )
        client.get_mcp_job_status.side_effect = [in_progress_response, completed_response]
        
        # 调用方法
        response = await client.wait_for_mcp_job_completion(TEST_JOB_ID, poll_interval=0.1)
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "COMPLETED"
        assert response.progress == 100
        assert "message" in response.result
        
        # 验证调用次数
        assert client.get_mcp_job_status.call_count == 2
        client.get_mcp_job_status.assert_called_with(TEST_JOB_ID)

# 同步客户端的 MCP 高级方法测试
class TestDeepExecClientMCPMethods:
    @pytest.fixture
    def client(self):
        with DeepExecClient(endpoint="https://test-api.example.com") as client:
            yield client
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_submit_mcp_job(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_submit_job_response()["output"]
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.submit_mcp_job(
            name="test_mcp_job",
            job_type="code_execution",
            data={"code": TEST_CODE, "language": TEST_LANGUAGE},
            timeout=120,
            priority=5,
            tags=["test", "mcp"]
        )
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "PENDING"
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert "name" in json_data
        assert json_data["name"] == "test_mcp_job"
        assert json_data["type"] == "code_execution"
        assert json_data["timeout"] == 120
        assert json_data["priority"] == 5
        assert "test" in json_data["tags"]
        assert "mcp" in json_data["tags"]
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_get_mcp_job_status(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_job_status_response()["output"]
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.get_mcp_job_status(TEST_JOB_ID)
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "COMPLETED"
        assert response.progress == 100
        assert "message" in response.result
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert "job_id" in json_data
        assert json_data["job_id"] == TEST_JOB_ID
    
    @patch("deepexec_sdk.core.client.requests.Session.post")
    def test_cancel_mcp_job(self, mock_post, client):
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = mock_cancel_job_response()["output"]
        mock_post.return_value = mock_response
        
        # 调用方法
        response = client.cancel_mcp_job(TEST_JOB_ID, reason="Testing MCP cancellation")
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "CANCELED"
        assert response.canceled_at is not None
        
        # 验证请求
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        json_data = kwargs.get("json", {})
        assert "job_id" in json_data
        assert json_data["job_id"] == TEST_JOB_ID
        assert json_data["reason"] == "Testing MCP cancellation"
    
    @patch("deepexec_sdk.core.client.DeepExecClient.get_mcp_job_status")
    def test_wait_for_mcp_job_completion(self, mock_get_status, client):
        # 设置模拟响应
        # 首先返回进行中的状态，然后返回已完成的状态
        in_progress_response = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="IN_PROGRESS",
            progress=50,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        completed_response = MCPJobStatusResponse(
            job_id=TEST_JOB_ID,
            status="COMPLETED",
            progress=100,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            result={"message": "Job completed successfully"}
        )
        mock_get_status.side_effect = [in_progress_response, completed_response]
        
        # 调用方法
        response = client.wait_for_mcp_job_completion(TEST_JOB_ID, poll_interval=0.1)
        
        # 验证结果
        assert response.job_id == TEST_JOB_ID
        assert response.status == "COMPLETED"
        assert response.progress == 100
        assert "message" in response.result
        
        # 验证调用次数
        assert mock_get_status.call_count == 2
        mock_get_status.assert_called_with(TEST_JOB_ID)
