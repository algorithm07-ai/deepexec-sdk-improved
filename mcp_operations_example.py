import asyncio
import time
from deepexec_sdk import DeepExecAsyncClient, DeepExecClient

# 同步客户端示例
def sync_example():
    print("\n===== 同步客户端示例 =====")
    
    # 创建客户端实例
    with DeepExecClient(
        endpoint="https://api.deepexec.com/v1",  # 替换为实际的 API 端点
        deepseek_key="sk-...",  # 替换为您的 DeepSeek API 密钥
        e2b_key="e2b_..."       # 替换为您的 E2B API 密钥
    ) as client:
        # 执行代码示例
        print("\n-- 代码执行示例 --")
        try:
            # 使用便捷方法执行代码并等待结果
            result = client.execute_code_and_wait(
                code="import sys\nprint(f'Python version: {sys.version}')\nprint('Hello from DeepExec!')\n",
                language="python",
                timeout=30
            )
            
            print(f"输出: {result.output}")
            print(f"退出码: {result.exit_code}")
            print(f"执行时间: {result.execution_time} ms")
            print(f"内存使用: {result.memory_usage} bytes")
        except Exception as e:
            print(f"代码执行失败: {e}")
        
        # 文本生成示例
        print("\n-- 文本生成示例 --")
        try:
            # 使用便捷方法生成文本并等待结果
            result = client.generate_text_and_wait(
                prompt="用简单的语言解释量子计算",
                model="deepseek-v3",
                max_tokens=300,
                temperature=0.7
            )
            
            print(f"生成的文本: {result.text[:100]}...")
            print(f"模型: {result.model}")
            print(f"生成时间: {result.generation_time} ms")
            if hasattr(result, 'usage') and result.usage:
                print(f"Token 使用情况: {result.usage}")
        except Exception as e:
            print(f"文本生成失败: {e}")
        
        # 高级 MCP 方法示例
        print("\n-- 高级 MCP 方法示例 --")
        try:
            # 使用高级方法提交作业
            job_response = client.submit_mcp_job(
                name="high_level_test",
                job_type="code_execution",
                data={
                    "code": "print('Testing high-level MCP methods')",
                    "language": "python"
                },
                timeout=60,
                priority=1,
                tags=["test", "high-level"]
            )
            
            job_id = job_response.job_id
            print(f"作业已提交，ID: {job_id}")
            
            # 获取作业状态
            status = client.get_mcp_job_status(job_id)
            print(f"初始状态: {status.status}, 进度: {status.progress or 0}%")
            
            # 等待作业完成（自定义轮询间隔和最大等待时间）
            print("等待作业完成...")
            status_response = client.wait_for_mcp_job_completion(
                job_id=job_id,
                poll_interval=0.5,  # 每 0.5 秒检查一次状态
                max_wait_time=30.0  # 最多等待 30 秒
            )
            
            print(f"最终状态: {status_response.status}")
            if status_response.result:
                print(f"结果: {status_response.result}")
            
            # 尝试取消已完成的作业（将引发异常）
            try:
                cancel_response = client.cancel_mcp_job(
                    job_id=job_id,
                    reason="测试取消 API"
                )
                print(f"作业已取消，取消时间: {cancel_response.canceled_at}")
            except Exception as e:
                print(f"取消失败（对于已完成的作业是预期行为）: {e}")
        except Exception as e:
            print(f"高级 MCP 方法示例失败: {e}")

# 异步客户端示例
async def async_example():
    print("\n===== 异步客户端示例 =====")
    
    # 创建客户端实例
    async with DeepExecAsyncClient(
        endpoint="https://api.deepexec.com/v1",  # 替换为实际的 API 端点
        deepseek_key="sk-...",  # 替换为您的 DeepSeek API 密钥
        e2b_key="e2b_..."       # 替换为您的 E2B API 密钥
    ) as client:
        # 作业管理示例
        print("\n-- 作业管理示例 --")
        try:
            # 提交作业
            job_response = await client.submit_job(
                name="data_analysis_job",
                job_type="code_execution",
                data={
                    "code": "import time\nfor i in range(3):\n    print(f'Processing step {i}')\n    time.sleep(1)\nprint('Analysis complete!')",
                    "language": "python"
                },
                timeout=30
            )
            
            job_id = job_response.job_id
            print(f"作业已提交，ID: {job_id}")
            print(f"初始状态: {job_response.status}")
            
            # 检查作业状态
            status = await client.get_job_status(job_id)
            print(f"当前状态: {status.status}")
            
            # 等待作业完成
            print("等待作业完成...")
            start_time = time.time()
            while status.status not in ["COMPLETED", "FAILED", "CANCELED"]:
                await asyncio.sleep(1)
                status = await client.get_job_status(job_id)
                elapsed = time.time() - start_time
                print(f"状态: {status.status}, 已用时间: {elapsed:.1f}s, 进度: {status.progress or 0}%")
                
                # 超过 15 秒则取消作业
                if elapsed > 15 and status.status not in ["COMPLETED", "FAILED", "CANCELED"]:
                    print("作业执行时间过长，正在取消...")
                    cancel_response = await client.cancel_job(job_id, reason="演示取消功能")
                    print(f"作业已取消，取消时间: {cancel_response.canceled_at}")
                    break
            
            # 获取结果
            if status.status == "COMPLETED":
                print(f"作业完成!")
                if status.result:
                    print(f"结果: {status.result}")
                else:
                    print("无结果数据")
            elif status.status == "FAILED":
                print(f"作业失败: {status.error}")
            elif status.status == "CANCELED":
                print("作业已取消")
        except Exception as e:
            print(f"作业管理示例失败: {e}")
        
        # 代码执行示例
        print("\n-- 代码执行示例 --")
        try:
            # 使用专用方法执行代码
            result = await client.execute_code_and_wait(
                code="print('Hello, Async World!')",
                language="python"
            )
            
            print(f"输出: {result.output}")
            print(f"退出码: {result.exit_code}")
            print(f"执行时间: {result.execution_time} ms")
        except Exception as e:
            print(f"代码执行失败: {e}")
        
        # 文本生成示例
        print("\n-- 文本生成示例 --")
        try:
            # 提交文本生成作业
            job = await client.generate_text_job(
                prompt="写一首关于人工智能的短诗",
                model="deepseek-v3",
                max_tokens=200,
                temperature=0.8
            )
            
            print(f"文本生成作业已提交，ID: {job.job_id}")
            
            # 获取结果
            result = await client.get_text_generation_result(job.job_id)
            
            print(f"生成的文本:\n{result.text}")
            print(f"模型: {result.model}")
            print(f"生成时间: {result.generation_time} ms")
        except Exception as e:
            print(f"文本生成失败: {e}")
        
        # 高级 MCP 方法示例
        print("\n-- 异步高级 MCP 方法示例 --")
        try:
            # 使用高级方法提交长时间运行的作业
            job_response = await client.submit_mcp_job(
                name="async_high_level_test",
                job_type="code_execution",
                data={
                    "code": "import time\nfor i in range(5):\n    print(f'Step {i}')\n    time.sleep(1)\nprint('Done!')",
                    "language": "python"
                },
                timeout=60,
                priority=1,
                tags=["test", "async", "high-level"]
            )
            
            job_id = job_response.job_id
            print(f"异步作业已提交，ID: {job_id}")
            
            # 立即检查状态
            status = await client.get_mcp_job_status(job_id)
            print(f"初始状态: {status.status}, 进度: {status.progress or 0}%")
            
            # 等待几秒钟，让作业开始执行
            await asyncio.sleep(2)
            
            # 取消作业
            print("正在取消作业...")
            cancel_response = await client.cancel_mcp_job(
                job_id=job_id,
                reason="测试异步取消"
            )
            print(f"作业已取消，取消时间: {cancel_response.canceled_at}")
            
            # 验证取消状态
            final_status = await client.get_mcp_job_status(job_id)
            print(f"最终状态: {final_status.status}")
            
            # 演示等待作业完成方法（使用另一个作业）
            print("\n提交另一个作业并使用 wait_for_mcp_job_completion 方法...")
            another_job = await client.submit_mcp_job(
                name="quick_job",
                job_type="code_execution",
                data={
                    "code": "print('This is a quick job')",
                    "language": "python"
                }
            )
            
            print(f"快速作业已提交，ID: {another_job.job_id}")
            print("等待作业完成...")
            
            # 使用高级等待方法
            completion_status = await client.wait_for_mcp_job_completion(
                job_id=another_job.job_id,
                poll_interval=0.5,
                max_wait_time=10.0
            )
            
            print(f"作业完成状态: {completion_status.status}")
            if completion_status.result:
                print(f"结果: {completion_status.result}")
        except Exception as e:
            print(f"异步高级 MCP 方法示例失败: {e}")

# 主函数
async def main():
    # 运行同步示例
    sync_example()
    
    # 运行异步示例
    await async_example()

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
