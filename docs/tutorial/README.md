# 零基础入门：如何用 RAG (检索增强生成) 打造知识库 QA 系统

## 写在前面

马上今年要过去了，这个项目是在 2025 年 1 月份闲暇时间发起一个类似于教育类的项目。

其目的更多是希望可以在不依赖其他大的基础设施，结合自己多个 RAG 项目的经验，

用大家手头上已有的工具，通过跑通一个全流程的 RAG 知识库项目，来帮助更多的同学认识和入门 RAG 和知识库。

所以在这个项目里面，你当前还不会看到很多关于 RAG 的细节，例如多路召回、HyDE、Query 改写等能力（当然，我看到社区里面有能力的同学已经在帮忙实现这些能力 ING 了）。

项目流程图：

```mermaid
graph TB
    %% Role Definitions
    client["Caller/User"]
    open_api["Open API"]
    
    subgraph import_process["Document Ingestion Process"]
        direction TB
        %% File Storage and Document Processing Flow
        docs["Document Input<br/>(PDF/MD/TXT/DOCX)"]
        job_id["Return Job ID"]
        
        nfs["NFS"]

        subgraph async_process["Asynchronous Document Processing"]
            direction TB
            preprocess["Document Preprocessing<br/>(Text Extraction/Cleaning)"]
            split["Text Splitting<br/>(Segmentation/Overlap)"]
            
            subgraph embedding_process["Embedding Service"]
                direction LR
                embedding_api["Embedding API"] --> embedding_server["Embedding Server"]
            end
            
            store[(Vector Database)]
            
            %% Internal Flow of Asynchronous Processing
            preprocess --> split
            split --> embedding_api
            embedding_server --> store
        end
        
        subgraph job_query["Job Status Query"]
            direction TB
            job_status["Job Status<br/>(Processing/Completed/Failed)"]
        end
    end
    
    %% Query Service Flow  
    subgraph query_process["Query Service"]
        direction LR
        user_history["User History"] --> query["User Query<br/>(Based on User History)"]
        query --> query_embed["Query Embedding"]
        query_embed --> retrieve["Vector Retrieval"]
        retrieve --> rerank["Re-ranking<br/>(Cross-Encoder)"]
        rerank --> context["Context Assembly"]
        context --> llm["LLM Generation"]
        llm --> response["Final Response"]
        query -.-> rerank
    end
    
    %% Main Flow Connections
    client --> |"1.Upload Document"| docs
    docs --> |"2.Generate"| job_id
    docs --> |"3a.Trigger"| async_process
    job_id --> |"3b.Return"| client
    docs --> nfs
    nfs --> preprocess

    %% Open API Retrieval Flow
    open_api --> |"Retrieve Context"| retrieval_service["Retrieval Service"]
    retrieval_service --> |"Access"| store
    retrieval_service --> |"Return Context"| open_api

    %% Status Query Flow
    client --> |"4.Poll"| job_status
    job_status --> |"5.Return Progress"| client
    
    %% Database connects to Query Service
    store --> retrieve

    %% Style Definitions (Adjusted to match GitHub theme colors)
    classDef process fill:#d1ecf1,stroke:#0077b6,stroke-width:1px
    classDef database fill:#e2eafc,stroke:#003566,stroke-width:1px
    classDef input fill:#caf0f8,stroke:#0077b6,stroke-width:1px
    classDef output fill:#ffc8dd,stroke:#d00000,stroke-width:1px
    classDef rerank fill:#cdb4db,stroke:#5a189a,stroke-width:1px
    classDef async fill:#f8edeb,stroke:#7f5539,stroke-width:1px,stroke-dasharray: 5 5
    classDef actor fill:#fefae0,stroke:#606c38,stroke-width:1px
    classDef jobQuery fill:#ffedd8,stroke:#ca6702,stroke-width:1px
    classDef queryProcess fill:#d8f3dc,stroke:#40916c,stroke-width:1px
    classDef embeddingService fill:#ffe5d9,stroke:#9d0208,stroke-width:1px
    classDef importProcess fill:#e5e5e5,stroke:#495057,stroke-width:1px

    %% Applying classes to nodes
    class docs,query,retrieval_service input
    class preprocess,split,query_embed,retrieve,context,llm process
    class store,nfs database
    class response,job_id,job_status output
    class rerank rerank
    class async_process async
    class client,open_api actor
    class job_query jobQuery
    style query_process fill:#d8f3dc,stroke:#40916c,stroke-width:1px
    style embedding_process fill:#ffe5d9,stroke:#9d0208,stroke-width:1px
    style import_process fill:#e5e5e5,stroke:#495057,stroke-width:1px
    style job_query fill:#ffedd8,stroke:#ca6702,stroke-width:1px
```

## 1. 认识 RAG：为什么要"检索 + 生成"

### 1.1 什么是 RAG

RAG 是 Retrieval-Augmented Generation 的缩写，中文翻译为"检索增强生成"。它是一种将检索系统和生成式 AI 模型结合的技术方案，主要包含两个核心步骤：

1. 检索（Retrieval）：根据用户输入的问题，从知识库中检索出相关的文档或信息片段
2. 生成（Generation）：将检索到的相关信息作为上下文，结合用户问题，让大语言模型生成准确的回答

这种方案既能让模型基于最新的知识作答，又可以提供可溯源的参考依据，有效解决了大语言模型的知识时效性和事实准确性问题。

下面这张图展示了 RAG 在对话过程中的工作流程:

```mermaid
flowchart TD
    User["用户: 问题"] --> Retrieval["检索模块"]
    KB["知识库"] --> Doc1["相关文档1"]
    KB --> Doc2["相关文档2"]
    Retrieval --> Doc1
    Retrieval --> Doc2
    Doc1 --> LLM["大语言模型"]
    Doc2 --> LLM
    LLM --> Answer["助手: 生成的回答"]

    style User fill:#f9f,stroke:#333
    style KB fill:#bbf,stroke:#333
    style LLM fill:#bfb,stroke:#333
    style Answer fill:#fbb,stroke:#333
```

### 1.2 为什么需要 RAG

让我们对比三种问答方案的优缺点，来理解为什么 RAG 是一个更好的选择：

1. 传统检索式问答 (Retrieval QA)
   - ✅ 可靠性高：答案直接来自知识库，有明确的来源
   - ✅ 知识可更新：添加新文档即可更新知识
   - ❌ 灵活性差：只能返回知识库中已有的内容
   - ❌ 表达生硬：难以用自然语言组织答案

2. 纯 LLM 问答
   - ✅ 表达自然：能用流畅的语言组织答案
   - ✅ 灵活理解：可以理解各种表达方式的问题
   - ❌ 知识固化：知识仅限于训练数据，无法及时更新
   - ❌ 可靠性差：容易产生幻觉，难以验证答案准确性

3. RAG 方案
   - ✅ 可靠且可溯源：答案基于检索到的具体文档
   - ✅ 知识可更新：可以持续添加新的知识
   - ✅ 表达自然：利用 LLM 的语言能力组织答案
   - ✅ 灵活理解：能理解各种形式的问题
   - ✅ 成本可控：主要消耗在必要的 API 调用上

RAG 通过将检索和生成相结合，既保留了传统检索问答的可靠性，又获得了 LLM 的灵活性和自然表达能力。它能让 AI 始终基于最新的、可信的知识来回答问题，同时保持对话的流畅自然。

RAG 的典型应用场景

- 企业知识库问答：帮助企业构建对内员工知识库或对外客户问答系统。
- 法律法规、论文等参考场景：需要给出权威来源或证据的回答。
- 任何需要"带有引用信息"的回答场景。

## 2. RAG 系统整体架构与数据流

### 2.1 核心组件

- 向量数据库：用来存储文档分块后的向量（如 ChromaDB、Qdrant）。
- Embedding（文本向量化）：将文本转化为可比较的数值向量，形如 [0.1, 0.2, 0.3, 0.4, 0.5]
- 检索 (Retrieval)：根据用户查询的向量相似度，检索出最相关的文档切片。
- 大语言模型：将检索到的上下文与用户问题组合，再由模型 (LLM) 生成最终答案。
- 生成 (Generation) 与引用：如何在回答中嵌入引用链接或标注，方便用户溯源。

### 2.2 RAG 的典型工作流

1) 用户输入问题。
2) 将问题向量化，然后检索最相似的文档切片。
3) 将检索到的上下文与问题拼接后输入 LLM。
4) LLM 输出带引用信息的回答。
5) 前端渲染回答、可选地在可视化界面中展示引用详情。

下面用一张图展示各个组件的交互流程：

```mermaid
flowchart TD
    User["用户问题"] --> Embedding["文本向量化\n(Embedding)"]
    DB[(知识库\n向量数据库)] --> Retrieval
    Embedding --> Retrieval["检索模块\n(相似度匹配)"]
    Retrieval --> Context["相关文档片段"]
    Context --> Assembly["上下文组装"]
    Assembly --> LLM["大语言模型"]
    LLM --> Answer["带引用的回答"]
    Answer --> Frontend["前端展示\n- 回答内容\n- 引用来源\n- 相关度"]

    style User fill:#f9f,stroke:#333
    style DB fill:#bbf,stroke:#333
    style LLM fill:#bfb,stroke:#333
    style Frontend fill:#fbb,stroke:#333
```

## 3. 构建知识库：文档处理、嵌入、存储

### 3.1 文档上传与分块 (Chunking)

#### 3.1.1 为什么要对文档进行分块？

文档分块是 RAG 系统中的一个关键步骤，主要有以下几个原因：

1. 向量相似度计算的精度

   - 过长的文本会导致向量表示不够精确
   - 较小的文本块能更好地捕捉局部语义
   - 有助于提高检索的准确性

2. LLM 的上下文窗口限制

   - LLM 的输入长度是有限的 （虽然 Qwen 已经推出了 1M token 的上下文窗口 0.0）
   - 需要将文档切分为适合 LLM 处理的大小
   - 避免超出 token 限制导致信息丢失

3. 检索效率与成本

   - 更小的文本块便于建立细粒度的索引
   - 只需检索最相关的片段，节省 token 用量
   - 减少无关信息，提高回答质量

4. 引用与溯源 （这个是 RAG 的特色功能）

   - 便于定位信息的具体来源
   - 可以给出更精确的引用范围
   - 有助于用户验证答案的可靠性

#### 3.1.2 常见的分块策略

1. 固定长度分块

   - 按字符数或 token 数进行切分
   - 实现简单，但可能切断语义完整的段落
   - 适合结构统一的文档

2. 语义分块

   - 按段落、章节等自然语义单位切分
   - 保持上下文的连贯性
   - 需要考虑文档的具体结构

3. 重叠分块

   - 相邻块之间保留一定重叠
   - 避免关键信息被切分
   - 增加了存储和计算开销

4. 递归分块

   - 先大块后细分
   - 保持层次结构
   - 适合长文档处理

选择合适的分块策略需要考虑：

- 文档的类型和结构
- 向量数据库的特性
- LLM 的上下文窗口大小
- 检索效率与成本的平衡

例如如果是 markdown，可以按段落进行分块，如果是一般文档，可以按章节进行分块。

```text
+--------------------------------------------------+
|  # Chapter 1 Title                               |
|  Main content...                                 |
|  Main content...                                 |
|                                                  |
|  ## 1.1 Section Title                            |
|  - List item 1                                   |
|  - List item 2                                   |
|                                                  |
|  ### 1.1.1 Subsection Title                      |
|  Main paragraph...                               |
|                                                  |
|  # Chapter 2 Title                               |
|  Another paragraph...                            |
+--------------------------------------------------+
                              |
                              v
                          Chunking 切片
                              |
                              v
+------------------+  +-------------------+  +------------------+
| Chunk 1:         |  | Chunk 2:          |  | Chunk 3:         |
| # Chapter 1      |  | ## 1.1 Section    |  | # Chapter 2      |
| Title            |  | Title             |  | Title            |
| Main content...  |  | - List item 1     |  | Another          |
| Main content...  |  | - List item 2     |  | paragraph...     |
+------------------+  |                   |  +------------------+
                      | ### 1.1.1         |
                      | Subsection Title  |
                      | Main paragraph... |
                      +-------------------+

```

### 3.2 文本向量化 (Embedding)

文本向量化是将自然语言文本转换为高维向量空间中的数值向量的过程。这种转换使得我们可以：

- 用数学方法计算文本之间的语义相似度
- 在向量空间中进行高效的相似度搜索
- 保留文本的语义信息和上下文关系

常用的文本向量化模型包括：

1. OpenAI Embeddings

   - text-embedding-ada-002 模型
   - 1536 维向量输出
   - 适用于英文等多种语言
   - 语义表达能力强

2. Sentence Transformers

   - 开源的句子级别编码器
   - 支持多语言
   - 可以根据场景微调
   - 计算效率高

在 RAG Web UI 中，主要是用的 OpenAI 的 text-embedding-ada-002 模型。

```python
from langchain_openai import OpenAIEmbeddings
...

embeddings = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY,
    openai_api_base=settings.OPENAI_API_BASE
)
```

### 3.3 向量数据库

在文本 Embedding 之后，需要将向量存储到向量数据库中，以便后续的检索和相似度计算。

在 RAG Web UI 中，主要是用的 ChromaDB 作为向量数据库， 同时支持使用 Factory 模式， 支持多种向量数据库，例如：

1. ChromaDB
2. Qdrant
3. Milvus
4. Faiss
5. Annoy
6. Pinecone
7. Zilliz

向量数据库除了存储向量，还要携带某些元信息(文档来源、段落位置等)方便查阅， 一般情况下，我们会存入这样的数据结构到向量数据库中：

除了向量之外， 我们还需要存入一些元数据， 例如：

```python
{
    "id": "chunk_id",
    "text": "段落内容",
    "metadata": {"source": "文档来源", "position": "段落位置", "hash": "段落哈希值"}
}
```

## 4. 检索与重排序：用最相关的上下文喂给大模型

### 4.1 相似度检索 (Similarity Search)

常用的相似度度量：余弦相似度、向量距离 (欧几里得距离) 等。

ChromaDB 支持多种相似度计算方法:

1. Cosine Similarity (余弦相似度)

   - 计算两个向量夹角的余弦值
   - 值域范围为 [-1,1]，越接近 1 表示越相似
   - 不受向量长度影响，只关注方向
   - 计算公式: cos(θ) = (A·B)/(||A||·||B||)

2. L2 Distance (欧氏距离)

   - 计算两个向量间的直线距离
   - 值越小表示越相似
   - 受向量长度影响
   - 计算公式: d = √(Σ(ai-bi)²)

3. IP (Inner Product, 内积)

   - 两个向量对应位置相乘后求和
   - 值越大表示越相似
   - 受向量长度影响
   - 计算公式: IP = Σ(ai×bi)

ChromaDB 默认使用 Cosine Similarity，这也是最常用的相似度计算方法，因为:

- 计算简单高效
- 不受向量绝对大小影响
- 对于文本语义相似度计算效果好
- 结果容易解释和标准化

在实际使用中，可以根据具体场景选择合适的相似度算法:

- 如果向量已归一化，三种方法等价
- 对向量长度敏感时选择 Cosine
- 关注绝对距离时选择 L2
- 需要快速计算时可用 IP

### 4.2 重排序 (Re-ranking) 重要吗？

重排序是一个重要的步骤，可以显著提升检索结果的质量。其工作原理如下：

1. 初步检索

   - 首先使用向量相似度搜索召回一批候选文档(如前20-100条)
   - 这一步计算快速但可能不够精确

2. Cross-Encoder 重排序

   - 对召回的候选文档进行更精细的相关性打分
   - Cross-Encoder 会同时看到 query 和文档内容，计算它们的匹配度
   - 相比向量相似度，能更好地理解语义关联
   - 但计算开销较大，所以只用于重排少量候选

3. 应用场景

   - 多路召回：不同检索方式召回的结果需要统一排序
   - 高精度要求：需要更准确的相关性排序
   - 复杂查询：简单向量相似度可能不足以理解查询意图

4. 常见实现

   - 使用预训练的 Cross-Encoder 模型(如 BERT)
   - 可以针对具体任务进行微调
   - 输出相关性分数用于重新排序

虽然重排序会增加一定延迟，但在对准确度要求较高的场景下，这个成本通常是值得的。

### 4.3 拼接上下文与用户问题

在检索到相关文档片段后，需要将它们与用户问题拼接成合适的 prompt，以供 LLM 生成回答。

用户问题 + 检索到的上下文 = Prompt，最终由 LLM 输出回答。

以下是一些常见的拼接策略：

1. 基本结构

   - System: 系统指令，说明 AI 助手的角色和任务
   - Context: 检索到的相关文档片段
   - Human: 用户的实际问题
   - Assistant: AI 的回答

2. 拼接技巧

我们在项目中做了一个有意思的事情，就是可以使用 `[[citation:1]]` 这样的格式来引用检索到的上下文。

然后用户可以在前端通过 Markdown 的格式来展示引用信息, 并且通过弹窗来展示引用详情。

![引用信息](../images/screenshot4.png)

在 RAG Web UI 中， 我们使用 LangChain 的模板来实现这个功能：

可查阅： `backend/app/services/chat_service.py`

```python
from langchain.prompts import PromptTemplate

qa_system_prompt = (
      "You are given a user question, and please write clean, concise and accurate answer to the question. "
      "You will be given a set of related contexts to the question, which are numbered sequentially starting from 1. "
      "Each context has an implicit reference number based on its position in the array (first context is 1, second is 2, etc.). "
      "Please use these contexts and cite them using the format [citation:x] at the end of each sentence where applicable. "
      "Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. "
      "Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. "
      "Say 'information is missing on' followed by the related topic, if the given context do not provide sufficient information. "
      "If a sentence draws from multiple contexts, please list all applicable citations, like [citation:1][citation:2]. "
      "Other than code and specific names and citations, your answer must be written in the same language as the question. "
      "Be concise.\n\nContext: {context}\n\n"
      "Remember: Cite contexts by their position number (1 for first context, 2 for second, etc.) and don't blindly "
      "repeat the contexts verbatim."
  )
```

## 5. 工程实战示例：RAG 在知识库 QA 中的流程

理论的事情，相信大家都了解了，相信大家也看过不少的文章，但是可能没有真正动手实践过，或者项目太复杂无从下手，或是没有一个完整的项目可以参考。

在工程的实践中，去掉那些花里胡哨的东西， 直接上代码，直接上手实践，才是这个项目的意义所在。

这个项目中，用的都是目前最为流行的技术栈， 例如：

- 前端：React（Nextjs） + TailwindCSS + AI SDK
- 后端：FastAPI + LangChain + ChromaDB/Qdrant + MySQL + MinIO
- 部署：Docker + Docker Compose

让我们通过一个完整的工程实现示例，来理解 RAG 在知识库问答中的具体应用流程。我们将按照数据流的顺序，逐步解析关键代码的实现。

### 5.1 文档上传 → 异步处理

详细代码可以参考： `backend/app/services/document_processor.py`

![文档上传](../images/screenshot2.png)

从上面的系统架构图中可以看到，文档上传和处理的流程如下：

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant NFS
    participant Queue
    participant Worker
    participant VectorDB

    Client->>API: 上传文档
    API->>NFS: 存储文档
    API->>Queue: 创建处理任务
    API-->>Client: 返回 Job ID

    loop 状态查询
        Client->>API: 查询进度 (Job ID)
        API-->>Client: 返回处理状态
    end

    Queue->>Worker: 分发任务
    Worker->>NFS: 读取文档
    Worker->>Worker: 文本提取
    Worker->>Worker: 文本分块
    Worker->>Worker: 向量化处理
    Worker->>VectorDB: 存储向量数据
    Worker->>Queue: 更新任务状态
```

1. 用户上传文档 (PDF/MD/TXT/DOCX)
   - 客户端发起文档上传请求
   - 文档被临时存储到 NFS (Network File System)
   - 系统生成并返回一个 Job ID 给客户端

2. 异步处理流程启动
   - 文档预处理：提取文本、清洗数据
   - 文本分块：按照设定的策略进行分段
   - 向量化：通过 Embedding 服务将文本转换为向量
   - 存储：将向量数据保存到向量数据库

3. 状态查询
   - 客户端通过 Job ID 轮询任务状态
   - 系统返回当前进度 (Processing/Completed/Failed)

这种异步处理的设计有以下优点：

- 支持大文件处理：不会因处理时间过长导致请求超时
- 提升用户体验：用户可以实时查看处理进度
- 系统解耦：文档处理与存储服务可以独立扩展
- 错误处理：失败任务可以重试，不影响其他上传

在代码实现中，主要涉及以下几个关键组件：

1. 文件上传接口
2. 任务队列系统
3. 异步处理服务
4. 状态查询接口

这种设计让整个文档处理流程更加健壮和可扩展。

当然这里也设计也有设计到一些小细节，例如在处理文档的时候，可能很多系统都会选择先删后增，但是这样会导致向量数据库中的数据被删除，从而导致检索结果不准确。所以我们这里会通过一个临时表来实现这个功能，确保新的文件被处理后，旧的文件才被删除。

### 5.2 用户提问 → 检索 + LLM 生成

代码可查阅： `backend/app/services/chat_service.py`

从前端使用 AI SDK 发送到后台，后台接口接收后会进行，用户 Query 的处理流程如下:

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant VectorStore
    participant LLM

    User->>Frontend: 发送问题
    Frontend->>Backend: 发送请求
    
    rect rgb(200, 220, 250)
        Note over Backend: 消息存储阶段
        Backend->>DB: 存储用户问题(user类型)
        Backend->>DB: 创建空assistant记录
    end
    
    rect rgb(200, 250, 220)
        Note over Backend: 知识库准备阶段
        Backend->>VectorStore: 初始化向量存储
        Backend->>VectorStore: 获取相关知识库
    end
    
    rect rgb(250, 220, 200)
        Note over Backend: RAG处理阶段
        Backend->>VectorStore: 执行相似度检索
        VectorStore-->>Backend: 返回相关文档
        Backend->>LLM: 发送上下文化问题请求
        LLM-->>Backend: 返回重构后的问题
        Backend->>LLM: 发送最终生成请求
        LLM-->>Backend: 流式返回答案
    end
    
    Backend-->>Frontend: 流式返回(context + answer)
    
    rect rgb(220, 220, 250)
        Note over Frontend: 响应处理阶段
        Frontend->>Frontend: 解析context(base64)
        Frontend->>Frontend: 解析引用标记
        Frontend->>Frontend: 渲染回答和引用
    end
    
    Frontend-->>User: 展示答案和引用
```

1. **消息存储**
   - 将用户的提问内容保存为 user 类型的消息记录
   - 创建一个空的 assistant 类型消息记录作为占位符

2. **知识库准备**
   - 根据传入的 knowledge_base_ids 获取相关知识库
   - 初始化 OpenAI Embeddings
   - 为每个知识库创建对应的向量存储 (Vector Store)

3. **检索增强生成 (RAG) 处理**
   - 使用向量存储创建检索器 (Retriever)
   - 构建两个关键提示词模板:
     - `contextualize_q_prompt`: 用于理解聊天历史上下文,重新构造独立的问题
     - `qa_prompt`: 用于生成最终答案,包含引用格式要求和语言适配等规则

4. **响应生成**
   - 处理历史聊天记录,构建对话上下文
   - 使用流式响应逐步生成内容
   - 响应内容包含两部分:
     - 相关文档上下文 (base64 编码)
     - LLM 生成的回答内容

5. **结果处理**
   - 实时返回生成的内容片段
   - 更新数据库中的 assistant 消息记录
   - 完整响应格式: `{context_base64}__LLM_RESPONSE__{answer}`

6. **异常处理**
   - 捕获并记录生成过程中的错误
   - 更新错误信息到消息记录
   - 确保数据库会话正确关闭

前端接收到后台返回的 stream 返回以后，可开始解析这个 stream 后， 除了正常和其他 QA 聊天工具一样， 这里还多了一个引用信息， 所以需要解析出引用信息， 然后展示在页面上。

他是怎么运作的呢？这里前端会通过 `__LLM_RESPONSE__` 这个分隔符来解析, 前面一部分是 RAG 检索出来的 context 信息（base64 编码， 可以理解为是检索出来的切片的数组），后面是 LLM 按照 context 回来的信息， 然后通过 `[[citation:1]]` 这个格式来解析出引用信息。

```mermaid
flowchart TD
    A[接收Stream响应] --> B{解析响应}
    B -->|分割| C[Context部分]
    B -->|分割| D[Answer部分]
    
    C --> E[Base64解码]
    E --> F[解析引用信息]
    
    D --> G[解析引用标记]
    G --> H[[citation:1]]
    
    F --> I[准备引用数据]
    H --> I
    
    I --> J[渲染回答内容]
    J --> K[显示引用弹窗]
```

代码可查询：

- Chat 页面：`frontend/src/app/dashboard/chat/[id]/page.tsx`
- 引用信息展示：`frontend/src/components/chat/answer.tsx`

```js
  const CitationLink = useMemo(
    () =>
      (
        props: ClassAttributes<HTMLAnchorElement> &
          AnchorHTMLAttributes<HTMLAnchorElement>
      ) => {
        const citationId = props.href?.match(/^(\d+)$/)?.[1];
        const citation = citationId
          ? citations[parseInt(citationId) - 1]
          : null;

        if (!citation) {
          return <a>[{props.href}]</a>;
        }

        const citationInfo =
          citationInfoMap[
            `${citation.metadata.kb_id}-${citation.metadata.document_id}`
          ];

        return (
          <Popover>
            <PopoverTrigger asChild>
              <a
                {...props}
                href="#"
                role="button"
                className="inline-flex items-center gap-1 px-1.5 py-0.5 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors relative"
              >
                <span className="absolute -top-3 -right-1">[{props.href}]</span>
              </a>
            </PopoverTrigger>
            <PopoverContent
              side="top"
              align="start"
              className="max-w-2xl w-[calc(100vw-100px)] p-4 rounded-lg shadow-lg"
            >
              <div className="text-sm space-y-3">
                {citationInfo && (
                  <div className="flex items-center gap-2 text-xs font-medium text-gray-700 bg-gray-50 p-2 rounded">
                    <div className="w-5 h-5 flex items-center justify-center">
                      <FileIcon
                        extension={
                          citationInfo.document.file_name.split(".").pop() || ""
                        }
                        color="#E2E8F0"
                        labelColor="#94A3B8"
                      />
                    </div>
                    <span className="truncate">
                      {citationInfo.knowledge_base.name} /{" "}
                      {citationInfo.document.file_name}
                    </span>
                  </div>
                )}
                <Divider />
                <p className="text-gray-700 leading-relaxed">{citation.text}</p>
                <Divider />
                {Object.keys(citation.metadata).length > 0 && (
                  <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                    <div className="font-medium mb-2">Debug Info:</div>
                    <div className="space-y-1">
                      {Object.entries(citation.metadata).map(([key, value]) => (
                        <div key={key} className="flex">
                          <span className="font-medium min-w-[100px]">
                            {key}:
                          </span>
                          <span className="text-gray-600">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </PopoverContent>
          </Popover>
        );
      },
    [citations, citationInfoMap]
  );
```

当用户点击引用信息的时候， 会弹出一个弹窗， 展示引用详情， 包括知识库名称， 文件名称， 以及引用内容。

## 6. 拓展：根据需求定制你的 RAG

### 6.1 不同的向量数据库或大语言模型

目前已经通过 Factory 模式， 支持了不同的向量数据库、不同的大模型，例如 Ollama 也有同学在支持， 可以参考 `backend/app/services/vector_store/factory.py` 这个文件。

### 6.2 Chunk 分割策略与 Embedding 模型的调整

不同的 Embedding 模型对多语言支持和文本类型有不同的特点：

- **多语言支持**：
  - `text-embedding-ada-002`：支持多种语言，但对中文等亚洲语言的支持相对较弱
  - `bge-large-zh`：对中文有很好的支持
  - `multilingual-e5-large`：对多语言都有较好的支持

- **文本类型适用性**：
  - 代码文本：建议使用专门的代码 Embedding 模型，如 `CodeBERT`
  - 通用文本：可以使用 `text-embedding-ada-002` 或 `bge-large-zh`
  - 专业领域文本：建议使用该领域的专门模型

选择合适的 Embedding 模型可以显著提升检索效果。

## 7. 总结与下一步

整个项目到这里就结束了， 整个项目中， 我们通过一个完整的工程实现示例， 来理解 RAG 在知识库问答中的具体应用流程。

如果你需要 Ask Me Anything， 可以通过 [Issue](https://github.com/rag-web-ui/rag-web-ui/issues) 来联系我。

你可以深入研究的方向

- 多路召回（多个数据库或不同关注点检索结果的合并）
- RAG + 交叉编码 re-ranking 提高回答精度
- 长文本多轮对话（上下文记忆 / Conversation Memory）

- [LangChain 官网](https://python.langchain.com/)  
- [ChromaDB](https://docs.trychroma.com/)  
- [OpenAI Embeddings 介绍](https://platform.openai.com/docs/guides/embeddings)  

## 8. 处理网络错误和无法访问的服务器

在注册账户时，可能会遇到网络错误或服务器无法访问的问题。以下是一些处理这些问题的方法：

### 8.1 更新依赖项

确保 `backend/requirements.txt` 文件中指定的依赖项版本是可用的。例如，将 `langchain-deepseek` 的版本更新为 `==0.1.1`：

```plaintext
langchain-deepseek==0.1.1
```

### 8.2 错误处理

在 `backend/app/api/api_v1/auth.py` 文件中添加错误处理，以捕获注册过程中可能出现的网络错误和无法访问的服务器问题：

```python
from requests.exceptions import RequestException

@router.post("/register", response_model=UserResponse)
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Register a new user.
    """
    try:
        # Check if user with this email exists
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists.",
            )
        
        # Check if user with this username exists
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists.",
            )
        
        # Create new user
        user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=security.get_password_hash(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except RequestException as e:
        raise HTTPException(
            status_code=503,
            detail="Network error or server is unreachable. Please try again later.",
        ) from e
```

### 8.3 重试机制

在 `backend/Dockerfile` 和 `docker-compose.yml` 文件中添加重试机制，以处理构建过程中可能出现的网络错误：

#### `backend/Dockerfile`

```dockerfile
# Install Python packages with retry mechanism
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Retrying in 5 seconds..." && sleep 5 && pip install --no-cache-dir -r requirements.txt) || \
    (echo "Retrying in 10 seconds..." && sleep 10 && pip install --no-cache-dir -r requirements.txt)
```

#### `docker-compose.yml`

```yaml
services:
  backend:
    build: ./backend
    restart: on-failure
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

通过以上方法，尝试处理注册账户时可能遇到的网络错误和无法访问的服务器问题。
