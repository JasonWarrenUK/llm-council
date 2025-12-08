# LLM Council Fork - Project Context for Claude Code

## Project Overview

This is a fork of the original LLM Council project, being transformed into a specialized GitHub-integrated portfolio development tool for a Level 4 Software Developer End-Point Assessment (EPA).

**Primary Goal**: Help create a compelling EPA portfolio by retrieving and analyzing evidence of competencies from GitHub history.

**User Profile**: TypeScript developer learning Python, with employer-provided API keys (Anthropic, OpenAI, Google).

---

## Key Transformations

### From → To

| Aspect | Original | Fork |
|--------|----------|------|
| **Model Provider** | OpenRouter | Langchain (Anthropic/OpenAI/Google) |
| **Knowledge Source** | General LLM knowledge | User's GitHub history (12 months) |
| **Council Use Case** | General Q&A deliberation | Portfolio evidence analysis |
| **Storage** | Ephemeral | Local Chroma vector DB + JSON |
| **Output** | Web UI responses | Markdown-ready for Obsidian |

---

## Core Architecture

**3-Stage Council with GitHub Integration**:

1. **Stage 1**: Each model autonomously retrieves GitHub context (via tools), constructs evidence-based responses
2. **Stage 2**: Models anonymously evaluate discrete evidence units (not whole responses)
3. **Stage 3**: Chairman synthesizes best evidence, eliminates redundancy, maintains attribution

**Retrieval System** (Hybrid):
- **Vector DB (Chroma)**: Semantic search for patterns, code concepts, documentation
- **GitHub MCP**: Live API queries for attribution, freshness, exact commits
- Combined for speed + accuracy + temporal awareness

---

## Critical Design Principles

1. **Attribution First**: Must distinguish user's work from colleagues' at every level (commits, PRs, docs, code lines)
2. **Temporal Awareness**: Track skill evolution; support queries like "how I approached X in 2024 vs 2025"
3. **Pattern Recognition**: Cross-repo insights essential for EPA competency mapping
4. **Semantic Understanding**: Code-level comprehension, not just text matching
5. **Markdown Native**: All outputs must transfer cleanly to Obsidian/external docs
6. **No Portfolio Writing**: Never generate actual portfolio content; only retrieve evidence and suggest reflection

---

## When Working on This Project

### Always Consult

- **FEATURES.md**: Feature specifications by category and priority phase
- **DEVELOPMENT_PLAN.md**: Detailed implementation plan, code templates, architecture decisions
- **CLAUDE.md**: Original project notes, config structure, API details

### Always Remember

- Explain Python concepts using TypeScript equivalents
- Maintain attribution accuracy (core to EPA requirement)
- Preserve temporal metadata (when, how evolution occurred)
- Keep outputs markdown-ready
- Never write portfolio words—analyze and suggest evidence
- Graceful degradation on failures (continue with partial results)

### Current Tech Stack

**Backend**: FastAPI + Langchain + Chroma DB + GitHub MCP
**Frontend**: React 18 + Vite
**Deployment**: Local development (macOS)
**APIs**: Anthropic, OpenAI, Google (via employer keys)

---

## Development Phases

**Phase 1** (Foundation): Langchain migration, basic GitHub MCP, Chroma setup
**Phase 2** (Knowledge Base): Embedding pipeline, hybrid retrieval
**Phase 3** (Enhanced Council): Tool-calling agents, discrete evaluation, user control
**Phase 4** (EPA Features): Competency mapping, evidence-to-KSB matching, pattern analysis
**Phase 5** (Polish): Mermaid diagrams, export, documentation

---

## Quick Reference

**Key Files**:
- Backend orchestration: `backend/council.py`
- Model abstraction: `backend/langchain_models.py` (new)
- Retrieval: `backend/retrieval.py` (new)
- Vector DB: `backend/vector_db.py` (new)
- Tools: `backend/tools.py` (new)
- User control: `backend/intervention.py` (new)

**Configuration**:
- Models & API keys: `backend/config.py`
- Frontend API: `frontend/src/api.js`

**Data**:
- Conversations: `data/conversations/` (JSON)
- Vector DB: `chroma_db/` (auto-created)
- EPA specs: `data/epa_ksbs.json` (new)

---

## Learning Focus

This fork is intentionally a learning project. When implementing, ensure:
- Python async/await patterns explained (relate to TS promises)
- Langchain concepts documented
- Vector DB fundamentals clear
- MCP architecture understood
- Type hints used throughout (helps TS developers)

---

## Success Criteria Summary

**Technical**: Langchain replaces OpenRouter, local vector DB handles 12mo history, <60sec response time, >95% attribution accuracy

**Functional**: Council retrieves context autonomously, user can intervene at any stage, outputs are markdown-ready, EPA mapping produces evidence suggestions

**Learning**: User understands Python codebase, can explain Langchain/vector DB/MCP, can modify system independently

---

**Current Status**: Planning complete (FEATURES.md + DEVELOPMENT_PLAN.md created)
**Next Step**: Begin Phase 1 implementation
**Main Branch**: `master`
**Feature Branch**: `docs/feature-planning`
