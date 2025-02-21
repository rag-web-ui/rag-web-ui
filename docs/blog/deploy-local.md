# 🚀 十分钟搭建属于自己的 DeepSeek 知识库！完全开源、离线部署方案详解

## 💡 序言

还在为高额的 ChatGPT Plus 订阅费用发愁吗？担心公司机密文档上传到云端吗？本教程将带你使用完全开源的工具，在本地搭建一个基于 RAG (Retrieval-Augmented Generation) 技术的智能知识库系统。不仅完全离线，还能保护隐私，让你的文档秘密更有保障！

## 🛠️ 环境准备

在开始之前，请确保你的系统满足以下要求：

- 操作系统：Linux/macOS/Windows
- RAM：至少 8GB (推荐 16GB 以上)
- 硬盘空间：至少 20GB 可用空间
- 已安装：
  - [Docker & Docker Compose v2.0+](https://docs.docker.com/get-docker/)
  - [Ollama](https://ollama.com/)

### 1. 安装 Ollama

1. 访问 [Ollama 官网](https://ollama.com/) 下载并安装对应系统版本
2. 验证安装：

````bash
ollama --version
````

### 2. 下载必要的模型

我们需要两个模型：

- deepseek-r1:7b 用于对话生成
- nomic-embed-text 用于文本向量化

执行以下命令下载模型：

````bash
# 下载对话模型
ollama pull deepseek-r1:7b

# 下载向量模型  
ollama pull nomic-embed-text
````

## 🔧 部署知识库系统

### 1. 克隆项目

````bash
git clone https://github.com/rag-web-ui/rag-web-ui.git
cd rag-web-ui
````

### 2. 配置环境变量

复制环境变量模板并编辑：

````bash
cp .env.example .env
````

编辑 .env 文件，配置如下：

````env
# LLM 配置
CHAT_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434
OLLAMA_MODEL=deepseek-r1:7b
# Embedding 配置
EMBEDDINGS_PROVIDER=ollama
OLLAMA_EMBEDDINGS_MODEL=nomic-embed-text

# 向量数据库配置
VECTOR_STORE_TYPE=chroma
CHROMA_DB_HOST=chromadb
CHROMA_DB_PORT=8000

# MySQL 配置
MYSQL_SERVER=db
MYSQL_USER=ragwebui
MYSQL_PASSWORD=ragwebui
MYSQL_DATABASE=ragwebui

# MinIO 配置
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=documents
````

注意：这里使用的是 Docker Compose 的服务名而不是 localhost，这样容器之间才能正确通信。

### 3. 启动服务

使用 Docker Compose 启动所有服务：

````bash
docker compose up -d --build
````

这将启动以下服务：

- 前端界面 (Next.js)
- 后端 API (FastAPI)
- MySQL 数据库
- ChromaDB 向量数据库
- MinIO 对象存储
- Ollama 服务

### 4. 验证部署

服务启动后，可以通过以下地址访问：

- 前端界面：<http://localhost:3000>
- API 文档：<http://localhost:8000/redoc>
- MinIO 控制台：<http://localhost:9001>

## 📚 使用指南

### 1. 创建知识库

1. 访问 <http://localhost:3000>
2. 登录后，点击"创建知识库"
3. 填写知识库名称和描述
4. 上传文档，选择切片方式和大小
5. 点击"创建"
6. 等待文档处理完成

支持以下格式：

- PDF
- DOCX
- Markdown
- Text
- ...

### 2. 开始对话

1. 点击"开始对话"
2. 输入问题
3. 系统会自动：
   - 检索相关文档片段
   - 使用 deepseek-r1:7b 模型生成回答
   - 显示引用来源

## ❓ 常见问题

1. Ollama 服务无法连接
   - 检查 Ollama 是否正常运行：`ollama list`
   - 检查 Docker 网络配置是否正确

2. 文档处理失败
   - 检查文档格式是否支持
   - 查看后端日志：`docker compose logs -f backend`

3. 内存不足
   - 调整 Docker 容器内存限制
   - 考虑使用更小的模型

> 💡 性能与安全提示：建议单个文档不超过 10MB，定期备份数据，并及时修改默认密码以确保系统安全。

## 🎯 结语

通过以上步骤，你已经成功搭建了一个基于 RAG 技术的本地知识库系统。该系统完全本地化部署，无需担心数据隐私问题，同时借助 Ollama 的能力，可以实现高质量的知识问答服务。

需要注意的是，这个系统主要用于学习和个人使用，如果要用于生产环境，还需要进行更多的安全性和稳定性优化。

## 📚 参考资源

- [Ollama 官方文档](https://ollama.com/)
- [RAG Web UI 项目](https://github.com/rag-web-ui/rag-web-ui)
- [Docker 文档](https://docs.docker.com/)

希望这个教程对你搭建个人知识库有所帮助！如果遇到问题，欢迎查阅项目文档或在 GitHub 上提出 issue。
