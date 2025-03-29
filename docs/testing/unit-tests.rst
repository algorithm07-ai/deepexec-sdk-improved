u5355u5143u6d4bu8bd5
========

u5ba2u6237u7aefu6d4bu8bd5
--------

u5ba2u6237u7aefu6d4bu8bd5u4e3bu8981u6d4bu8bd5 DeepExecClient u7c7bu7684u529fu80fduff0cu5305u62ecu521du59cbu5316u3001u4f1au8bddu7ba1u7406u3001u4ee3u7801u6267u884cu548cu6587u672cu751fu6210u3002

.. code-block:: python

   # tests/unit/test_client.py u793au4f8b
   
   import pytest
   from unittest.mock import patch, MagicMock
   from src.core.client import DeepExecClient
   from src.core.exceptions import AuthenticationError, ExecutionError
   
   class TestDeepExecClient:
       @pytest.fixture
       def client(self):
           return DeepExecClient(
               deepseek_key="test_key",
               e2b_key="test_e2b_key"
           )
       
       def test_initialization(self, client):
           assert client.deepseek_key == "test_key"
           assert client.e2b_key == "test_e2b_key"
           assert client.session_id is None
       
       @patch("src.core.client.requests.post")
       def test_create_session(self, mock_post, client):
           mock_response = MagicMock()
           mock_response.json.return_value = {"session_id": "test_session"}
           mock_response.status_code = 200
           mock_post.return_value = mock_response
           
           session_id = client.create_session("test_user")
           
           assert session_id == "test_session"
           assert client.session_id == "test_session"
           mock_post.assert_called_once()

u534fu8baeu6d4bu8bd5
-------

u534fu8baeu6d4bu8bd5u4e3bu8981u6d4bu8bd5 MCP u534fu8baeu7684u5b9eu73b0uff0cu5305u62ecu8bf7u6c42u683cu5f0fu5316u548cu54cdu5e94u89e3u6790u3002

.. code-block:: python

   # tests/unit/test_protocol.py u793au4f8b
   
   import pytest
   from src.core.protocol import build_execution_request, parse_execution_response
   from src.core.exceptions import ProtocolError
   
   def test_build_execution_request():
       request = build_execution_request(
           code="print('Hello, World!')",
           language="python",
           session_id="test_session"
       )
       
       assert request["type"] == "execution"
       assert request["payload"]["code"] == "print('Hello, World!')"
       assert request["payload"]["language"] == "python"
       assert request["session_id"] == "test_session"
   
   def test_parse_execution_response_success():
       response = {
           "status": "success",
           "result": {
               "output": "Hello, World!\n",
               "execution_time": 0.05
           }
       }
       
       result = parse_execution_response(response)
       
       assert result.status == "success"
       assert result.output == "Hello, World!\n"
       assert result.execution_time == 0.05
       assert result.error is None

u5de5u5177u6d4bu8bd5
-------

u5de5u5177u6d4bu8bd5u4e3bu8981u6d4bu8bd5u5404u79cdu5de5u5177u51fdu6570uff0cu5305u62ecu914du7f6eu52a0u8f7du3001u9a8cu8bc1u548cu7ed3u679cu683cu5f0fu5316u3002

.. code-block:: python

   # tests/unit/test_utils.py u793au4f8b
   
   import pytest
   from src.core.utils import validate_language, validate_code, format_execution_result
   from src.core.exceptions import ValidationError
   
   def test_validate_language_success():
       # u6d4bu8bd5u6709u6548u8bedu8a00
       validate_language("python")
       validate_language("javascript")
       # u4e0du5e94u629bu51fau5f02u5e38
   
   def test_validate_language_invalid():
       # u6d4bu8bd5u65e0u6548u8bedu8a00
       with pytest.raises(ValidationError):
           validate_language("invalid_language")
   
   def test_validate_code_success():
       # u6d4bu8bd5u6709u6548u4ee3u7801
       validate_code("print('Hello')")
       # u4e0du5e94u629bu51fau5f02u5e38
   
   def test_validate_code_empty():
       # u6d4bu8bd5u7a7au4ee3u7801
       with pytest.raises(ValidationError):
           validate_code("")

u6d4bu8bd5u8986u76d6u7387
--------

u8981u8fd0u884cu6d4bu8bd5u5e76u751fu6210u8986u76d6u7387u62a5u544auff0cu53efu4ee5u4f7fu7528 pytest-cov u63d2u4ef6uff1a

.. code-block:: bash

   # u5b89u88c5 pytest-cov
   pip install pytest-cov
   
   # u8fd0u884cu6d4bu8bd5u5e76u751fu6210u8986u76d6u7387u62a5u544a
   pytest --cov=src tests/
   
   # u751fu6210 HTML u683cu5f0fu7684u8be6u7ec6u62a5u544a
   pytest --cov=src --cov-report=html tests/

u8fd9u5c06u751fu6210u4e00u4efdu8be6u7ec6u7684u8986u76d6u7387u62a5u544auff0cu663eu793au6bcfu4e2au6587u4ef6u548cu51fdu6570u7684u8986u76d6u7387u3002HTML u62a5u544au5c06u4fddu5b58u5728 htmlcov/ u76eeu5f55u4e2du3002
