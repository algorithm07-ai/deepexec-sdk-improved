# -*- coding: utf-8 -*-
# 编码测试脚本 - 使用直接的Python执行而非pytest

import os
import sys
import io

# 强制标准流使用UTF-8
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 设置环境变量
os.environ["PYTHONUTF8"] = "1"  # Python 3.7+
os.environ["PYTHONIOENCODING"] = "utf-8"

# 添加项目根目录到Python路径
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入需要的模块
from unittest.mock import patch, MagicMock

# 打印当前编码信息
print(f"系统默认编码: {sys.getdefaultencoding()}")
print(f"标准输入编码: {sys.stdin.encoding}")
print(f"标准输出编码: {sys.stdout.encoding}")
print(f"标准错误编码: {sys.stderr.encoding}")
print(f"文件系统编码: {sys.getfilesystemencoding()}")

# 测试中文输出
print("\n测试中文输出: 这是一段中文测试文本")

# 模拟客户端测试
print("\n开始模拟客户端测试...")

# 模拟DeepExecClient类
class MockDeepExecClient:
    def __init__(self, endpoint="mock://"):
        self.endpoint = endpoint
        self.session_id = None
        print(f"初始化客户端: {endpoint}")
    
    def create_session(self, user_id):
        self.session_id = f"session_{user_id}_{id(self)}"
        print(f"创建会话: {self.session_id}")
        return self.session_id
    
    def execute_code(self, code, language="python"):
        print(f"执行代码: {language}\n{code}")
        # 模拟执行结果
        class Result:
            def __init__(self):
                self.output = "模拟输出结果\n成功执行代码"
                self.exit_code = 0
                self.execution_time = 100
                self.memory_usage = 10
            
            def __str__(self):
                return f"Result(output='{self.output}', exit_code={self.exit_code})"
        
        return Result()
    
    def generate_text(self, prompt, model="test-model"):
        print(f"生成文本: {prompt}")
        # 模拟生成结果
        class Result:
            def __init__(self):
                self.text = "这是生成的文本响应"
                self.model = model
                self.usage = type('Usage', (), {
                    'prompt_tokens': 10,
                    'completion_tokens': 50,
                    'total_tokens': 60,
                    '__str__': lambda self: f"Usage(total_tokens={self.total_tokens})"
                })()
            
            def __str__(self):
                return f"Result(text='{self.text}', model='{self.model}')"
        
        return Result()


def test_client_methods():
    """测试客户端方法"""
    # 创建模拟客户端
    client = MockDeepExecClient(endpoint="mock://test")
    
    # 测试创建会话
    session_id = client.create_session("test_user")
    print(f"会话ID: {session_id}")
    
    # 测试代码执行
    code = "print('Hello, World!')\nresult = 42 * 2\nprint(f'The answer is {result}')"
    result = client.execute_code(code, "python")
    print(f"执行结果: {result}")
    
    # 测试文本生成
    prompt = "解释什么是人工智能"
    result = client.generate_text(prompt, "test-model")
    print(f"生成结果: {result}")
    
    print("\n所有测试完成!")


if __name__ == "__main__":
    try:
        test_client_methods()
    except Exception as e:
        print(f"测试过程中出现错误: {type(e).__name__}: {str(e)}")
