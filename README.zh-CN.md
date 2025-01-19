<div align="center">
  <h1>RAG Web UI</h1>
  <p>
    <strong>基于 RAG (Retrieval-Augmented Generation) 的智能对话系统</strong>
  </p>

  <p>
    <a href="https://github.com/yourusername/rag-web-ui/blob/main/LICENSE"><img src="https://img.shields.io/github/license/yourusername/rag-web-ui" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python"></a>
    <a href="#"><img src="https://img.shields.io/badge/node-%3E%3D18-green.svg" alt="Node"></a>
    <a href="#"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  </p>

  <p>
    <a href="#特性">特性</a> •
    <a href="#快速开始">快速开始</a> •
    <a href="#部署指南">部署指南</a> •
    <a href="#技术架构">技术架构</a> •
    <a href="#开发指南">开发指南</a> •
    <a href="#贡献指南">贡献指南</a>
  </p>

  <h4>
    <a href="README.md">English</a> |
    <span>简体中文</span>
  </h4>

  <img src="docs/images/demo.png" alt="RAG Web UI Demo" width="600">
</div>

## 📖 简介

RAG Web UI 是一个基于 RAG (Retrieval-Augmented Generation) 技术的智能对话系统，它能够帮助企业和个人构建基于自有知识库的智能问答系统。通过结合文档检索和大语言模型，实现了准确、可靠的知识问答服务。

## ✨ 特性

- 🔐 **安全可靠**
  - 完整的用户认证和权限管理系统
  - 数据加密存储
  - 可审计的操作日志

- 📚 **智能文档管理**
  - 支持多种文档格式 (PDF、DOCX、Markdown、Text)
  - 文档自动分块和向量化
  - 智能文档标签和分类

- 🤖 **先进的对话引擎**
  - 基于 RAG 的精准检索和生成
  - 支持上下文记忆和多轮对话
  - 可配置的模型参数和提示词

- 🎯 **企业级架构**
  - 前后端分离设计
  - 分布式文件存储
  - 高性能向量数据库

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose v2.0+
- Node.js 18+
- Python 3.9+
- 8GB+ RAM

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/rag-web-ui.git
cd rag-web-ui
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填写必要的配置项
```

3. 启动服务
```bash
docker-compose up -d
```

### 验证安装

服务启动后，可以通过以下地址访问：

- 🌐 前端界面: http://localhost:3000
- 📚 API 文档: http://localhost:8000/docs
- 💾 MinIO 控制台: http://localhost:9001

## 🏗️ 技术架构

### 后端技术栈

- 🐍 **Python FastAPI**: 高性能异步 Web 框架
- 🗄️ **MySQL + ChromaDB**: 关系型数据库 + 向量数据库
- 📦 **MinIO**: 分布式对象存储
- 🔗 **Langchain**: LLM 应用开发框架
- 🔒 **JWT + OAuth2**: 身份认证

### 前端技术栈

- ⚛️ **Next.js 14**: React 应用框架
- 📘 **TypeScript**: 类型安全
- 🎨 **Tailwind CSS**: 原子化 CSS
- 🎯 **Shadcn/UI**: 高质量组件库
- 🤖 **Vercel AI SDK**: AI 功能集成

## 📈 性能优化

系统在以下方面进行了性能优化：

- ⚡️ 文档增量处理和异步分块
- 🔄 流式响应和实时反馈
- 📑 向量数据库性能调优
- 🎯 分布式任务处理

## 📖 开发指南

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
pnpm install
pnpm dev
```

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

## 🔧 配置说明

### 核心配置项

| 配置项                      | 说明                     | 默认值    | 必填 |
| --------------------------- | ------------------------ | --------- | ---- |
| MYSQL_SERVER                | MySQL 服务器地址         | localhost | ✅    |
| MYSQL_USER                  | MySQL 用户名             | postgres  | ✅    |
| MYSQL_PASSWORD              | MySQL 密码               | postgres  | ✅    |
| MYSQL_DATABASE              | MySQL 数据库名           | ragwebui  | ✅    |
| SECRET_KEY                  | JWT 加密密钥             | -         | ✅    |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT token 过期时间(分钟) | 30        | ✅    |
| CHROMA_DB_HOST              | ChromaDB 服务器地址      | localhost | ✅    |
| CHROMA_DB_PORT              | ChromaDB 端口            | 8000      | ✅    |
| OPENAI_API_KEY              | OpenAI API 密钥          | -         | ✅    |
| OPENAI_API_BASE             | OpenAI API 代理 URL      | -         | ❌    |

## 🤝 贡献指南

我们非常欢迎社区贡献！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循 [Python PEP 8](https://pep8.org/) 代码规范
- 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 提交规范


## 📄 许可证

本项目采用 [Apache-2.0 许可证](LICENSE)

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Langchain](https://python.langchain.com/)
- [Next.js](https://nextjs.org/)
- [ChromaDB](https://www.trychroma.com/)

---

<div align="center">
  如果这个项目对你有帮助，请考虑给它一个 ⭐️
</div> 