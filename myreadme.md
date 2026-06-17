<div align="center">
 
 
  <p>
    <strong>Knowledge Base Management Based on RAG (Retrieval-Augmented Generation)</strong>
  </p>


  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#deployment-guide">Deployment</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#development">Development</a> •
    <a href="#contributing">Contributing</a> •
    <a href="https://deepwiki.com/rag-web-ui/rag-web-ui" target="_blank">DeepWiki</a>
  </p>
</div>

## 📖 Introduction
RAG Web UI is an intelligent dialogue system based on RAG (Retrieval-Augmented Generation) technology that helps build intelligent Q&A systems based on your own knowledge base. By combining document retrieval and large language models, it achieves accurate and reliable knowledge-based question answering services.

The system supports multiple **LLM** deployment options, including cloud services like **OpenAI**, **DeepSeek**, and **[MiniMax](https://www.minimax.io)**, as well as local model deployment through **Ollama**, meeting privacy and cost requirements in different scenarios.

It also provides OpenAPI interfaces for convenient knowledge base access via API calls.

## ✨ Features
- 📚 **Intelligent Document Management**
  - Support for multiple document formats (PDF, DOCX, Markdown, Text)
  - Automatic document chunking and vectorization
  - Support for async document processing and incremental updates

- 🤖 **Advanced Dialogue Engine**
  - Precise retrieval and generation based on RAG
  - Support for multi-turn contextual dialogue
  - Support for reference citations in conversations

- 🎯 **Robust Architecture**
  - Frontend-backend separation design
  - Distributed file storage
  - High-performance vector database: Support for ChromaDB, Qdrant with easy switching through Factory pattern

## 🖼️ Screenshots

<div align="center">
  <img src="./docs/images/screenshot1.png" alt="Knowledge Base Management" width="800">
  <p><em>Knowledge Base Management Dashboard</em></p>
  
  <img src="./docs/images/screenshot2.png" alt="Chat Interface" width="800">
  <p><em>Document Processing Dashboard</em></p>
  
  <img src="./docs/images/screenshot3.png" alt="Document Processing" width="800">
  <p><em>Document List</em></p>
  
  <img src="./docs/images/screenshot4.png" alt="System Settings" width="800">
  <p><em>Intelligent Chat Interface with References</em></p>
  
  <img src="./docs/images/screenshot5.png" alt="Analytics Dashboard" width="800">
  <p><em>API Key Management</em></p>

  <img src="./docs/images/screenshot6.png" alt="Analytics Dashboard" width="800">
  <p><em>API Reference</em></p>
</div>
