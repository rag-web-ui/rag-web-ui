<div align="center">
  <h1>RAG Web UI</h1>
  <p>
    <strong>An Intelligent Dialogue System Based on RAG (Retrieval-Augmented Generation)</strong>
  </p>

  <p>
    <a href="https://github.com/yourusername/rag-web-ui/blob/main/LICENSE"><img src="https://img.shields.io/github/license/yourusername/rag-web-ui" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python"></a>
    <a href="#"><img src="https://img.shields.io/badge/node-%3E%3D18-green.svg" alt="Node"></a>
    <a href="#"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  </p>

  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#deployment-guide">Deployment</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#development">Development</a> •
    <a href="#contributing">Contributing</a>
  </p>

  <h4>
    <span>English</span> |
    <a href="README.zh-CN.md">简体中文</a>
  </h4>

  <img src="docs/images/demo.png" alt="RAG Web UI Demo" width="600">
</div>

## 📖 Introduction

RAG Web UI is an intelligent dialogue system based on RAG (Retrieval-Augmented Generation) technology. It helps enterprises and individuals build intelligent Q&A systems based on their own knowledge bases. By combining document retrieval and large language models, it delivers accurate and reliable knowledge-based question-answering services.

## ✨ Features

- 📚 **Intelligent Document Management**
  - Support for multiple document formats (PDF, DOCX, Markdown, Text)
  - Automatic document chunking and vectorization
  - Smart document tagging and classification

- 🤖 **Advanced Dialogue Engine**
  - Precise retrieval and generation based on RAG
  - Context memory and multi-turn dialogue support
  - Configurable model parameters and prompts

- 🎯 **Enterprise Architecture**
  - Frontend-backend separation
  - Distributed file storage
  - High-performance vector database
  - Complete monitoring and alerting system

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose v2.0+
- Node.js 18+
- Python 3.9+
- 8GB+ RAM

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/rag-web-ui.git
cd rag-web-ui
```

2. Configure environment variables
```bash
cp .env.example .env
# Edit .env file with necessary configurations
```

3. Start services
```bash
docker-compose up -d
```

### Verification

Access the following URLs after service startup:

- 🌐 Frontend UI: http://localhost:3000
- 📚 API Documentation: http://localhost:8000/docs
- 💾 MinIO Console: http://localhost:9001

## 🏗️ Architecture

### Backend Stack

- 🐍 **Python FastAPI**: High-performance async web framework
- 🗄️ **MySQL + ChromaDB**: Relational + Vector databases
- 📦 **MinIO**: Distributed object storage
- 🔗 **Langchain**: LLM application framework
- 🔒 **JWT + OAuth2**: Authentication

### Frontend Stack

- ⚛️ **Next.js 14**: React framework
- 📘 **TypeScript**: Type safety
- 🎨 **Tailwind CSS**: Utility-first CSS
- 🎯 **Shadcn/UI**: High-quality components
- 🤖 **Vercel AI SDK**: AI integration

## 📈 Performance Optimization

The system is optimized in the following aspects:

- ⚡️ Incremental document processing and async chunking
- 🔄 Streaming responses and real-time feedback
- 📑 Vector database performance tuning
- 🎯 Distributed task processing

## 📖 Development Guide

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

### Database Migration

```bash
cd backend
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

## 🔧 Configuration

### Core Configuration

| Parameter                   | Description                | Default   | Required |
| --------------------------- | -------------------------- | --------- | -------- |
| MYSQL_SERVER                | MySQL Server Address       | localhost | ✅        |
| MYSQL_USER                  | MySQL Username             | postgres  | ✅        |
| MYSQL_PASSWORD              | MySQL Password             | postgres  | ✅        |
| MYSQL_DATABASE              | MySQL Database Name        | ragwebui  | ✅        |
| SECRET_KEY                  | JWT Secret Key             | -         | ✅        |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT Token Expiry (minutes) | 30        | ✅        |
| CHROMA_DB_HOST              | ChromaDB Server Address    | localhost | ✅        |
| CHROMA_DB_PORT              | ChromaDB Port              | 8000      | ✅        |
| OPENAI_API_KEY              | OpenAI API Key             | -         | ✅        |
| OPENAI_API_BASE             | OpenAI API Proxy URL       | -         | ❌        |

## 🤝 Contributing

We welcome community contributions!

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### Development Guidelines

- Follow [Python PEP 8](https://pep8.org/) coding standards
- Follow [Conventional Commits](https://www.conventionalcommits.org/)

## 📄 License

This project is licensed under the [Apache-2.0 License](LICENSE)

## 🙏 Acknowledgments

Thanks to these open source projects:

- [FastAPI](https://fastapi.tiangolo.com/)
- [Langchain](https://python.langchain.com/)
- [Next.js](https://nextjs.org/)
- [ChromaDB](https://www.trychroma.com/)

---

<div align="center">
  If this project helps you, please consider giving it a ⭐️
</div>
