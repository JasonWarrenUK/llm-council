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
    """Test listing user repositories including organization repos."""
    print("\n" + "=" * 60)
    print("TEST: List User Repositories (Including Organizations)")
    print("=" * 60)

    username = "JasonWarrenUK"  # Replace with your GitHub username
    repos = list_user_repos(username, since_date="2024-01-01", include_orgs=True)

    if repos:
        # Count user vs org repos
        user_repos = [r for r in repos if r['owner_type'] == 'User']
        org_repos = [r for r in repos if r['owner_type'] == 'Organization']

        print(f"✓ Found {len(repos)} repositories (since 2024-01-01)")
        print(f"  - {len(user_repos)} personal repos")
        print(f"  - {len(org_repos)} organization repos")

        print("\nFirst 5 repos:")
        for repo in repos[:5]:
            lang = repo['language'] or "N/A"
            owner_badge = "🏢" if repo['owner_type'] == 'Organization' else "👤"
            print(f"  {owner_badge} {repo['full_name']} ({lang})")
            print(f"    {repo['description'][:80] if repo['description'] else 'No description'}")

        if org_repos:
            print(f"\n✓ Organization access verified! Found {len(org_repos)} org repos")
        else:
            print("\n⚠️  No organization repos found (may not be part of any orgs)")

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


def test_specific_org_repo():
    """Test access to a specific organization repository."""
    print("\n" + "=" * 60)
    print("TEST: Access Specific Organization Repo")
    print("=" * 60)

    org_repo = "foundersandcoders/rhea"
    username = "JasonWarrenUK"

    print(f"Testing access to {org_repo}...")

    # Test 1: Can we access the repo at all?
    print("\n1. Fetching README from org repo...")
    readme = get_file_contents(org_repo, "README.md")

    if readme:
        print(f"   ✓ Successfully accessed {org_repo}")
        print(f"   README length: {len(readme)} bytes")
    else:
        print(f"   ✗ Cannot access {org_repo}")
        print("   This may be due to:")
        print("   - Repo is private and token lacks access")
        print("   - Repo doesn't exist or was renamed")
        print("   - Token needs 'read:org' scope")
        return False

    # Test 2: Can we see commits by this user?
    print(f"\n2. Fetching commits by {username} in org repo...")
    commits = get_commits_by_author(org_repo, username, since_date="2024-01-01")

    if commits:
        print(f"   ✓ Found {len(commits)} commits by {username}")
        if commits:
            print(f"   Most recent: {commits[0]['date'][:10]} - {commits[0]['message'][:50]}")
    else:
        print(f"   ⚠️  No commits found by {username} in this repo")
        print("   (This is okay if you haven't committed to this repo)")

    # Test 3: Can we see PRs by this user?
    print(f"\n3. Fetching PRs by {username} in org repo...")
    prs = get_prs_by_author(org_repo, username)

    if prs:
        print(f"   ✓ Found {len(prs)} PRs by {username}")
        if prs:
            print(f"   Latest PR: #{prs[0]['number']} - {prs[0]['title'][:50]}")
    else:
        print(f"   ⚠️  No PRs found by {username} in this repo")
        print("   (This is okay if you haven't created PRs here)")

    return True


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

    # Test 7: Specific org repo access
    test_specific_org_repo()

    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
