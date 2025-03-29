import pytest
import asyncio
import json
from typing import Dict, Any, List, Optional
from aiohttp import web


class MockServer:
    """Mock server for testing the DeepExec client."""

    def __init__(self):
        self.app = web.Application()
        self.app.router.add_post("/v1/execute", self.handle_execute)
        self.app.router.add_post("/v1/generate", self.handle_generate)
        self.app.router.add_post("/v1/sessions", self.handle_create_session)
        self.runner = None
        self.site = None
        self.url = ""
        self.delay = 0.0
        self.responses: Dict[str, Any] = {}
        self.requests: List[Dict[str, Any]] = []
        self.error_mode = False
        self.error_status = 500
        self.error_message = "Internal Server Error"

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "localhost", 0)
        await self.site.start()
        self.url = f"http://localhost:{self.site._server.sockets[0].getsockname()[1]}"
        return self

    async def stop(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    def set_delay(self, delay: float):
        """Set a delay for all responses."""
        self.delay = delay

    def set_response(self, path: str, response: Dict[str, Any]):
        """Set a custom response for a specific path."""
        self.responses[path] = response

    def set_error_mode(self, enabled: bool, status: int = 500, message: str = "Internal Server Error"):
        """Enable or disable error mode."""
        self.error_mode = enabled
        self.error_status = status
        self.error_message = message

    def get_requests(self) -> List[Dict[str, Any]]:
        """Get all received requests."""
        return self.requests

    def clear_requests(self):
        """Clear the request history."""
        self.requests = []

    async def handle_execute(self, request):
        """Handle code execution requests."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        body = await request.json()
        self.requests.append({"path": "/v1/execute", "body": body})

        if self.error_mode:
            return web.json_response(
                {"error": {"message": self.error_message}},
                status=self.error_status
            )

        if "/v1/execute" in self.responses:
            return web.json_response(self.responses["/v1/execute"])

        # Default response
        code = body.get("input", {}).get("code", "")
        language = body.get("metadata", {}).get("language", "python")

        # Simulate Python execution for testing
        if language == "python" and "time.sleep" in code:
            output = ""
            exit_code = 0
        else:
            # Extract print statements for simple simulation
            output = ""
            if "print(" in code:
                import re
                matches = re.findall(r"print\((.+?)\)", code)
                for match in matches:
                    # Simple evaluation for testing only
                    try:
                        if match.startswith("'"): 
                            output += match.strip("'") + "\n"
                        elif match.startswith('"'):
                            output += match.strip('"') + "\n"
                        else:
                            output += str(eval(match)) + "\n"
                    except:
                        output += f"[Error evaluating: {match}]\n"
            exit_code = 0

        return web.json_response({
            "protocol_version": "2024.1",
            "type": "code_execution_result",
            "session_id": body.get("session_id", "test_session"),
            "request_id": "req_" + str(len(self.requests)),
            "status": "success",
            "output": {
                "execution_result": {
                    "output": output,
                    "exit_code": exit_code,
                    "execution_time": 100,
                    "memory_usage": 10
                }
            }
        })

    async def handle_generate(self, request):
        """Handle text generation requests."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        body = await request.json()
        self.requests.append({"path": "/v1/generate", "body": body})

        if self.error_mode:
            return web.json_response(
                {"error": {"message": self.error_message}},
                status=self.error_status
            )

        if "/v1/generate" in self.responses:
            return web.json_response(self.responses["/v1/generate"])

        # Default response
        prompt = body.get("input", {}).get("prompt", "")
        return web.json_response({
            "protocol_version": "2024.1",
            "type": "text_generation_result",
            "session_id": body.get("session_id", "test_session"),
            "request_id": "req_" + str(len(self.requests)),
            "status": "success",
            "output": {
                "text": f"Generated response for: {prompt[:20]}..."
            },
            "metadata": {
                "model": body.get("metadata", {}).get("model", "deepseek-v3"),
                "usage": {
                    "prompt_tokens": len(prompt) // 4,
                    "completion_tokens": 100,
                    "total_tokens": len(prompt) // 4 + 100
                }
            }
        })

    async def handle_create_session(self, request):
        """Handle session creation requests."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        body = await request.json()
        self.requests.append({"path": "/v1/sessions", "body": body})

        if self.error_mode:
            return web.json_response(
                {"error": {"message": self.error_message}},
                status=self.error_status
            )

        if "/v1/sessions" in self.responses:
            return web.json_response(self.responses["/v1/sessions"])

        # Default response
        return web.json_response({
            "protocol_version": "2024.1",
            "type": "session_created",
            "session_id": "test_session_" + str(len(self.requests)),
            "request_id": "req_" + str(len(self.requests)),
            "status": "success"
        })


@pytest.fixture
async def mock_server():
    """Fixture that provides a mock server for testing."""
    server = MockServer()
    await server.start()
    yield server
    await server.stop()


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
