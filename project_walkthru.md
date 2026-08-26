# RAG Demo — Azure / Python / Terraform

**A small-scale RAG application designed to demonstrate enterprise-oriented Data Engineering, Cloud Engineering and AI/LLM engineering principles.**

**Interview walkthrough:** ~10–15 minutes

---

## 1. Why this project?

The goal was not to build a large production system.
The dataset is intentionally small. 

I wanted a **small, understandable RAG application** that demonstrates how I approach an AI application from an engineering perspective:

- **Cloud Data Engineering** — ingestion, chunking, embeddings, indexing and deduplication, using Azure-managed services.
- **AI / LLM Engineering** — embeddings, retrieval and grounded generation
- **Infrastructure as Code** — Terraform
- **Security** — Azure Key Vault for application secrets
- **Best Practices** — modular architecture and config vs. application-logic separation



### Design principles

| Principle | How it is applied |
|---|---|
| **Infrastructure as Code** | Azure resources are defined through Terraform |
| **Separation of layers** | Ingestion, retrieval, generation, API, GUI and infrastructure are separated |
| **Config ≠ app. logic** | Runtime settings are centralized in configuration |
| **Security by design** | Azure credentials/endpoints are retrieved through Key Vault |
| **API serving-interface** | The API can serve clients other than Streamlit |


---

## 2. Architecture at a glance

Application modules dependency graph:

```mermaid
flowchart TB
    APP["Application"]

    APP --> ING["Ingestion"]
    APP --> RET["Retrieval"]
    APP --> GEN["Generation"]
    APP --> CORE["Core"]

    CORE --> AZ["Azure services"]

    UI["Streamlit"] --> API["API"]

    API --> APP
```

Data-flow graph:

```mermaid
flowchart TD
    A["Wikipedia HTML articles"] --> B["INGESTION<br/>Load → Chunk → Hash → Embed → Index"]
    B --> C["Azure AI Search<br/>Text + embeddings + metadata"]

    U["User"] --> F["Streamlit GUI"]
    F --> API["OpenAPI / FastAPI layer"]
    API --> R["RAG application"]
    R --> C
    R --> G["Generation"]
    G --> OAI["Azure OpenAI"]
    C --> R

    style B fill:#eef,stroke:#447
    style R fill:#eef,stroke:#447
    style C fill:#efe,stroke:#484
    style OAI fill:#efe,stroke:#484
```

---

# 3. The data

The demo uses a small collection of **Wikipedia articles about The Hobbit / Middle-earth**.

The repository contains the source URL list under:

```text
data/
├── README.md
└── sources/
    └── wiki_urls.txt
```

The goal of the project is not web-crawling, therefore **downloaded HTML documents** are used as the input to the ingestion pipeline (with some parsing logic applied).

Pages:
1. https://en.wikipedia.org/wiki/The_Hobbit
1. https://en.wikipedia.org/wiki/Middle-earth
1. https://en.wikipedia.org/wiki/Bilbo_Baggins
1. https://en.wikipedia.org/wiki/Hobbit
1. https://en.wikipedia.org/wiki/Gandalf
1. https://en.wikipedia.org/wiki/Dwarves_in_Middle-earth
1. https://en.wikipedia.org/wiki/List_of_The_Hobbit_characters
1. https://en.wikipedia.org/wiki/Smaug
1. https://en.wikipedia.org/wiki/Thorin_Oakenshield
1. https://en.wikipedia.org/wiki/Lonely_Mountain
1. https://en.wikipedia.org/wiki/Elrond
1. https://en.wikipedia.org/wiki/Gollum
1. https://en.wikipedia.org/wiki/Warg#J._R._R._Tolkien
1. https://en.wikipedia.org/wiki/Beorn
1. https://en.wikipedia.org/wiki/Esgaroth
1. https://en.wikipedia.org/wiki/Bard_the_Bowman
1. https://en.wikipedia.org/wiki/Rivendell
1. https://en.wikipedia.org/wiki/Geography_of_Middle-earth#Misty_Mountains
1. https://en.wikipedia.org/wiki/One_Ring
1. https://en.wikipedia.org/wiki/Mirkwood

### Why Wikipedia?

For a demo, the important thing is not the domain itself.

Wikipedia provides:

- real-world unstructured text
- different article lengths
- headings and paragraphs
- entity-rich content
- enough semantic relationships to demonstrate retrieval

It also makes the demo easy to understand during an interview.

---

# 4. Live demo

'Who is Bilbo Baggins?' vs. 'Who is Harry Potter?'

---

# 5. Azure infrastructure

The infrastructure is defined in:

```text
terraform/
```

The main Azure resources are:

| Resource | Purpose |
|---|---|
| **Resource Group** | logical container |
| **Azure Key Vault** | Secrets and service endpoints |
| **Azure Storage Account** | Terraform state |
| **Azure OpenAI** | AI-endpoint container, where  models can be deployed (gpt-4o, text-embedding-3-large) |
| **GPT-4o-mini** | actual LLM engine |
| **text-embedding-3-small** | embeddings |
| **Azure AI Search** | Vector-search, Document-indexing |

At a high level:

```mermaid
flowchart TB
    RAG["RAG Application"]

    RAG --> OAI["Azure OpenAI<br/>GPT-4o-mini + Embeddings"]
    RAG --> SEARCH["Azure AI Search<br/>Vector + Keyword Search"]
    RAG --> KV["Azure Key Vault<br/>Secrets / Endpoints"]

    TF["Terraform"] --> OAI
    TF --> SEARCH
    TF --> KV
    TF --> STORAGE["Azure Storage<br/>Terraform State"]
    TF --> RG["Azure Resource Group"]
```

The Terraform configuration creates Azure OpenAI with separate deployments for embeddings and generation.



---

# 6. Security / secrets

Application secrets are not hardcoded into the RAG modules.

The application retrieves secrets through the central client layer, while Terraform provisions the relevant Key Vault secrets.


That keeps credentials out of the application logic and makes the application configuration easier to manage.

---

# 7. RAG pipeline

The RAG implementation is deliberately separated into three major stages - Ingestion, Retrieval and Generation.

Each stage has its own module:

```text
rag_app/
├── ingestion/
├── retrieval/
└── generation/
```

---

## 7.1 Ingestion

The ingestion flow is:

```mermaid
flowchart LR
    H["HTML"] --> L["Load / clean text"]
    L --> C["Chunk"]
    C --> E["Generate embeddings"]
    E --> D["Create Search documents"]
    D --> U["Upload to Azure AI Search"]
```

The orchestration lives in:

```text
rag_app/ingestion/ingest.py
```

The ingestion process loads each HTML document, chunks it, generates embeddings and uploads the resulting documents to Azure AI Search.

---

## 7.2 Chunking strategy

Chunking is intentionally isolated from the rest of ingestion.

```text
rag_app/ingestion/chunking.py
```

Instead of embedding chunking decisions throughout the ingestion code, ingestion simply receives a `ChunkingStrategy`.

That makes it easier to experiment with chunking parameters without rewriting the ingestion pipeline.

---

# 8. Embeddings and indexing

Each chunk is converted into an embedding using the Azure OpenAI embedding deployment.

The embedding layer validates that:

- an input was provided
- the number of embeddings matches the number of inputs
- the returned embedding dimension matches the configured dimension

The resulting Search document contains both the original content and its vector:

```text
{
    chunk_id
    content
    contentVector
    source
    title
    chunk_index
    strategy_name
    content_hash
}
```


### Why keep the metadata?

The vector is useful for retrieval, but metadata is useful for everything around retrieval (filtering, debugging, governance etc):

```text
content
source
title
chunk_index
strategy
hash
```

---

# 9. Incremental / idempotent ingestion

The ingestion pipeline also includes a simple deduplication mechanism.

Before processing a file:

```mermaid
flowchart TD
    F["HTML file"] --> H["SHA-256 hash"]
    H --> Q{"Already ingested?"}
    Q -->|"YES"| SKIP["Skip"]
    Q -->|"NO"| PROCESS["Process"]
```

The ingestion metadata index stores:

```text
file_hash
strategy_name
embedding_model
source
ingested_at
```

A pipeline should not blindly regenerate embeddings every time it runs (prevents data-skew if same chunk gets re-ingested 100 times by mistake).

---

# 10. Retrieval

The retrieval path is:

```mermaid
flowchart LR
    Q["User question"] --> E["Generate query embedding"]
    E --> S["Azure AI Search"]
    Q --> S
    S --> D["Retrieved chunks"]
    D --> DD["Deduplicate"]
    DD --> SORT["Sort by score"]
    SORT --> K["Top-K"]
    K --> B["Context"]
    B --> C["Formatted context"]
```

The active search implementation generates an embedding for the query and sends both:

- the original query as `search_text`
- the embedding as a vector query

to Azure AI Search.

This gives the system both:

**Semantic retrieval**

```text
"What happened to the dragon?"
```

and

**Keyword/entity matching**

```text
"Smaug"
"Bilbo"
"Thorin"
```

---

## Retrieval post-processing

Raw search results are not immediately passed to the LLM.

The retrieval layer performs several steps:

```mermaid
flowchart LR
    RAW["Raw results"] --> N["Normalize"]
    N --> D["Deduplicate"]
    D --> S["Sort by score"]
    S --> K["Top-K"]
    K --> B["Context-size budget"]
    B --> F["Formatted context"]
```



---

# 11. Generation

Once retrieval has produced the relevant context:

```mermaid
flowchart LR
    Q["Question"] --> P["Prompt"]
    C["Retrieved context"] --> P
    P --> OAI["Azure OpenAI"]
    OAI --> A["Answer"]
```

Generation is separated from retrieval under:

```text
rag_app/generation/
```

This keeps the LLM interaction independent from the mechanism used to find the supporting documents.

This separation would make it possible to change the retrieval implementation without redesigning the generation layer.

---

# 12. Project structure

```text
dabrm-rag_phase2_azure_iac/
│
├── data/
│   ├── README.md
│   └── sources/
│       └── wiki_urls.txt
│
├── frontend/
│   └── streamlit_app.py
│
├── loaders/
│   └── wiki_loader.py
│
├── rag_app/
│   │
│   ├── api/
│   │   └── app.py
│   │
│   ├── core/
│   │   ├── clients.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── generation/
│   │   ├── generate.py
│   │   └── prompts.py
│   │
│   ├── ingestion/
│   │   ├── chunking.py
│   │   ├── create_index.py
│   │   ├── embeddings.py
│   │   ├── hashing.py
│   │   ├── indexing.py
│   │   └── ingest.py
│   │
│   └── retrieval/
│       ├── query_rewrite.py
│       ├── retrieve.py
│       └── search.py
│
├── terraform/
│   ├── openai.tf
│   ├── openai_deployment.tf
│   ├── search.tf
│   ├── key_vault.tf
│   ├── storage.tf
│   └── ...
│
└── requirements.txt
```


---
