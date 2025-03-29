u5f02u6b65u5ba2u6237u7aef
========

u6982u8ff0
----

DeepExec SDK u63d0u4f9bu4e86u5f3au5927u7684u5f02u6b65u5ba2u6237u7aefuff0cu5141u8bb8u5e94u7528u7a0bu5e8fu5728u4e0du963bu585eu4e3bu7ebfu7a0bu7684u60c5u51b5u4e0bu6267u884cu4ee3u7801u548cu751fu6210u6587u672cu3002u8fd9u5bf9u4e8eu9700u8981u5904u7406u5927u91cfu5e76u53d1u8bf7u6c42u7684u5e94u7528u7a0bu5e8fu5c24u4e3au91cdu8981u3002

u4e3bu8981u7279u70b9
-------

* **u5f02u6b65u4e0au4e0bu6587u7ba1u7406**: u652fu6301 Python u7684 `async with` u8bed u6cd5
* **u5e76u53d1u8bf7u6c42**: u652fu6301u540cu65f6u53d1u9001u591au4e2au4ee3u7801u6267u884cu8bf7u6c42
* **u6539u8fdeu63a5u91cdu8bd5**: u81eau52a8u5904u7406u7f51u7edcu9519u8befu5e76u5b9eu73b0u6307u6570u9000u907fu7b56u7565
* **u8d44u6e90u7ba1u7406**: u81eau52a8u5173u95edu4e0du518du4f7fu7528u7684u8fdeu63a5
* **u5f02u5e38u5904u7406**: u5b8cu5584u7684u5f02u6b65u5f02u5e38u5904u7406u673au5236

u5b89u88c5
----

.. code-block:: bash

   pip install deepexec-sdk

u57fau672cu4f7fu7528
-------

.. code-block:: python

   import asyncio
   from src.core.async_client import DeepExecAsyncClient
   
   async def main():
       # u521bu5efau5f02u6b65u5ba2u6237u7aef
       async with DeepExecAsyncClient(
           deepseek_key="your_deepseek_key",
           e2b_key="your_e2b_key"
       ) as client:
           # u521bu5efau4f1au8bdd
           session_id = await client.create_session("user_id")
           print(f"Created session: {session_id}")
           
           # u6267u884cu4ee3u7801
           result = await client.execute_code(
               "print('Hello, async world!')", 
               "python"
           )
           print(f"Output: {result.output}")
           
           # u751fu6210u6587u672c
           generation = await client.generate_text(
               "Tell me a joke about programming"
           )
           print(f"Generated text: {generation.text}")
   
   if __name__ == "__main__":
       asyncio.run(main())

u5e76u53d1u8bf7u6c42
-------

u5f02u6b65u5ba2u6237u7aefu7684u4e00u4e2au4e3bu8981u4f18u52bfu662fu80fdu5904u7406u5e76u53d1u8bf7u6c42uff0cu4f8bu5982u540cu65f6u6267u884cu591au4e2au4ee3u7801u7247u6bb5uff1a

.. code-block:: python

   import asyncio
   from src.core.async_client import DeepExecAsyncClient
   
   async def main():
       async with DeepExecAsyncClient(
           deepseek_key="your_deepseek_key",
           e2b_key="your_e2b_key"
       ) as client:
           await client.create_session("user_id")
           
           # u5b9au4e49u591au4e2au4ee3u7801u6267u884cu4efbu52a1
           tasks = [
               client.execute_code(f"print('Task {i}')", "python")
               for i in range(5)
           ]
           
           # u5e76u53d1u6267u884cu6240u6709u4efbu52a1
           results = await asyncio.gather(*tasks)
           
           # u5904u7406u7ed3u679c
           for i, result in enumerate(results):
               print(f"Task {i} output: {result.output}")
   
   if __name__ == "__main__":
       asyncio.run(main())

u9519u8befu5904u7406
-------

u5f02u6b65u5ba2u6237u7aefu63d0u4f9bu4e86u5168u9762u7684u9519u8befu5904u7406u673au5236uff1a

.. code-block:: python

   import asyncio
   from src.core.async_client import DeepExecAsyncClient
   from src.core.exceptions import (
       AuthenticationError, 
       ExecutionError, 
       ConnectionError, 
       TimeoutError
   )
   
   async def main():
       try:
           async with DeepExecAsyncClient(
               deepseek_key="your_deepseek_key",
               e2b_key="your_e2b_key",
               max_retries=3,  # u8fdeu63a5u5931u8d25u65f6u91cdu8bd5 3 u6b21
               retry_delay=1.0  # u521du59cbu91cdu8bd5u5ef6u8fdf 1 u79d2uff0cu4f1au6307u6570u589eu957f
           ) as client:
               await client.create_session("user_id")
               
               try:
                   # u5c1du8bd5u6267u884cu53efu80fdu5931u8d25u7684u4ee3u7801
                   result = await client.execute_code(
                       "print(undefined_variable)", 
                       "python"
                   )
               except ExecutionError as e:
                   print(f"Execution error: {e}")
               
               # u5c1du8bd5u8d85u65f6u60c5u51b5
               try:
                   result = await client.execute_code(
                       "import time; time.sleep(30)", 
                       "python",
                       timeout=5  # 5 u79d2u8d85u65f6
                   )
               except TimeoutError as e:
                   print(f"Timeout error: {e}")
               
       except AuthenticationError as e:
           print(f"Authentication failed: {e}")
       except ConnectionError as e:
           print(f"Connection error: {e}")
   
   if __name__ == "__main__":
       asyncio.run(main())

u81eau5b9au4e49u914du7f6e
---------

u5f02u6b65u5ba2u6237u7aefu63d0u4f9bu4e86u591au79cdu914du7f6eu9009u9879uff0cu53efu4ee5u6839u636eu9700u8981u8fdb u884cu8c03u6574uff1a

.. code-block:: python

   import asyncio
   import logging
   from src.core.async_client import DeepExecAsyncClient
   from src.core.logging import configure_logging
   
   # u914du7f6eu65e5u5fd7
   logger = configure_logging(level=logging.DEBUG)
   
   async def main():
       async with DeepExecAsyncClient(
           deepseek_key="your_deepseek_key",
           e2b_key="your_e2b_key",
           base_url="https://api.deepseek.com",  # u81eau5b9au4e49 API u7aef u70b9
           max_retries=5,                        # u6700u5927u91cdu8bd5u6b21u6570
           retry_delay=0.5,                      # u521du59cbu91cdu8bd5u5ef6u8fdf
           retry_backoff=2.0,                    # u91cdu8bd5u9000u907fu7cfbu6570
           timeout=10.0,                         # u8bf7u6c42u8d85u65f6u65f6u95f4
           max_concurrent_requests=20,           # u6700u5927u5e76u53d1u8bf7u6c42u6570
           logger=logger                         # u81eau5b9au4e49u65e5u5fd7u8bb0u5f55u5668
       ) as client:
           # u4f7fu7528u5ba2u6237u7aef...
           pass
   
   if __name__ == "__main__":
       asyncio.run(main())

API u53c2u8003
-------

.. toctree::
   :maxdepth: 2
   
   ../api/async_client

u4e0eu540cu6b65u5ba2u6237u7aefu7684u5dee u5f02
--------------

u5f02u6b65u5ba2u6237u7aefu4e0eu540cu6b65u5ba2u6237u7aefu7684u4e3bu8981u5dee u5f02uff1a

1. **u4f7fu7528u65b9u5f0f**: 
   - u5f02u6b65u5ba2u6237u7aefu4f7fu7528 `async/await` u8bed u6cd5
   - u540cu6b65u5ba2u6237u7aefu4f7fu7528u5e38u89c4u51fdu6570u8c03u7528

2. **u4e0au4e0bu6587u7ba1u7406**:
   - u5f02u6b65u5ba2u6237u7aefu4f7fu7528 `async with` u8bed u6cd5
   - u540cu6b65u5ba2u6237u7aefu4f7fu7528 `with` u8bed u6cd5

3. **u5e76u53d1u80fdu529b**:
   - u5f02u6b65u5ba2u6237u7aefu652fu6301u771fu6b63u7684u5e76u53d1u8bf7u6c42
   - u540cu6b65u5ba2u6237u7aefu9700u8981u4f7fu7528u7ebfu7a0bu6c60u6216u591au8fdb u7a0bu5b9eu73b0u5e76u53d1

4. **u6027u80fd**:
   - u5f02u6b65u5ba2u6237u7aefu5728u9ad8u5e76u53d1u60c5u51b5u4e0bu6027u80fdu66f4u597d
   - u540cu6b65u5ba2u6237u7aefu5b9eu73b0u66f4u7b80u5355uff0cu66f4u5bb9u6613u7406u89e3

5. **u5f02u5e38u5904u7406**:
   - u5f02u6b65u5ba2u6237u7aefu9700u8981u4f7fu7528 `try/except` u6355u83b7u5f02u6b65u5f02u5e38
   - u540cu6b65u5ba2u6237u7aefu4f7fu7528u6807u51c6u7684u5f02u5e38u5904u7406u673au5236

u9009u62e9u5408u9002u7684u5ba2u6237u7aef
-----------

* u5982u679cu60a8u7684u5e94u7528u7a0bu5e8fu9700u8981u5904u7406u5927u91cfu5e76u53d1u8bf7u6c42uff0cu9009u62e9u5f02u6b65u5ba2u6237u7aef
* u5982u679cu60a8u7684u5e94u7528u7a0bu5e8fu5df2u7ecfu662fu5f02u6b65u67b6u6784uff08u4f8bu5982 FastAPI u6216 aiohttp u5e94u7528uff09uff0cu9009u62e9u5f02u6b65u5ba2u6237u7aef
* u5982u679cu60a8u9700u8981u7b80u5355u76f4u63a5u7684u5b9eu73b0uff0cu9009u62e9u540cu6b65u5ba2u6237u7aef
* u5982u679cu60a8u7684u5e94u7528u7a0bu5e8fu662fu811au672cu6216u547du4ee4u884cu5de5u5177uff0cu540cu6b65u5ba2u6237u7aefu53efu80fdu66f4u5408u9002
