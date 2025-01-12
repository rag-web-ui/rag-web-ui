# RAG Web UI

一个基于 RAG (Retrieval-Augmented Generation) 的 Web UI 应用，用于实践 RAG 相关知识。

## 项目特点

- 前后端分离架构
- 完整的用户认证系统
- 知识库和文档管理
- 基于 RAG 的智能对话
- 文件存储使用 MinIO
- 支持多种文档格式

## 技术栈

### 后端
- Python FastAPI
- MySQL 数据库
- ChromaDB 向量数据库
- MinIO 对象存储
- Langchain 框架
- JWT 认证

### 前端
- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn/UI 组件库
- Vercel AI SDK

## 功能模块

### 用户系统
- 注册
- 登录
- 登出

### 知识库管理
- 创建知识库
- 上传文档（支持 PDF、DOCX、Markdown、Text）
- 文档管理

### 聊天系统
- 创建对话
- 选择知识库
- 智能对话
- 对话历史

## 目录结构

```
.
├── backend/                 # 后端代码
│   ├── alembic/            # 数据库迁移
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── db/           # 数据库配置
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── services/     # 业务逻辑
│   └── requirements.txt   # Python 依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── app/          # Next.js 页面
│   │   ├── components/   # React 组件
│   │   ├── lib/         # 工具函数
│   │   └── styles/      # 样式文件
│   └── package.json      # Node.js 依赖
└── docker-compose.yml     # Docker 配置
```

## 数据模型

- 用户表 (users)
- 知识库表 (knowledge_bases)
- 文档表 (documents)
- 聊天表 (chats)
- 消息表 (messages)
- 聊天知识库关联表 (chat_knowledge_bases)

## 部署说明

### 环境要求
- Docker
- Docker Compose

### 配置文件
1. 创建 `.env` 文件：
```bash
cp .env.example .env
```

2. 配置必要的环境变量：
- OPENAI_API_KEY
- SECRET_KEY
- 其他可选配置

### 启动服务

1. 使用 Docker Compose（推荐）：
```bash
# 首次启动或重建
docker-compose up --build

# 后续启动
docker-compose up

# 停止服务
docker-compose down
```

2. 开发模式：
```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
pnpm install
pnpm dev
```

### 访问服务
- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8000
- MinIO 控制台：http://localhost:9001
  - 用户名：minioadmin
  - 密码：minioadmin

## 开发说明

### 后端开发
- API 文档：http://localhost:8000/docs
- 数据库迁移：
```bash
cd backend
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

### 前端开发
- 组件开发遵循 Shadcn/UI 规范
- 使用 Tailwind CSS 进行样式开发
- 状态管理使用 React Hooks


### 文档处理
- 文档处理使用 Langchain 框架
- 文档处理使用 ChromaDB 向量数据库
- 文档处理使用 MinIO 对象存储

### 优化
- 文档增量 chunk 处理，增加 langchain recorder 
- 文档 preview 异步处理
- 多文档预览