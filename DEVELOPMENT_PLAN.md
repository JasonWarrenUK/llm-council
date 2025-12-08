# LLM Council Fork - Development Plan & Steering Document

**Last Updated**: 2025-12-08
**Status**: Planning Phase
**Target**: Level 4 Software Developer EPA Portfolio Support Tool

---

## Executive Summary

This fork transforms the original LLM Council from a general-purpose multi-model deliberation tool into a specialized GitHub-integrated portfolio development assistant. The core council mechanism remains but gains autonomous context retrieval, semantic code understanding, and EPA competency mapping capabilities.

**Primary User**: TypeScript developer learning Python, building tool to support EPA portfolio creation

**Key Technical Shift**: OpenRouter → Langchain + Local Vector DB + GitHub MCP

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        USER QUERY                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  RETRIEVAL LAYER (Hybrid)                                   │
│  ├─ Vector DB (Chroma): Semantic code/doc search            │
│  ├─ GitHub MCP: Live API queries, attribution               │
│  └─ Orchestrator: Combines results, ranks relevance         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Parallel Model Responses                          │
│  Each model independently:                                   │
│  1. Receives user query                                      │
│  2. Calls retrieval tools (as if only model)                 │
│  3. Constructs response with evidence                        │
│  Output: 5 responses with discrete evidence units            │
└────────────────────────┬────────────────────────────────────┘
                         │
                    [Manual Gate?]
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Discrete Evidence Evaluation                      │
│  ├─ Parse Stage 1 into evidence/explanation units            │
│  ├─ Anonymize and shuffle units                             │
│  ├─ Models rank individual pieces (not whole responses)     │
│  └─ Aggregate rankings per evidence unit                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                    [Manual Gate?]
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: Intelligent Synthesis                             │
│  Chairman:                                                   │
│  ├─ Combines top-ranked evidence units                      │
│  ├─ Eliminates redundancy                                   │
│  ├─ Maintains source attribution (repo/file/commit)         │
│  └─ Structures output as markdown-ready content             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT + METADATA                                          │
│  ├─ Final synthesized answer                                │
│  ├─ Raw retrieved evidence                                  │
│  ├─ Process flow Mermaid diagram                            │
│  └─ Debugging info (tool calls, rankings, token usage)      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Principles

1. **Retrieval First**: Context gathered before any model reasoning
2. **Independent Exploration**: Each Stage 1 model retrieves autonomously
3. **Atomic Evaluation**: Stage 2 evaluates discrete units, not holistic responses
4. **Attribution Preservation**: GitHub metadata flows through entire pipeline
5. **Markdown Native**: All outputs formatted for external consumption

---

## Technical Stack

### Backend (`backend/`)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | API server (port 8001) |
| **LLM Orchestration** | Langchain | Model management, chains, agents |
| **Model Providers** | Anthropic, OpenAI, Google | Via Langchain chat model classes |
| **Vector DB** | Chroma | Local semantic search (no cloud) |
| **Embeddings** | OpenAI `text-embedding-3-small` | Code/doc vectorization |
| **GitHub Integration** | GitHub MCP Server | Live API access, tool calling |
| **Storage** | JSON files | Conversation persistence (`data/conversations/`) |

### Frontend (`frontend/src/`)

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Framework** | React 18 | Existing, keep for now |
| **Build Tool** | Vite | Port 5173 |
| **Styling** | CSS Modules | Light theme, markdown-first |
| **Markdown** | ReactMarkdown | With `.markdown-content` wrapper |
| **Visualization** | Mermaid | For post-query flow diagrams |

### Infrastructure

- **Development**: macOS local environment
- **Containerization**: Docker (for Chroma DB only)
- **Version Control**: Git, current branch: `docs/feature-planning`
- **Environment Variables**: `.env` file (not committed)

---

## Phase 1: Foundation (Target: Proof of Concept)

### Objective
Working Langchain-based council that can query GitHub via MCP, with basic vector DB integration.

### Tasks

#### 1.1: Langchain Model Integration
**File**: `backend/langchain_models.py` (new)

```python
# Create abstraction layer for Langchain model providers
# Requirements:
# - Support ChatAnthropic, ChatOpenAI, ChatGoogleGenerativeAI
# - Async query_model() function (replaces openrouter.py equivalent)
# - Async query_models_parallel() using asyncio.gather()
# - Graceful degradation: return None on failure, continue with successes
# - Return format: {'content': str, 'reasoning_details': Optional[str]}

# TypeScript equivalent concept: Abstract factory pattern
# Python concept: async/await (similar to TS, but with asyncio library)
```

**Configuration**: Update `backend/config.py`
```python
# Replace OPENROUTER_API_KEY with:
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# COUNCIL_MODELS becomes list of dicts:
COUNCIL_MODELS = [
    {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    {"provider": "openai", "model": "gpt-4-turbo-preview"},
    {"provider": "google", "model": "gemini-1.5-pro"},
    # ... etc
]

CHAIRMAN_MODEL = {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
```

**Testing**: Create `backend/test_langchain_models.py`
- Test each provider independently
- Test parallel queries
- Test failure handling

#### 1.2: Update Council Logic
**File**: `backend/council.py`

- Replace `openrouter.py` imports with `langchain_models.py`
- Ensure all 3 stages work with new model interface
- Maintain existing anonymization and ranking logic (no changes yet)
- Update return format to match Langchain responses

**Testing**:
- Run existing council flow with Langchain backend
- Verify Stage 1, 2, 3 outputs match expected format
- Test with failing models to ensure graceful degradation

#### 1.3: GitHub MCP Setup
**Documentation**: Create `docs/github-mcp-setup.md`

Step-by-step guide:
1. Install GitHub MCP server (link to official docs)
2. Configure authentication (personal access token with org permissions)
3. Test basic queries (list repos, get commits, search code)
4. Document available MCP tools for later integration

**File**: `backend/github_mcp.py` (new)
```python
# Wrapper for GitHub MCP client
# Functions:
# - initialize_github_mcp(): Connect to MCP server
# - list_user_repos(since_date): Get all repos user contributed to
# - get_commits_by_author(repo, author, since_date): Attribution-aware commits
# - get_pr_by_author(repo, author): User's PRs
# - search_code_by_author(query, author): Code search with attribution

# Python concept: Context managers (with statement) for MCP connection
# TypeScript equivalent: try-finally or using pattern
```

#### 1.4: Markdown Output Formatting
**File**: `backend/formatters.py` (new)

```python
# Functions to format outputs as clean markdown:
# - format_evidence(evidence_dict) -> str: Code block with metadata
# - format_stage1_response(model_name, response, evidence_used) -> str
# - format_stage3_synthesis(response, source_attributions) -> str

# Ensure all code blocks have language markers
# Include GitHub URLs as proper links
# Add metadata as markdown tables or definition lists
```

**Update**: `backend/main.py` API responses
- Format stage outputs before returning to frontend
- Include markdown formatting in conversation storage

### Phase 1 Success Criteria

✅ All council models use Langchain (no OpenRouter references)
✅ GitHub MCP connected and testable via Python script
✅ Council flow completes end-to-end with Langchain
✅ Outputs are markdown-formatted
✅ Documentation explains Python concepts for TypeScript developer

---

## Phase 2: Knowledge Base (Target: Semantic GitHub Search)

### Objective
Local Chroma vector DB with embedded GitHub history, hybrid retrieval system combining semantic search and live MCP queries.

### Tasks

#### 2.1: Chroma DB Setup
**Documentation**: Create `docs/vector-db-setup.md`

**For TypeScript Developer**:
- **What is a vector database?**: Stores numerical representations (embeddings) of text/code, enables "fuzzy" search based on meaning rather than exact keywords
- **TypeScript equivalent**: Think of it like a specialized search index, but instead of matching strings, it matches concepts
- **Why Chroma?**: Simplest local option, no cloud dependencies, stores data as files

**Setup Steps**:
```bash
# Option 1: Python library (easiest)
pip install chromadb

# Option 2: Docker (if you want isolated service)
docker pull chromadb/chroma
docker run -p 8000:8000 chromadb/chroma

# We'll use Option 1 initially for simplicity
```

**File**: `backend/vector_db.py` (new)
```python
import chromadb
from chromadb.config import Settings

# Initialize persistent local client
# Python concept: Persistent storage in local directory
# Files will be in ./chroma_db/ directory

def get_chroma_client():
    """
    Returns ChromaDB client pointing to local persistent storage.
    This is like opening a database connection in TypeScript.
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    return client

def get_or_create_collection(client, name="github_knowledge"):
    """
    Collections are like tables in SQL or collections in MongoDB.
    """
    collection = client.get_or_create_collection(
        name=name,
        metadata={"description": "GitHub history embeddings"}
    )
    return collection
```

#### 2.2: Embedding Pipeline
**File**: `backend/embeddings.py` (new)

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Python concept: Text chunking
# Large files are split into smaller pieces for better retrieval
# Each chunk gets its own embedding vector

class GitHubEmbedder:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Characters per chunk
            chunk_overlap=200,  # Overlap to maintain context
            separators=["\n\n", "\n", " ", ""]  # Split on paragraphs first
        )

    async def embed_code_file(self, file_content, metadata):
        """
        Takes code file content, splits into chunks, generates embeddings.
        Metadata: {repo, file_path, author, last_modified, language}
        """
        pass

    async def embed_commit(self, commit_message, diff, metadata):
        """
        Embeds commit message + diff.
        Metadata: {repo, commit_hash, author, date, files_changed}
        """
        pass

    async def embed_pr_description(self, title, body, metadata):
        """
        Embeds PR title + description.
        Metadata: {repo, pr_number, author, date, reviewers}
        """
        pass
```

**File**: `backend/indexing.py` (new)
```python
# Orchestrates the embedding process:
# 1. Query GitHub MCP for user's repos (last 12 months)
# 2. For each repo:
#    - Get all commits by user
#    - Get all PRs by user
#    - Get all code files user authored/modified
# 3. Embed each artifact with metadata
# 4. Store in Chroma collection
# 5. Progress logging (this will take a while first time)

async def index_github_history(author_username, since_date):
    """
    Main indexing function.
    Params:
        author_username: GitHub username (for attribution)
        since_date: ISO date string (e.g., "2024-01-01")

    Returns:
        Stats: {repos_indexed, commits_indexed, files_indexed, duration}
    """
    pass

# Manual trigger: python -m backend.indexing --author=USERNAME --since=2024-01-01
```

#### 2.3: Hybrid Retrieval System
**File**: `backend/retrieval.py` (new)

```python
class HybridRetriever:
    """
    Combines vector DB semantic search with GitHub MCP live queries.

    TypeScript equivalent: Service class with multiple data sources
    """

    def __init__(self, chroma_client, github_mcp_client):
        self.chroma = chroma_client
        self.github_mcp = github_mcp_client

    async def retrieve_context(self, query: str, author: str, top_k: int = 10):
        """
        1. Semantic search in Chroma (finds similar code/concepts)
        2. Live GitHub MCP query (fresh attribution data)
        3. Combine and rank by relevance

        Returns: List[EvidenceItem]
        EvidenceItem = {
            'content': str,
            'metadata': {
                'source': 'vector_db' | 'github_api',
                'repo': str,
                'file_path': str,
                'author': str,
                'date': str,
                'commit_hash': str | None,
                'relevance_score': float
            }
        }
        """
        pass

    async def retrieve_by_competency(self, competency_code: str, author: str):
        """
        EPA-specific retrieval.
        Maps competency code (e.g., "K8") to search queries.
        """
        pass
```

#### 2.4: Attribution Verification
**File**: `backend/attribution.py` (new)

```python
# Critical for EPA portfolio: MUST be user's own work

def verify_authorship(evidence_item, target_author):
    """
    Checks that evidence is actually authored by target user.
    Uses git blame data, commit author, PR author.

    Returns: {
        'is_verified': bool,
        'confidence': float,  # 0.0 - 1.0
        'attribution_details': {
            'primary_author': str,
            'contribution_percentage': float,  # For code files
            'collaborators': List[str]
        }
    }
    """
    pass

def filter_user_only(evidence_list, target_author):
    """
    Removes or flags evidence not authored by user.
    Important: PR comments/reviews by user on others' code should be flagged differently.
    """
    pass
```

### Phase 2 Success Criteria

✅ Chroma DB running locally with persistent storage
✅ GitHub history (12 months) embedded and queryable
✅ Hybrid retrieval returns relevant, attributed evidence
✅ Attribution verification distinguishes user's work from colleagues'
✅ Query response time < 60 seconds
✅ Documentation explains vector DB concepts clearly

---

## Phase 3: Enhanced Council (Target: Autonomous Context Retrieval)

### Objective
Stage 1 models autonomously call GitHub retrieval tools, Stage 2 evaluates discrete evidence units, Stage 3 synthesizes without redundancy.

### Tasks

#### 3.1: Tool Definitions for Stage 1
**File**: `backend/tools.py` (new)

```python
from langchain.tools import tool

@tool
def search_github_code(query: str, author: str) -> str:
    """
    Semantic search for code examples matching query.
    Returns: Formatted markdown with code snippets and metadata.
    """
    pass

@tool
def search_github_commits(query: str, author: str, since_date: str) -> str:
    """
    Find commits related to query topic.
    Returns: Commit messages, dates, files changed.
    """
    pass

@tool
def search_github_prs(query: str, author: str) -> str:
    """
    Find PRs related to query.
    Returns: PR titles, descriptions, review comments.
    """
    pass

@tool
def get_competency_evidence(competency_code: str, author: str) -> str:
    """
    EPA-specific: Get evidence for a specific KSB code.
    Returns: Best examples demonstrating that competency.
    """
    pass

# Export tool list for Langchain agent initialization
GITHUB_TOOLS = [
    search_github_code,
    search_github_commits,
    search_github_prs,
    get_competency_evidence
]
```

#### 3.2: Stage 1 with Tool Calling
**Update**: `backend/council.py`

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .tools import GITHUB_TOOLS

async def stage1_collect_responses(user_query: str, author_username: str):
    """
    Modified to give each model tool access.

    For each council model:
    1. Create agent with GITHUB_TOOLS
    2. Give query + instruction: "Retrieve relevant context from GitHub"
    3. Agent autonomously decides which tools to call
    4. Agent constructs response with evidence

    Returns: List[{
        'model': str,
        'response': str,  # Final answer with evidence
        'tool_calls': List[str],  # Which tools were called (for debugging)
        'evidence_units': List[dict]  # Parsed discrete evidence pieces
    }]
    """
    pass

def parse_evidence_units(response_text: str) -> List[dict]:
    """
    Break Stage 1 response into discrete evidence/explanation units.

    Example: Response containing 3 code examples and 2 explanations
    → Returns 5 separate units

    Each unit: {
        'type': 'code_example' | 'explanation' | 'commit_reference',
        'content': str,
        'source_metadata': dict  # From GitHub retrieval
    }
    """
    pass
```

**Python Concept: Langchain Agents**
- **For TypeScript Developer**: Think of agents as LLMs with a `while` loop
- Agent receives tools (functions it can call)
- Agent decides: "Do I need more info? Which tool should I call?"
- Calls tool, gets result, decides next action
- Repeats until it has enough information to answer
- Similar to: Recursive function with early returns

#### 3.3: Stage 2 Discrete Evaluation
**Update**: `backend/council.py`

```python
async def stage2_collect_rankings(evidence_units: List[dict], evaluator_models: List[str]):
    """
    Changed from evaluating whole responses to evaluating discrete units.

    Process:
    1. Collect all evidence units from all Stage 1 models
    2. Anonymize: Assign "Unit A", "Unit B", etc.
    3. Create unit_to_source mapping: {"Unit A": {"model": "claude", "original_index": 0}}
    4. Prompt models: "Rank these evidence units by quality/relevance"
    5. Parse rankings per unit

    Returns: {
        'unit_rankings': {
            'Unit A': {'avg_rank': 2.3, 'votes': [2, 3, 2, 2, 2]},
            'Unit B': {'avg_rank': 1.8, 'votes': [1, 2, 3, 1, 2]},
            ...
        },
        'unit_to_source': dict,  # Mapping back to original models
        'raw_evaluations': List[str]  # For debugging/transparency
    }
    """
    pass
```

**Prompt Template for Stage 2** (discrete evaluation):
```
You are evaluating discrete pieces of evidence retrieved from GitHub to answer the user's query.

USER QUERY: {query}

EVIDENCE UNITS:

Unit A:
{content}
Source: [anonymized]

Unit B:
{content}
Source: [anonymized]

...

Evaluate each unit on:
1. Relevance to query
2. Quality of evidence (code quality, specificity)
3. Clarity of explanation

FINAL RANKING:
1. Unit [X]
2. Unit [Y]
...

Provide brief justification for top 3.
```

#### 3.4: Stage 3 Intelligent Synthesis
**Update**: `backend/council.py`

```python
async def stage3_synthesize_final(
    user_query: str,
    unit_rankings: dict,
    unit_to_source: dict,
    chairman_model: dict
):
    """
    Chairman receives:
    - Original user query
    - Top-ranked evidence units (sorted by avg_rank)
    - Source metadata for each unit

    Task:
    1. Select top N units (e.g., top 5-7)
    2. Detect and eliminate redundancy
    3. Synthesize coherent answer that:
       - Uses best evidence
       - Maintains attribution (repo/file/commit)
       - Structures as markdown
       - Includes "Further Evidence" section with lower-ranked but still relevant units

    Returns: {
        'synthesis': str,  # Markdown formatted
        'units_included': List[str],  # Which units made it to final
        'attribution_map': dict  # Unit ID → GitHub source details
    }
    """
    pass
```

**Chairman Prompt Template**:
```
You are synthesizing the final answer using the highest-ranked evidence from peer review.

USER QUERY: {query}

TOP-RANKED EVIDENCE:

1. [Score: {avg_rank}] {content}
   Source: {repo}/{file_path} (commit {hash}, authored by {author} on {date})

2. [Score: {avg_rank}] {content}
   Source: ...

...

Your task:
1. Create a coherent answer to the user's query
2. Use the best evidence, eliminating redundancy
3. Maintain attribution in markdown format: `[source](github_url)`
4. Structure output as:
   - Summary answer
   - Key Evidence (with code blocks)
   - Additional Context (lower-ranked but relevant evidence)
   - Further Reading (related repos/files not directly used)

Format all code examples with proper syntax highlighting and source links.
```

#### 3.5: User Control Mechanisms
**File**: `backend/intervention.py` (new)

```python
class CouncilSession:
    """
    Stateful session manager for user-controlled council execution.

    TypeScript equivalent: State machine class
    """

    def __init__(self, query: str, author: str, mode: str):
        self.query = query
        self.author = author
        self.mode = mode  # 'auto' or 'manual'
        self.state = 'initialized'  # → stage1 → stage2 → stage3 → complete
        self.stage1_results = None
        self.stage2_results = None
        self.stage3_results = None
        self.user_interventions = []

    async def execute_stage1(self):
        """Runs Stage 1, returns results, waits for approval if mode='manual'"""
        pass

    async def regenerate_model(self, model_name: str, additional_instruction: str = None):
        """Regenerate single Stage 1 response with optional user guidance"""
        pass

    async def execute_stage2(self):
        """Runs Stage 2, returns results, waits for approval if mode='manual'"""
        pass

    async def execute_stage3(self):
        """Runs Stage 3, returns final answer"""
        pass

    def add_user_intervention(self, stage: str, instruction: str):
        """Records user's mid-process intervention for context in next stages"""
        pass

    def get_current_state(self):
        """Returns current stage results for UI display"""
        pass
```

**API Updates**: `backend/main.py`

```python
# New endpoints for controlled execution:

@app.post("/api/conversations/{id}/message/start")
async def start_council_session(
    conversation_id: str,
    message: str,
    mode: str = "auto"  # or "manual"
):
    """
    Initiates council session, returns session_id.
    If mode='auto', executes all stages immediately.
    If mode='manual', executes Stage 1 only and waits.
    """
    pass

@app.post("/api/sessions/{session_id}/continue")
async def continue_session(session_id: str, intervention: dict = None):
    """
    Continues to next stage.
    If intervention provided: {stage: str, instruction: str, target_model: str}
    """
    pass

@app.post("/api/sessions/{session_id}/regenerate")
async def regenerate_model_response(
    session_id: str,
    model_name: str,
    additional_instruction: str = None
):
    """
    Regenerates single model's Stage 1 response.
    """
    pass
```

### Phase 3 Success Criteria

✅ Stage 1 models autonomously call GitHub retrieval tools
✅ Stage 2 evaluates discrete evidence units, not holistic responses
✅ Stage 3 synthesizes without redundancy, maintains attribution
✅ User can choose auto-run or manual-gate mode pre-query
✅ User can regenerate individual model responses
✅ User can inject clarifications between stages

---

## Phase 4: EPA-Specific Features (Target: Portfolio-Ready Evidence)

### Objective
Map EPA Level 4 KSBs to evidence retrieval, provide competency-specific suggestions, support iterative refinement.

### Tasks

#### 4.1: EPA Specification Parser
**File**: `backend/epa_parser.py` (new)

```python
# Parse PDF from: https://skillsengland.education.gov.uk/media/cd4amafd/st0116_software-developer_l4_ap-for-publication_270521.pdf

# Extract:
# - Knowledge statements (K1, K2, ..., K15)
# - Skills statements (S1, S2, ..., S14)
# - Behaviors (B1, B2, ..., B5)

# Store as structured data: backend/data/epa_ksbs.json

{
    "knowledge": [
        {
            "code": "K1",
            "description": "All stages of the software development life-cycle...",
            "keywords": ["SDLC", "waterfall", "agile", "requirements", "design"]
        },
        ...
    ],
    "skills": [...],
    "behaviors": [...]
}

# Function: load_epa_specification() → dict
```

#### 4.2: Competency-to-Query Mapping
**File**: `backend/epa_mapping.py` (new)

```python
def generate_search_queries_for_ksb(ksb_code: str) -> List[str]:
    """
    Given KSB code (e.g., "K8" = testing), generate GitHub search queries.

    Example:
    K8 (testing) →
    - "test files"
    - "unit test"
    - "integration test"
    - "CI/CD pipeline"
    - "jest configuration"
    - "test coverage"

    Returns: List of queries to run against GitHub knowledge base
    """
    pass

async def retrieve_evidence_for_ksb(ksb_code: str, author: str) -> dict:
    """
    Comprehensive evidence retrieval for a specific KSB.

    Returns: {
        'ksb_code': str,
        'ksb_description': str,
        'evidence_items': List[EvidenceItem],
        'suggested_projects': List[str],  # Repos with strongest evidence
        'temporal_evolution': dict,  # How skill evolved over time
        'reflection_prompts': List[str]  # Questions to help user reflect
    }
    """
    pass
```

#### 4.3: Council Query Templates for EPA
**File**: `backend/epa_prompts.py` (new)

```python
# Specialized prompts for EPA-related queries

EPA_EVIDENCE_RETRIEVAL_PROMPT = """
You are helping a developer demonstrate competency {ksb_code} for their Level 4 Software Developer End-Point Assessment.

KSB Description: {ksb_description}

Search the developer's GitHub history for concrete evidence. Focus on:
1. Code they personally wrote (not code review comments)
2. Projects where this competency is clearly demonstrated
3. Evolution of their approach to this skill over time

Use the search_github_code, search_github_commits, and search_github_prs tools to find evidence.

Return:
- Specific file paths and line numbers
- Commit hashes where competency is evident
- PR descriptions that explain their approach
- Timeline showing skill development

DO NOT write portfolio content for the developer. Only retrieve and present evidence.
"""

EPA_REFLECTION_PROMPT = """
Based on the evidence retrieved for {ksb_code}, suggest reflection questions that would help the developer write a strong portfolio entry.

Evidence summary:
{evidence_summary}

Generate 3-5 open-ended questions that:
1. Encourage analysis of technical decisions
2. Prompt reflection on challenges and learning
3. Help connect evidence to the KSB description
4. Are specific to their actual work (not generic)

Example format:
- "Looking at your test suite in project X, what influenced your choice of testing framework?"
- "How did your approach to error handling evolve between project Y (Jan 2024) and project Z (Jun 2024)?"
"""
```

#### 4.4: Cross-Repo Pattern Analysis
**File**: `backend/pattern_analysis.py` (new)

```python
async def analyze_patterns_across_repos(author: str, pattern_type: str):
    """
    Identifies recurring patterns in user's work across multiple repos.

    Pattern types:
    - 'architecture': How they structure projects
    - 'testing': Testing approaches and coverage
    - 'error_handling': Error handling patterns
    - 'documentation': Documentation quality and style
    - 'code_review': Code review participation and quality

    Returns: {
        'pattern_type': str,
        'occurrences': List[{
            'repo': str,
            'files': List[str],
            'example': str,  # Code snippet
            'date': str
        }],
        'evolution': str,  # Markdown describing how pattern changed
        'strength_assessment': str  # Is this a strong demonstration?
    }
    """
    pass

async def compare_approaches_over_time(author: str, topic: str):
    """
    Compare how developer approached same problem at different times.

    Example: "authentication" → finds all auth implementations, compares

    Returns: {
        'topic': str,
        'instances': List[{
            'date': str,
            'repo': str,
            'approach': str,  # Description
            'code_example': str
        }],
        'progression_narrative': str  # Markdown describing evolution
    }
    """
    pass
```

#### 4.5: Frontend UI for EPA Features
**New Component**: `frontend/src/components/EPAHelper.jsx`

```jsx
// Toggle between "General Query" and "EPA Competency" modes

// EPA Competency mode shows:
// - Dropdown of all KSBs (K1-K15, S1-S14, B1-B5)
// - Selected KSB description
// - "Retrieve Evidence" button
// - Results display:
//   - Evidence items (code, commits, PRs)
//   - Suggested projects
//   - Timeline visualization (optional, markdown-based)
//   - Reflection prompts
//   - "Start Council Discussion" button to analyze evidence

// General Query mode:
// - Standard chat interface
// - Option to link query to specific KSB for context
```

### Phase 4 Success Criteria

✅ EPA specification parsed and queryable
✅ Per-KSB evidence retrieval working
✅ Cross-repo pattern analysis identifies recurring practices
✅ Temporal comparison shows skill evolution
✅ Reflection prompts are specific and useful
✅ Council discussions never write portfolio content, only analyze evidence

---

## Phase 5: Visualization & Polish (Target: Production-Ready Tool)

### Tasks

#### 5.1: Mermaid Flow Diagrams
**File**: `backend/visualization.py` (new)

```python
def generate_query_flow_diagram(session: CouncilSession) -> str:
    """
    Creates Mermaid diagram showing:
    - User query input
    - Which models were used
    - Which tools each model called
    - How evidence flowed through stages
    - What got included in final synthesis

    Returns: Mermaid markdown string
    """

    # Example output:
    """
    ```mermaid
    graph TD
        A[User Query: Testing Competency K8] --> B1[Claude - Stage 1]
        A --> B2[GPT-4 - Stage 1]
        A --> B3[Gemini - Stage 1]

        B1 --> T1[search_github_code: 'unit test']
        B1 --> T2[search_github_commits: 'jest']
        B2 --> T3[search_github_code: 'test coverage']
        B3 --> T4[get_competency_evidence: K8]

        T1 --> E1[Evidence: auth.test.ts]
        T2 --> E2[Evidence: commit abc123]
        T3 --> E3[Evidence: coverage report]
        T4 --> E4[Evidence: CI pipeline]

        E1 --> S2[Stage 2: Anonymous Ranking]
        E2 --> S2
        E3 --> S2
        E4 --> S2

        S2 --> S3[Stage 3: Chairman Synthesis]
        S3 --> OUT[Final Answer + Attribution]
    ```
    """
    pass
```

#### 5.2: Debugging & Transparency Panel
**Frontend Component**: `frontend/src/components/DebugPanel.jsx`

```jsx
// Collapsible panel showing:
// - Token usage per stage
// - Tool calls made by each model (with timestamps)
// - Retrieval queries and result counts
// - Ranking scores (raw data)
// - Attribution verification results
// - Timing breakdown (which stage took how long)

// Markdown export of entire session including debug info
```

#### 5.3: Export Capabilities
**File**: `backend/export.py` (new)

```python
def export_conversation_to_markdown(conversation_id: str, include_debug: bool = False):
    """
    Exports entire conversation as markdown file.

    Structure:
    # Conversation: [timestamp]

    ## Query 1
    [user message]

    ### Retrieved Evidence
    [formatted evidence with links]

    ### Stage 1: Individual Responses
    [each model's response]

    ### Stage 2: Peer Evaluation
    [rankings and justifications]

    ### Stage 3: Final Synthesis
    [chairman's answer]

    [if include_debug: debugging info, Mermaid diagram]

    ---

    ## Query 2
    ...
    """
    pass

def export_evidence_collection(evidence_items: List[dict], output_path: str):
    """
    Exports just the evidence (no council discussion) as structured markdown.
    Useful for: "Give me all my testing examples" → save to file → paste into portfolio
    """
    pass
```

#### 5.4: Documentation Improvements
**Create**: `docs/for-typescript-devs.md`

Topics:
- Python async/await vs TypeScript promises
- Python type hints vs TypeScript types
- Python decorators vs TypeScript decorators
- Python context managers (with statement)
- Python list comprehensions vs array methods
- Python virtual environments (venv) vs node_modules
- Python modules/packages vs npm packages

**Create**: `docs/architecture-deep-dive.md`

Topics:
- How Langchain chains work
- Vector DB embedding and retrieval
- MCP server architecture
- FastAPI request lifecycle
- React state management for council sessions

**Create**: `docs/troubleshooting.md`

Common issues:
- Chroma DB connection errors
- GitHub API rate limits
- Langchain model timeout handling
- Embedding cost estimation
- Vector DB re-indexing when needed

### Phase 5 Success Criteria

✅ Mermaid diagrams accurately show query flow
✅ Debug panel provides useful transparency
✅ Conversations export to clean markdown
✅ Evidence collections export independently
✅ Documentation covers Python concepts for TS devs
✅ Troubleshooting guide addresses common issues

---

## Implementation Conventions

### File Organization

```
backend/
├── main.py              # FastAPI app, endpoints
├── config.py            # Environment vars, model configs
├── langchain_models.py  # Model provider abstraction (NEW)
├── council.py           # 3-stage deliberation logic (UPDATED)
├── tools.py             # Langchain tool definitions (NEW)
├── retrieval.py         # Hybrid retrieval system (NEW)
├── vector_db.py         # Chroma client (NEW)
├── embeddings.py        # Embedding pipeline (NEW)
├── indexing.py          # GitHub history indexing (NEW)
├── github_mcp.py        # GitHub MCP wrapper (NEW)
├── attribution.py       # Authorship verification (NEW)
├── intervention.py      # User control mechanisms (NEW)
├── epa_parser.py        # EPA spec parsing (NEW)
├── epa_mapping.py       # KSB to query mapping (NEW)
├── epa_prompts.py       # EPA-specific prompts (NEW)
├── pattern_analysis.py  # Cross-repo analysis (NEW)
├── visualization.py     # Mermaid diagram generation (NEW)
├── export.py            # Markdown export (NEW)
├── formatters.py        # Output formatting (NEW)
├── storage.py           # JSON conversation storage (EXISTING)
└── test_*.py            # Test files

frontend/src/
├── App.jsx                      # Main app (EXISTING)
├── api.js                       # Backend API calls (UPDATED)
├── components/
│   ├── ChatInterface.jsx        # Chat UI (EXISTING)
│   ├── Stage1.jsx               # Stage 1 display (UPDATED)
│   ├── Stage2.jsx               # Stage 2 display (UPDATED)
│   ├── Stage3.jsx               # Stage 3 display (UPDATED)
│   ├── EPAHelper.jsx            # EPA mode UI (NEW)
│   ├── DebugPanel.jsx           # Debugging display (NEW)
│   ├── EvidenceDisplay.jsx      # Raw evidence formatting (NEW)
│   ├── MermaidDiagram.jsx       # Flow visualization (NEW)
│   └── SessionControls.jsx      # Manual gate buttons (NEW)

docs/
├── github-mcp-setup.md          # GitHub MCP installation (NEW)
├── vector-db-setup.md           # Chroma setup guide (NEW)
├── for-typescript-devs.md       # Python concepts for TS devs (NEW)
├── architecture-deep-dive.md    # Technical architecture (NEW)
└── troubleshooting.md           # Common issues (NEW)

data/
├── conversations/               # JSON conversation storage (EXISTING)
├── epa_ksbs.json               # EPA specification data (NEW)
└── indexing_state.json         # Track last GitHub sync (NEW)

chroma_db/                       # Vector DB storage (auto-created)
```

### Python Code Style

**Type Hints** (helps TypeScript developers):
```python
from typing import List, Dict, Optional, Union

async def query_model(
    model_config: Dict[str, str],
    prompt: str,
    temperature: float = 0.7
) -> Optional[Dict[str, str]]:
    """
    Always use type hints for function signatures.
    Makes code more readable for TS developers.
    """
    pass
```

**Docstrings** (explain Python-specific concepts):
```python
def example_function():
    """
    Brief description.

    Python Concept: [If using Python-specific feature, explain it]
    TypeScript Equivalent: [If applicable, relate to TS]

    Args:
        param1: Description

    Returns:
        Description
    """
    pass
```

**Error Handling**:
```python
# Graceful degradation throughout
try:
    result = await risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return None  # Continue with partial results
```

**Async Patterns**:
```python
# Parallel operations
results = await asyncio.gather(
    task1(),
    task2(),
    task3(),
    return_exceptions=True  # Don't fail if one fails
)

# Filter out failures
successful = [r for r in results if r is not None]
```

### Testing Strategy

**Unit Tests**:
- `test_langchain_models.py`: Each model provider
- `test_retrieval.py`: Vector DB queries
- `test_attribution.py`: Authorship verification
- `test_epa_mapping.py`: KSB to query mapping

**Integration Tests**:
- `test_council_e2e.py`: Full 3-stage flow
- `test_github_integration.py`: MCP + vector DB hybrid
- `test_epa_workflow.py`: Competency evidence retrieval

**Manual Tests**:
- Portfolio creation workflow (user acceptance)
- Query response time benchmarking
- Markdown export validation

---

## Performance Targets

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| Query response time | 30-45 sec | 60 sec |
| Chroma DB query time | < 2 sec | 5 sec |
| GitHub MCP query time | < 5 sec | 10 sec |
| Stage 1 completion | < 20 sec | 30 sec |
| Stage 2 completion | < 15 sec | 20 sec |
| Stage 3 completion | < 10 sec | 15 sec |
| Embedding 1 file | < 1 sec | 2 sec |
| Full history indexing | 10-20 min | 30 min |

---

## Migration Checklist (OpenRouter → Langchain)

- [ ] Create `langchain_models.py` with provider abstraction
- [ ] Update `config.py` with new API key env vars
- [ ] Update `council.py` to use Langchain models
- [ ] Test Stage 1, 2, 3 with Langchain backend
- [ ] Remove all OpenRouter references
- [ ] Update frontend API expectations if needed
- [ ] Update `CLAUDE.md` to reflect Langchain usage

---

## Open Questions & Decision Log

### Decision: Local vs Cloud Vector DB
**Decision**: Local Chroma DB
**Rationale**: No budget for cloud services, 12 months of history manageable locally, simplifies deployment
**Trade-off**: No multi-device sync, manual backup responsibility

### Decision: Embedding Model
**Decision**: OpenAI `text-embedding-3-small`
**Rationale**: Good balance of cost/quality, employer-provided API key
**Alternative Considered**: Open-source models (slow, requires GPU)

### Decision: Tool Framework
**Decision**: Langchain's built-in tool calling
**Rationale**: Integrates cleanly with agents, well-documented
**Alternative Considered**: Custom wrapper (unnecessary complexity)

### Decision: GitHub Rate Limits
**Decision**: Cache-first approach, only live query for attribution
**Rationale**: Avoid hitting rate limits, faster responses
**Implementation**: Vector DB = primary, MCP = attribution verification

### Open Question: Council Specialization
Should different models have different roles/tools?
**Options**:
- All models have same tools (current plan)
- Specialized models (code analyzer, doc analyzer, synthesizer)

**Decision Point**: After Phase 3, evaluate if specialization would improve results

### Open Question: CLI Interface
Should there be a command-line interface for quick queries?
**Use Case**: `council-query "show me testing evidence for K8"`
**Decision Point**: Phase 5, if user requests it

---

## Success Metrics

**Learning Goals**:
- [ ] User can explain Langchain architecture
- [ ] User can modify existing Python modules confidently
- [ ] User understands vector DB concepts and operations
- [ ] User can debug council flow issues independently

**Technical Goals**:
- [ ] All Phase 1 success criteria met
- [ ] All Phase 2 success criteria met
- [ ] All Phase 3 success criteria met
- [ ] All Phase 4 success criteria met
- [ ] Query response time < 60 sec
- [ ] Attribution accuracy > 95%

**Portfolio Goals**:
- [ ] Tool successfully retrieves evidence for all 34 KSBs
- [ ] Cross-repo patterns identified for key competencies
- [ ] Temporal evolution shown for critical skills
- [ ] Reflection prompts deemed useful by user
- [ ] User completes EPA portfolio with tool assistance

---

## Next Steps

1. **Immediate**: Begin Phase 1, Task 1.1 (Langchain model integration)
2. **Within 1 week**: Complete Phase 1 (proof of concept)
3. **Within 2 weeks**: Complete Phase 2 (knowledge base)
4. **Within 3 weeks**: Complete Phase 3 (enhanced council)
5. **Ongoing**: Document learning, update this plan with decisions made

---

## Contact & Collaboration

- **Developer**: Jason Warren (TypeScript → Python learner)
- **Project Status**: Planning complete, ready for implementation
- **Git Branch**: `docs/feature-planning` → merge to `master` when Phase 1 complete
- **Issue Tracking**: GitHub issues for feature tracking
- **Documentation**: Update `CLAUDE.md` with implementation notes as you go

---

**When working on this project, Claude Code should**:
1. Always check this plan for architectural decisions
2. Explain Python concepts in comments
3. Relate to TypeScript equivalents where helpful
4. Maintain markdown-first output philosophy
5. Prioritize attribution accuracy and temporal awareness
6. Never write portfolio content, only analyze/retrieve evidence
7. Update this document when making significant architectural decisions
