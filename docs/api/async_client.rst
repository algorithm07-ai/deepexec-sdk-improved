异步客户端 API
==============

DeepExecAsyncClient
------------------

.. autoclass:: src.core.async_client.DeepExecAsyncClient
   :members:
   :undoc-members:
   :show-inheritance:
   
   .. automethod:: __aenter__
   .. automethod:: __aexit__
   
使用示例
-------

.. code-block:: python

   import asyncio
   from src.core.async_client import DeepExecAsyncClient
   
   async def main():
       async with DeepExecAsyncClient(
           deepseek_key="your_key",
           e2b_key="your_e2b_key"
       ) as client:
           session_id = await client.create_session("user_id")
           result = await client.execute_code("print('Hello, World!')", "python")
           print(f"Output: {result.output}")
   
   if __name__ == "__main__":
       asyncio.run(main())
