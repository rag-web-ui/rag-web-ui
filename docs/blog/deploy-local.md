# 🚀 Build Your Own DeepSeek Knowledge Base in 10 Minutes! Fully Open Source & Offline Deployment Guide

## 💡 Introduction

Tired of expensive ChatGPT Plus subscriptions? Worried about uploading confidential company documents to the cloud? This tutorial will guide you through building an intelligent knowledge base system locally using fully open-source tools based on RAG (Retrieval-Augmented Generation) technology. Enjoy complete offline deployment and privacy protection—keep your documents secure and confidential!

## 🛠️ Environment Preparation

Before you begin, make sure your system meets the following requirements:

- Operating System: Linux/macOS/Windows
- RAM: At least 8GB (16GB or more recommended)
- Disk Space: At least 20GB available
- Installed:
   - [Docker & Docker Compose v2.0+](https://docs.docker.com/get-docker/)
   - [Ollama](https://ollama.com/)

### 1. Install Ollama

1. Visit the [Ollama official website](https://ollama.com/) to download and install the version for your operating system.
2. Verify the installation:

````bash
ollama --version
````

### 2. Download Required Models

You will need two models:

- `deepseek-r1:7b` for conversational generation
- `nomic-embed-text` for text embedding

Run the following commands to download the models:

````bash
# Download the conversational model
ollama pull deepseek-r1:7b

# Download the embedding model
ollama pull nomic-embed-text
````

## 🔧 Deploy the Knowledge Base System

### 1. Clone the Project

````bash
git clone https://github.com/rag-web-ui/rag-web-ui.git
cd rag-web-ui
````

### 2. Configure Environment Variables

Copy the environment variable template and edit it:

````bash
cp .env.example .env
````

Edit the `.env` file as follows:

````env
# LLM Configuration
CHAT_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434
OLLAMA_MODEL=deepseek-r1:7b
# Embedding Configuration
EMBEDDINGS_PROVIDER=ollama
OLLAMA_EMBEDDINGS_MODEL=nomic-embed-text

# Vector Database Configuration
VECTOR_STORE_TYPE=chroma
CHROMA_DB_HOST=chromadb
CHROMA_DB_PORT=8000

# MySQL Configuration
MYSQL_SERVER=db
MYSQL_USER=ragwebui
MYSQL_PASSWORD=ragwebui
MYSQL_DATABASE=ragwebui

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=documents
````

Note: Here we use Docker Compose service names instead of localhost so that containers can communicate with each other correctly.

### 3. Start the Services

Use Docker Compose to start all services:

````bash
docker compose up -d --build
````

This will start the following services:

- Frontend (Next.js)
- Backend API (FastAPI)
- MySQL Database
- ChromaDB Vector Database
- MinIO Object Storage
- Ollama Service

### 4. Verify Deployment

Once the services are running, you can access them at:

- Frontend: <http://localhost:80>
- API Docs: <http://localhost:8000/redoc>
- MinIO Console: <http://localhost:9001>

## 📚 User Guide

### 1. Create a Knowledge Base

1. Visit <http://localhost:3000>
2. Log in and click "Create Knowledge Base"
3. Enter the knowledge base name and description
4. Upload documents, select chunking method and size
5. Click "Create"
6. Wait for document processing to complete

Supported formats:

- PDF
- DOCX
- Markdown
- Text
- ...
### 2. Start a Conversation

1. Click "Start Conversation"
2. Enter your question
3. The system will automatically:
   - Retrieve relevant document fragments
   - Use the deepseek-r1:7b model to generate an answer
   - Display the cited sources

## ❓ Frequently Asked Questions

1. Ollama service cannot connect
   - Check if Ollama is running: `ollama list`
   - Check if Docker network configuration is correct

2. Document processing failed
   - Check if the document format is supported
   - View backend logs: `docker compose logs -f backend`

3. Out of memory
   - Adjust Docker container memory limits
   - Consider using a smaller model

> 💡 Performance & Security Tips: It is recommended that a single document does not exceed 10MB. Regularly back up your data and change default passwords promptly to ensure system security.

## 🎯 Conclusion

By following the above steps, you have successfully set up a local knowledge base system based on RAG technology. This system is fully deployed locally, so you don't need to worry about data privacy issues. With the power of Ollama, you can achieve high-quality knowledge Q&A services.

Note: This system is mainly for learning and personal use. For production environments, further security and stability optimizations are required.

## 📚 References

- [Ollama Official Documentation](https://ollama.com/)
- [RAG Web UI Project](https://github.com/rag-web-ui/rag-web-ui)
- [Docker Documentation](https://docs.docker.com/)

Hope this tutorial helps you build your personal knowledge base! If you encounter any issues, please refer to the project documentation or open an issue on GitHub.
