"""Test GitHub API wrapper functions."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.github_api import (
    list_user_repos,
    get_commits_by_author,
    get_prs_by_author,
    search_code_by_author,
    get_file_contents,
    get_user_stats
)


def test_user_stats():
    """Test getting user statistics."""
    print("\n" + "=" * 60)
    print("TEST: Get User Stats")
    print("=" * 60)

    username = "JasonWarrenUK"  # Replace with your GitHub username
    stats = get_user_stats(username)

    if stats:
        print(f"✓ User: {stats['name']} (@{stats['username']})")
        print(f"  Public repos: {stats['public_repos']}")
        print(f"  Followers: {stats['followers']}")
        print(f"  Account created: {stats['created_at']}")
        print(f"  Profile: {stats['html_url']}")
        return True
    else:
        print("✗ Failed to fetch user stats")
        return False


def test_list_repos():
    """Test listing user repositories."""
    print("\n" + "=" * 60)
    print("TEST: List User Repositories")
    print("=" * 60)

    username = "JasonWarrenUK"  # Replace with your GitHub username
    repos = list_user_repos(username, since_date="2024-01-01")

    if repos:
        print(f"✓ Found {len(repos)} repositories (since 2024-01-01)")
        print("\nFirst 5 repos:")
        for repo in repos[:5]:
            lang = repo['language'] or "N/A"
            print(f"  • {repo['full_name']} ({lang})")
            print(f"    {repo['description'][:80] if repo['description'] else 'No description'}")
        return True, repos
    else:
        print("✗ No repositories found or error occurred")
        return False, []


def test_get_commits(repo_full_name):
    """Test getting commits by author."""
    print("\n" + "=" * 60)
    print(f"TEST: Get Commits from {repo_full_name}")
    print("=" * 60)

    username = "JasonWarrenUK"  # Replace with your GitHub username
    commits = get_commits_by_author(repo_full_name, username, since_date="2024-01-01")

    if commits:
        print(f"✓ Found {len(commits)} commits by {username} (since 2024-01-01)")
        print("\nMost recent 3 commits:")
        for commit in commits[:3]:
            print(f"  • {commit['date'][:10]}: {commit['message'][:60]}")
            print(f"    SHA: {commit['sha'][:7]}")
            print(f"    Files: {len(commit['files_changed'])} changed")
        return True
    else:
        print(f"✗ No commits found for {username} in {repo_full_name}")
        return False


def test_get_prs(repo_full_name):
    """Test getting pull requests by author."""
    print("\n" + "=" * 60)
    print(f"TEST: Get Pull Requests from {repo_full_name}")
    print("=" * 60)

    username = "JasonWarrenUK"  # Replace with your GitHub username
    prs = get_prs_by_author(repo_full_name, username)

    if prs:
        print(f"✓ Found {len(prs)} PRs by {username}")
        print("\nPRs:")
        for pr in prs[:3]:
            status = "merged" if pr['merged_at'] else pr['state']
            print(f"  • #{pr['number']}: {pr['title']} ({status})")
            print(f"    Created: {pr['created_at'][:10]}")
            print(f"    Files changed: {pr['files_changed']}")
        return True
    else:
        print(f"✗ No PRs found for {username} in {repo_full_name}")
        return False


def test_search_code():
    """Test searching for code by author."""
    print("\n" + "=" * 60)
    print("TEST: Search Code by Author")
    print("=" * 60)

    username = "JasonWarrenUK"  # Replace with your GitHub username
    query = "test"  # Search for files containing "test"

    print(f"Searching for '{query}' in {username}'s code...")
    results = search_code_by_author(query, username, max_results=5)

    if results:
        print(f"✓ Found {len(results)} code matches")
        print("\nMatches:")
        for result in results:
            print(f"  • {result['repository']}/{result['path']}")
            print(f"    Score: {result['score']}")
        return True
    else:
        print(f"✗ No code matches found")
        return False


def test_get_file(repo_full_name, file_path):
    """Test getting file contents."""
    print("\n" + "=" * 60)
    print(f"TEST: Get File Contents")
    print("=" * 60)

    print(f"Fetching {file_path} from {repo_full_name}...")
    content = get_file_contents(repo_full_name, file_path)

    if content:
        lines = content.split('\n')
        print(f"✓ Retrieved file ({len(lines)} lines, {len(content)} bytes)")
        print("\nFirst 5 lines:")
        for line in lines[:5]:
            print(f"  {line}")
        return True
    else:
        print(f"✗ Failed to retrieve file")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GitHub API Wrapper Test Suite")
    print("=" * 60)
    print("\nNote: Replace 'JasonWarrenUK' with your GitHub username")
    print("      in the test functions to test with your account")

    # Test 1: User stats
    test_user_stats()

    # Test 2: List repos
    success, repos = test_list_repos()

    if success and repos:
        # Use first repo for further tests
        test_repo = repos[0]['full_name']

        # Test 3: Get commits
        test_get_commits(test_repo)

        # Test 4: Get PRs
        test_get_prs(test_repo)

        # Test 5: Get file (try README.md)
        test_get_file(test_repo, "README.md")

    # Test 6: Search code
    test_search_code()

    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
