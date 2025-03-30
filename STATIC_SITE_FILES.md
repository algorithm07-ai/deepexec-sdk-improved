# DeepExec SDK 静态网站文件清单

以下是需要上传到静态网站（如 GitHub Pages）的所有文件列表。这些文件包含了完整的 DeepExec SDK 文档。

## 核心 HTML 文件

1. `index.html` - 主页，包含 SDK 概述和快速入门指南
2. `mcp_protocol.html` - MCP 协议文档，详细说明协议结构和使用方法
3. `api_reference.html` - API 参考，包含 SDK 的类和方法详细说明
4. `examples.html` - 代码示例，展示 SDK 的各种用法
5. `testing.html` - 测试指南，包含单元测试和集成测试方法

## 样式和资源文件

1. `styles.css` - 主要样式表
2. `assets/` 目录 - 包含图片和其他资源
   - `assets/logo.png` - SDK logo
   - `assets/favicon.ico` - 网站图标
   - `assets/diagrams/` - 包含各种流程图和架构图

## JavaScript 文件

1. `scripts/main.js` - 主要 JavaScript 文件，用于交互功能
2. `scripts/highlight.js` - 代码高亮功能

## 部署说明

### 方法一：手动部署到 GitHub Pages

1. 创建并切换到 `gh-pages` 分支：

```bash
git checkout -b gh-pages
```

2. 删除除文档相关文件外的所有文件（保留上述列出的所有 HTML、CSS 和 JavaScript 文件）

3. 提交并推送更改：

```bash
git add .
git commit -m "Add documentation for GitHub Pages"
git push origin gh-pages
```

4. 在 GitHub 仓库设置中，启用 GitHub Pages，选择 `gh-pages` 分支作为源

### 方法二：使用 GitHub Actions 自动部署

1. 确保 `.github/workflows/docs.yml` 文件已正确配置
2. 将更改推送到主分支，GitHub Actions 将自动构建和部署文档
3. 在 GitHub 仓库设置中，确认 GitHub Pages 已启用，并选择 GitHub Actions 作为源

## 本地预览

在上传到静态网站之前，您可以使用以下命令在本地预览文档：

```bash
cd docs
python serve_docs.py
```

这将启动一个本地 HTTP 服务器，并自动在浏览器中打开文档网站。

## 注意事项

1. 确保所有链接都是相对路径，以便在不同环境中正常工作
2. 验证所有图片和资源文件都已包含在上传的文件中
3. 测试所有页面的导航和功能是否正常工作
4. 确保文档内容与最新版本的 SDK 保持同步

## Web 应用集成

根据项目需求，文档中包含了 Web 应用集成的示例，展示了如何在 Next.js 前端中使用 DeepExec SDK。这符合指定的 Web 部署方案：

- 前端使用 Next.js 框架
- 后端使用 Node.js + Express
- 通过 Vercel 平台部署前端
- 后端可以部署在 Docker 容器或云服务上
