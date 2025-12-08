# LLM Council Fork - Feature Roadmap

## Project Goals
1. Understand Python codebase (coming from TypeScript background)
2. Migrate from OpenRouter to Langchain
3. Transform into specialized "NotebookLM-adjacent" portfolio development tool
4. Use entire GitHub history (focus: last 12 months) as knowledge base
5. Support Level 4 Software Developer EPA portfolio creation

## Core Principles
- **Attribution**: Must distinguish user's work from colleagues' at every level (commits, PRs, docs, conversations, code files)
- **Temporal Awareness**: Track evolution of skills, patterns, approaches over time
- **Pattern Recognition**: Cross-repo insights, common approaches, skill demonstrations
- **Semantic Understanding**: Code-level comprehension, not just text search
- **Markdown-First**: All outputs must transfer cleanly to Obsidian/other markdown tools
- **Iterative Refinement**: Support multiple rounds of query/response/refinement
- **No Budget Vector Storage**: Local-only solution (Chroma DB)
- **Learning-Oriented**: Explicit documentation of Python concepts, Docker setup, architecture decisions

---

## Feature List by Category

### 1. Foundation: OpenRouter → Langchain Migration
- **F1.1**: Replace `openrouter.py` with Langchain model providers
  - Support Anthropic (Claude), OpenAI (GPT), Google (Gemini)
  - Maintain async/parallel query capabilities
  - Preserve graceful degradation on model failures

- **F1.2**: Maintain existing 3-stage council flow with Langchain
  - Stage 1: Parallel independent responses
  - Stage 2: Anonymous peer evaluation
  - Stage 3: Chairman synthesis

- **F1.3**: Configuration management for Langchain
  - Environment variables for API keys (Anthropic, OpenAI, Google)
  - Council model selection via config file
  - Chairman model selection

### 2. GitHub Integration (MCP + Direct API)
- **F2.1**: GitHub MCP server integration
  - Install and configure GitHub MCP server
  - Authenticate with GitHub (personal + organization access)
  - Test connectivity and permissions

- **F2.2**: Repository discovery and indexing
  - Query all repos user has contributed to (personal + org)
  - Filter by date range (configurable, default: last 12 months)
  - Manual or periodic refresh mechanism

- **F2.3**: Attribution-aware data extraction
  - Commits: Author, date, message, diff, files changed
  - PRs: Author, reviewers, description, comments, review comments
  - Issues: Author, participants, comments, labels
  - Code files: Line-by-line authorship (git blame equivalent)
  - Distinguish user's contributions from colleagues'

- **F2.4**: Temporal metadata capture
  - Timestamp all artifacts
  - Track evolution of files over time
  - Support queries like "how I handled X in 2024 vs 2025"

### 3. Knowledge Base & RAG (Local Vector DB)
- **F3.1**: Local Chroma DB setup
  - Installation instructions (beginner-friendly)
  - Docker setup guide with explanations
  - Initial database creation

- **F3.2**: Embedding pipeline
  - Embed code files, commit messages, PR descriptions, issue discussions, README files
  - Use OpenAI embeddings API (employer-provided key)
  - Chunk strategy for large files
  - Metadata preservation (author, date, repo, file path)

- **F3.3**: Semantic code understanding
  - Parse and embed at function/class/module level
  - Maintain code structure context
  - Support queries about patterns, approaches, implementations

- **F3.4**: Hybrid retrieval system
  - Vector search for semantic similarity (patterns, concepts)
  - MCP tools for live attribution queries (exact commits, authorship)
  - Combined results with relevance ranking

### 4. Enhanced Council Mechanism
- **F4.1**: Tool access for Stage 1 models
  - Define pre-built toolset (GitHub search, vector DB query, attribution lookup)
  - Each Stage 1 model gets independent tool instance
  - Models retrieve context autonomously as if they're the only model

- **F4.2**: Discrete evidence evaluation in Stage 2
  - Parse Stage 1 responses into discrete evidence/explanation units
  - Models evaluate and rank individual pieces, not entire responses
  - Track which evidence came from which model

- **F4.3**: Intelligent synthesis in Stage 3
  - Chairman aggregates best evidence/explanation combinations
  - Eliminate redundancy across responses
  - Maintain attribution to original sources (repos, files, commits)

- **F4.4**: Council specialization (future consideration)
  - Different models for different tasks (code analysis vs documentation vs architecture)
  - Configurable council composition per query type

### 5. User Control & Intervention
- **F5.1**: Pre-query execution mode selection
  - **Auto-run**: Execute all 3 stages automatically
  - **Manual gates**: Pause after each stage for user review/approval
  - UI toggle or command-line flag

- **F5.2**: Per-model intervention
  - View individual Stage 1 responses before proceeding
  - Regenerate single model response with modified prompt
  - Remove/replace specific model contributions

- **F5.3**: Global intervention
  - Add clarifying context between stages
  - Re-run entire stage with updated instructions
  - Override stage results before proceeding

- **F5.4**: Evidence review and curation
  - View raw retrieved evidence before council sees it
  - Include/exclude specific artifacts
  - Request additional retrieval

### 6. EPA Portfolio Support
- **F6.1**: Competency mapping integration
  - Parse EPA Level 4 specification PDF (from provided link)
  - Extract knowledge, skills, behaviors (KSBs) requirements
  - Map user queries to relevant KSB categories

- **F6.2**: Evidence-to-competency matching
  - Query: "Show evidence for testing competency K8"
  - Retrieve relevant code, commits, discussions
  - Council suggests how evidence demonstrates competency
  - User maintains control over final portfolio writing

- **F6.3**: Cross-repo skill demonstration
  - Find patterns across multiple projects
  - Show skill evolution over time
  - Identify strongest examples for each competency

- **F6.4**: Reflection prompts (not writing)
  - Suggest reflection questions based on evidence
  - Highlight interesting patterns worth reflecting on
  - Never write the actual portfolio content for user

### 7. Output & Evidence Display
- **F7.1**: Raw evidence presentation
  - Show retrieved GitHub artifacts alongside council responses
  - Include metadata (repo, file, date, author, commit hash)
  - Format for easy copy-paste to Obsidian

- **F7.2**: Markdown-native formatting
  - All outputs as clean markdown
  - Code blocks with syntax highlighting markers
  - Proper heading hierarchy
  - Link preservation (GitHub URLs)

- **F7.3**: Structured evidence packages
  - Group related evidence (e.g., "all testing examples")
  - Include context (surrounding code, related PRs)
  - Attribution trail (who wrote what, when)

- **F7.4**: Export capabilities
  - Save conversation + evidence to markdown file
  - Export specific evidence collections
  - Preserve formatting for external tools

### 8. Visualization & Debugging
- **F8.1**: Post-query Mermaid diagram generation
  - Flow of information through system
  - Which models called which tools
  - How context was retrieved and passed
  - Evidence flow from retrieval → Stage 1 → Stage 2 → Stage 3

- **F8.2**: Debugging transparency
  - Show tool calls made by each model
  - Display retrieval queries and results
  - Expose ranking/scoring logic
  - Token usage per stage

### 9. Learning & Documentation
- **F9.1**: Python concept explanations
  - Inline comments explaining Python-specific patterns
  - Comparison to TypeScript equivalents where helpful
  - Async/await, type hints, decorators, etc.

- **F9.2**: Architecture documentation
  - Langchain concepts (chains, agents, tools, memory)
  - Vector DB fundamentals (embeddings, similarity search, chunking)
  - MCP server architecture

- **F9.3**: Setup guides
  - Step-by-step Docker setup for Chroma
  - Environment configuration
  - Troubleshooting common issues

---

## Priority Sequencing

### Phase 1: Foundation (Proof of Concept)
1. F1.1, F1.2, F1.3 - Langchain migration
2. F2.1, F2.2 - Basic GitHub integration
3. F3.1 - Chroma DB setup
4. F7.2 - Markdown output formatting

**Goal**: Working Langchain-based council that can query GitHub

### Phase 2: Knowledge Base
1. F2.3, F2.4 - Attribution and temporal data
2. F3.2, F3.3, F3.4 - Vector DB and hybrid retrieval
3. F7.1, F7.3 - Raw evidence display

**Goal**: Semantic search over GitHub history with proper attribution

### Phase 3: Enhanced Council
1. F4.1 - Tool access for Stage 1 models
2. F4.2, F4.3 - Discrete evaluation and synthesis
3. F5.1, F5.2, F5.3 - User control mechanisms

**Goal**: Council that autonomously retrieves context and can be guided by user

### Phase 4: EPA-Specific Features
1. F6.1 - Competency mapping
2. F6.2, F6.3, F6.4 - Evidence matching and skill demonstration

**Goal**: Portfolio-ready evidence retrieval and competency mapping

### Phase 5: Polish & Visualization
1. F8.1, F8.2 - Mermaid diagrams and debugging
2. F7.4 - Export capabilities
3. F9.1, F9.2, F9.3 - Documentation improvements

**Goal**: Production-ready tool with transparency and learning resources

---

## Success Criteria

**Technical**
- Langchain successfully replaces OpenRouter
- Local Chroma DB handles 12 months of GitHub history
- Query response time < 60 seconds
- Accurate attribution (user vs colleagues)
- Semantic code search works across repos

**Functional**
- Council retrieves relevant evidence autonomously
- User can intervene at any stage
- Outputs are markdown-ready for Obsidian
- EPA competency mapping produces useful evidence suggestions

**Learning**
- User understands Python codebase structure
- User can explain Langchain, vector DB, MCP integration
- User can modify and extend system independently

---

## Technical Constraints & Decisions

- **No budget for vector storage**: Local Chroma DB only
- **API budgets**: Reasonable usage of Anthropic, OpenAI, Google (employer-provided)
- **Deployment**: Local development environment (Mac)
- **Frontend**: React (Vite), keep current architecture initially
- **Backend**: Python FastAPI, port 8001
- **Temporal scope**: Focus on last 12 months of GitHub history
- **Response time**: Target 30-45 sec, max 60 sec acceptable

---

## Open Questions & Future Considerations

1. **Council specialization**: Should different models have different roles/capabilities?
2. **Caching strategy**: Should frequently-accessed GitHub data be cached beyond vector DB?
3. **Multi-user support**: Eventually support team usage (currently single-user)
4. **Version control**: Should the tool track its own evolution and decisions?
5. **Alternative frontends**: CLI interface for quick queries? VS Code extension?
6. **RAG optimization**: Chunking strategy, embedding model selection, retrieval tuning
7. **Tool framework**: Should we use Langchain's tool calling or build custom wrapper?
