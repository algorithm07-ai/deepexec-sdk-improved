日志系统 API
==========

.. automodule:: src.core.logging
   :members:
   :undoc-members:
   :show-inheritance:

配置日志
-------

.. autofunction:: src.core.logging.configure_logging

获取日志记录器
-----------

.. autofunction:: src.core.logging.get_logger

日志请求和响应
-----------

.. autofunction:: src.core.logging.log_request
.. autofunction:: src.core.logging.log_response

使用示例
-------

基本配置
^^^^^^^

.. code-block:: python

   from src.core.logging import configure_logging
   import logging
   
   # 配置基本日志
   logger = configure_logging(level=logging.INFO)
   logger.info("DeepExec SDK 已初始化")

高级配置
^^^^^^^

.. code-block:: python

   from src.core.logging import configure_logging, get_logger
   import logging
   import os
   
   # 创建日志目录
   os.makedirs("logs", exist_ok=True)
   
   # 配置详细日志，包括文件输出
   configure_logging(
       level=logging.DEBUG,
       log_file="logs/deepexec.log",
       format_string="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
   )
   
   # 获取模块特定的日志记录器
   client_logger = get_logger("client")
   client_logger.debug("客户端初始化中...")
   
   # 在异步客户端中使用
   from src.core.async_client import DeepExecAsyncClient
   
   async def main():
       client = DeepExecAsyncClient()
       client.logger = get_logger("async_client")
       client.logger.info("异步客户端已创建")
