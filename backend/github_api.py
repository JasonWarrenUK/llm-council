"""GitHub API wrapper for retrieving user's code and contributions.

This module provides functions to query GitHub for a user's repositories,
commits, pull requests, and code - essential for building an EPA portfolio.

TypeScript Equivalent: This is like a service class with async methods,
similar to how you'd structure API clients in TypeScript.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, GithubException
from .config import GITHUB_PERSONAL_ACCESS_TOKEN


def initialize_github_client() -> Github:
    """
    Initialize GitHub API client with authentication.

    Returns:
        Github: Authenticated GitHub client instance

    Raises:
        ValueError: If GITHUB_PERSONAL_ACCESS_TOKEN is not set

    TypeScript Equivalent:
        const client = new Octokit({ auth: process.env.GITHUB_TOKEN })
    """
    if not GITHUB_PERSONAL_ACCESS_TOKEN:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in environment")

    return Github(GITHUB_PERSONAL_ACCESS_TOKEN)


def list_user_repos(username: str, since_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all repositories a user has contributed to.

    Args:
        username: GitHub username
        since_date: ISO date string (e.g., "2024-01-01") to filter repos
                   Only returns repos with activity after this date

    Returns:
        List of repository dicts with keys:
        - name: Repository name
        - full_name: Owner/repo format
        - description: Repo description
        - html_url: GitHub URL
        - language: Primary language
        - updated_at: Last update timestamp
        - owner: Repository owner username
        - private: Whether repo is private

    Example:
        repos = list_user_repos("JasonWarrenUK", "2024-01-01")
        for repo in repos:
            print(f"{repo['full_name']}: {repo['description']}")
    """
    client = initialize_github_client()
    user = client.get_user(username)

    repos = []
    since_dt = datetime.fromisoformat(since_date) if since_date else None

    try:
        # Get repos owned by user
        for repo in user.get_repos():
            if since_dt and repo.updated_at < since_dt:
                continue

            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "",
                "html_url": repo.html_url,
                "language": repo.language,
                "updated_at": repo.updated_at.isoformat(),
                "owner": repo.owner.login,
                "private": repo.private
            })

    except GithubException as e:
        print(f"Error fetching repos for {username}: {e}")

    return repos


def get_commits_by_author(
    repo_full_name: str,
    author: str,
    since_date: Optional[str] = None,
    until_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all commits by a specific author in a repository.

    Args:
        repo_full_name: Repository in "owner/repo" format
        author: GitHub username of commit author
        since_date: ISO date string - start of date range
        until_date: ISO date string - end of date range

    Returns:
        List of commit dicts with keys:
        - sha: Commit SHA hash
        - message: Commit message
        - author: Author username
        - date: Commit date (ISO format)
        - html_url: GitHub URL for commit
        - files_changed: List of file paths modified

    Python Concept: datetime objects are converted to ISO strings
    TypeScript Equivalent: commit.commit.author.date.toISOString()

    Example:
        commits = get_commits_by_author("owner/repo", "JasonWarrenUK", "2024-01-01")
        for commit in commits:
            print(f"{commit['date']}: {commit['message']}")
    """
    client = initialize_github_client()

    try:
        repo = client.get_repo(repo_full_name)
        commits = []

        # Convert date strings to datetime objects
        since_dt = datetime.fromisoformat(since_date) if since_date else None
        until_dt = datetime.fromisoformat(until_date) if until_date else None

        # Get commits with filters
        for commit in repo.get_commits(author=author, since=since_dt, until=until_dt):
            commits.append({
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat(),
                "html_url": commit.html_url,
                "files_changed": [f.filename for f in commit.files] if commit.files else []
            })

        return commits

    except GithubException as e:
        print(f"Error fetching commits from {repo_full_name}: {e}")
        return []


def get_prs_by_author(
    repo_full_name: str,
    author: str,
    state: str = "all"
) -> List[Dict[str, Any]]:
    """
    Get all pull requests created by a specific author.

    Args:
        repo_full_name: Repository in "owner/repo" format
        author: GitHub username
        state: PR state - "open", "closed", or "all" (default: "all")

    Returns:
        List of PR dicts with keys:
        - number: PR number
        - title: PR title
        - body: PR description
        - state: "open" or "closed"
        - created_at: Creation date (ISO format)
        - merged_at: Merge date if merged (ISO format or None)
        - html_url: GitHub URL
        - author: PR author username
        - files_changed: Number of files changed

    Example:
        prs = get_prs_by_author("owner/repo", "JasonWarrenUK")
        for pr in prs:
            status = "merged" if pr['merged_at'] else pr['state']
            print(f"#{pr['number']}: {pr['title']} ({status})")
    """
    client = initialize_github_client()

    try:
        repo = client.get_repo(repo_full_name)
        prs = []

        for pr in repo.get_pulls(state=state):
            # Filter by author
            if pr.user.login != author:
                continue

            prs.append({
                "number": pr.number,
                "title": pr.title,
                "body": pr.body or "",
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                "html_url": pr.html_url,
                "author": pr.user.login,
                "files_changed": pr.changed_files
            })

        return prs

    except GithubException as e:
        print(f"Error fetching PRs from {repo_full_name}: {e}")
        return []


def search_code_by_author(
    query: str,
    author: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for code written by a specific author across GitHub.

    Args:
        query: Search query (e.g., "test", "authentication", "useState")
        author: GitHub username to filter results
        max_results: Maximum number of results to return (default: 10)

    Returns:
        List of code search result dicts with keys:
        - repository: Full repo name (owner/repo)
        - path: File path
        - html_url: GitHub URL to file
        - score: Search relevance score

    Note: GitHub's code search API has rate limits (10 requests/minute)

    Example:
        results = search_code_by_author("test", "JasonWarrenUK", max_results=5)
        for result in results:
            print(f"{result['repository']}: {result['path']}")
    """
    client = initialize_github_client()

    try:
        # GitHub search query format: "query user:username"
        search_query = f"{query} user:{author}"

        results = []
        for code_result in client.search_code(search_query)[:max_results]:
            results.append({
                "repository": code_result.repository.full_name,
                "path": code_result.path,
                "html_url": code_result.html_url,
                "score": code_result.score
            })

        return results

    except GithubException as e:
        print(f"Error searching code for {author}: {e}")
        return []


def get_file_contents(
    repo_full_name: str,
    file_path: str,
    ref: str = "main"
) -> Optional[str]:
    """
    Get the contents of a specific file from a repository.

    Args:
        repo_full_name: Repository in "owner/repo" format
        file_path: Path to file in repository
        ref: Branch, tag, or commit SHA (default: "main")

    Returns:
        File contents as string, or None if file not found

    Python Concept: base64 decoding happens automatically via PyGithub
    TypeScript Equivalent: Buffer.from(content, 'base64').toString('utf-8')

    Example:
        content = get_file_contents("owner/repo", "src/index.ts")
        if content:
            print(content)
    """
    client = initialize_github_client()

    try:
        repo = client.get_repo(repo_full_name)
        file = repo.get_contents(file_path, ref=ref)

        # PyGithub automatically decodes base64 content
        return file.decoded_content.decode('utf-8')

    except GithubException as e:
        print(f"Error fetching file {file_path} from {repo_full_name}: {e}")
        return None


def get_user_stats(username: str) -> Dict[str, Any]:
    """
    Get summary statistics for a GitHub user.

    Args:
        username: GitHub username

    Returns:
        Dict with user statistics:
        - username: GitHub username
        - name: User's display name
        - public_repos: Number of public repositories
        - followers: Number of followers
        - following: Number of users following
        - created_at: Account creation date
        - html_url: GitHub profile URL

    Example:
        stats = get_user_stats("JasonWarrenUK")
        print(f"{stats['name']}: {stats['public_repos']} public repos")
    """
    client = initialize_github_client()

    try:
        user = client.get_user(username)

        return {
            "username": user.login,
            "name": user.name or username,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at.isoformat(),
            "html_url": user.html_url
        }

    except GithubException as e:
        print(f"Error fetching stats for {username}: {e}")
        return {}
