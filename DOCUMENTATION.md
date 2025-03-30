# DeepExec SDK u6587u6863u6307u5357

## u6587u6863u6982u8ff0

DeepExec SDK u63d0u4f9bu4e86u4e0e DeepExec u670du52a1u4ea4u4e92u7684u5b8cu6574u529fu80fduff0cu5305u62ecu5b89u5168u7684u4ee3u7801u6267u884cu548c AI u6587u672cu751fu6210u80fdu529bu3002u672cu6587u6863u63d0u4f9bu4e86 SDK u7684u5b8cu6574u53c2u8003u548cu4f7fu7528u6307u5357u3002

## u6587u6863u7ed3u6784

u6211u4eecu7684u6587u6863u5305u542bu4ee5u4e0bu4e3bu8981u90e8u5206uff1a

1. **u4e3bu9875 (index.html)**
   - SDK u6982u8ff0
   - u5febu901fu5165u95e8u6307u5357
   - u4e3bu8981u529fu80fdu4ecbu7ecd

2. **MCP u534fu8baeu6587u6863 (mcp_protocol.html)**
   - u534fu8baeu7ed3u6784u8be6u89e3
   - u8bf7u6c42u548cu54cdu5e94u683cu5f0f
   - u9519u8befu5904u7406
   - u5b9eu73b0u7ec6u8282

3. **API u53c2u8003 (api_reference.html)**
   - DeepExecAsyncClient u7c7bu53c2u8003
   - u6570u636eu6a21u578bu8be6u89e3
   - u65b9u6cd5u548cu53c2u6570u8bf4u660e
   - u9519u8befu7c7bu578bu548cu5904u7406

4. **u4ee3u7801u793au4f8b (examples.html)**
   - u57fau672cu4f7fu7528u793au4f8b
   - u4ee3u7801u6267u884cu793au4f8b
   - u6587u672cu751fu6210u793au4f8b
   - u6d41u5f0fu751fu6210u793au4f8b
   - u9519u8befu5904u7406u793au4f8b

5. **u6d4bu8bd5u6307u5357 (testing.html)**
   - u5355u5143u6d4bu8bd5
   - u96c6u6210u6d4bu8bd5
   - Mock u6d4bu8bd5u65b9u6848
   - Web u96c6u6210u6d4bu8bd5

## u6587u6863u751fu6210

u6211u4eecu63d0u4f9bu4e86u4e24u79cdu65b9u5f0fu6765u751fu6210u548cu67e5u770bu6587u6863uff1a

### 1. u672cu5730u6587u6863u670du52a1u5668

u6211u4eecu63d0u4f9bu4e86u4e00u4e2au7b80u5355u7684 Python u811au672cu6765u542fu52a8u672cu5730u6587u6863u670du52a1u5668uff1a

```bash
cd docs
python serve_docs.py
```

u8fd9u5c06u542fu52a8u4e00u4e2a HTTP u670du52a1u5668uff0cu5e76u81eau52a8u5728u6d4fu89c8u5668u4e2du6253u5f00u6587u6863u7f51u7ad9u3002

### 2. u6587u6863u751fu6210u811au672c

u6211u4eecu8fd8u63d0u4f9bu4e86u4e00u4e2au811au672cu6765u751fu6210u9759u6001 HTML u6587u6863uff1a

```bash
cd docs
python generate_docs.py
```

u8fd9u5c06u751fu6210u6240u6709u5fc5u8981u7684 HTML u6587u4ef6u548c CSS u6587u4ef6uff0cu4ee5u4fbfu90e8u7f72u5230 GitHub Pages u6216u5176u4ed6u9759u6001u7f51u7ad9u670du52a1u3002

## u90e8u7f72u5230 GitHub Pages

u8981u5c06u6587u6863u90e8u7f72u5230 GitHub Pagesuff0cu60a8u6709u4e24u79cdu9009u62e9uff1a

### 1. u624bu52a8u90e8u7f72

1. u521bu5efau5e76u5207u6362u5230 `gh-pages` u5206u652fuff1a

```bash
git checkout -b gh-pages
```

2. u5220u9664u9664u6587u6863u76f8u5173u6587u4ef6u5916u7684u6240u6709u6587u4ef6uff08u4fddu7559 HTML u548c CSS u6587u4ef6uff09

3. u63d0u4ea4u5e76u63a8u9001u66f4u6539uff1a

```bash
git add .
git commit -m "Add documentation for GitHub Pages"
git push origin gh-pages
```

4. u5728 GitHub u4ed3u5e93u8bbeu7f6eu4e2du542fu7528 GitHub Pagesuff0cu9009u62e9 `gh-pages` u5206u652fu4f5cu4e3au6e90

### 2. u4f7fu7528 GitHub Actions

u6211u4eecu63d0u4f9bu4e86u4e00u4e2a GitHub Actions u5de5u4f5cu6d41u7a0bu6587u4ef6uff0cu53efu4ee5u81eau52a8u6784u5efau548cu90e8u7f72u6587u6863u3002u8be6u7ec6u4fe1u606fu8bf7u53c2u8003 `docs/README.md`u3002

## u9759u6001u7f51u7ad9u6587u4ef6

u4ee5u4e0bu662fu9700u8981u4e0au4f20u5230u9759u6001u7f51u7ad9u7684u6240u6709u6587u4ef6uff1a

1. `index.html` - u4e3bu9875
2. `mcp_protocol.html` - MCP u534fu8baeu6587u6863
3. `api_reference.html` - API u53c2u8003
4. `examples.html` - u4ee3u7801u793au4f8b
5. `testing.html` - u6d4bu8bd5u6307u5357
6. `styles.css` - u6837u5f0fu8868
7. `assets/` u76eeu5f55 - u5305u542bu56feu7247u548cu5176u4ed6u8d44u6e90

## Web u5e94u7528u96c6u6210

u6839u636eu60a8u7684u9879u76eeu9700u6c42uff0cu6211u4eecu5df2u7ecfu5728u6587u6863u4e2du5305u542bu4e86 Web u5e94u7528u96c6u6210u7684u793au4f8buff0cu5c55u793au4e86u5982u4f55u5728 Next.js u524du7aefu4e2du4f7fu7528 DeepExec SDKu3002u8fd9u7b26u5408u60a8u6307u5b9au7684 Web u90e8u7f72u65b9u6848uff1a

- u524du7aefu4f7fu7528 Next.js u6846u67b6
- u540eu7aefu4f7fu7528 Node.js + Express
- u901au8fc7 Vercel u5e73u53f0u90e8u7f72u524du7aef
- u540eu7aefu53efu4ee5u90e8u7f72u5728 Docker u5bb9u5668u6216u4e91u670du52a1u4e0a

## u6d4bu8bd5 Mocking u65b9u6848

u6211u4eecu4e3a DeepExec SDK u8bbeu8ba1u4e86u5168u9762u7684u6d4bu8bd5 Mocking u65b9u6848uff0cu5305u62ecuff1a

1. **HTTP u8bf7u6c42 Mock** - u6a21u62dfu4e0e DeepSeek API u548c E2B u670du52a1u7684u901au4fe1
2. **u4f1au8bddu7ba1u7406 Mock** - u6a21u62dfu4f1au8bddu521bu5efau548cu7ba1u7406
3. **u4ee3u7801u6267u884c Mock** - u6a21u62dfu6c99u7bb1u73afu5883u4e2du7684u4ee3u7801u6267u884c
4. **u6587u672cu751fu6210 Mock** - u6a21u62df AI u6a21u578bu7684u6587u672cu751fu6210u54cdu5e94
5. **u9519u8befu60c5u51b5 Mock** - u6a21u62dfu5404u79cdu9519u8befu573au666fu548cu8fb9u7f18u60c5u51b5

u8be6u7ec6u7684u6d4bu8bd5u65b9u6848u548cu4ee3u7801u793au4f8bu53efu4ee5u5728 `testing.html` u4e2du627eu5230u3002

## u7ed3u8bba

u8fd9u4e2au6587u6863u7cfbu7edfu63d0u4f9bu4e86 DeepExec SDK u7684u5b8cu6574u53c2u8003u548cu4f7fu7528u6307u5357uff0cu5305u62ec MCP u534fu8baeu5b9eu73b0u3001API u53c2u8003u3001u4ee3u7801u793au4f8bu548cu6d4bu8bd5u65b9u6848u3002u901au8fc7u8fd9u4e9bu6587u6863uff0cu5f00u53d1u8005u53efu4ee5u5febu901fu4e86u89e3u548cu4f7fu7528 SDKuff0cu5e76u5c06u5176u96c6u6210u5230u81eau5df1u7684 Web u5e94u7528u4e2du3002
