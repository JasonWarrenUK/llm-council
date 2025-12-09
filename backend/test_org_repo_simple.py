"""Simple test for specific org repo access."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.github_api import get_file_contents, get_commits_by_author, get_prs_by_author

print("Testing access to foundersandcoders/rhea...")

# Test 1: Can we access the repo README?
print("\n1. Fetching README...")
readme = get_file_contents("foundersandcoders/rhea", "README.md")

if readme:
    print(f"   ✓ Successfully accessed repo")
    print(f"   README length: {len(readme)} bytes")
    print(f"   First line: {readme.split(chr(10))[0][:80]}")
else:
    print(f"   ✗ Cannot access repo")
    print("   Possible reasons:")
    print("   - Private repo without access")
    print("   - Token needs 'read:org' scope")
    print("   - Repo doesn't exist")

# Test 2: Check commits
print("\n2. Fetching commits by JasonWarrenUK...")
commits = get_commits_by_author("foundersandcoders/rhea", "JasonWarrenUK", since_date="2024-01-01")

if commits:
    print(f"   ✓ Found {len(commits)} commits")
    print(f"   Latest: {commits[0]['date'][:10]} - {commits[0]['message'][:50]}")
else:
    print(f"   ⚠️  No commits found (may not have committed to this repo)")

# Test 3: Check PRs
print("\n3. Fetching PRs by JasonWarrenUK...")
prs = get_prs_by_author("foundersandcoders/rhea", "JasonWarrenUK")

if prs:
    print(f"   ✓ Found {len(prs)} PRs")
    print(f"   Latest: #{prs[0]['number']} - {prs[0]['title'][:50]}")
else:
    print(f"   ⚠️  No PRs found (may not have created PRs here)")

print("\nTest complete!")
