测试框架
========

概述
----

DeepExec SDK 提供了全面的测试框架，支持单元测试和集成测试，以确保代码质量和功能稳定性。测试框架的目标是实现以下覆盖率：

* 核心逻辑: ≥ 95%
* 整体覆盖率: ≥ 85%

测试目录结构
----------

.. code-block:: text

   tests/
   ├── unit/                  # 单元测试
   │   ├── test_client.py     # 客户端单元测试
   │   ├── test_protocol.py   # 协议处理单元测试
   │   └── test_utils.py      # 工具函数单元测试
   ├── integration/           # 集成测试
   │   ├── test_auth.py       # 认证集成测试
   │   ├── test_execution.py  # 代码执行集成测试
   │   └── test_connection.py # 连接处理集成测试
   └── conftest.py            # 测试配置和模拟服务器

单元测试
-------

单元测试专注于测试各个组件的独立功能，包括：

* **客户端测试**: 测试 DeepExecClient 类的初始化、会话管理、代码执行和文本生成功能
* **协议测试**: 测试 MCP 协议实现，包括请求格式化、响应解析和错误处理
* **工具测试**: 测试配置加载、验证和结果格式化工具

.. toctree::
   :maxdepth: 1
   
   unit-tests

集成测试
-------

集成测试专注于测试组件之间的交互和端到端功能，包括：

* **执行测试**: 测试代码执行功能，包括成功路径测试、超时处理、错误情况和并发执行
* **认证测试**: 测试认证流程，包括成功认证、无效 API 密钥和令牌过期
* **连接测试**: 测试连接处理，包括重试机制、超时处理和并发连接

.. toctree::
   :maxdepth: 1
   
   integration-tests

模拟服务器
--------

测试框架包含一个模拟服务器，用于在不需要实际 API 访问的情况下进行测试。模拟服务器提供以下功能：

* 模拟代码执行响应
* 模拟文本生成响应
* 模拟会话创建和管理
* 模拟错误情况和超时
* 请求记录和分析

.. toctree::
   :maxdepth: 1
   
   mock-server

运行测试
-------

使用 pytest 运行测试：

.. code-block:: bash

   # 运行所有测试
   pytest
   
   # 运行单元测试
   pytest tests/unit/
   
   # 运行集成测试
   pytest tests/integration/
   
   # 运行特定测试文件
   pytest tests/unit/test_client.py
   
   # 运行特定测试函数
   pytest tests/unit/test_client.py::TestDeepExecClient::test_execute_code_success
