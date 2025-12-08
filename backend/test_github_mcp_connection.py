"""Test script for GitHub MCP remote server connection."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_remote_mcp_connection():
    """Test connection to GitHub's remote MCP server."""

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        print("❌ Error: GITHUB_PERSONAL_ACCESS_TOKEN not found in .env")
        return

    print("🔑 GitHub token found")
    print(f"   Token starts with: {token[:10]}...")

    try:
        # Import MCP client
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        print("\n📦 MCP Python SDK imported successfully")

        # For remote servers, we'll need to use HTTP transport
        # The remote server URL is: https://api.githubcopilot.com/mcp/

        print("\n🌐 Remote MCP Server: https://api.githubcopilot.com/mcp/")
        print("⚠️  Note: Remote HTTP transport may require additional setup")
        print("   The MCP Python SDK primarily supports stdio transport")
        print("   We may need to implement custom HTTP transport or use stdio server locally")

        # TODO: Implement HTTP client for remote MCP server
        # The standard MCP Python SDK uses stdio transport (for local servers)
        # For remote HTTP servers, we'll need to either:
        # 1. Use the Docker/binary version locally with stdio
        # 2. Implement custom HTTP transport using httpx
        # 3. Use a different approach

        print("\n💡 Next steps:")
        print("   1. The remote server is best accessed via Claude Desktop/VS Code clients")
        print("   2. For our Python backend, we should use local stdio server (Docker/binary)")
        print("   3. Alternatively, we can implement direct GitHub API calls")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub MCP Remote Server Connection Test")
    print("=" * 60)
    asyncio.run(test_remote_mcp_connection())
