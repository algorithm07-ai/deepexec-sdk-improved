u6a21u62dfu670du52a1u5668
========

u6982u8ff0
----

DeepExec SDK u6d4bu8bd5u6846u67b6u5305u542bu4e00u4e2au5f3au5927u7684u6a21u62dfu670du52a1u5668uff0cu7528u4e8eu6a21u62dfu4e0eu771fu5b9eu670du52a1u5668u7684u4ea4u4e92u3002u8fd9u4f7fu5f97u6d4bu8bd5u53efu4ee5u5728u4e0du9700u8981u5b9eu9645 API u8bbfu95eeu7684u60c5u51b5u4e0bu8fd0u884cuff0cu63d0u9ad8u4e86u6d4bu8bd5u7684u7a33u5b9au6027u548cu53efu91cdu590du6027u3002

u6a21u62dfu670du52a1u5668u7684u4e3bu8981u529fu80fd
--------------

1. **u6a21u62dfu4ee3u7801u6267u884cu54cdu5e94**: u6a21u62dfu4e0du540cu8bedu8a00u7684u4ee3u7801u6267u884cu7ed3u679c
2. **u6a21u62dfu6587u672cu751fu6210u54cdu5e94**: u6a21u62dfu6587u672cu751fu6210u548cu5bf9u8bddu54cdu5e94
3. **u6a21u62dfu8ba4u8bc1u6d41u7a0b**: u6a21u62dfu4f1au8bddu521bu5efau548cu7ba1u7406
4. **u6a21u62dfu9519u8befu60c5u51b5**: u6a21u62dfu5404u79cdu5f02u5e38u60c5u51b5uff0cu5982u8ba4u8bc1u5931u8d25u3001u6267u884cu9519u8befu7b49
5. **u6a21u62dfu7f51u7edcu60c5u51b5**: u6a21u62dfu8d85u65f6u3001u8fdeu63a5u5931u8d25u7b49u7f51u7edcu95eeu9898
6. **u8bf7u6c42u8bb0u5f55u548cu5206u6790**: u8bb0u5f55u5e76u5206u6790u6240u6709u8bf7u6c42uff0cu4fbfu4e8eu8c03u8bd5

u5b9eu73b0u7ec6u8282
-------

u6a21u62dfu670du52a1u5668u5b9eu73b0u5728 `tests/conftest.py` u6587u4ef6u4e2duff0cu4f5cu4e3a pytest u7684u56fau5b9au88c5u7f6eu3002

.. code-block:: python

   # tests/conftest.py u4e2du7684u6a21u62dfu670du52a1u5668u5b9eu73b0u793au4f8b
   
   import pytest
   import threading
   import time
   import json
   from http.server import HTTPServer, BaseHTTPRequestHandler
   from urllib.parse import urlparse, parse_qs
   
   class MockServerHandler(BaseHTTPRequestHandler):
       def do_POST(self):
           # u83b7u53d6u8bf7u6c42u6570u636e
           content_length = int(self.headers.get('Content-Length', 0))
           post_data = self.rfile.read(content_length).decode('utf-8')
           request_data = json.loads(post_data) if post_data else {}
           
           # u8bb0u5f55u8bf7u6c42
           self.server.record_request(self.path, request_data)
           
           # u5904u7406u6a21u62dfu5ef6u8fdf
           if self.server.response_delay > 0:
               time.sleep(self.server.response_delay)
           
           # u5904u7406u8bf7u6c42
           if self.path == '/api/session':
               self._handle_session_request(request_data)
           elif self.path == '/api/execute':
               self._handle_execution_request(request_data)
           elif self.path == '/api/generate':
               self._handle_generation_request(request_data)
           else:
               self._send_response(404, {'status': 'error', 'message': 'Not found'})
       
       def _handle_session_request(self, request_data):
           # u5904u7406u8ba4u8bc1u548cu4f1au8bddu521bu5efau8bf7u6c42
           api_key = request_data.get('api_key')
           response = self.server.get_auth_response(api_key)
           status_code = 200 if response.get('status') == 'success' else 401
           self._send_response(status_code, response)
       
       def _handle_execution_request(self, request_data):
           # u5904u7406u4ee3u7801u6267u884cu8bf7u6c42
           code = request_data.get('payload', {}).get('code')
           language = request_data.get('payload', {}).get('language')
           response = self.server.get_execution_response(code, language)
           status_code = 200
           self._send_response(status_code, response)
       
       def _send_response(self, status_code, data):
           self.send_response(status_code)
           self.send_header('Content-Type', 'application/json')
           self.end_headers()
           self.wfile.write(json.dumps(data).encode('utf-8'))
   
   class MockServer:
       def __init__(self, host='localhost', port=0):
           self.server = HTTPServer((host, port), MockServerHandler)
           self.server.response_delay = 0
           self.server.auth_responses = {}
           self.server.execution_responses = {}
           self.server.generation_responses = {}
           self.server.requests = []
           self.server.record_request = self.record_request
           self.server.get_auth_response = self.get_auth_response
           self.server.get_execution_response = self.get_execution_response
           self.server.get_generation_response = self.get_generation_response
           
           # u542fu52a8u670du52a1u5668u7ebfu7a0b
           self.thread = threading.Thread(target=self.server.serve_forever)
           self.thread.daemon = True
           self.thread.start()
           
           # u670du52a1u5668 URL
           self.host = host
           self.port = self.server.server_port
           self.url = f'http://{host}:{self.port}'
           
           # u7edf u8ba1u4fe1u606f
           self.request_count = 0
           self.max_concurrent_requests = 0
           self.current_concurrent_requests = 0
       
       def record_request(self, path, data):
           self.requests.append({'path': path, 'data': data, 'time': time.time()})
           self.request_count += 1
           self.current_concurrent_requests += 1
           self.max_concurrent_requests = max(self.max_concurrent_requests, self.current_concurrent_requests)
           # u6a21u62dfu5e76u53d1u8bf7u6c42u5904u7406u5b8cu6210
           time.sleep(0.05)
           self.current_concurrent_requests -= 1
       
       def add_auth_response(self, api_key, response, status_code=200):
           self.server.auth_responses[api_key] = response
       
       def get_auth_response(self, api_key):
           return self.server.auth_responses.get(api_key, {
               'status': 'error',
               'message': 'Invalid API key'
           })
       
       def add_execution_response(self, code, language, response=None, status_code=200, delay=0, times=None):
           key = f"{code}:{language}"
           if response is None:
               # u9ed8u8ba4u6210u529fu54cdu5e94
               response = {
                   'status': 'success',
                   'result': {
                       'output': f"Executed {language} code\n",
                       'execution_time': 0.1
                   }
               }
           
           self.server.execution_responses[key] = {
               'response': response,
               'status_code': status_code,
               'delay': delay,
               'times': times,
               'count': 0
           }
       
       def get_execution_response(self, code, language):
           key = f"{code}:{language}"
           if key not in self.server.execution_responses:
               return {
                   'status': 'error',
                   'message': 'No mock response configured for this code and language'
               }
           
           response_config = self.server.execution_responses[key]
           response_config['count'] += 1
           
           # u5982u679cu914du7f6eu4e86u6b21u6570u9650u5236uff0cu5219u6839u636eu8bf7u6c42u6b21u6570u8fd4u56deu4e0du540cu54cdu5e94
           if response_config['times'] is not None and response_config['count'] <= response_config['times']:
               return {
                   'status': 'error',
                   'message': 'Service temporarily unavailable'
               }
           
           # u8bbeu7f6eu6a21u62dfu5ef6u8fdf
           self.server.response_delay = response_config['delay']
           
           return response_config['response']
       
       def shutdown(self):
           self.server.shutdown()
           self.thread.join()

@pytest.fixture
def mock_server():
    server = MockServer()
    yield server
    server.shutdown()

u4f7fu7528u6a21u62dfu670du52a1u5668
-----------

u5728u6d4bu8bd5u4e2du4f7fu7528u6a21u62dfu670du52a1u5668u975eu5e38u7b80u5355uff0cu53efu4ee5u901au8fc7 pytest u7684u88c5u7f6eu673au5236u6765u5b9eu73b0u3002

.. code-block:: python

   # u4f7fu7528u6a21u62dfu670du52a1u5668u7684u6d4bu8bd5u793au4f8b
   
   def test_with_mock_server(mock_server):
       # 1. u914du7f6eu6a21u62dfu670du52a1u5668u7684u54cdu5e94
       mock_server.add_auth_response(
           api_key="test_key",
           response={
               "status": "success",
               "session_id": "test_session"
           }
       )
       
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
       
       # 2. u521bu5efau5ba2u6237u7aefu5e76u6307u5411u6a21u62dfu670du52a1u5668
       client = DeepExecClient(
           deepseek_key="test_key",
           e2b_key="test_e2b_key",
           base_url=mock_server.url  # u4f7fu7528u6a21u62dfu670du52a1u5668u7684 URL
       )
       
       # 3. u8c03u7528u5ba2u6237u7aefu65b9u6cd5
       session_id = client.create_session("test_user")
       result = client.execute_code("print('Hello, World!')", "python")
       
       # 4. u9a8cu8bc1u7ed3u679c
       assert session_id == "test_session"
       assert result.status == "success"
       assert result.output == "Hello, World!\n"
       
       # 5. u9a8cu8bc1u8bf7u6c42u8bb0u5f55
       assert mock_server.request_count == 2  # u4e00u6b21u8ba4u8bc1u8bf7u6c42u548cu4e00u6b21u6267u884cu8bf7u6c42

u9ad8u7ea7u529fu80fd
-------

u6a21u62dfu670du52a1u5668u8fd8u63d0u4f9bu4e86u4e00u4e9bu9ad8u7ea7u529fu80fduff0cu7528u4e8eu6d4bu8bd5u590du6742u60c5u51b5uff1a

1. **u6a21u62dfu5ef6u8fdf**: u6a21u62dfu54cdu5e94u5ef6u8fdfu4ee5u6d4bu8bd5u8d85u65f6u5904u7406
2. **u6a21u62dfu9519u8befu5e8fu5217**: u6a21u62dfu5148u5931u8d25u540eu6210u529fu7684u60c5u51b5u4ee5u6d4bu8bd5u91cdu8bd5u673au5236
3. **u5e76u53d1u8bf7u6c42u7edf u8ba1**: u8bb0u5f55u5e76u53d1u8bf7u6c42u6570u91cfu4ee5u9a8cu8bc1u5f02u6b65u5ba2u6237u7aefu7684u5e76u53d1u6027u80fdu
4. **u8bf7u6c42u5386u53f2**: u8bb0u5f55u6240u6709u8bf7u6c42u4ee5u8fdb u884cu8be6u7ec6u5206u6790

u8fd9u4e9bu529fu80fdu4f7fu u5f97u6d4bu8bd5u6846u67b6u53efu4ee5u6a21u62dfu5404u79cdu590du6742u7684u771fu5b9eu4e16u754cu60c5u51b5uff0cu63d0u9ad8u6d4bu8bd5u7684u8986u76d6u8303u56f4u548cu6709u6548u6027u3002
