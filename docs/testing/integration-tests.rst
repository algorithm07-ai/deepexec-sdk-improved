u96c6u6210u6d4bu8bd5
========

u4ee3u7801u6267u884cu6d4bu8bd5
---------

u4ee3u7801u6267u884cu6d4bu8bd5u4e3bu8981u6d4bu8bd5u5ba2u6237u7aefu4e0eu670du52a1u5668u4e4bu95f4u7684u4ea4u4e92uff0cu5305u62ecu6210u529fu6267u884cu3001u9519u8befu5904u7406u548cu8d85u65f6u60c5u51b5u3002

.. code-block:: python

   # tests/integration/test_execution.py u793au4f8b
   
   import pytest
   from src.core.client import DeepExecClient
   from src.core.exceptions import ExecutionError, TimeoutError
   
   class TestCodeExecution:
       @pytest.fixture
       def client(self, mock_server):
           # mock_server u7531 conftest.py u63d0u4f9b
           client = DeepExecClient(
               deepseek_key="test_key",
               e2b_key="test_e2b_key",
               base_url=mock_server.url
           )
           client.create_session("test_user")
           return client
       
       def test_execute_code_success(self, client, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u8fd4u56deu6210u529fu54cdu5e94
           mock_server.add_execution_response(
               code="print('Hello, World!')",
               language="python",
               response={
                   "status": "success",
                   "result": {
                       "output": "Hello, World!\n",
                       "execution_time": 0.05
                   }
               }
           )
           
           # u6267u884cu4ee3u7801
           result = client.execute_code("print('Hello, World!')", "python")
           
           # u9a8cu8bc1u7ed3u679c
           assert result.status == "success"
           assert result.output == "Hello, World!\n"
           assert result.execution_time == 0.05
       
       def test_execute_code_error(self, client, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u8fd4u56deu9519u8befu54cdu5e94
           mock_server.add_execution_response(
               code="print(undefined_variable)",
               language="python",
               response={
                   "status": "error",
                   "result": {
                       "error": "NameError: name 'undefined_variable' is not defined",
                       "execution_time": 0.01
                   }
               }
           )
           
           # u6267u884cu4ee3u7801
           result = client.execute_code("print(undefined_variable)", "python")
           
           # u9a8cu8bc1u7ed3u679c
           assert result.status == "error"
           assert "NameError" in result.error
           assert result.execution_time == 0.01

u8ba4u8bc1u6d4bu8bd5
-------

u8ba4u8bc1u6d4bu8bd5u4e3bu8981u6d4bu8bd5u5ba2u6237u7aefu7684u8ba4u8bc1u6d41u7a0buff0cu5305u62ecu6210u529fu8ba4u8bc1u548cu5931u8d25u60c5u51b5u3002

.. code-block:: python

   # tests/integration/test_auth.py u793au4f8b
   
   import pytest
   from src.core.client import DeepExecClient
   from src.core.exceptions import AuthenticationError
   
   class TestAuthentication:
       def test_authentication_success(self, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u8fd4u56deu6210u529fu54cdu5e94
           mock_server.add_auth_response(
               api_key="valid_key",
               response={
                   "status": "success",
                   "session_id": "test_session"
               }
           )
           
           # u521bu5efau5ba2u6237u7aefu5e76u8ba4u8bc1
           client = DeepExecClient(
               deepseek_key="valid_key",
               e2b_key="valid_e2b_key",
               base_url=mock_server.url
           )
           
           session_id = client.create_session("test_user")
           
           # u9a8cu8bc1u7ed3u679c
           assert session_id == "test_session"
           assert client.session_id == "test_session"
       
       def test_authentication_failure(self, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u8fd4u56deu5931u8d25u54cdu5e94
           mock_server.add_auth_response(
               api_key="invalid_key",
               response={
                   "status": "error",
                   "message": "Invalid API key"
               },
               status_code=401
           )
           
           # u521bu5efau5ba2u6237u7aef
           client = DeepExecClient(
               deepseek_key="invalid_key",
               e2b_key="valid_e2b_key",
               base_url=mock_server.url
           )
           
           # u9a8cu8bc1u8ba4u8bc1u5931u8d25
           with pytest.raises(AuthenticationError):
               client.create_session("test_user")

u8fdeu63a5u6d4bu8bd5
-------

u8fdeu63a5u6d4bu8bd5u4e3bu8981u6d4bu8bd5u5ba2u6237u7aefu7684u8fdeu63a5u5904u7406u80fdu529buff0cu5305u62ecu91cdu8bd5u673au5236u548cu8d85u65f6u5904u7406u3002

.. code-block:: python

   # tests/integration/test_connection.py u793au4f8b
   
   import pytest
   import time
   from src.core.client import DeepExecClient
   from src.core.exceptions import ConnectionError, TimeoutError
   
   class TestConnection:
       def test_retry_mechanism(self, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u5148u8fd4u56deu5931u8d25uff0cu7136u540eu6210u529f
           mock_server.add_execution_response(
               code="print('test')",
               language="python",
               response={
                   "status": "error",
                   "message": "Service temporarily unavailable"
               },
               status_code=503,
               times=2  # u524du4e24u6b21u8bf7u6c42u5931u8d25
           )
           
           mock_server.add_execution_response(
               code="print('test')",
               language="python",
               response={
                   "status": "success",
                   "result": {
                       "output": "test\n",
                       "execution_time": 0.01
                   }
               }
           )
           
           # u521bu5efau5ba2u6237u7aefu5e76u914du7f6eu91cdu8bd5
           client = DeepExecClient(
               deepseek_key="test_key",
               e2b_key="test_e2b_key",
               base_url=mock_server.url,
               max_retries=3,
               retry_delay=0.1  # u7f29u77edu6d4bu8bd5u65f6u95f4
           )
           client.create_session("test_user")
           
           # u6267u884cu4ee3u7801uff0cu5e94u8be5u5728u7b2cu4e09u6b21u5c1du8bd5u65f6u6210u529f
           result = client.execute_code("print('test')", "python")
           
           # u9a8cu8bc1u7ed3u679c
           assert result.status == "success"
           assert result.output == "test\n"
           assert mock_server.request_count == 3  # u603bu5171u5c1du8bd5u4e86u4e09u6b21
       
       def test_timeout_handling(self, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u6a21u62dfu8d85u65f6
           mock_server.add_execution_response(
               code="time.sleep(10)",
               language="python",
               delay=2.0  # u6a21u62dfu54cdu5e94u5ef6u8fdf
           )
           
           # u521bu5efau5ba2u6237u7aefu5e76u8bbeu7f6eu8d85u65f6
           client = DeepExecClient(
               deepseek_key="test_key",
               e2b_key="test_e2b_key",
               base_url=mock_server.url,
               timeout=1.0  # 1u79d2u8d85u65f6
           )
           client.create_session("test_user")
           
           # u9a8cu8bc1u8d85u65f6u5f02u5e38
           with pytest.raises(TimeoutError):
               client.execute_code("time.sleep(10)", "python")

u5e76u53d1u6d4bu8bd5
-------

u5e76u53d1u6d4bu8bd5u4e3bu8981u6d4bu8bd5u5ba2u6237u7aefu5728u5e76u53d1u60c5u51b5u4e0bu7684u8868u73b0uff0cu7279u522bu662fu4f7fu7528u5f02u6b65u5ba2u6237u7aefu65f6u3002

.. code-block:: python

   # tests/integration/test_async_client.py u793au4f8b
   
   import pytest
   import asyncio
   from src.core.async_client import DeepExecAsyncClient
   
   @pytest.mark.asyncio
   class TestAsyncClient:
       @pytest.fixture
       async def async_client(self, mock_server):
           async with DeepExecAsyncClient(
               deepseek_key="test_key",
               e2b_key="test_e2b_key",
               base_url=mock_server.url
           ) as client:
               await client.create_session("test_user")
               yield client
       
       async def test_concurrent_executions(self, async_client, mock_server):
           # u914du7f6eu6a21u62dfu670du52a1u5668u54cdu5e94
           for i in range(5):
               mock_server.add_execution_response(
                   code=f"print({i})",
                   language="python",
                   response={
                       "status": "success",
                       "result": {
                           "output": f"{i}\n",
                           "execution_time": 0.01
                       }
                   },
                   delay=0.1  # u6a21u62dfu5c0fu5ef6u8fdf
               )
           
           # u5e76u53d1u6267u884c 5 u4e2au4ee3u7801u7247u6bb5
           tasks = [
               async_client.execute_code(f"print({i})", "python")
               for i in range(5)
           ]
           
           # u7b49u5f85u6240u6709u4efbu52a1u5b8cu6210
           results = await asyncio.gather(*tasks)
           
           # u9a8cu8bc1u7ed3u679c
           for i, result in enumerate(results):
               assert result.status == "success"
               assert result.output == f"{i}\n"
           
           # u9a8cu8bc1u5e76u53d1u6267u884cu6bd4u4e32u884cu5feb
           assert mock_server.max_concurrent_requests > 1
