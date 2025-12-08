# LLM Council Fork - Executive Summary

## 1. Overview

### 1A. Current State
The LLM Council is a multi-model deliberation tool that gathers opinions from multiple AI models, has them evaluate each other anonymously, and synthesizes a final answer. It works purely from general knowledge and has no understanding of the user's specific work or context.

### 1B. Proposed Enhancement
Transform LLM Council into a **personalized portfolio development assistant** that uses the user's complete GitHub history as its knowledge base. When answering questions, the system will automatically retrieve relevant evidence from the user's own code, pull requests, commits, and documentation—then have multiple AI models analyze that evidence collaboratively.

---

## 2. Key New Capabilities

### 2A. **GitHub-Aware Evidence Retrieval**
- System automatically searches user's GitHub repositories for relevant code examples, commits, pull requests, and documentation
- Distinguishes between user's own work and colleagues' contributions (critical for portfolio attribution)
- Tracks temporal patterns—shows how approaches evolved over time

### 2B. **Evidence-Based Deliberation**
- Instead of generic answers, models receive user's actual GitHub artifacts as context
- Models evaluate specific pieces of evidence (code files, commit messages, PR descriptions) rather than generic advice
- Final synthesis pulls together the strongest evidence in a coherent narrative

### 2C. **EPA Portfolio Support** (Level 4 Software Developer Assessment)
- Maps to the official Level 4 competency framework (Knowledge, Skills, Behaviors)
- User can ask: "Show me evidence for testing competency K8" → system retrieves all relevant testing code/commits
- Provides reflection prompts to guide portfolio writing without writing it for the user
- Shows cross-repo skill demonstrations and evolution over time

### 2D. **Iterative Refinement**
- User can pause after each stage of deliberation to review and provide feedback
- Can regenerate individual model responses with additional context
- Can inject clarifications between deliberation stages

### 2E. **Markdown-Ready Output**
- All outputs formatted to paste directly into portfolio documents or note-taking apps (Obsidian, etc.)
- Preserves attribution (links to specific GitHub commits and files)
- Shows reasoning flow and evidence sources for transparency

---

## 3. Business Value
- **Faster portfolio creation**: Evidence automatically organized by competency
- **Higher quality narratives**: Models analyze real examples rather than generic best practices
- **Time savings**: Eliminates manual searching through GitHub history
- **Learning tool**: Helps developers understand their own skill evolution and strengths
- **Verifiable**: Every piece of evidence links back to actual work in GitHub

---

## 4. Current vs. Future Comparison

| Capability | Today | After Implementation |
|-----------|-------|----------------------|
| **Context Source** | General AI knowledge only | User's GitHub history + AI knowledge |
| **Evidence Type** | Conceptual advice | Actual code examples with attribution |
| **Use Case** | General Q&A | Portfolio/competency evidence gathering |
| **Temporal Awareness** | None | Shows skill evolution over 12+ months |
| **Cross-Repo Insights** | No | Identifies patterns across all projects |
| **Portfolio Ready** | Generic output | EPA-mapped evidence with reflection prompts |
| **User Control** | Static output | Intervention at each deliberation stage |

---

## 5. Implementation Order
- **Phase 1**: GitHub integration + foundational setup
- **Phase 2**: Knowledge base and semantic search
- **Phase 3**: Enhanced deliberation with autonomous evidence retrieval
- **Phase 4**: EPA-specific features and competency mapping
- **Phase 5**: Polish, optimization, documentation

---

## 6. Success Metrics
- System retrieves relevant evidence for all EPA competencies
- Response time under 60 seconds
- Attribution accuracy > 95% (correctly identifying user's vs. colleagues' work)
- User can create portfolio entries from generated evidence
- User understands their own skill evolution from temporal patterns

---

## 7. Summary

This fork transforms LLM Council from a generic deliberation tool into a **GitHub-aware evidence retrieval and analysis system** specifically designed to support portfolio creation and competency demonstration. Rather than giving generic advice, it analyzes the user's actual code and contributions to provide specific, verifiable evidence of skills and competencies.
