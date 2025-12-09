"""Test pagination - check if foundersandcoders/rhea appears in repo list."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.github_api import list_user_repos

print("Testing pagination - looking for foundersandcoders/rhea...")
print("(This will iterate through ALL repos, may take a moment)\n")

repos = list_user_repos("JasonWarrenUK", since_date="2020-01-01", include_orgs=True)

# Count repos by type
user_repos = [r for r in repos if r['owner_type'] == 'User']
org_repos = [r for r in repos if r['owner_type'] == 'Organization']

print(f"Total repos found: {len(repos)}")
print(f"  Personal: {len(user_repos)}")
print(f"  Organization: {len(org_repos)}\n")

# Check if foundersandcoders/rhea is in the list
rhea_repo = next((r for r in repos if r['full_name'] == 'foundersandcoders/rhea'), None)

if rhea_repo:
    print("✓ SUCCESS! Found foundersandcoders/rhea in repo list:")
    print(f"  Name: {rhea_repo['full_name']}")
    print(f"  Description: {rhea_repo['description']}")
    print(f"  Language: {rhea_repo['language']}")
    print(f"  Updated: {rhea_repo['updated_at']}")
    print(f"  Owner Type: {rhea_repo['owner_type']}")
else:
    print("✗ foundersandcoders/rhea NOT found in repo list")
    print("\nOrg repos found:")
    for repo in org_repos[:10]:
        print(f"  - {repo['full_name']}")
    if len(org_repos) > 10:
        print(f"  ... and {len(org_repos) - 10} more")

# List all unique organizations
orgs = set(r['owner'] for r in org_repos)
print(f"\nOrganizations you're a member of ({len(orgs)}):")
for org in sorted(orgs):
    org_repo_count = len([r for r in org_repos if r['owner'] == org])
    print(f"  - {org} ({org_repo_count} repos)")
