"""Tests for markdown formatting utilities.

Run with: python -m pytest backend/test_formatters.py -v
"""

import pytest
from backend.formatters import (
    format_code_block,
    format_github_link,
    format_metadata_table,
    format_evidence,
    format_stage1_response,
    format_stage3_synthesis,
    format_full_conversation,
    _format_model_name,
    _looks_like_code
)


class TestCodeBlockFormatting:
    """Test code block formatting with metadata."""

    def test_simple_code_block(self):
        """Test basic code block without metadata."""
        code = "def hello():\n    print('Hello, world!')"
        result = format_code_block(code, "python")

        assert "```python" in result
        assert "def hello():" in result
        assert "```" in result

    def test_code_block_with_metadata(self):
        """Test code block with source metadata."""
        code = "const x = 42;"
        metadata = {
            "source": "app/main.ts",
            "author": "testuser",
            "date": "2024-12-09"
        }
        result = format_code_block(code, "typescript", metadata)

        assert "**Source:** `app/main.ts`" in result
        assert "**Author:** testuser" in result
        assert "**Date:** 2024-12-09" in result
        assert "```typescript" in result

    def test_code_block_with_github_commit(self):
        """Test code block with GitHub commit link."""
        code = "import os"
        metadata = {
            "repo": "user/project",
            "file_path": "src/main.py",
            "commit_hash": "abc123def456"
        }
        result = format_code_block(code, "python", metadata)

        assert "**File:** `user/project/src/main.py`" in result
        assert "**Commit:** [abc123d]" in result  # Shows 7 chars (GitHub standard)
        assert "https://github.com/user/project/commit/abc123def456" in result


class TestGitHubLinks:
    """Test GitHub URL generation."""

    def test_simple_repo_link(self):
        """Test basic repository link."""
        result = format_github_link("user/repo")
        assert result == "[user/repo](https://github.com/user/repo)"

    def test_file_link(self):
        """Test link to specific file."""
        result = format_github_link("user/repo", "src/main.py")
        assert "user/repo/src/main.py" in result
        assert "https://github.com/user/repo/blob/main/src/main.py" in result

    def test_file_with_line_number(self):
        """Test link to specific line in file."""
        result = format_github_link("user/repo", "src/main.py", line_number=42)
        assert "#L42" in result
        assert "https://github.com/user/repo/blob/main/src/main.py#L42" in result

    def test_file_with_commit(self):
        """Test link to file at specific commit."""
        result = format_github_link("user/repo", "src/main.py", commit_hash="abc123def")
        assert "@abc123" in result
        assert "https://github.com/user/repo/blob/abc123def/src/main.py" in result


class TestMetadataFormatting:
    """Test metadata table formatting."""

    def test_simple_metadata(self):
        """Test basic metadata formatting."""
        metadata = {
            "repo": "user/project",
            "language": "Python"
        }
        result = format_metadata_table(metadata)

        assert "**Repo:** user/project" in result
        assert "**Language:** Python" in result

    def test_title_case_conversion(self):
        """Test automatic title casing of keys."""
        metadata = {"author": "testuser", "date": "2024-12-09"}
        result = format_metadata_table(metadata)

        # Should title case lowercase keys
        assert "**Author:**" in result
        assert "**Date:**" in result


class TestEvidenceFormatting:
    """Test complete evidence item formatting."""

    def test_code_evidence(self):
        """Test formatting code evidence with metadata."""
        evidence = {
            'content': 'def test_example():\n    assert True',
            'metadata': {
                'repo': 'user/project',
                'file_path': 'tests/test_main.py',
                'author': 'testuser',
                'date': '2024-12-09T10:30:00',
                'language': 'python',
                'relevance_score': 0.95
            }
        }
        result = format_evidence(evidence)

        assert "### Evidence:" in result
        assert "user/project/tests/test_main.py" in result
        assert "**Author:** testuser" in result
        assert "**Language:** python" in result
        assert "**Relevance:** 0.95" in result
        assert "```python" in result
        assert "def test_example():" in result

    def test_text_evidence(self):
        """Test formatting text (non-code) evidence."""
        evidence = {
            'content': 'This is a text description of the feature.',
            'metadata': {
                'repo': 'user/docs',
                'file_path': 'README.md',
                'author': 'testuser',
                'date': '2024-12-09'
            }
        }
        result = format_evidence(evidence)

        # Text content should not be in code block
        assert "```" not in result or "```md" in result  # Might still be formatted as markdown
        assert "This is a text description" in result


class TestStage1Formatting:
    """Test Stage 1 response formatting."""

    def test_simple_stage1_response(self):
        """Test basic Stage 1 response formatting."""
        result = format_stage1_response(
            "claude-sonnet-4-5",
            "This is the model's response to the query."
        )

        assert "## Claude" in result  # Model name formatted
        assert "This is the model's response" in result

    def test_stage1_with_evidence(self):
        """Test Stage 1 response with evidence items."""
        evidence = [
            {
                'content': 'print("test")',
                'metadata': {
                    'repo': 'user/project',
                    'file_path': 'main.py',
                    'language': 'python'
                }
            }
        ]
        result = format_stage1_response(
            "gpt-4-turbo",
            "Here's an example from the codebase.",
            evidence_used=evidence
        )

        assert "## GPT-4 Turbo" in result  # Model name formatted
        assert "### Evidence Retrieved" in result
        assert "```python" in result


class TestStage3Formatting:
    """Test Stage 3 synthesis formatting."""

    def test_simple_synthesis(self):
        """Test basic synthesis without attributions."""
        result = format_stage3_synthesis("This is the final synthesized answer.")
        assert "This is the final synthesized answer." in result

    def test_synthesis_with_sources(self):
        """Test synthesis with source attributions."""
        attributions = [
            {
                'repo': 'user/project1',
                'file_path': 'src/main.py',
                'commit_hash': 'abc123',
                'description': 'Core implementation'
            },
            {
                'repo': 'user/project1',
                'file_path': 'tests/test_main.py',
                'description': 'Test coverage'
            },
            {
                'repo': 'user/project2',
                'file_path': 'README.md'
            }
        ]
        result = format_stage3_synthesis(
            "Based on the evidence...",
            source_attributions=attributions
        )

        assert "## Sources" in result
        assert "### [user/project1]" in result
        assert "### [user/project2]" in result
        assert "src/main.py" in result
        assert "Core implementation" in result


class TestFullConversationFormatting:
    """Test full conversation export formatting."""

    def test_conversation_export(self):
        """Test complete conversation formatting."""
        conversation = {
            'id': 'test-123',
            'created_at': '2024-12-09T10:00:00',
            'messages': [
                {
                    'role': 'user',
                    'content': 'What is testing?'
                },
                {
                    'role': 'assistant',
                    'stage1': [
                        {
                            'model': 'claude-sonnet-4',
                            'response': 'Testing is...'
                        }
                    ],
                    'stage2': [
                        {
                            'model': 'claude-sonnet-4',
                            'evaluation': 'Good response'
                        }
                    ],
                    'stage3': 'Final answer about testing.'
                }
            ]
        }
        result = format_full_conversation(conversation)

        assert "# LLM Council Conversation" in result
        assert "**Date:** 2024-12-09T10:00:00" in result
        assert "## Query 1" in result
        assert "What is testing?" in result
        assert "## Response 1" in result
        assert "### Stage 1: Individual Model Responses" in result
        assert "### Stage 3: Final Synthesis" in result


class TestHelperFunctions:
    """Test helper functions."""

    def test_format_model_name_claude(self):
        """Test Claude model name formatting."""
        assert "Claude" in _format_model_name("claude-sonnet-4-5-20250929")
        assert "Sonnet" in _format_model_name("claude-3-5-sonnet-20241022")

    def test_format_model_name_gpt(self):
        """Test GPT model name formatting."""
        result = _format_model_name("gpt-4-turbo")
        assert "GPT-4" in result
        assert "Turbo" in result

    def test_format_model_name_gemini(self):
        """Test Gemini model name formatting."""
        result = _format_model_name("gemini-1.5-pro")
        assert "Gemini" in result
        assert "1.5" in result
        assert "Pro" in result

    def test_looks_like_code_python(self):
        """Test code detection for Python."""
        python_code = """
def example():
    x = 42
    return x
        """
        assert _looks_like_code(python_code) is True

    def test_looks_like_code_javascript(self):
        """Test code detection for JavaScript."""
        js_code = """
const example = () => {
    return 42;
};
        """
        assert _looks_like_code(js_code) is True

    def test_looks_like_code_prose(self):
        """Test that prose is not detected as code."""
        prose = "This is a simple paragraph of text describing something."
        assert _looks_like_code(prose) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
