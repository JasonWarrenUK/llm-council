# Phase 2 Implementation Plan: Knowledge Base & Semantic Search

**Target**: Local Chroma vector DB with embedded GitHub history and hybrid retrieval system
**Status**: Ready to implement
**Prerequisites**: ✅ Phase 1 complete (Langchain + GitHub API + Formatters)

---

## Overview

Phase 2 builds the RAG (Retrieval-Augmented Generation) infrastructure that enables semantic search over your GitHub history. This unlocks the ability for council models to autonomously retrieve relevant code examples, commits, and PRs when answering questions.

**Key deliverables**:
1. Local Chroma DB for vector storage
2. Embedding pipeline for GitHub artifacts
3. Indexing orchestrator to populate the knowledge base
4. Hybrid retrieval combining semantic search with live GitHub API queries
5. Attribution verification to ensure evidence is user-authored

---

## Task Breakdown

### Task 2.1: Chroma DB Setup & Documentation
**Priority**: High (foundation for all other Phase 2 tasks)
**Estimated complexity**: Low
**Files to create**:
- `docs/vector-db-setup.md` (documentation)
- `backend/vector_db.py` (implementation)
- `backend/test_vector_db.py` (tests)

#### Subtasks

**2.1.1: Install Chroma dependencies**
```bash
# Add to pyproject.toml dependencies
uv add chromadb
uv add langchain-chroma  # Langchain integration
```

**2.1.2: Create documentation (`docs/vector-db-setup.md`)**

Content outline:
- What is a vector database (concept explanation for TypeScript dev)
- Why Chroma vs alternatives (local, file-based, no server needed)
- Installation options (Python library vs Docker)
- Storage location (`.gitignore` entry for `chroma_db/`)
- TypeScript analogies (like IndexedDB but for semantic search)
- Basic operations (create collection, add documents, query)

**2.1.3: Implement `backend/vector_db.py`**

Functions to implement:
```python
def get_chroma_client() -> chromadb.PersistentClient:
    """Returns persistent client pointing to ./chroma_db/"""

def get_or_create_collection(
    client: chromadb.PersistentClient,
    name: str = "github_knowledge"
) -> chromadb.Collection:
    """Get or create collection for GitHub artifacts"""

def add_documents(
    collection: chromadb.Collection,
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str]
) -> None:
    """Add documents with metadata to collection"""

def query_collection(
    collection: chromadb.Collection,
    query_text: str,
    n_results: int = 10,
    where_filter: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Query collection by semantic similarity"""

def delete_collection(client: chromadb.PersistentClient, name: str) -> None:
    """Delete collection (useful for re-indexing)"""

def get_collection_stats(collection: chromadb.Collection) -> Dict[str, Any]:
    """Get stats: document count, metadata summary"""
```

**Implementation notes**:
- Use `chromadb.PersistentClient(path="./chroma_db")` for local storage
- Collection metadata should include: `description`, `created_at`, `last_indexed_at`
- Document IDs format: `{repo_name}:{artifact_type}:{identifier}` (e.g., `user/repo:commit:abc123`)
- Add educational comments explaining ChromaDB concepts for TypeScript developer

**2.1.4: Create tests (`backend/test_vector_db.py`)**

Test cases:
- Test client initialization creates directory
- Test collection creation and retrieval
- Test adding documents with metadata
- Test semantic query returns relevant results
- Test filtering by metadata (`where` clause)
- Test collection deletion
- Test stats retrieval

**2.1.5: Update `.gitignore`**
```
# Add to .gitignore
chroma_db/
```

**Success criteria**:
- ✅ Chroma DB can be initialized and persists data locally
- ✅ Collections can be created/retrieved/deleted
- ✅ Documents can be added with metadata
- ✅ Semantic queries return results ranked by similarity
- ✅ Documentation explains vector DB concepts clearly
- ✅ All tests pass

---

### Task 2.2: Embedding Pipeline
**Priority**: High (required for indexing)
**Estimated complexity**: Medium
**Files to create**:
- `backend/embeddings.py` (implementation)
- `backend/test_embeddings.py` (tests)

**Dependencies**: Task 2.1 (Chroma DB setup)

#### Subtasks

**2.2.1: Install embedding dependencies**
```bash
# Add to pyproject.toml dependencies
uv add langchain-openai  # Already installed, includes embeddings
uv add tiktoken  # Token counting for OpenAI
```

**2.2.2: Implement `backend/embeddings.py`**

**Class: `GitHubEmbedder`**
```python
class GitHubEmbedder:
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize embedder with OpenAI model.

        TypeScript Equivalent: Constructor with dependency injection
        Python Concept: __init__ is like a constructor
        """
        from langchain_openai import OpenAIEmbeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        self.embeddings = OpenAIEmbeddings(model=model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    async def embed_text(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Embed text, returning chunks with embeddings and metadata.

        Returns: List[{
            'content': str,
            'embedding': List[float],
            'metadata': Dict[str, Any]
        }]
        """

    async def embed_code_file(
        self,
        file_content: str,
        repo: str,
        file_path: str,
        author: str,
        commit_hash: str,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Embed code file with file-specific metadata"""

    async def embed_commit(
        self,
        commit_message: str,
        diff: str,
        repo: str,
        commit_hash: str,
        author: str,
        date: str,
        files_changed: List[str]
    ) -> List[Dict[str, Any]]:
        """Embed commit (message + diff) with commit metadata"""

    async def embed_pr(
        self,
        title: str,
        body: str,
        repo: str,
        pr_number: int,
        author: str,
        date: str,
        state: str
    ) -> List[Dict[str, Any]]:
        """Embed PR (title + description) with PR metadata"""

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for cost prediction"""
```

**Implementation notes**:
- For code files: Include language in metadata for syntax-aware retrieval
- For commits: Combine message + diff, but weight message more heavily (semantic importance)
- For PRs: Combine title + body, title weighted higher
- Chunk size 1000 chars ≈ 250 tokens (safe for most models)
- Chunk overlap 200 chars maintains context across boundaries
- Metadata must include: `repo`, `author`, `artifact_type`, `date`
- Document ID format: `{repo}:{type}:{hash/number}:{chunk_index}`

**2.2.3: Create tests (`backend/test_embeddings.py`)**

Test cases:
- Test text embedding returns vector of correct dimensions
- Test code file chunking respects function boundaries
- Test commit embedding combines message + diff
- Test PR embedding prioritizes title over body
- Test metadata preservation through embedding process
- Test token estimation accuracy
- Mock OpenAI API calls (use `pytest-mock` or create fixtures)

**Success criteria**:
- ✅ Embeddings are generated for all artifact types
- ✅ Chunking preserves semantic units (functions, paragraphs)
- ✅ Metadata flows through pipeline correctly
- ✅ Token estimation within 10% of actual usage
- ✅ All tests pass without hitting OpenAI API (mocked)

---

### Task 2.3: GitHub History Indexing
**Priority**: High (populates knowledge base)
**Estimated complexity**: High
**Files to create**:
- `backend/indexing.py` (implementation)
- `backend/test_indexing.py` (tests)
- `data/indexing_state.json` (tracking file, gitignored)

**Dependencies**: Task 2.1 (Chroma DB), Task 2.2 (Embeddings), Phase 1 (GitHub API)

#### Subtasks

**2.3.1: Implement `backend/indexing.py`**

**Main orchestration function**:
```python
async def index_github_history(
    username: str,
    since_date: str = "2024-01-01",
    include_orgs: bool = True,
    force_reindex: bool = False
) -> Dict[str, Any]:
    """
    Main indexing function. Orchestrates:
    1. Fetch repos from GitHub API
    2. For each repo, fetch commits, PRs, and files
    3. Embed all artifacts
    4. Store in Chroma DB
    5. Track progress in indexing_state.json

    Returns: {
        'repos_indexed': int,
        'commits_indexed': int,
        'prs_indexed': int,
        'files_indexed': int,
        'chunks_created': int,
        'duration_seconds': float,
        'errors': List[str]
    }
    """
```

**Supporting functions**:
```python
async def index_repository(
    repo_full_name: str,
    username: str,
    since_date: str,
    embedder: GitHubEmbedder,
    collection: chromadb.Collection
) -> Dict[str, Any]:
    """Index single repository: commits, PRs, files"""

async def index_commits(
    repo_full_name: str,
    username: str,
    since_date: str,
    embedder: GitHubEmbedder,
    collection: chromadb.Collection
) -> int:
    """Fetch and embed commits from repo"""

async def index_prs(
    repo_full_name: str,
    username: str,
    embedder: GitHubEmbedder,
    collection: chromadb.Collection
) -> int:
    """Fetch and embed PRs from repo"""

async def index_code_files(
    repo_full_name: str,
    username: str,
    commit_hash: str,
    embedder: GitHubEmbedder,
    collection: chromadb.Collection
) -> int:
    """Fetch and embed code files from specific commit"""

def load_indexing_state() -> Dict[str, Any]:
    """Load state from data/indexing_state.json"""

def save_indexing_state(state: Dict[str, Any]) -> None:
    """Save state to data/indexing_state.json"""

def should_reindex_repo(repo_full_name: str, state: Dict[str, Any]) -> bool:
    """Check if repo needs reindexing based on last update"""
```

**Implementation strategy**:

1. **Fetch repos** using existing `github_api.list_user_repos()`
2. **For each repo**:
   - Check indexing state (skip if recently indexed and not force_reindex)
   - Fetch commits by author using `github_api.get_commits_by_author()`
   - Fetch PRs by author using `github_api.get_prs_by_author()`
   - For latest commit, fetch file tree (use PyGithub `get_contents()`)
   - Filter files by author using git blame or commit authorship
3. **Embed artifacts**:
   - Batch embedding calls where possible (OpenAI supports batch)
   - Progress logging with percentage complete
   - Error handling: continue on failure, log error, don't crash
4. **Store in Chroma**:
   - Use `vector_db.add_documents()` in batches
   - Document IDs: `{repo}:{type}:{hash}:{chunk_idx}`
   - Metadata includes all GitHub metadata + `indexed_at` timestamp
5. **Track state**:
   - `data/indexing_state.json`: `{repo: {last_indexed_at, commit_count, pr_count, file_count}}`
   - Update after each repo completes

**Rate limiting strategy**:
- GitHub API: Authenticated = 5000 req/hour
- OpenAI Embeddings: 3000 req/min (unlikely to hit)
- Add exponential backoff on rate limit errors
- Progress checkpointing (can resume if interrupted)

**2.3.2: Create CLI entry point**

Add to `backend/indexing.py`:
```python
if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Index GitHub history")
    parser.add_argument("--username", required=True, help="GitHub username")
    parser.add_argument("--since", default="2024-01-01", help="Index commits since date")
    parser.add_argument("--force", action="store_true", help="Force reindex")

    args = parser.parse_args()

    stats = asyncio.run(index_github_history(
        args.username,
        args.since,
        force_reindex=args.force
    ))

    print("\nIndexing complete!")
    print(f"Repos: {stats['repos_indexed']}")
    print(f"Commits: {stats['commits_indexed']}")
    print(f"PRs: {stats['prs_indexed']}")
    print(f"Files: {stats['files_indexed']}")
    print(f"Chunks: {stats['chunks_created']}")
    print(f"Duration: {stats['duration_seconds']:.1f}s")
```

**Usage**:
```bash
uv run python -m backend.indexing --username=JasonWarrenUK --since=2024-01-01
```

**2.3.3: Update data directory structure**

Create `data/indexing_state.json`:
```json
{
  "last_global_index": "2025-12-15T10:30:00Z",
  "repositories": {
    "user/repo": {
      "last_indexed_at": "2025-12-15T10:30:00Z",
      "commits_indexed": 145,
      "prs_indexed": 23,
      "files_indexed": 87,
      "chunks_created": 342
    }
  }
}
```

**Update `.gitignore`**:
```
# Add to data/ section
data/indexing_state.json
```

**2.3.4: Create tests (`backend/test_indexing.py`)**

Test strategy:
- Use mocked GitHub API responses (fixture files with sample data)
- Use mocked embedder (returns dummy vectors)
- Test single repo indexing flow
- Test state tracking and resume capability
- Test error handling (API failures, rate limits)
- Integration test with small real repo (optional, slow)

**Success criteria**:
- ✅ Indexing completes successfully for test repositories
- ✅ Progress is logged clearly with percentage completion
- ✅ State file correctly tracks indexed repos
- ✅ Resumable: Can stop and restart without duplicating work
- ✅ Error handling: Continues indexing other repos if one fails
- ✅ Performance: ~1-2 repos per minute (depends on size)

---

### Task 2.4: Hybrid Retrieval System
**Priority**: High (core query functionality)
**Estimated complexity**: Medium
**Files to create**:
- `backend/retrieval.py` (implementation)
- `backend/test_retrieval.py` (tests)

**Dependencies**: Task 2.1 (Chroma DB), Task 2.3 (Indexing), Phase 1 (GitHub API)

#### Subtasks

**2.4.1: Implement `backend/retrieval.py`**

**Main retrieval class**:
```python
class HybridRetriever:
    """
    Combines vector DB semantic search with live GitHub API queries.

    Strategy:
    1. Query vector DB for semantically similar content
    2. Query GitHub API for exact matches and fresh attribution
    3. Merge results, de-duplicate, rank by relevance
    4. Verify authorship for all evidence
    """

    def __init__(
        self,
        collection: chromadb.Collection,
        embedder: GitHubEmbedder,
        github_username: str
    ):
        self.collection = collection
        self.embedder = embedder
        self.username = github_username

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 10,
        filter_by_author: bool = True,
        include_live_api: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Main retrieval function.

        Returns: List[{
            'content': str,
            'metadata': {
                'source': 'vector_db' | 'github_api',
                'repo': str,
                'file_path': str | None,
                'author': str,
                'date': str,
                'commit_hash': str | None,
                'artifact_type': 'commit' | 'pr' | 'code',
                'relevance_score': float
            }
        }]
        """
        # 1. Vector DB semantic search
        vector_results = await self._semantic_search(query, top_k)

        # 2. Live GitHub API search (optional)
        api_results = []
        if include_live_api:
            api_results = await self._github_api_search(query, top_k // 2)

        # 3. Merge and deduplicate
        merged = self._merge_results(vector_results, api_results)

        # 4. Verify authorship
        if filter_by_author:
            merged = self._filter_by_author(merged, self.username)

        # 5. Sort by relevance
        merged.sort(key=lambda x: x['metadata']['relevance_score'], reverse=True)

        return merged[:top_k]

    async def _semantic_search(
        self,
        query: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Query vector DB for semantic matches"""
        # Use embedder to embed query
        # Query collection with embedding
        # Return results with metadata

    async def _github_api_search(
        self,
        query: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Query GitHub API for exact/recent matches"""
        # Use github_api.search_code_by_author()
        # Fetch file contents for matches
        # Return formatted results

    def _merge_results(
        self,
        vector_results: List[Dict[str, Any]],
        api_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge and deduplicate results from both sources"""
        # Deduplicate by repo + file_path + content_hash
        # Prefer vector_db source for relevance scores
        # Prefer api source for attribution freshness

    def _filter_by_author(
        self,
        results: List[Dict[str, Any]],
        author: str
    ) -> List[Dict[str, Any]]:
        """Keep only results authored by specified user"""
        # Filter metadata['author'] == author

    async def retrieve_by_repo(
        self,
        repo_full_name: str,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve context from specific repository only"""
        # Add repo filter to vector DB query

    async def retrieve_by_artifact_type(
        self,
        artifact_type: str,  # 'commit' | 'pr' | 'code'
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve specific artifact types only"""
        # Add artifact_type filter to vector DB query

    async def retrieve_temporal_range(
        self,
        query: str,
        start_date: str,
        end_date: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve from specific date range (for evolution analysis)"""
        # Add date filter to vector DB query
```

**Implementation notes**:
- Relevance scoring: Combine cosine similarity (vector DB) with recency and author confidence
- Deduplication key: `{repo}:{file_path}:{first_100_chars_hash}`
- For live API results, fetch full file contents (not just snippets)
- Format results using `backend/formatters.py` functions

**2.4.2: Create tests (`backend/test_retrieval.py`)**

Test cases:
- Test semantic search returns relevant results
- Test GitHub API search integration
- Test result merging and deduplication
- Test author filtering
- Test repo-specific retrieval
- Test artifact type filtering
- Test temporal filtering
- Test empty result handling
- Mock both Chroma and GitHub API

**Success criteria**:
- ✅ Semantic search returns contextually relevant results
- ✅ Live API search provides fresh attribution data
- ✅ Results are properly merged and deduplicated
- ✅ Author filtering works correctly
- ✅ Retrieval time < 5 seconds for top 10 results
- ✅ All tests pass

---

### Task 2.5: Attribution Verification
**Priority**: Medium (important for EPA, but retrieval works without it)
**Estimated complexity**: Medium
**Files to create**:
- `backend/attribution.py` (implementation)
- `backend/test_attribution.py` (tests)

**Dependencies**: Task 2.4 (Retrieval), Phase 1 (GitHub API)

#### Subtasks

**2.5.1: Implement `backend/attribution.py`**

**Core verification functions**:
```python
def verify_authorship(
    evidence_item: Dict[str, Any],
    target_author: str
) -> Dict[str, Any]:
    """
    Verify evidence is authored by target user.

    Args:
        evidence_item: Evidence dict with content and metadata
        target_author: GitHub username to verify against

    Returns: {
        'is_verified': bool,
        'confidence': float,  # 0.0 - 1.0
        'attribution_details': {
            'primary_author': str,
            'contribution_type': 'full_author' | 'co_author' | 'reviewer' | 'commenter',
            'line_percentage': float | None,  # For code files
            'collaborators': List[str]
        }
    }
    """
    artifact_type = evidence_item['metadata'].get('artifact_type')

    if artifact_type == 'commit':
        return _verify_commit_authorship(evidence_item, target_author)
    elif artifact_type == 'pr':
        return _verify_pr_authorship(evidence_item, target_author)
    elif artifact_type == 'code':
        return _verify_code_authorship(evidence_item, target_author)
    else:
        return {'is_verified': False, 'confidence': 0.0}

def _verify_commit_authorship(
    evidence_item: Dict[str, Any],
    target_author: str
) -> Dict[str, Any]:
    """Verify commit authorship (straightforward: check commit author)"""

def _verify_pr_authorship(
    evidence_item: Dict[str, Any],
    target_author: str
) -> Dict[str, Any]:
    """Verify PR authorship (check PR author, not just commenters)"""

def _verify_code_authorship(
    evidence_item: Dict[str, Any],
    target_author: str
) -> Dict[str, Any]:
    """
    Verify code authorship using git blame.

    Strategy:
    1. Get file from GitHub API
    2. Use git blame to get line-by-line authorship
    3. Calculate percentage of lines authored by target
    4. High percentage (>70%) = high confidence
    """

def filter_user_only(
    evidence_list: List[Dict[str, Any]],
    target_author: str,
    min_confidence: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Filter evidence list to only include user-authored items.

    Args:
        evidence_list: List of evidence items
        target_author: GitHub username
        min_confidence: Minimum confidence threshold (0.0 - 1.0)

    Returns:
        Filtered list with only verified user-authored evidence
    """

def flag_collaborative_work(
    evidence_list: List[Dict[str, Any]],
    target_author: str
) -> List[Dict[str, Any]]:
    """
    Flag evidence with multiple authors.
    Adds 'is_collaborative' flag to metadata.
    Important for EPA: distinguish solo vs team work.
    """

def get_attribution_summary(
    evidence_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Summarize attribution across evidence set.

    Returns: {
        'total_items': int,
        'verified_items': int,
        'confidence_distribution': {
            'high': int,  # >0.8
            'medium': int,  # 0.5-0.8
            'low': int  # <0.5
        },
        'collaboration_stats': {
            'solo_work': int,
            'pair_work': int,
            'team_work': int
        }
    }
    """
```

**Implementation notes**:
- Git blame requires additional GitHub API call (use PyGithub `get_git_blob()`)
- Confidence calculation factors:
  - Commits: 1.0 if author matches, 0.0 otherwise
  - PRs: 1.0 if PR author, 0.5 if reviewer, 0.2 if commenter
  - Code: `lines_by_author / total_lines`
- Caching: Store git blame results to avoid redundant API calls
- For EPA: Flag pair/team work but don't exclude (still valid portfolio evidence)

**2.5.2: Create tests (`backend/test_attribution.py`)**

Test cases:
- Test commit authorship verification (direct author)
- Test PR authorship verification (author vs commenter)
- Test code authorship with git blame
- Test filtering by confidence threshold
- Test collaborative work flagging
- Test attribution summary generation
- Mock GitHub API responses

**Success criteria**:
- ✅ Commit authorship verified with 100% accuracy
- ✅ PR authorship distinguishes author from participants
- ✅ Code authorship calculated correctly via git blame
- ✅ Confidence thresholds effectively filter results
- ✅ Collaborative work properly flagged
- ✅ All tests pass

---

### Task 2.6: Integration & Testing
**Priority**: High (validate entire Phase 2)
**Estimated complexity**: Medium
**Files to create**:
- `backend/test_phase2_integration.py` (end-to-end tests)
- `docs/phase2-verification.md` (verification guide)

**Dependencies**: All Phase 2 tasks complete

#### Subtasks

**2.6.1: Create end-to-end integration test**

```python
# backend/test_phase2_integration.py

@pytest.mark.asyncio
async def test_full_retrieval_pipeline():
    """
    Test complete flow:
    1. Index sample GitHub data
    2. Query with semantic search
    3. Verify results are attributed correctly
    4. Check formatting for council consumption
    """

@pytest.mark.asyncio
async def test_incremental_indexing():
    """
    Test indexing resume capability:
    1. Index subset of data
    2. Simulate interruption
    3. Resume indexing
    4. Verify no duplication
    """

@pytest.mark.asyncio
async def test_hybrid_retrieval_accuracy():
    """
    Test retrieval quality:
    1. Query for specific topic (e.g., "testing")
    2. Verify top results contain test files/commits
    3. Check relevance scores make sense
    """

@pytest.mark.asyncio
async def test_attribution_filtering():
    """
    Test author filtering:
    1. Retrieve context (mixed authorship)
    2. Apply author filter
    3. Verify only target author's work remains
    """
```

**2.6.2: Create verification guide (`docs/phase2-verification.md`)**

Content outline:
- Manual verification steps for Phase 2
- How to verify Chroma DB is working (query sample data)
- How to verify indexing completed successfully (check stats)
- How to verify retrieval returns relevant results (sample queries)
- How to verify attribution filtering works (test with known data)
- Troubleshooting common issues
- Performance benchmarks (expected indexing/query times)

**2.6.3: Performance testing**

Benchmarks to establish:
- Indexing speed: repos/minute, commits/minute
- Query latency: semantic search < 2s, hybrid < 5s
- Storage efficiency: MB per repo, compression ratio
- Token usage: avg tokens per artifact, estimated cost

Create `backend/benchmark_phase2.py`:
```python
async def benchmark_indexing(sample_repos: List[str]) -> Dict[str, Any]:
    """Measure indexing performance"""

async def benchmark_retrieval(sample_queries: List[str]) -> Dict[str, Any]:
    """Measure retrieval performance"""

if __name__ == "__main__":
    # Run benchmarks and output report
```

**Success criteria**:
- ✅ All integration tests pass
- ✅ Manual verification guide confirms functionality
- ✅ Performance meets targets (< 60s query time, 1-2 repos/min indexing)
- ✅ Documentation is clear and accurate

---

## Implementation Order

**Recommended sequence**:

1. **Week 1: Foundation**
   - Task 2.1: Chroma DB setup (days 1-2)
   - Task 2.2: Embedding pipeline (days 3-5)

2. **Week 2: Indexing**
   - Task 2.3: GitHub history indexing (days 1-5)
   - Initial indexing of your GitHub history (day 6-7)

3. **Week 3: Retrieval & Verification**
   - Task 2.4: Hybrid retrieval (days 1-3)
   - Task 2.5: Attribution verification (days 4-5)
   - Task 2.6: Integration testing (days 6-7)

**Critical path**: 2.1 → 2.2 → 2.3 → 2.4 (must be sequential)
**Can be parallel**: 2.5 can start after 2.4 begins

---

## Success Metrics

**Phase 2 is complete when**:

✅ **Functionality**:
- Chroma DB running locally with persistent storage
- GitHub history (12 months) successfully indexed
- Semantic search returns contextually relevant results
- Hybrid retrieval combines vector DB + live API effectively
- Attribution verification distinguishes user's work from colleagues'

✅ **Performance**:
- Query response time < 5 seconds (vector DB alone)
- Query response time < 10 seconds (hybrid retrieval)
- Full indexing time < 30 minutes for 1 year of history
- Storage usage < 500 MB for typical developer portfolio

✅ **Quality**:
- Retrieval accuracy: >80% of top 10 results are relevant
- Attribution accuracy: >95% correct author identification
- No duplicate results in retrieval
- Proper error handling and graceful degradation

✅ **Documentation**:
- Vector DB concepts explained clearly for TypeScript developer
- Setup guide enables fresh install without issues
- Troubleshooting guide addresses common problems
- Code includes educational comments

---

## Next Steps After Phase 2

Once Phase 2 is complete, the system will have:
- Semantic understanding of your GitHub history
- Fast retrieval of relevant code examples
- Verified attribution for portfolio use

**Phase 3** will then enable:
- Council models autonomously calling retrieval tools
- Discrete evidence evaluation (not whole responses)
- User intervention at each deliberation stage

The foundation built in Phase 2 makes Phase 3's autonomous retrieval possible.

---

## Notes for Implementation

**Python concepts to understand**:
- `async/await`: All I/O operations should be async (API calls, file I/O)
- Type hints: Use `List[Dict[str, Any]]` etc. for clarity
- Context managers: Use `with` statements for file operations
- List comprehensions: Pythonic way to filter/transform lists
- Dataclasses: Consider using for evidence/metadata structures

**Testing approach**:
- Unit tests: Test individual functions with mocked dependencies
- Integration tests: Test component interactions with real Chroma DB
- End-to-end tests: Test full pipeline with sample data
- Fixtures: Create reusable test data (sample repos, commits, PRs)

**Error handling strategy**:
- Graceful degradation: Continue on partial failures
- Detailed logging: Log all errors with context
- User feedback: Clear progress messages during indexing
- Retry logic: Exponential backoff for rate limits

**Cost considerations**:
- OpenAI embeddings: ~$0.00002 per 1000 tokens
- Estimated cost for 12 months of history: ~$5-10 (depends on repo size)
- GitHub API: Free (5000 req/hour authenticated)
- Chroma DB: Free (local storage)

**Security considerations**:
- Store API keys in `.env` only (never commit)
- Chroma DB in `.gitignore` (may contain private code)
- Indexing state in `.gitignore` (reveals repo structure)
- Consider encrypting vector DB for sensitive repositories
