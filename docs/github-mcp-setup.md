# GitHub MCP Setup Guide

**Last Updated**: 2025-12-08
**For**: TypeScript developers learning Python

---

## What is MCP?

**Model Context Protocol (MCP)** is an open protocol created by Anthropic that enables LLM applications to securely connect to external data sources and tools. Think of it as a standardized API that lets AI models fetch real-time information.

### TypeScript Equivalent
MCP is similar to a well-defined REST API or GraphQL schema, but specifically designed for AI/LLM integrations. It's like having a type-safe API client that any LLM can use to access your data.

### Key Concepts

**MCP Server**: A service that exposes tools, resources, and prompts through the MCP protocol
**MCP Client**: Code that connects to an MCP server (in our case, our Python backend)
**Tools**: Functions the LLM can call (e.g., "search GitHub code")
**Resources**: Data the LLM can read (e.g., "README.md from repo X")
**Prompts**: Predefined prompt templates

---

## Architecture Overview

```
┌──────────────────┐
│   LLM Council    │ ← Our Python Backend
│   (MCP Client)   │
└────────┬─────────┘
         │
         │ MCP Protocol (JSON-RPC over stdio/HTTP)
         │
         ▼
┌──────────────────┐
│  GitHub MCP      │ ← Standalone Server Process
│   Server         │
└────────┬─────────┘
         │
         │ GitHub REST API
         │
         ▼
┌──────────────────┐
│   GitHub API     │
└──────────────────┘
```

---

## Installation

### Prerequisites

1. **Python 3.10+** (you should already have this)
2. **uv package manager** (you should already have this)
3. **GitHub Personal Access Token** with repository access

### Install MCP Python SDK

```bash
uv add "mcp[cli]"
```

**TypeScript Equivalent**: `npm install @modelcontextprotocol/sdk`

### Install GitHub MCP Server

The GitHub MCP server is available in the official MCP servers repository. We'll install it as a Node.js package (yes, it's Node even though our backend is Python - MCP servers can be in any language).

```bash
# Install Node.js if not already installed (via homebrew on macOS)
brew install node

# Install the GitHub MCP server globally
npm install -g @modelcontextprotocol/server-github
```

**Why Node.js?**: The official GitHub MCP server is written in TypeScript/Node.js. Our Python code will communicate with it via MCP protocol (language-agnostic).

---

## Configuration

### 1. Get GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "MCP Server - LLM Council"
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
   - `read:user` (Read user profile data)
5. Click "Generate token"
6. **Copy the token immediately** (you won't be able to see it again)

### 2. Add to `.env` File

Add your GitHub token to `/Users/jasonwarren/Code/llm-council/.env`:

```bash
# GitHub MCP Server
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

**Security Note**: This token grants access to your GitHub data. Never commit `.env` to git (it's already in `.gitignore`).

---

## Available Tools

The GitHub MCP server provides the following tools (functions our LLMs can call):

### Repository Tools

**`list_repos`**
- Lists repositories for a user or organization
- Parameters: `username` (string), `org` (optional string)
- Returns: List of repository names with descriptions

**`get_file_contents`**
- Retrieves file contents from a repository
- Parameters: `owner` (string), `repo` (string), `path` (string), `branch` (optional string)
- Returns: File content as text

**`search_repositories`**
- Search for repositories on GitHub
- Parameters: `query` (string), `page` (optional number), `perPage` (optional number)
- Returns: Repository search results

### Commit & History Tools

**`get_commits`**
- List commits in a repository
- Parameters: `owner` (string), `repo` (string), `sha` (optional string), `author` (optional string), `since` (optional ISO date), `until` (optional ISO date)
- Returns: List of commit objects with message, author, date, SHA

**`get_commit_details`**
- Get detailed information about a specific commit
- Parameters: `owner` (string), `repo` (string), `sha` (string)
- Returns: Commit details including diff/patch

### Issue & PR Tools

**`list_issues`**
- List issues for a repository
- Parameters: `owner` (string), `repo` (string), `state` (optional: "open", "closed", "all")
- Returns: List of issues

**`list_pull_requests`**
- List pull requests for a repository
- Parameters: `owner` (string), `repo` (string), `state` (optional: "open", "closed", "all"), `head` (optional: filter by branch)
- Returns: List of PRs with titles, descriptions, authors, dates

**`get_pull_request_details`**
- Get detailed information about a specific PR
- Parameters: `owner` (string), `repo` (string), `pullNumber` (number)
- Returns: PR details including reviews, comments, file changes

### Code Search Tools

**`search_code`**
- Search for code across GitHub repositories
- Parameters: `query` (string), `page` (optional number), `perPage` (optional number)
- Returns: Code search results with file paths and snippets

---

## Testing the Connection

### Manual Test (Command Line)

The GitHub MCP server runs as a standalone process. You can test it manually:

```bash
# Start the GitHub MCP server
GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here npx @modelcontextprotocol/server-github

# In another terminal, you can send JSON-RPC commands to test
# (More advanced - we'll handle this in Python code)
```

### Python Test Script

Create `backend/test_github_mcp.py`:

```python
"""Test GitHub MCP connection."""
import asyncio
from backend.github_mcp import initialize_github_mcp, list_user_repos

async def test_connection():
    \"\"\"Test basic MCP connection and GitHub API access.\"\"\"

    # Initialize connection
    client = await initialize_github_mcp()

    # Test: List your GitHub repos
    username = "YOUR_GITHUB_USERNAME"  # Replace with your username
    repos = await list_user_repos(client, username)

    print(f"Found {len(repos)} repositories:")
    for repo in repos[:5]:  # Show first 5
        print(f"  - {repo['name']}: {repo['description']}")

    # Cleanup
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run the test:

```bash
uv run python backend/test_github_mcp.py
```

---

## Python Concepts for TypeScript Developers

### JSON-RPC over stdio

MCP uses [JSON-RPC 2.0](https://www.jsonrpc.org/) for communication. The Python client sends JSON requests to the Node.js server via standard input/output pipes.

**TypeScript Equivalent**: Similar to `child_process.spawn()` with IPC or HTTP client-server communication.

### Async Context Managers

Python's `async with` is used for managing MCP connections:

```python
async with mcp.Client() as client:
    # Connection automatically opened
    result = await client.call_tool("list_repos", {"username": "JasonWarrenUK"})
    # Connection automatically closed when block exits
```

**TypeScript Equivalent**:
```typescript
// No direct equivalent, closest is:
try {
  const client = await createClient();
  const result = await client.callTool("list_repos", {username: "JasonWarrenUK"});
} finally {
  await client.close();
}
```

---

## Troubleshooting

### Error: "GITHUB_PERSONAL_ACCESS_TOKEN not set"

**Solution**: Make sure your `.env` file contains the token and you've restarted any running processes.

### Error: "Connection refused" or "Server not responding"

**Solution**: The GitHub MCP server might not be running or installed correctly. Try:
```bash
npm list -g @modelcontextprotocol/server-github
# If not found, reinstall:
npm install -g @modelcontextprotocol/server-github
```

### Error: "GitHub API rate limit exceeded"

**Solution**: GitHub has rate limits (5000 requests/hour for authenticated users). Wait or optimize queries to reduce API calls.

### Error: "403 Forbidden" from GitHub API

**Solution**: Your Personal Access Token might not have the required scopes. Regenerate with correct permissions (see Configuration section).

---

## Next Steps

1. Install the MCP Python SDK: `uv add "mcp[cli]"`
2. Install the GitHub MCP server: `npm install -g @modelcontextprotocol/server-github`
3. Add your GitHub token to `.env`
4. Proceed to creating `backend/github_mcp.py` wrapper

---

## Resources

- [Model Context Protocol Official Site](https://modelcontextprotocol.io/)
- [MCP Python SDK on GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [GitHub MCP Server npm package](https://www.npmjs.com/package/@modelcontextprotocol/server-github)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)
- [MCP for GitHub Integration Tutorial](https://medium.com/@EleventhHourEnthusiast/model-context-protocol-for-github-integration-0605ecf29f62)
