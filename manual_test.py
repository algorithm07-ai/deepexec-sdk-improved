import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.conftest import MockServer
from src.core.async_client import DeepExecAsyncClient


async def test_execute_code_with_mock_server():
    """使用 MockServer 测试代码执行功能"""
    # 启动模拟服务器
    server = MockServer()
    await server.start()
    print(f"MockServer 启动在: {server.url}")
    
    try:
        # 创建客户端连接到模拟服务器
        client = DeepExecAsyncClient(
            endpoint=server.url,
            deepseek_key="test_deepseek_key",
            e2b_key="test_e2b_key"
        )
        
        async with client:
            # 1. 测试创建会话
            print("\n测试创建会话...")
            session_id = await client.create_session("test_user")
            print(f"会话创建成功，ID: {session_id}")
            
            # 查看服务器收到的请求
            requests = server.get_requests()
            print(f"服务器收到的请求数: {len(requests)}")
            print(f"请求路径: {requests[0]['path']}")
            print(f"请求体: {requests[0]['body']}")
            
            # 清除请求历史
            server.clear_requests()
            
            # 2. 测试代码执行
            print("\n测试代码执行...")
            python_code = """print('Hello, DeepExec!')
result = 42 * 2
print(f'The answer is {result}')"""
            
            result = await client.execute_code(
                code=python_code,
                language="python"
            )
            
            print(f"执行结果:\n{result.output}")
            print(f"退出代码: {result.exit_code}")
            print(f"执行时间: {result.execution_time}ms")
            
            # 查看服务器收到的请求
            requests = server.get_requests()
            print(f"服务器收到的请求数: {len(requests)}")
            print(f"请求路径: {requests[0]['path']}")
            print(f"代码: {requests[0]['body'].get('input', {}).get('code', '')}")
            
            # 清除请求历史
            server.clear_requests()
            
            # 3. 测试文本生成
            print("\n测试文本生成...")
            prompt = "解释什么是人工智能"
            
            # 设置自定义响应
            server.set_response("/v1/generate", {
                "protocol_version": "2024.1",
                "type": "text_generation_result",
                "session_id": session_id,
                "request_id": "custom_req_id",
                "status": "success",
                "output": {
                    "text": "人工智能（AI）是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统可以学习、推理、感知、规划和解决问题。AI 技术包括机器学习、深度学习、自然语言处理和计算机视觉等。"
                },
                "metadata": {
                    "model": "deepseek-v3",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 100,
                        "total_tokens": 110
                    }
                }
            })
            
            result = await client.generate_text(
                prompt=prompt,
                model="deepseek-v3"
            )
            
            print(f"生成的文本:\n{result.text}")
            print(f"模型: {result.model}")
            print(f"Token 使用情况: {result.usage.total_tokens}")
            
            # 查看服务器收到的请求
            requests = server.get_requests()
            print(f"服务器收到的请求数: {len(requests)}")
            print(f"请求路径: {requests[0]['path']}")
            print(f"提示词: {requests[0]['body'].get('input', {}).get('prompt', '')}")
            
            # 4. 测试错误处理
            print("\n测试错误处理...")
            server.set_error_mode(True, 401, "Invalid API key")
            
            try:
                await client.execute_code(
                    code="print('This should fail')",
                    language="python"
                )
            except Exception as e:
                print(f"成功捕获到预期的错误: {type(e).__name__}: {str(e)}")
            
            # 恢复正常模式
            server.set_error_mode(False)
            
            # 5. 测试延迟响应
            print("\n测试延迟响应...")
            server.set_delay(1.0)  # 设置 1 秒延迟
            
            start_time = asyncio.get_event_loop().time()
            await client.execute_code(
                code="print('Testing delayed response')",
                language="python"
            )
            end_time = asyncio.get_event_loop().time()
            
            print(f"延迟响应耗时: {end_time - start_time:.2f} 秒")
            
            # 重置延迟
            server.set_delay(0.0)
            
            print("\n所有测试完成!")
    
    finally:
        # 停止模拟服务器
        await server.stop()
        print("MockServer 已停止")


async def main():
    await test_execute_code_with_mock_server()


if __name__ == "__main__":
    asyncio.run(main())
