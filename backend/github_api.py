"""GitHub API wrapper for retrieving user's code and contributions.

This module provides functions to query GitHub for a user's repositories,
commits, pull requests, and code - essential for building an EPA portfolio.

TypeScript Equivalent: This is like a service class with async methods,
similar to how you'd structure API clients in TypeScript.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
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


def list_user_repos(
    username: str,
    since_date: Optional[str] = None,
    include_orgs: bool = True,
    include_forks: bool = False
) -> List[Dict[str, Any]]:
    """
    List all repositories a user owns or has contributed to.

    Args:
        username: GitHub username
        since_date: ISO date string (e.g., "2024-01-01") to filter repos
                   Only returns repos with activity after this date
        include_orgs: If True, includes organization repos the user has access to
        include_forks: If True, includes forked repositories

    Returns:
        List of repository dicts with keys:
        - name: Repository name
        - full_name: Owner/repo format (e.g., "organization/repo")
        - description: Repo description
        - html_url: GitHub URL
        - language: Primary language
        - updated_at: Last update timestamp
        - owner: Repository owner username (may be an org)
        - owner_type: "User" or "Organization"
        - private: Whether repo is private
        - fork: Whether this is a fork

    Example:
        # Get all repos including org repos
        repos = list_user_repos("JasonWarrenUK", "2024-01-01", include_orgs=True)
        for repo in repos:
            owner_type = f"({repo['owner_type']})"
            print(f"{repo['full_name']} {owner_type}: {repo['description']}")
    """
    client = initialize_github_client()
    user = client.get_user(username)

    repos = []
    # Make datetime timezone-aware to match GitHub's timezone-aware timestamps
    since_dt = None
    if since_date:
        since_dt = datetime.fromisoformat(since_date).replace(tzinfo=timezone.utc)

    try:
        # Get repos owned by user or orgs they're part of
        # type='all' includes: owned, member (org repos), and collaborator repos
        # PyGithub returns a PaginatedList - we need to iterate through ALL pages
        repo_list = user.get_repos(type='all')

        # Iterate through ALL pages of results
        for repo in repo_list:
            # Skip if repo updated before since_date
            if since_dt and repo.updated_at < since_dt:
                continue

            # Skip forks if not requested
            if repo.fork and not include_forks:
                continue

            # Determine if owner is an org or user
            owner_type = "Organization" if repo.owner.type == "Organization" else "User"

            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "",
                "html_url": repo.html_url,
                "language": repo.language,
                "updated_at": repo.updated_at.isoformat(),
                "owner": repo.owner.login,
                "owner_type": owner_type,
                "private": repo.private,
                "fork": repo.fork
            })

        print(f"Found {len(repos)} repos for {username} (after filtering)")

    except GithubException as e:
        print(f"Error fetching repos for {username}: {e}")

    return repos


def get_commits_by_author(
    repo_full_name: str,
    author: str,
    since_date: Optional[str] = None,
    until_date: Optional[str] = None,
    max_results: Optional[int] = 100
) -> List[Dict[str, Any]]:
    """
    Get commits by a specific author in a repository.

    Args:
        repo_full_name: Repository in "owner/repo" format
        author: GitHub username of commit author
        since_date: ISO date string - start of date range
        until_date: ISO date string - end of date range
        max_results: Maximum number of commits to return (default: 100, None for all)

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

        # Convert date strings to timezone-aware datetime objects
        since_dt = None
        until_dt = None
        if since_date:
            since_dt = datetime.fromisoformat(since_date).replace(tzinfo=timezone.utc)
        if until_date:
            until_dt = datetime.fromisoformat(until_date).replace(tzinfo=timezone.utc)

        # Get commits with filters (only pass params if not None)
        kwargs = {"author": author}
        if since_dt:
            kwargs["since"] = since_dt
        if until_dt:
            kwargs["until"] = until_dt

        # Iterate through commits with optional limit
        for i, commit in enumerate(repo.get_commits(**kwargs)):
            if max_results and i >= max_results:
                break

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
    state: str = "all",
    max_results: Optional[int] = 50
) -> List[Dict[str, Any]]:
    """
    Get pull requests created by a specific author.

    Args:
        repo_full_name: Repository in "owner/repo" format
        author: GitHub username
        state: PR state - "open", "closed", or "all" (default: "all")
        max_results: Maximum number of PRs to return (default: 50, None for all)

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

        # Iterate through PRs with optional limit
        pr_count = 0
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

            pr_count += 1
            if max_results and pr_count >= max_results:
                break

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


def list_org_repos_with_user_commits(
    org_name: str,
    username: str,
    since_date: Optional[str] = None,
    max_repos_to_check: int = 50
) -> List[Dict[str, Any]]:
    """
    Find repositories in an organization where a user has commits.

    This is useful for large orgs where user.get_repos() doesn't return all repos.

    Args:
        org_name: GitHub organization name
        username: GitHub username to search for
        since_date: ISO date string - only check repos updated after this date
        max_repos_to_check: Maximum number of org repos to check (default: 50)

    Returns:
        List of repo dicts with commit counts

    Example:
        # Find which foundersandcoders repos Jason has contributed to
        repos = list_org_repos_with_user_commits("foundersandcoders", "JasonWarrenUK", "2024-01-01")
    """
    client = initialize_github_client()

    since_dt = None
    if since_date:
        since_dt = datetime.fromisoformat(since_date).replace(tzinfo=timezone.utc)

    repos_with_commits = []

    try:
        org = client.get_organization(org_name)

        print(f"Checking {org_name} repos for {username}'s commits...")
        print(f"(Org has {org.public_repos} public repos, checking first {max_repos_to_check})")

        checked_count = 0
        for repo in org.get_repos(sort="updated", direction="desc"):
            if checked_count >= max_repos_to_check:
                break

            # Skip if repo updated before since_date
            if since_dt and repo.updated_at < since_dt:
                continue

            checked_count += 1

            # Quick check: see if user has any commits in this repo
            try:
                commit_iterator = repo.get_commits(author=username, since=since_dt)
                # Try to get the first commit
                try:
                    first_commit = next(iter(commit_iterator))
                    # User has commits in this repo!
                    repos_with_commits.append({
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "description": repo.description or "",
                        "html_url": repo.html_url,
                        "language": repo.language,
                        "updated_at": repo.updated_at.isoformat(),
                        "owner": repo.owner.login,
                        "owner_type": "Organization",
                        "private": repo.private,
                        "has_commits_by_user": True
                    })
                    print(f"  ✓ Found commits in: {repo.full_name}")
                except StopIteration:
                    # No commits by this user
                    pass
            except GithubException:
                # Repo might be private or have other access issues
                continue

        print(f"Found {len(repos_with_commits)} repos with {username}'s commits")
        return repos_with_commits

    except GithubException as e:
        print(f"Error searching {org_name} for {username}'s commits: {e}")
        return []


def list_all_repos_with_contributions(
    username: str,
    since_date: Optional[str] = None,
    include_forks: bool = False,
    max_repos_per_org: int = 50
) -> List[Dict[str, Any]]:
    """
    Get ALL repositories where a user has contributed, including:
    - Personal repos
    - Direct member repos
    - Organization repos with commits (even if not a direct member of the repo)

    This is the most comprehensive way to find all of a user's work.

    Args:
        username: GitHub username
        since_date: ISO date string - filter by last update date
        include_forks: Include forked repositories
        max_repos_per_org: Max repos to check per organization

    Returns:
        Combined list of all repos with user's contributions

    Example:
        # Get everything!
        all_repos = list_all_repos_with_contributions("JasonWarrenUK", "2024-01-01")
    """
    client = initialize_github_client()
    user = client.get_user(username)

    all_repos = {}  # Use dict to avoid duplicates (key = full_name)

    # Step 1: Get direct member repos (from user.get_repos())
    print(f"Step 1: Getting direct member repos for {username}...")
    direct_repos = list_user_repos(username, since_date, include_forks=include_forks)
    for repo in direct_repos:
        all_repos[repo['full_name']] = repo

    # Step 2: Discover ALL organizations via commit search
    # GitHub API limitation: user.get_orgs() only returns member orgs
    # Solution: Search commits by author, extract orgs from results
    print(f"\nStep 2: Discovering organizations via commit search...")
    orgs_set = set()

    try:
        # Search for commits by this user (limited to recent results due to API)
        # Query format: author:username
        search_query = f"author:{username}"
        if since_date:
            # Add date filter to search query
            search_query += f" committer-date:>={since_date}"

        print(f"  Searching GitHub for commits by {username} (sorted by date, newest first)...")
        # Sort by committer-date descending to get recent commits first
        commit_results = client.search_commits(search_query, sort="committer-date", order="desc")

        # Extract unique organizations from commit results
        # Check first 100 commits (should be most recent due to sort order)
        checked_commits = 0
        for commit in commit_results:
            if checked_commits >= 100:  # Limit to avoid rate limits
                break

            checked_commits += 1
            repo = commit.repository
            if repo.owner.type == "Organization":
                org_name = repo.owner.login
                if org_name not in orgs_set:
                    orgs_set.add(org_name)
                    print(f"  Found org from commits: {org_name}")

        print(f"  Checked {checked_commits} recent commits")

    except GithubException as e:
        print(f"  Warning: Commit search failed ({e}), falling back to member orgs only")

    # Also add formal member orgs
    try:
        for org in user.get_orgs():
            if org.login not in orgs_set:
                orgs_set.add(org.login)
                print(f"  Found org (member): {org.login}")
    except GithubException as e:
        print(f"  Error getting member orgs: {e}")

    orgs = list(orgs_set)
    print(f"  Total organizations discovered: {len(orgs)}")

    # Step 3: Search each org for repos with user's commits
    print(f"\nStep 3: Searching {len(orgs)} organizations for contributions...")
    for org_name in orgs:
        org_repos = list_org_repos_with_user_commits(
            org_name,
            username,
            since_date,
            max_repos_to_check=max_repos_per_org
        )
        for repo in org_repos:
            # Add if not already in list
            if repo['full_name'] not in all_repos:
                all_repos[repo['full_name']] = repo

    # Convert back to list and sort by update date
    result = list(all_repos.values())
    result.sort(key=lambda r: r['updated_at'], reverse=True)

    print(f"\nTotal repos with contributions: {len(result)}")
    return result


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
