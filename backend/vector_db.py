"""
Vector Database Management for GitHub Knowledge Base

This module provides a clean interface to ChromaDB for storing and querying
embedded GitHub artifacts (commits, PRs, code files).

TypeScript Analogy: Think of this like a database ORM (similar to Prisma or TypeORM)
but specialized for semantic search instead of traditional CRUD operations.
"""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Any, Optional
from datetime import datetime
import os


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Returns a persistent ChromaDB client that stores data locally.

    TypeScript Equivalent:
        const db = await open('./chroma_db', { persistent: true });

    Python Concept:
        - PersistentClient saves data to disk (survives restarts)
        - EphemeralClient only exists in memory (lost on restart)
        - We use PersistentClient to avoid re-indexing on every startup

    Returns:
        chromadb.PersistentClient: Client instance pointing to ./chroma_db/

    Side Effects:
        - Creates ./chroma_db/ directory if it doesn't exist
        - Creates SQLite database file for metadata storage
    """
    # Define storage path relative to project root
    # TypeScript: path.join(process.cwd(), 'chroma_db')
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

    # Ensure parent directory exists
    os.makedirs(db_path, exist_ok=True)

    # Create persistent client
    # Python Note: Settings() configures ChromaDB behavior (anonymized telemetry disabled)
    client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(
            anonymized_telemetry=False,  # Respect user privacy
            allow_reset=True  # Enable collection deletion
        )
    )

    return client


def get_or_create_collection(
    client: chromadb.PersistentClient,
    name: str = "github_knowledge"
) -> chromadb.Collection:
    """
    Get existing collection or create new one if it doesn't exist.

    TypeScript Equivalent:
        const collection = db.collection('github_knowledge')
            ?? await db.createCollection('github_knowledge');

    Python Concept:
        Collections are like database tables or IndexedDB object stores.
        They group related documents and provide query capabilities.

    Args:
        client: ChromaDB client instance
        name: Collection name (default: "github_knowledge")

    Returns:
        chromadb.Collection: Collection instance for adding/querying documents

    Example:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        # Now you can add/query documents
    """
    # Collection metadata: structured info about the collection itself
    # (not to be confused with document metadata)
    metadata = {
        "description": "Embedded GitHub history for portfolio evidence",
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

    # get_or_create_collection is idempotent:
    # - If collection exists: returns it (ignores metadata param)
    # - If doesn't exist: creates it with metadata
    # TypeScript: Similar to "upsert" pattern
    collection = client.get_or_create_collection(
        name=name,
        metadata=metadata
    )

    return collection


def add_documents(
    collection: chromadb.Collection,
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str]
) -> None:
    """
    Add documents to the collection with metadata and unique IDs.

    TypeScript Equivalent:
        await Promise.all(
            documents.map((doc, i) =>
                collection.add({ content: doc, metadata: metadatas[i] }, ids[i])
            )
        );

    Python Concept:
        - ChromaDB automatically generates embeddings using its default model
        - We provide: text content, metadata, and unique IDs
        - ChromaDB handles: embedding generation, vector storage, indexing

    Args:
        collection: ChromaDB collection instance
        documents: List of text content to embed (code, commit messages, etc.)
        metadatas: List of metadata dicts (one per document)
        ids: List of unique identifiers (format: {repo}:{type}:{hash}:{chunk})

    Document ID Format:
        "{repo_name}:{artifact_type}:{identifier}:{chunk_index}"
        Examples:
            - "user/repo:commit:abc123:0"
            - "user/repo:pr:42:0"
            - "user/repo:code:path/file.py:3"

    Metadata Schema:
        {
            "repo": "user/repo",
            "artifact_type": "commit" | "pr" | "code",
            "author": "github_username",
            "date": "ISO 8601 timestamp",
            "file_path": "path/to/file" (for code artifacts),
            "commit_hash": "abc123" (optional),
            "indexed_at": "ISO 8601 timestamp"
        }

    Raises:
        ValueError: If list lengths don't match
        chromadb.errors.DuplicateIDError: If ID already exists

    Example:
        add_documents(
            collection,
            documents=["async function auth() {...}"],
            metadatas=[{"repo": "user/app", "artifact_type": "code", "author": "jasonwarren"}],
            ids=["user/app:code:auth.ts:0"]
        )
    """
    # Validation: All lists must be same length
    # TypeScript: if (documents.length !== metadatas.length || ...)
    if not (len(documents) == len(metadatas) == len(ids)):
        raise ValueError(
            f"List length mismatch: documents={len(documents)}, "
            f"metadatas={len(metadatas)}, ids={len(ids)}"
        )

    # Add indexed_at timestamp to all metadata entries
    # TypeScript: metadatas.map(m => ({ ...m, indexed_at: new Date().toISOString() }))
    enriched_metadatas = [
        {**metadata, "indexed_at": datetime.now().isoformat()}
        for metadata in metadatas
    ]

    # Batch insert all documents
    # Python Note: ChromaDB handles embedding generation asynchronously
    collection.add(
        documents=documents,
        metadatas=enriched_metadatas,
        ids=ids
    )


def query_collection(
    collection: chromadb.Collection,
    query_text: str,
    n_results: int = 10,
    where_filter: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Query collection by semantic similarity to query text.

    TypeScript Equivalent:
        const results = await collection.search(queryText, {
            limit: nResults,
            filter: whereFilter
        });

    How Semantic Search Works:
        1. Your query text is converted to a vector (embedding)
        2. ChromaDB finds vectors with smallest distance to your query
        3. Returns original documents ranked by similarity
        4. Lower distance = more similar

    Args:
        collection: ChromaDB collection instance
        query_text: Natural language query (e.g., "authentication patterns")
        n_results: Maximum number of results to return (default: 10)
        where_filter: MongoDB-style metadata filter (optional)

    Where Filter Examples:
        # Find only commits by specific author
        {"author": "jasonwarren"}

        # Find code from specific repo
        {"artifact_type": "code", "repo": "user/repo"}

        # Find recent commits (requires date as string)
        {"date": {"$gte": "2024-01-01"}}

        # Complex AND query
        {"$and": [{"author": "jasonwarren"}, {"artifact_type": "pr"}]}

    Returns:
        Dict with keys:
            - ids: List[List[str]] - Document IDs (nested for batch queries)
            - documents: List[List[str]] - Original text content
            - metadatas: List[List[Dict]] - Document metadata
            - distances: List[List[float]] - Similarity scores (0=identical, higher=less similar)

    Example:
        results = query_collection(
            collection,
            query_text="How to handle authentication?",
            n_results=5,
            where_filter={"artifact_type": "code"}
        )

        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            print(f"Similarity: {1 - distance:.2%}")
            print(f"File: {metadata['file_path']}")
            print(f"Code: {doc[:100]}...")
    """
    # Query ChromaDB with semantic search
    # Python Note: query_texts is a list to support batch queries
    # We use single-item list for single query
    query_params = {
        "query_texts": [query_text],  # Wrap in list for API consistency
        "n_results": n_results
    }

    # Add metadata filter if provided
    # TypeScript: { ...queryParams, ...(whereFilter && { where: whereFilter }) }
    if where_filter:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    return results


def delete_collection(
    client: chromadb.PersistentClient,
    name: str
) -> None:
    """
    Delete a collection and all its documents.

    TypeScript Equivalent:
        await db.dropCollection(name);

    Use Cases:
        - Full re-indexing (delete old data, start fresh)
        - Cleanup during testing
        - Removing outdated knowledge base

    Args:
        client: ChromaDB client instance
        name: Name of collection to delete

    Raises:
        ValueError: If collection doesn't exist

    Warning:
        This operation is IRREVERSIBLE. All embeddings will be lost.
        You'll need to re-run indexing to restore the data.

    Example:
        client = get_chroma_client()
        delete_collection(client, "github_knowledge")
        # Collection is gone, re-indexing required
    """
    try:
        client.delete_collection(name=name)
    except Exception as e:
        raise ValueError(f"Failed to delete collection '{name}': {str(e)}")


def get_collection_stats(collection: chromadb.Collection) -> Dict[str, Any]:
    """
    Get statistics about a collection.

    TypeScript Equivalent:
        const stats = {
            count: await collection.count(),
            metadata: collection.metadata,
            sample: await collection.findMany({ limit: 3 })
        };

    Returns:
        Dict with keys:
            - name: Collection name
            - count: Total number of documents
            - metadata: Collection-level metadata
            - sample_ids: First 5 document IDs (for inspection)
            - artifact_types: Count of documents by type (if metadata available)

    Example:
        stats = get_collection_stats(collection)
        print(f"Collection: {stats['name']}")
        print(f"Documents: {stats['count']}")
        print(f"Sample IDs: {stats['sample_ids']}")
    """
    # Get total document count
    count = collection.count()

    # Get collection metadata
    metadata = collection.metadata or {}

    # Peek at first few documents to show IDs
    # (useful for debugging document ID format)
    sample = collection.peek(limit=5)
    sample_ids = sample.get("ids", [])

    # Try to extract artifact type distribution from sample
    # TypeScript: sample.reduce((acc, doc) => { ... }, {})
    artifact_types: Dict[str, int] = {}
    if sample.get("metadatas"):
        for doc_metadata in sample["metadatas"]:
            artifact_type = doc_metadata.get("artifact_type", "unknown")
            artifact_types[artifact_type] = artifact_types.get(artifact_type, 0) + 1

    return {
        "name": collection.name,
        "count": count,
        "metadata": metadata,
        "sample_ids": sample_ids,
        "artifact_types_sample": artifact_types,  # Only from sample, not full collection
    }


# Module-level helper for common workflow
def initialize_knowledge_base() -> tuple[chromadb.PersistentClient, chromadb.Collection]:
    """
    Convenience function to initialize both client and collection.

    TypeScript Equivalent:
        async function setup() {
            const client = await createClient();
            const collection = await client.getOrCreateCollection('github_knowledge');
            return { client, collection };
        }

    Python Note:
        Tuple unpacking lets you do:
            client, collection = initialize_knowledge_base()

    Returns:
        Tuple of (client, collection) ready for use

    Example:
        # Quick setup in one line
        client, collection = initialize_knowledge_base()

        # Now you can immediately add/query
        add_documents(collection, [...], [...], [...])
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)
    return client, collection


if __name__ == "__main__":
    """
    Demo script showing basic usage.
    Run with: python -m backend.vector_db
    """
    print("ChromaDB Vector Database Demo\n")

    # Initialize
    print("1. Initializing client and collection...")
    client, collection = initialize_knowledge_base()

    # Add sample documents
    print("2. Adding sample documents...")
    add_documents(
        collection,
        documents=[
            "async function authenticate(username, password) { return jwt.sign({username}); }",
            "def authenticate(username: str, password: str) -> str: return jwt.encode({'username': username})",
            "Testing authentication with pytest and mock JWT tokens"
        ],
        metadatas=[
            {"repo": "demo/app", "artifact_type": "code", "author": "jasonwarren", "file_path": "auth.ts", "date": "2024-03-15"},
            {"repo": "demo/api", "artifact_type": "code", "author": "jasonwarren", "file_path": "auth.py", "date": "2024-06-20"},
            {"repo": "demo/api", "artifact_type": "commit", "author": "jasonwarren", "commit_hash": "abc123", "date": "2024-06-21"}
        ],
        ids=[
            "demo/app:code:auth.ts:0",
            "demo/api:code:auth.py:0",
            "demo/api:commit:abc123:0"
        ]
    )

    # Query
    print("3. Querying for 'authentication'...")
    results = query_collection(collection, "user login and authentication", n_results=3)

    print(f"\nFound {len(results['ids'][0])} results:")
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"\n  Result {i+1} (similarity: {(1-distance)*100:.1f}%)")
        print(f"  Type: {metadata['artifact_type']}")
        print(f"  Repo: {metadata['repo']}")
        print(f"  Content: {doc[:80]}...")

    # Stats
    print("\n4. Collection statistics:")
    stats = get_collection_stats(collection)
    print(f"  Name: {stats['name']}")
    print(f"  Total documents: {stats['count']}")
    print(f"  Sample IDs: {stats['sample_ids'][:3]}")

    # Cleanup
    print("\n5. Cleaning up demo collection...")
    delete_collection(client, "github_knowledge")
    print("  Demo complete!")
