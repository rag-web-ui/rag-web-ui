<div align="center">
  <h1>RAG Web UI</h1>
  <p>
    <strong>基于 RAG (Retrieval-Augmented Generation) 的智能对话系统</strong>
  </p>
  <p>
    <a href="#特性">特性</a> •
    <a href="#快速开始">快速开始</a> •
    <a href="#部署指南">部署指南</a> •
    <a href="#技术架构">技术架构</a> •
    <a href="#开发指南">开发指南</a>
  </p>
</div>

## ✨ 特性

- 🔐 完整的用户认证系统
- 📚 知识库和文档智能管理
- 🤖 基于 RAG 的智能对话引擎
- 📂 支持多种文档格式 (PDF、DOCX、Markdown、Text)
- ☁️ MinIO 分布式文件存储
- 🎯 前后端分离架构

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Node.js 18+
- Python 3.9+

### 基础配置

1. 克隆项目
```bash
git clone https://github.com/yourusername/rag-web-ui.git
cd rag-web-ui
```

2. 环境配置
```bash
cp .env.example .env
```

3. 启动服务
```bash
docker-compose up -d
```

🌐 访问地址:
- 前端界面: http://localhost:3000
- API 文档: http://localhost:8000/docs
- MinIO 控制台: http://localhost:9001

## 🏗️ 技术架构

<details>
<summary>后端技术栈</summary>

- 🐍 Python FastAPI
- 🗄️ MySQL + ChromaDB
- 📦 MinIO 对象存储
- 🔗 Langchain 框架
- 🔒 JWT 认证
</details>

<details>
<summary>前端技术栈</summary>

- ⚛️ Next.js 14
- 📘 TypeScript
- 🎨 Tailwind CSS
- 🎯 Shadcn/UI
- 🤖 Vercel AI SDK
</details>

## 📁 项目结构

```
rag-web-ui/
├── backend/                # 后端服务
│   ├── app/
│   │   ├── api/          # RESTful API 接口
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据模型
│   │   └── services/     # 业务逻辑
│   └── alembic/          # 数据库迁移
├── frontend/              # 前端应用
│   └── src/
│       ├── app/         # Next.js 路由
│       ├── components/  # UI 组件
│       └── lib/        # 工具函数
└── docker-compose.yml    # 容器编排配置
```

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

## 🔧 系统配置

主要环境变量:

| 变量名          | 说明            | 必填 |
| --------------- | --------------- | ---- |
| OPENAI_API_KEY  | OpenAI API 密钥 | ✅    |
| SECRET_KEY      | JWT 密钥        | ✅    |
| DATABASE_URL    | 数据库连接串    | ✅    |
| MINIO_ROOT_USER | MinIO 用户名    | ✅    |

## 📈 性能优化

- ⚡️ 文档增量 chunk 处理
- 🔄 异步文档预览
- 📑 多文档并行处理
- 🎯 向量数据库优化

## 📄 许可证

[MIT License](LICENSE)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request

</div>

citations
https://python.langchain.com/docs/how_to/qa_citations/