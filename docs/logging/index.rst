u65e5u5fd7u7cfbu7edf
========

u6982u8ff0
----

DeepExec SDK u63d0u4f9bu4e86u5168u9762u7684u65e5u5fd7u7cfbu7edfuff0cu53efu4ee5u5e2eu52a9u5f00u53d1u4ebau5458u548cu7528u6237u8ffd u8e2au548cu8c03u8bd5u5e94u7528u7a0bu5e8fu3002u65e5u5fd7u7cfbu7edfu652fu6301u591au79cdu8f93u51fau65b9u5f0fuff0cu5305u62ecu63a7u5236u53f0u548cu6587u4ef6u65e5u5fd7uff0cu5e76u63d0u4f9bu4e86u7075u6d3bu7684u914du7f6eu9009u9879u3002

u4e3bu8981u7279u70b9
-------

* **u7075u6d3bu914du7f6e**: u53efu4ee5u6839u636eu9700u8981u8c03u6574u65e5u5fd7u7ea7u522bu548cu683cu5f0f
* **u591au79cdu8f93u51fau65b9u5f0f**: u652fu6301u63a7u5236u53f0u548cu6587u4ef6u8f93u51fa
* **u5c42u6b21u7ed3u6784**: u652fu6301u6a21u5757u7ea7u522bu7684u65e5u5fd7u8bb0u5f55u5668
* **u654fu611fu4fe1u606fu4fdd u62a4**: u81eau52a8u5c4fu853du654fu611fu4fe1u606fuff0cu5982 API u5bc6u94a5
* **u7b2cu4e09u65b9u5e93u65e5u5fd7u7ba1u7406**: u6291u5236u975eu5fc5u8981u7684u7b2cu4e09u65b9u5e93u65e5u5fd7

u57fau672cu4f7fu7528
-------

.. code-block:: python

   from src.core.logging import configure_logging
   import logging
   
   # u914du7f6eu57fau672cu65e5u5fd7
   logger = configure_logging(level=logging.INFO)
   
   # u4f7fu7528u65e5u5fd7u8bb0u5f55u4fe1u606f
   logger.info("DeepExec SDK u521du59cbu5316u5b8cu6210")
   logger.debug("u8fd9u662fu4e00u6761u8c03u8bd5u4fe1u606f")
   logger.warning("u8fd9u662fu4e00u6761u8b66u544au4fe1u606f")
   logger.error("u8fd9u662fu4e00u6761u9519u8befu4fe1u606f")

u914du7f6eu6587u4ef6u65e5u5fd7
-----------

.. code-block:: python

   from src.core.logging import configure_logging
   import logging
   import os
   
   # u521bu5efau65e5u5fd7u76eeu5f55
   os.makedirs("logs", exist_ok=True)
   
   # u914du7f6eu540cu65f6u8f93u51fau5230u63a7u5236u53f0u548cu6587u4ef6
   logger = configure_logging(
       level=logging.DEBUG,
       log_file="logs/deepexec.log"
   )
   
   logger.info("u65e5u5fd7u5c06u540cu65f6u8f93u51fau5230u63a7u5236u53f0u548cu6587u4ef6")

u81eau5b9au4e49u65e5u5fd7u683cu5f0f
-----------

.. code-block:: python

   from src.core.logging import configure_logging
   import logging
   
   # u81eau5b9au4e49u65e5u5fd7u683cu5f0f
   custom_format = "%(asctime)s - [%(levelname)s] - %(name)s - %(filename)s:%(lineno)d - %(message)s"
   
   logger = configure_logging(
       level=logging.INFO,
       format_string=custom_format
   )
   
   logger.info("u4f7fu7528u81eau5b9au4e49u683cu5f0fu7684u65e5u5fd7u4fe1u606f")

u83b7u53d6u6a21u5757u7ea7u522bu7684u65e5u5fd7u8bb0u5f55u5668
---------------

.. code-block:: python

   from src.core.logging import configure_logging, get_logger
   import logging
   
   # u914du7f6eu4e3bu65e5u5fd7u8bb0u5f55u5668
   configure_logging(level=logging.INFO)
   
   # u83b7u53d6u4e0du540cu6a21u5757u7684u65e5u5fd7u8bb0u5f55u5668
   client_logger = get_logger("client")
   protocol_logger = get_logger("protocol")
   utils_logger = get_logger("utils")
   
   # u4f7fu7528u6a21u5757u7ea7u522bu7684u65e5u5fd7u8bb0u5f55u5668
   client_logger.info("u5ba2u6237u7aefu6a21u5757u65e5u5fd7")
   protocol_logger.debug("u534fu8baeu6a21u5757u8c03u8bd5u4fe1u606f")
   utils_logger.warning("u5de5u5177u6a21u5757u8b66u544au4fe1u606f")

u5728u5ba2u6237u7aefu4e2du4f7fu7528u65e5u5fd7
--------------

.. code-block:: python

   from src.core.client import DeepExecClient
   from src.core.logging import configure_logging, get_logger
   import logging
   
   # u914du7f6eu65e5u5fd7
   configure_logging(level=logging.DEBUG, log_file="deepexec.log")
   
   # u521bu5efau5ba2u6237u7aef
   client = DeepExecClient(
       deepseek_key="your_deepseek_key",
       e2b_key="your_e2b_key"
   )
   
   # u83b7u53d6u5ba2u6237u7aefu7684u65e5u5fd7u8bb0u5f55u5668
   client.logger = get_logger("client")
   
   # u4f7fu7528u5ba2u6237u7aefu65b9u6cd5
   client.logger.info("u521bu5efau4f1au8bdd...")
   session_id = client.create_session("user_id")
   client.logger.info(f"u4f1au8bddu521bu5efau6210u529fuff0cID: {session_id}")
   
   # u6267u884cu4ee3u7801
   client.logger.info("u6267u884cu4ee3u7801...")
   result = client.execute_code("print('Hello, World!')", "python")
   client.logger.info(f"u4ee3u7801u6267u884cu6210u529fuff0cu8f93u51fa: {result.output}")

u8bb0u5f55u8bf7u6c42u548cu54cdu5e94
-----------

.. code-block:: python

   from src.core.logging import configure_logging, get_logger, log_request, log_response
   import logging
   import requests
   
   # u914du7f6eu65e5u5fd7
   configure_logging(level=logging.DEBUG)
   logger = get_logger("api")
   
   # u53d1u9001u8bf7u6c42
   url = "https://api.example.com/data"
   headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer your_token"
   }
   data = {"query": "example"}
   
   # u8bb0u5f55u8bf7u6c42
   log_request(logger, "POST", url, headers, data)
   
   # u53d1u9001u8bf7u6c42
   response = requests.post(url, json=data, headers=headers)
   
   # u8bb0u5f55u54cdu5e94
   log_response(logger, response.status_code, response.headers, response.json())

u4e0eu5f02u6b65u5ba2u6237u7aefu96c6u6210
-----------

.. code-block:: python

   import asyncio
   from src.core.async_client import DeepExecAsyncClient
   from src.core.logging import configure_logging, get_logger
   import logging
   
   # u914du7f6eu65e5u5fd7
   configure_logging(level=logging.DEBUG, log_file="async_client.log")
   logger = get_logger("async_client")
   
   async def main():
       logger.info("u521du59cbu5316u5f02u6b65u5ba2u6237u7aef")
       
       async with DeepExecAsyncClient(
           deepseek_key="your_deepseek_key",
           e2b_key="your_e2b_key",
           logger=logger  # u4f20u5165u65e5u5fd7u8bb0u5f55u5668
       ) as client:
           logger.info("u521bu5efau4f1au8bdd")
           session_id = await client.create_session("user_id")
           logger.info(f"u4f1au8bddu521bu5efau6210u529fuff0cID: {session_id}")
           
           logger.info("u6267u884cu4ee3u7801")
           result = await client.execute_code("print('Hello, World!')", "python")
           logger.info(f"u4ee3u7801u6267u884cu6210u529fuff0cu8f93u51fa: {result.output}")
   
   if __name__ == "__main__":
       asyncio.run(main())

API u53c2u8003
-------

.. toctree::
   :maxdepth: 2
   
   ../api/logging
