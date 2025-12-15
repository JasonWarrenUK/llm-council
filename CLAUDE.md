# CLAUDE.md - Technical Notes for LLM Council

This file contains technical details, architectural decisions, and important implementation notes for future development sessions.

## Project Overview

LLM Council is a 3-stage deliberation system where multiple LLMs collaboratively answer user questions. The key innovation is anonymized peer review in Stage 2, preventing models from playing favorites.

## Architecture

### Backend Structure (`backend/`)

**`config.py`**
- Contains `COUNCIL_MODELS` (list of OpenRouter model identifiers)
- Contains `CHAIRMAN_MODEL` (model that synthesizes final answer)
- Uses environment variable `OPENROUTER_API_KEY` from `.env`
- Backend runs on **port 8001** (NOT 8000 - user had another app on 8000)

**`openrouter.py`**
- `query_model()`: Single async model query
- `query_models_parallel()`: Parallel queries using `asyncio.gather()`
- Returns dict with 'content' and optional 'reasoning_details'
- Graceful degradation: returns None on failure, continues with successful responses

**`council.py`** - The Core Logic
- `stage1_collect_responses()`: Parallel queries to all council models
- `stage2_collect_rankings()`:
  - Anonymizes responses as "Response A, B, C, etc."
  - Creates `label_to_model` mapping for de-anonymization
  - Prompts models to evaluate and rank (with strict format requirements)
  - Returns tuple: (rankings_list, label_to_model_dict)
  - Each ranking includes both raw text and `parsed_ranking` list
- `stage3_synthesize_final()`: Chairman synthesizes from all responses + rankings
- `parse_ranking_from_text()`: Extracts "FINAL RANKING:" section, handles both numbered lists and plain format
- `calculate_aggregate_rankings()`: Computes average rank position across all peer evaluations

**`storage.py`**
- JSON-based conversation storage in `data/conversations/`
- Each conversation: `{id, created_at, messages[]}`
- Assistant messages contain: `{role, stage1, stage2, stage3}`
- Note: metadata (label_to_model, aggregate_rankings) is NOT persisted to storage, only returned via API

**`main.py`**
- FastAPI app with CORS enabled for localhost:5173 and localhost:3000
- POST `/api/conversations/{id}/message` returns metadata in addition to stages
- Metadata includes: label_to_model mapping and aggregate_rankings

**`github_api.py`** - GitHub Integration
- Direct GitHub REST API integration using PyGithub library
- Comprehensive repository discovery across personal and organization repos
- Uses `GITHUB_PERSONAL_ACCESS_TOKEN` from config.py/.env
- **Architecture Decision**: Using direct API calls instead of MCP for immediate functionality
  - MCP (Model Context Protocol) integration earmarked for Phase 3 (autonomous tool calling)
  - Remote MCP servers (api.githubcopilot.com) designed for IDE clients, not programmatic Python
  - Docker MCP server option available for future integration

**Core Functions**:
- `list_user_repos()`: Get repos owned by user or orgs they're members of
  - Parameters: `include_orgs`, `include_forks`, `since_date`
  - Returns repos with `owner_type` field (User vs Organization)
  - Handles pagination automatically via PyGithub
- `get_commits_by_author()`: Fetch commits from specific repo
  - Parameters: `max_results` to prevent rate limit exhaustion
  - Timezone-aware datetime handling for date filters
- `get_prs_by_author()`: Get pull requests by author
- `search_code_by_author()`: Search code across repositories
- `get_file_contents()`: Retrieve file contents from any accessible repo
- `get_user_stats()`: User profile statistics

**Advanced Organization Discovery**:
- `list_org_repos_with_user_commits()`: Search specific org for user's contributions
  - Useful for large orgs (193+ repos) where pagination is critical
  - Sorts repos by update date descending to find recent work first
- `list_all_repos_with_contributions()`: **Most comprehensive discovery method**
  - 3-step process:
    1. Get direct member repos via `user.get_repos(type='all')`
    2. Discover ALL orgs programmatically via GitHub Search Commits API
       - Uses `search_commits()` with query: `author:username committer-date:>=YYYY-MM-DD`
       - Sorts by `committer-date` descending to prioritize recent orgs
       - Extracts unique org names from commit results
    3. Search each discovered org for user's contributions
  - Solves limitation: `user.get_orgs()` only returns formal member orgs, misses contributor orgs
  - Successfully tested: finds 44 repos across 6 orgs including foundersandcoders/rhea

**Testing Files**:
- `test_github_api.py`: Comprehensive test suite for all API functions
- `test_pagination.py`: Verifies pagination and org repo discovery (rhea test)
- `test_org_repo_simple.py`: Direct API access validation for specific org repo

**`vector_db.py`** - Chroma Vector Database Interface (Phase 2)
- Clean interface to ChromaDB for storing and querying embedded GitHub artifacts
- Local file-based storage in `./chroma_db/` (gitignored)
- Uses ChromaDB's default embedding model (all-MiniLM-L6-v2) for semantic search

**Core Functions**:
- `get_chroma_client()`: Returns persistent client pointing to `./chroma_db/`
  - Creates directory if needed
  - Configures settings (telemetry disabled, reset allowed)
- `get_or_create_collection()`: Manages collections (like database tables)
  - Default collection: "github_knowledge"
  - Metadata includes: `description`, `created_at`, `version`
- `add_documents()`: Adds documents with metadata and unique IDs
  - Document IDs format: `{repo}:{artifact_type}:{identifier}:{chunk}`
  - Auto-enriches metadata with `indexed_at` timestamp
  - Validates list lengths match
- `query_collection()`: Semantic search with optional metadata filtering
  - Returns: documents, metadatas, ids, distances (similarity scores)
  - Supports MongoDB-style where filters (`$and`, `$or`, `$gte`, etc.)
  - Lower distance = more similar
- `delete_collection()`: Cleanup for re-indexing scenarios
- `get_collection_stats()`: Document count, sample IDs, artifact type distribution
- `initialize_knowledge_base()`: Convenience function for quick setup (returns client + collection tuple)

**Implementation Details**:
- Educational docstrings with TypeScript analogies for learning
- Full type hints for IDE support
- Includes runnable demo: `uv run python -m backend.vector_db`
- First run downloads embedding model (~79MB) to `~/.cache/chroma/`
- Collection is idempotent (get_or_create pattern)

### Frontend Structure (`frontend/src/`)

**`App.jsx`**
- Main orchestration: manages conversations list and current conversation
- Handles message sending and metadata storage
- Important: metadata is stored in the UI state for display but not persisted to backend JSON

**`components/ChatInterface.jsx`**
- Multiline textarea (3 rows, resizable)
- Enter to send, Shift+Enter for new line
- User messages wrapped in markdown-content class for padding

**`components/Stage1.jsx`**
- Tab view of individual model responses
- ReactMarkdown rendering with markdown-content wrapper

**`components/Stage2.jsx`**
- **Critical Feature**: Tab view showing RAW evaluation text from each model
- De-anonymization happens CLIENT-SIDE for display (models receive anonymous labels)
- Shows "Extracted Ranking" below each evaluation so users can validate parsing
- Aggregate rankings shown with average position and vote count
- Explanatory text clarifies that boldface model names are for readability only

**`components/Stage3.jsx`**
- Final synthesized answer from chairman
- Green-tinted background (#f0fff0) to highlight conclusion

**Styling (`*.css`)**
- Light mode theme (not dark mode)
- Primary color: #4a90e2 (blue)
- Global markdown styling in `index.css` with `.markdown-content` class
- 12px padding on all markdown content to prevent cluttered appearance

## Key Design Decisions

### Stage 2 Prompt Format
The Stage 2 prompt is very specific to ensure parseable output:
```
1. Evaluate each response individually first
2. Provide "FINAL RANKING:" header
3. Numbered list format: "1. Response C", "2. Response A", etc.
4. No additional text after ranking section
```

This strict format allows reliable parsing while still getting thoughtful evaluations.

### De-anonymization Strategy
- Models receive: "Response A", "Response B", etc.
- Backend creates mapping: `{"Response A": "openai/gpt-5.1", ...}`
- Frontend displays model names in **bold** for readability
- Users see explanation that original evaluation used anonymous labels
- This prevents bias while maintaining transparency

### Error Handling Philosophy
- Continue with successful responses if some models fail (graceful degradation)
- Never fail the entire request due to single model failure
- Log errors but don't expose to user unless all models fail

### UI/UX Transparency
- All raw outputs are inspectable via tabs
- Parsed rankings shown below raw text for validation
- Users can verify system's interpretation of model outputs
- This builds trust and allows debugging of edge cases

## Important Implementation Details

### Relative Imports
All backend modules use relative imports (e.g., `from .config import ...`) not absolute imports. This is critical for Python's module system to work correctly when running as `python -m backend.main`.

### Port Configuration
- Backend: 8001 (changed from 8000 to avoid conflict)
- Frontend: 5173 (Vite default)
- Update both `backend/main.py` and `frontend/src/api.js` if changing

### Markdown Rendering
All ReactMarkdown components must be wrapped in `<div className="markdown-content">` for proper spacing. This class is defined globally in `index.css`.

### Model Configuration
Models are hardcoded in `backend/config.py`. Chairman can be same or different from council members. The current default is Gemini as chairman per user preference.

## Common Gotchas

1. **Module Import Errors**: Always run backend as `python -m backend.main` from project root, not from backend directory
2. **CORS Issues**: Frontend must match allowed origins in `main.py` CORS middleware
3. **Ranking Parse Failures**: If models don't follow format, fallback regex extracts any "Response X" patterns in order
4. **Missing Metadata**: Metadata is ephemeral (not persisted), only available in API responses
5. **GitHub API Timezone Issues**: Always use timezone-aware datetimes when comparing with GitHub timestamps
   - Fix: `datetime.fromisoformat(date).replace(tzinfo=timezone.utc)`
6. **GitHub API Rate Limits**: Authenticated API allows 5000 requests/hour
   - Use `max_results` parameters to limit expensive queries
   - Pagination iterators consume one request per page
7. **Organization Repo Discovery**: `user.get_repos()` misses orgs where user is contributor but not member
   - Solution: Use `list_all_repos_with_contributions()` which discovers orgs via commit search

## Future Enhancement Ideas

- Configurable council/chairman via UI instead of config file
- Streaming responses instead of batch loading
- Export conversations to markdown/PDF
- Model performance analytics over time
- Custom ranking criteria (not just accuracy/insight)
- Support for reasoning models (o1, etc.) with special handling
- **Phase 3: MCP Integration** - Enable autonomous tool calling with GitHub data
  - Docker-based MCP server for standardized tool interface
  - Allow council models to query GitHub API during deliberation
  - Provide code context when answering programming questions
- GitHub Integration Enhancements:
  - Cache repository data to reduce API calls
  - Support GitHub Enterprise instances
  - Add PR review comment extraction
  - Code contribution visualization/analytics

## Testing Notes

**OpenRouter Testing**:
Use `test_openrouter.py` to verify API connectivity and test different model identifiers before adding to council. The script tests both streaming and non-streaming modes.

**GitHub API Testing**:
- `python -m backend.test_github_api` - Comprehensive test suite for all GitHub functions
- `python -m backend.test_pagination` - Verifies org repo discovery (foundersandcoders/rhea test)
- `python -m backend.test_org_repo_simple` - Quick validation of specific org repo access
- All tests require `GITHUB_PERSONAL_ACCESS_TOKEN` in `.env`
- Token needs `repo` scope for private repos, `read:org` for org access

## Data Flow Summary

```
User Query
    ↓
Stage 1: Parallel queries → [individual responses]
    ↓
Stage 2: Anonymize → Parallel ranking queries → [evaluations + parsed rankings]
    ↓
Aggregate Rankings Calculation → [sorted by avg position]
    ↓
Stage 3: Chairman synthesis with full context
    ↓
Return: {stage1, stage2, stage3, metadata}
    ↓
Frontend: Display with tabs + validation UI
```

The entire flow is async/parallel where possible to minimize latency.
