# Vector Database Setup Guide - Chroma DB

**Target Audience**: TypeScript developers learning Python
**Last Updated**: 2024-12-15
**Status**: Phase 2 - Task 2.1

---

## What is a Vector Database?

### The Concept

A vector database stores data as **numerical vectors** (arrays of numbers) that represent the *meaning* of text or code. Instead of searching for exact keyword matches, you can search for semantic similarity.

**TypeScript Analogy**:
```typescript
// Traditional search (keyword matching)
const results = files.filter(f => f.content.includes('authentication'));

// Vector DB search (semantic matching)
const results = vectorDB.search('how to handle user login');
// ↑ This finds: authentication, auth, login, sign-in, user sessions
```

### How It Works

1. **Embedding**: Text/code → AI model → Vector (array of ~1500 numbers)
2. **Storage**: Vectors stored with metadata (file path, author, date)
3. **Search**: Your query → Vector → Find similar vectors → Return original text

**Key Insight**: Similar concepts produce similar vectors, even with different words.

Example:
- "unit test" and "testing framework" have similar vectors
- "authentication" and "user login" have similar vectors
- This works across programming languages!

---

## Why Chroma DB?

We evaluated several vector databases for this project:

| Database | Pros | Cons | Decision |
|----------|------|------|----------|
| **Chroma** | ✅ Local files (no server)<br>✅ Python native<br>✅ Free & open source<br>✅ Simple API | ⚠️ Single-user only<br>⚠️ No built-in sync | **✅ CHOSEN** |
| Pinecone | ✅ Cloud-hosted<br>✅ Scalable | ❌ Requires paid account<br>❌ Data leaves local machine | ❌ |
| Weaviate | ✅ Feature-rich<br>✅ Self-hostable | ❌ Complex setup (Docker required)<br>❌ Overkill for our needs | ❌ |
| FAISS | ✅ Fast<br>✅ Facebook-backed | ❌ Low-level API<br>❌ No metadata support | ❌ |

**Decision**: Chroma is the best fit for a local, personal portfolio tool with no budget constraints.

---

## Installation

### Option 1: Python Library (Recommended)

We've already installed Chroma via `uv`:

```bash
uv add chromadb langchain-chroma
```

**What this gives you**:
- `chromadb`: Core vector database library
- `langchain-chroma`: Langchain integration (makes it easy to use with our AI models)

**TypeScript Equivalent**: Like installing `npm install @types/node` + framework integration

### Option 2: Docker (Alternative)

If you want an isolated service (not necessary for our use case):

```bash
# Pull Chroma Docker image
docker pull chromadb/chroma

# Run as service on port 8000
docker run -p 8000:8000 chromadb/chroma
```

**TypeScript Equivalent**: Like running a PostgreSQL container instead of using SQLite

⚠️ **Note**: We're using Option 1 (Python library) for simplicity. Docker adds unnecessary complexity for a local tool.

---

## Storage & Data Location

### Where Data Lives

Chroma stores vectors as **local files** in your project directory:

```
llm-council/
├── chroma_db/              # ← Vector database storage
│   ├── chroma.sqlite3      # Metadata (file paths, authors, dates)
│   └── index/              # Vector indexes
├── backend/
├── frontend/
└── ...
```

**TypeScript Analogy**: Like having a `.next` cache or `node_modules/.cache` directory—it's data that can be regenerated but speeds up operations.

### Gitignore Configuration

**Critical**: Never commit vector databases to Git!

```gitignore
# Vector database (regenerable from GitHub history)
chroma_db/

# Indexing state (tracks what's been indexed)
data/indexing_state.json
```

**Why?**
- Vector DBs are large (~100MB-1GB for your GitHub history)
- They contain embedded representations of your code (privacy concern)
- They're regenerable—just re-run the indexing script

**TypeScript Equivalent**: Like gitignoring `dist/`, `build/`, or `node_modules/`

---

## TypeScript ↔ Python Concepts

### Async Operations

**TypeScript**:
```typescript
async function searchCode(query: string): Promise<Results> {
  const results = await vectorDB.query(query);
  return results;
}
```

**Python**:
```python
async def search_code(query: str) -> Results:
    results = await vector_db.query(query)
    return results
```

**Key Differences**:
- Python uses `async def` instead of `async function`
- Python type hints come after the colon: `query: str`
- Python uses `->` for return types instead of `: ReturnType`

### Collections (like Database Tables)

**TypeScript Mental Model**:
```typescript
// IndexedDB-style thinking
const db = await openDB('myDB');
const store = db.transaction('users').objectStore('users');
```

**Chroma**:
```python
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("github_knowledge")
```

**Analogy**: Collections are like tables in SQL or object stores in IndexedDB.

### CRUD Operations

| Operation | TypeScript (IndexedDB) | Chroma |
|-----------|----------------------|--------|
| **Create** | `store.add(data)` | `collection.add(documents, ids, metadatas)` |
| **Read** | `store.get(id)` | `collection.get(ids)` |
| **Query** | `store.getAll()` | `collection.query(query_texts, n_results)` |
| **Delete** | `store.delete(id)` | `collection.delete(ids)` |

---

## Basic Operations

### 1. Initialize Client

```python
import chromadb

# Create persistent client (data saved to disk)
client = chromadb.PersistentClient(path="./chroma_db")

# TypeScript equivalent:
# const db = await open('./chroma_db', { create: true });
```

### 2. Create/Get Collection

```python
collection = client.get_or_create_collection(
    name="github_knowledge",
    metadata={
        "description": "Embedded GitHub history for portfolio",
        "created_at": "2024-12-15"
    }
)

# TypeScript equivalent:
# const collection = db.collection('github_knowledge');
```

### 3. Add Documents

```python
collection.add(
    documents=[
        "async function authenticate(user) { ... }",
        "def authenticate(user): ..."
    ],
    metadatas=[
        {"file": "auth.ts", "author": "jasonwarren", "date": "2024-03-15"},
        {"file": "auth.py", "author": "jasonwarren", "date": "2024-06-20"}
    ],
    ids=["auth_ts_001", "auth_py_001"]
)

# TypeScript equivalent:
# await store.put({ content, metadata }, id);
```

**Important**:
- `documents`: The actual text/code to embed
- `metadatas`: Structured data about the document (must be JSON-serializable)
- `ids`: Unique identifiers (we use format: `{repo}:{type}:{hash}:{chunk}`)

### 4. Query by Semantic Similarity

```python
results = collection.query(
    query_texts=["how to handle user authentication"],
    n_results=10,  # Top 10 most similar
    where={"author": "jasonwarren"}  # Filter metadata
)

# Returns:
# {
#   'ids': [['auth_ts_001', 'auth_py_001', ...]],
#   'documents': [[code snippets...]],
#   'metadatas': [[{file, author, date}, ...]],
#   'distances': [[0.23, 0.45, ...]]  # Similarity scores (lower = more similar)
# }
```

**TypeScript Equivalent**: Imagine Algolia or Elasticsearch, but for semantic meaning instead of keywords.

### 5. Get Collection Stats

```python
# How many documents?
count = collection.count()

# Peek at first few
peek = collection.peek(limit=5)

# TypeScript equivalent:
# const count = await store.count();
# const first5 = await store.getAll(5);
```

---

## Common Patterns

### Pattern 1: Chunking Large Files

Large files need to be split into smaller pieces:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # ~250 tokens
    chunk_overlap=200,      # Maintain context
    separators=["\n\n", "\n", " ", ""]  # Split on paragraphs first
)

chunks = splitter.split_text(large_file_content)

# Add each chunk with metadata
for i, chunk in enumerate(chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{"file": "large_file.py", "chunk": i}],
        ids=[f"large_file_{i}"]
    )
```

**Why?**
- Embedding models have token limits (~8000 tokens)
- Smaller chunks = more precise retrieval
- Overlap prevents losing context at boundaries

**TypeScript Analogy**: Like pagination or virtual scrolling—break big lists into manageable pieces.

### Pattern 2: Metadata Filtering

```python
# Find all testing code from 2024
results = collection.query(
    query_texts=["testing strategies"],
    n_results=10,
    where={
        "$and": [
            {"artifact_type": "code"},
            {"date": {"$gte": "2024-01-01"}}
        ]
    }
)
```

**Chroma supports MongoDB-style queries**:
- `$and`, `$or`, `$not`
- `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`
- `$in`, `$nin`

**TypeScript Equivalent**: Like Mongoose/MongoDB query syntax.

### Pattern 3: Hybrid Search

Combine vector similarity with keyword filtering:

```python
# 1. Semantic search
semantic_results = collection.query(
    query_texts=["authentication patterns"],
    n_results=20
)

# 2. Keyword filter in application code
filtered = [
    r for r in semantic_results
    if "passport" in r['documents'][0].lower()
]

# Best of both: semantic understanding + exact keyword match
```

---

## Performance Characteristics

| Operation | Local Time | Notes |
|-----------|-----------|-------|
| **Initialize Client** | <100ms | Opens/creates database |
| **Create Collection** | <50ms | Lightweight |
| **Add Document** | ~200ms | Includes embedding call to OpenAI |
| **Add 100 Documents** | ~10s | Batch operations are faster |
| **Query (10 results)** | <2s | Fast vector similarity search |
| **Full Re-index** | 10-30min | One-time cost for 12 months of history |

**Optimization Tips**:
1. Batch inserts when possible (100s at a time)
2. Create indexes before bulk queries
3. Use metadata filters to reduce search space
4. Cache frequently-accessed results

---

## Troubleshooting

### Issue: "No module named 'chromadb'"

**Solution**: Ensure virtual environment is activated:
```bash
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
```

**TypeScript Equivalent**: Like forgetting to run `npm install`

### Issue: Database locked or permission errors

**Cause**: Multiple processes accessing same database

**Solution**: Chroma uses SQLite—only one writer at a time:
```python
# Don't do this:
client1 = chromadb.PersistentClient(path="./chroma_db")
client2 = chromadb.PersistentClient(path="./chroma_db")  # ❌ Conflict!

# Do this:
client = chromadb.PersistentClient(path="./chroma_db")
collection1 = client.get_collection("github_knowledge")
collection2 = client.get_collection("epa_evidence")  # ✅ Same client
```

### Issue: Slow queries after adding lots of data

**Solution**: Collections auto-optimize, but you can force it:
```python
# Force index rebuild (improves query performance)
collection.delete(where={})  # Clear
# Re-add documents in batches
```

**Consider**: If you have >1M documents, Chroma might not be the right tool. For our use case (12 months of GitHub history = ~10k-100k chunks), it's perfect.

### Issue: Embeddings cost too much

**Current Setup**: OpenAI `text-embedding-3-small` (~$0.00002 per 1000 tokens)

**Estimated Cost**:
- 12 months of history: ~500k tokens
- Cost: ~$0.01-$0.10 (negligible)

**If Concerned**:
- Use smaller chunk sizes
- Filter which files to embed (exclude generated code, vendor files)
- Switch to open-source embedding models (HuggingFace)

---

## Next Steps

Once Chroma is set up, you'll:

1. **Create embedding pipeline** (`backend/embeddings.py`)
   - Chunk code files intelligently
   - Generate embeddings via OpenAI
   - Store with proper metadata

2. **Index GitHub history** (`backend/indexing.py`)
   - Fetch all commits, PRs, code files
   - Embed each artifact
   - Track indexing state

3. **Build retrieval system** (`backend/retrieval.py`)
   - Hybrid search (vector DB + live GitHub API)
   - Attribution verification
   - Relevance ranking

---

## Resources

- **Chroma Docs**: https://docs.trychroma.com/
- **Langchain Chroma Integration**: https://python.langchain.com/docs/integrations/vectorstores/chroma
- **Embeddings Guide**: https://platform.openai.com/docs/guides/embeddings
- **Our Implementation**: See `backend/vector_db.py` for production code

---

**Status**: ✅ Chroma DB installed and ready for implementation
