"""Markdown formatting utilities for council outputs.

This module provides functions to format LLM council outputs as clean,
well-structured markdown for external consumption (e.g., EPA portfolio).

TypeScript Equivalent: Template literal functions with string interpolation
Python Concept: f-strings for string formatting, similar to template literals
"""

from typing import Dict, Any, List, Optional
import re


def format_code_block(code: str, language: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Format code snippet as markdown code block with optional metadata.

    Args:
        code: The code content
        language: Language identifier (e.g., 'python', 'typescript', 'bash')
        metadata: Optional metadata dict with keys like 'source', 'author', 'date'

    Returns:
        Formatted markdown code block with metadata header

    Example:
        >>> format_code_block("def hello(): pass", "python", {"source": "repo/file.py"})
        Source: `repo/file.py`

        ```python
        def hello(): pass
        ```
    """
    parts = []

    # Add metadata header if provided
    if metadata:
        if 'source' in metadata:
            parts.append(f"**Source:** `{metadata['source']}`")
        if 'repo' in metadata and 'file_path' in metadata:
            parts.append(f"**File:** `{metadata['repo']}/{metadata['file_path']}`")
        if 'author' in metadata:
            parts.append(f"**Author:** {metadata['author']}")
        if 'date' in metadata:
            parts.append(f"**Date:** {metadata['date']}")
        if 'commit_hash' in metadata:
            # Format as GitHub link if possible
            if 'repo' in metadata:
                commit_url = f"https://github.com/{metadata['repo']}/commit/{metadata['commit_hash']}"
                parts.append(f"**Commit:** [{metadata['commit_hash'][:7]}]({commit_url})")
            else:
                parts.append(f"**Commit:** `{metadata['commit_hash'][:7]}`")

        parts.append("")  # Blank line before code block

    # Add code block
    parts.append(f"```{language}")
    parts.append(code.rstrip())
    parts.append("```")

    return "\n".join(parts)


def format_github_link(repo: str, file_path: Optional[str] = None,
                       commit_hash: Optional[str] = None, line_number: Optional[int] = None) -> str:
    """
    Create GitHub URL markdown link.

    Args:
        repo: Repository in 'owner/repo' format
        file_path: Optional file path within repo
        commit_hash: Optional commit hash (links to specific version)
        line_number: Optional line number for direct code reference

    Returns:
        Markdown link to GitHub resource

    Examples:
        >>> format_github_link("user/repo")
        '[user/repo](https://github.com/user/repo)'

        >>> format_github_link("user/repo", "src/main.py", line_number=42)
        '[user/repo/src/main.py#L42](https://github.com/user/repo/blob/main/src/main.py#L42)'
    """
    base_url = f"https://github.com/{repo}"

    if file_path:
        if commit_hash:
            url = f"{base_url}/blob/{commit_hash}/{file_path}"
            display = f"{repo}/{file_path}@{commit_hash[:7]}"
        else:
            url = f"{base_url}/blob/main/{file_path}"
            display = f"{repo}/{file_path}"

        if line_number:
            url += f"#L{line_number}"
            display += f"#L{line_number}"

        return f"[{display}]({url})"
    else:
        return f"[{repo}]({base_url})"


def format_metadata_table(metadata: Dict[str, Any]) -> str:
    """
    Format metadata as markdown definition list.

    Python Concept: Dictionary iteration with .items()
    TypeScript Equivalent: Object.entries(metadata).map(...)

    Args:
        metadata: Dictionary of key-value pairs

    Returns:
        Markdown definition list

    Example:
        >>> format_metadata_table({"Repo": "user/project", "Language": "Python"})
        **Repo:** user/project
        **Language:** Python
    """
    lines = []
    for key, value in metadata.items():
        # Title case the key if it's all lowercase
        display_key = key.title() if key.islower() else key
        lines.append(f"**{display_key}:** {value}  ")  # Two spaces = line break in markdown
    return "\n".join(lines)


def format_evidence(evidence_dict: Dict[str, Any]) -> str:
    """
    Format a single piece of evidence as markdown.

    Evidence dict expected structure:
    {
        'content': str,          # The actual code/text content
        'metadata': {
            'source': str,       # 'vector_db' | 'github_api'
            'repo': str,         # 'owner/repo'
            'file_path': str,    # Path within repo
            'author': str,       # GitHub username
            'date': str,         # ISO date string
            'commit_hash': str,  # Optional
            'language': str,     # Optional, for code syntax highlighting
            'relevance_score': float  # Optional
        }
    }

    Returns:
        Formatted markdown with code block and source attribution
    """
    content = evidence_dict.get('content', '')
    metadata = evidence_dict.get('metadata', {})

    parts = []

    # Add source attribution header
    if 'repo' in metadata and 'file_path' in metadata:
        github_link = format_github_link(
            metadata['repo'],
            metadata.get('file_path'),
            metadata.get('commit_hash')
        )
        parts.append(f"### Evidence: {github_link}")
        parts.append("")

    # Add metadata summary
    meta_items = {}
    if 'author' in metadata:
        meta_items['Author'] = metadata['author']
    if 'date' in metadata:
        meta_items['Date'] = metadata['date'][:10]  # Just the date part
    if 'language' in metadata:
        meta_items['Language'] = metadata['language']
    if 'relevance_score' in metadata:
        score = metadata['relevance_score']
        meta_items['Relevance'] = f"{score:.2f}" if isinstance(score, float) else str(score)

    if meta_items:
        parts.append(format_metadata_table(meta_items))
        parts.append("")

    # Detect if content is code or text
    language = metadata.get('language', '').lower() if 'language' in metadata else ''

    # If content looks like code, format as code block
    if language or _looks_like_code(content):
        parts.append(format_code_block(content, language, {}))
    else:
        # Format as regular markdown text
        parts.append(content)

    return "\n".join(parts)


def format_stage1_response(model_name: str, response: str, evidence_used: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Format Stage 1 model response as markdown.

    Args:
        model_name: Name of the model (e.g., 'claude-sonnet-4')
        response: The model's response text
        evidence_used: Optional list of evidence items the model referenced

    Returns:
        Formatted markdown with model attribution and evidence references
    """
    parts = []

    # Model header
    parts.append(f"## {_format_model_name(model_name)}")
    parts.append("")

    # Main response
    parts.append(response)

    # Evidence section (if any)
    if evidence_used and len(evidence_used) > 0:
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append("### Evidence Retrieved")
        parts.append("")

        for i, evidence in enumerate(evidence_used, 1):
            parts.append(f"#### Evidence {i}")
            parts.append("")
            parts.append(format_evidence(evidence))
            parts.append("")

    return "\n".join(parts)


def format_stage3_synthesis(response: str, source_attributions: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Format Stage 3 chairman synthesis as markdown.

    Args:
        response: The chairman's synthesized response
        source_attributions: Optional list of sources cited in the synthesis

    Returns:
        Formatted markdown with proper attribution section
    """
    parts = []

    # Main synthesis
    parts.append(response)

    # Attribution section
    if source_attributions and len(source_attributions) > 0:
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append("## Sources")
        parts.append("")

        # Group by repo
        by_repo = {}
        for attr in source_attributions:
            repo = attr.get('repo', 'Unknown')
            if repo not in by_repo:
                by_repo[repo] = []
            by_repo[repo].append(attr)

        for repo, items in by_repo.items():
            parts.append(f"### {format_github_link(repo)}")
            parts.append("")
            for item in items:
                if 'file_path' in item:
                    link = format_github_link(
                        repo,
                        item['file_path'],
                        item.get('commit_hash')
                    )
                    parts.append(f"- {link}")
                    if 'description' in item:
                        parts.append(f"  - {item['description']}")
            parts.append("")

    return "\n".join(parts)


def format_full_conversation(conversation_data: Dict[str, Any]) -> str:
    """
    Format entire council conversation as markdown document.

    Args:
        conversation_data: Full conversation dict with stages

    Returns:
        Complete markdown document ready for export
    """
    parts = []

    # Header
    parts.append("# LLM Council Conversation")
    parts.append("")
    if 'created_at' in conversation_data:
        parts.append(f"**Date:** {conversation_data['created_at']}")
        parts.append("")

    # Process each message
    messages = conversation_data.get('messages', [])
    query_count = 0
    for message in messages:
        if message['role'] == 'user':
            query_count += 1
            parts.append(f"## Query {query_count}")
            parts.append("")
            parts.append(message['content'])
            parts.append("")
        elif message['role'] == 'assistant':
            parts.append(f"## Response {query_count}")
            parts.append("")

            # Stage 1
            if 'stage1' in message:
                parts.append("### Stage 1: Individual Model Responses")
                parts.append("")
                for response in message['stage1']:
                    parts.append(format_stage1_response(
                        response['model'],
                        response['response']
                    ))
                    parts.append("")

            # Stage 2
            if 'stage2' in message:
                parts.append("### Stage 2: Peer Review")
                parts.append("")
                parts.append("*Models evaluated each other's responses anonymously.*")
                parts.append("")
                # Could expand this with ranking details if needed

            # Stage 3
            if 'stage3' in message:
                parts.append("### Stage 3: Final Synthesis")
                parts.append("")
                parts.append(format_stage3_synthesis(message['stage3']))
                parts.append("")

        parts.append("---")
        parts.append("")

    return "\n".join(parts)


# Helper functions

def _format_model_name(model_name: str) -> str:
    """
    Format model name for display (e.g., 'claude-sonnet-4' -> 'Claude Sonnet 4').

    Python Concept: String methods chaining
    TypeScript Equivalent: model.split('-').map(capitalize).join(' ')
    """
    # Remove provider prefix if present (e.g., 'openai/' or 'anthropic/')
    if '/' in model_name:
        model_name = model_name.split('/')[-1]

    # Handle common model name patterns
    if 'claude' in model_name.lower():
        # 'claude-3-5-sonnet-20241022' -> 'Claude 3.5 Sonnet'
        parts = model_name.split('-')
        if len(parts) >= 3:
            return f"Claude {parts[1]}.{parts[2]} {parts[3].title()}" if len(parts) > 3 else f"Claude {parts[1]}"
    elif 'gpt' in model_name.lower():
        # 'gpt-4-turbo' -> 'GPT-4 Turbo'
        # 'gpt-4-turbo-preview' -> 'GPT-4 Turbo Preview'
        parts = model_name.split('-')
        # Keep 'gpt-X' together as 'GPT-X', then title case the rest
        if len(parts) >= 2:
            formatted_parts = [f"GPT-{parts[1]}"]
            formatted_parts.extend([p.title() for p in parts[2:]])
            return ' '.join(formatted_parts)
        return model_name.upper()
    elif 'gemini' in model_name.lower():
        # 'gemini-1.5-pro' -> 'Gemini 1.5 Pro'
        return ' '.join(part.title() for part in model_name.split('-'))

    # Default: title case with hyphens to spaces
    return ' '.join(part.title() for part in model_name.split('-'))


def _looks_like_code(content: str) -> bool:
    """
    Heuristic to detect if content is code vs prose.

    Checks for common code indicators:
    - Function/class definitions
    - Curly braces or indentation patterns
    - Semicolons or assignment operators
    - Import/require statements
    """
    code_indicators = [
        r'\bdef\s+\w+\(',           # Python function
        r'\bclass\s+\w+',           # Class definition
        r'\bfunction\s+\w+\(',      # JS function
        r'\bconst\s+\w+\s*=',       # JS const
        r'\blet\s+\w+\s*=',         # JS let
        r'\bimport\s+',             # Import statement
        r'\brequire\(',             # Node require
        r'=>',                       # Arrow function
        r'{\s*$',                    # Opening brace at end of line
        r';\s*$',                    # Semicolon at end of line (multiple lines)
        r'^\s{4,}\w+',              # Significant indentation
    ]

    lines = content.split('\n')
    if len(lines) < 2:
        return False

    matches = 0
    for pattern in code_indicators:
        if re.search(pattern, content, re.MULTILINE):
            matches += 1

    # If multiple code indicators present, probably code
    return matches >= 2
