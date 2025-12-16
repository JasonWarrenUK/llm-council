"""
Tests for vector_db.py - ChromaDB Interface

These are integration tests that use real ChromaDB instances in a temporary
test directory. This ensures we're testing actual behavior, not mocked interfaces.

Run with: pytest backend/test_vector_db.py -v
"""

import pytest
import chromadb
import os
import shutil
import time
from typing import Generator
from .vector_db import (
    get_chroma_client,
    get_or_create_collection,
    add_documents,
    query_collection,
    delete_collection,
    get_collection_stats,
    initialize_knowledge_base
)


# Test configuration
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_chroma_db")


@pytest.fixture(scope="function")
def test_client() -> Generator[chromadb.Client, None, None]:
    """
    Fixture providing a ChromaDB client for testing.

    Uses EphemeralClient (in-memory) to avoid file locking issues during tests.
    Scope is 'function' so each test gets a fresh database.

    TypeScript Equivalent:
        beforeEach(() => {
            db = await createTestDatabase();  // In-memory database
        });

        afterEach(() => {
            db = null;  // Let garbage collector handle cleanup
        });
    """
    # Create ephemeral (in-memory) client for testing
    # This avoids file locking issues while still testing the same API
    from chromadb.config import Settings
    client = chromadb.EphemeralClient(
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    yield client

    # No cleanup needed for ephemeral client - it's in-memory only


@pytest.fixture(scope="function")
def test_collection(test_client: chromadb.Client, request) -> chromadb.Collection:
    """
    Fixture providing a test collection.

    Creates a unique collection for each test, automatically cleaned up via test_client fixture.
    Uses request.node.name to create unique collection names.
    """
    # Create unique collection name for this test
    collection_name = f"test_collection_{request.node.name}"

    collection = test_client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Test collection for unit tests"}
    )
    return collection


class TestGetChromaClient:
    """Tests for get_chroma_client() function"""

    def test_creates_client_successfully(self):
        """Test that get_chroma_client returns a valid client"""
        client = get_chroma_client()
        assert client is not None
        # Check that client has the expected methods
        assert hasattr(client, 'get_or_create_collection')
        assert hasattr(client, 'delete_collection')

    def test_creates_database_directory(self):
        """Test that client creation creates the chroma_db directory"""
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

        client = get_chroma_client()

        # Verify directory exists
        assert os.path.exists(db_path)
        assert os.path.isdir(db_path)

    def test_client_is_persistent(self):
        """Test that client persists data across instances"""
        # Create client and collection with unique name
        client1 = get_chroma_client()
        test_name = f"persistence_test_{os.getpid()}"

        try:
            collection1 = client1.get_or_create_collection(test_name)

            # Add a document
            collection1.add(
                documents=["test document"],
                metadatas=[{"test": "data"}],
                ids=["test_id"]
            )

            # Create new client instance
            client2 = get_chroma_client()
            collection2 = client2.get_collection(test_name)

            # Verify document persisted
            assert collection2.count() == 1
        finally:
            # Cleanup
            try:
                client1.delete_collection(test_name)
            except:
                pass


class TestGetOrCreateCollection:
    """Tests for get_or_create_collection() function"""

    def test_creates_new_collection(self, test_client):
        """Test creating a new collection"""
        collection = get_or_create_collection(test_client, "new_collection")

        assert collection is not None
        assert collection.name == "new_collection"
        assert collection.count() == 0

    def test_retrieves_existing_collection(self, test_client):
        """Test that get_or_create returns existing collection"""
        # Create collection first time
        collection1 = get_or_create_collection(test_client, "existing_collection")
        collection1.add(
            documents=["test"],
            metadatas=[{"key": "value"}],
            ids=["id1"]
        )

        # Get same collection second time
        collection2 = get_or_create_collection(test_client, "existing_collection")

        # Should have same data
        assert collection2.name == "existing_collection"
        assert collection2.count() == 1

    def test_sets_collection_metadata(self, test_client):
        """Test that collection metadata is set correctly"""
        collection = get_or_create_collection(test_client, "metadata_test")

        metadata = collection.metadata
        assert metadata is not None
        assert metadata["description"] == "Embedded GitHub history for portfolio evidence"
        assert "created_at" in metadata
        assert "version" in metadata

    def test_default_collection_name(self, test_client):
        """Test using default collection name"""
        collection = get_or_create_collection(test_client)
        assert collection.name == "github_knowledge"


class TestAddDocuments:
    """Tests for add_documents() function"""

    def test_adds_single_document(self, test_collection):
        """Test adding a single document"""
        print(f"\n  → Adding document to collection...")
        add_documents(
            test_collection,
            documents=["Hello, world!"],
            metadatas=[{"source": "test"}],
            ids=["doc1"]
        )

        count = test_collection.count()
        print(f"  ✓ Document count: {count}")
        assert count == 1

    def test_adds_multiple_documents(self, test_collection):
        """Test adding multiple documents in batch"""
        add_documents(
            test_collection,
            documents=["Document 1", "Document 2", "Document 3"],
            metadatas=[
                {"type": "commit"},
                {"type": "pr"},
                {"type": "code"}
            ],
            ids=["doc1", "doc2", "doc3"]
        )

        assert test_collection.count() == 3

    def test_enriches_metadata_with_indexed_at(self, test_collection):
        """Test that indexed_at timestamp is added automatically"""
        add_documents(
            test_collection,
            documents=["Test doc"],
            metadatas=[{"author": "jasonwarren"}],
            ids=["test1"]
        )

        # Retrieve the document
        result = test_collection.get(ids=["test1"])
        metadata = result["metadatas"][0]

        # Verify indexed_at was added
        assert "indexed_at" in metadata
        assert "author" in metadata
        assert metadata["author"] == "jasonwarren"

    def test_validates_list_length_mismatch(self, test_collection):
        """Test that mismatched list lengths raise ValueError"""
        with pytest.raises(ValueError, match="List length mismatch"):
            add_documents(
                test_collection,
                documents=["Doc 1", "Doc 2"],  # 2 documents
                metadatas=[{"key": "value"}],  # 1 metadata
                ids=["id1", "id2"]  # 2 ids
            )

    def test_document_id_format(self, test_collection):
        """Test proper document ID format"""
        doc_id = "user/repo:commit:abc123:0"

        add_documents(
            test_collection,
            documents=["Commit message"],
            metadatas=[{
                "repo": "user/repo",
                "artifact_type": "commit",
                "commit_hash": "abc123"
            }],
            ids=[doc_id]
        )

        result = test_collection.get(ids=[doc_id])
        assert len(result["ids"]) == 1
        assert result["ids"][0] == doc_id


class TestQueryCollection:
    """Tests for query_collection() function"""

    @pytest.fixture
    def populated_collection(self, test_collection):
        """Fixture with pre-populated test data"""
        add_documents(
            test_collection,
            documents=[
                "async function authenticate(user, password) { return jwt.sign(user); }",
                "def authenticate(user: str, password: str) -> str: return encode(user)",
                "Testing authentication with mock credentials",
                "Database migration script for user table",
                "API endpoint for fetching user profile data"
            ],
            metadatas=[
                {"artifact_type": "code", "language": "javascript", "author": "jasonwarren"},
                {"artifact_type": "code", "language": "python", "author": "jasonwarren"},
                {"artifact_type": "commit", "author": "jasonwarren"},
                {"artifact_type": "commit", "author": "jasonwarren"},
                {"artifact_type": "code", "language": "python", "author": "collaborator"}
            ],
            ids=["js1", "py1", "commit1", "commit2", "py2"]
        )
        return test_collection

    def test_semantic_search_returns_results(self, populated_collection):
        """Test that semantic search returns relevant results"""
        print(f"\n  → Querying collection for 'user authentication'...")
        results = query_collection(
            populated_collection,
            query_text="user authentication",
            n_results=3
        )

        print(f"  ✓ Found {len(results['documents'][0])} results")
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            similarity = (1 - distance) * 100
            print(f"    [{i+1}] Similarity: {similarity:.1f}% - {doc[:50]}...")

        assert "documents" in results
        assert "metadatas" in results
        assert "distances" in results
        assert len(results["documents"][0]) <= 3

    def test_semantic_search_relevance(self, populated_collection):
        """Test that most relevant results come first"""
        results = query_collection(
            populated_collection,
            query_text="authentication code",
            n_results=3
        )

        # First result should be authentication-related
        top_doc = results["documents"][0][0]
        assert "authenticate" in top_doc.lower()

    def test_limits_results_to_n_results(self, populated_collection):
        """Test that n_results parameter limits returned results"""
        results = query_collection(
            populated_collection,
            query_text="test",
            n_results=2
        )

        assert len(results["documents"][0]) <= 2

    def test_filter_by_metadata(self, populated_collection):
        """Test filtering results by metadata using where clause"""
        print(f"\n  → Querying with filter: artifact_type='code'...")
        results = query_collection(
            populated_collection,
            query_text="code",
            n_results=10,
            where_filter={"artifact_type": "code"}
        )

        print(f"  ✓ Found {len(results['documents'][0])} code artifacts")
        for metadata in results["metadatas"][0]:
            print(f"    - {metadata['artifact_type']} ({metadata.get('language', 'unknown')})")

        # All results should be code artifacts
        for metadata in results["metadatas"][0]:
            assert metadata["artifact_type"] == "code"

    def test_filter_by_author(self, populated_collection):
        """Test filtering by author using where clause"""
        results = query_collection(
            populated_collection,
            query_text="python",
            n_results=10,
            where_filter={"author": "jasonwarren"}
        )

        # All results should be from jasonwarren
        for metadata in results["metadatas"][0]:
            assert metadata["author"] == "jasonwarren"

    def test_complex_and_filter(self, populated_collection):
        """Test complex AND filter with multiple conditions"""
        results = query_collection(
            populated_collection,
            query_text="code",
            n_results=10,
            where_filter={
                "$and": [
                    {"artifact_type": "code"},
                    {"language": "python"}
                ]
            }
        )

        # All results should be Python code
        for metadata in results["metadatas"][0]:
            assert metadata["artifact_type"] == "code"
            assert metadata["language"] == "python"

    def test_empty_results(self, test_collection):
        """Test querying empty collection returns empty results"""
        results = query_collection(
            test_collection,
            query_text="nonexistent",
            n_results=10
        )

        assert len(results["documents"][0]) == 0


class TestDeleteCollection:
    """Tests for delete_collection() function"""

    def test_deletes_existing_collection(self, test_client):
        """Test that delete_collection removes a collection"""
        # Create collection
        collection = test_client.get_or_create_collection("to_delete")
        collection.add(
            documents=["test"],
            metadatas=[{"key": "value"}],
            ids=["id1"]
        )

        # Delete it
        delete_collection(test_client, "to_delete")

        # Verify it's gone
        with pytest.raises(Exception):
            test_client.get_collection("to_delete")

    def test_delete_nonexistent_collection_raises_error(self, test_client):
        """Test that deleting non-existent collection raises ValueError"""
        with pytest.raises(ValueError, match="Failed to delete collection"):
            delete_collection(test_client, "nonexistent_collection")


class TestGetCollectionStats:
    """Tests for get_collection_stats() function"""

    def test_stats_for_empty_collection(self, test_collection):
        """Test stats for empty collection"""
        stats = get_collection_stats(test_collection)

        # Assert against actual collection name (which is unique per test)
        assert stats["name"] == test_collection.name
        assert stats["count"] == 0
        assert stats["sample_ids"] == []
        assert stats["artifact_types_sample"] == {}

    def test_stats_for_populated_collection(self, test_collection):
        """Test stats for collection with documents"""
        add_documents(
            test_collection,
            documents=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[
                {"artifact_type": "commit"},
                {"artifact_type": "commit"},
                {"artifact_type": "code"}
            ],
            ids=["id1", "id2", "id3"]
        )

        stats = get_collection_stats(test_collection)

        assert stats["count"] == 3
        assert len(stats["sample_ids"]) == 3
        assert "commit" in stats["artifact_types_sample"]
        assert "code" in stats["artifact_types_sample"]

    def test_stats_includes_metadata(self, test_client):
        """Test that stats include collection metadata"""
        collection = test_client.get_or_create_collection(
            "metadata_collection",
            metadata={"custom": "value"}
        )

        stats = get_collection_stats(collection)

        assert "metadata" in stats
        assert stats["metadata"]["custom"] == "value"

    def test_sample_ids_limited_to_five(self, test_collection):
        """Test that sample_ids returns max 5 IDs"""
        # Add 10 documents
        add_documents(
            test_collection,
            documents=[f"Doc {i}" for i in range(10)],
            metadatas=[{"index": i} for i in range(10)],
            ids=[f"id{i}" for i in range(10)]
        )

        stats = get_collection_stats(test_collection)

        # Should return max 5 sample IDs
        assert len(stats["sample_ids"]) == 5


class TestInitializeKnowledgeBase:
    """Tests for initialize_knowledge_base() convenience function"""

    def test_returns_client_and_collection(self):
        """Test that function returns both client and collection"""
        try:
            client, collection = initialize_knowledge_base()

            # Check client has expected methods
            assert hasattr(client, 'get_or_create_collection')
            # Check collection has expected methods
            assert hasattr(collection, 'add')
            assert hasattr(collection, 'query')
            assert collection.name == "github_knowledge"
        finally:
            # Cleanup
            try:
                client = get_chroma_client()
                client.delete_collection("github_knowledge")
            except:
                pass

    def test_collection_is_ready_to_use(self):
        """Test that returned collection can be used immediately"""
        try:
            client, collection = initialize_knowledge_base()

            # Should be able to add documents right away
            add_documents(
                collection,
                documents=["Test"],
                metadatas=[{"test": "data"}],
                ids=["test1"]
            )

            assert collection.count() == 1
        finally:
            # Cleanup
            try:
                client = get_chroma_client()
                client.delete_collection("github_knowledge")
            except:
                pass


class TestEndToEndWorkflow:
    """Integration tests for complete workflows"""

    def test_complete_workflow(self, test_client):
        """Test complete workflow: create, add, query, stats, delete"""
        print(f"\n  → Testing complete end-to-end workflow...")

        # 1. Create collection
        print(f"  [1/5] Creating collection...")
        collection = get_or_create_collection(test_client, "workflow_test")
        print(f"      ✓ Collection '{collection.name}' created")

        # 2. Add documents
        print(f"  [2/5] Adding 3 documents...")
        add_documents(
            collection,
            documents=[
                "React component for user authentication",
                "Python Flask API for user login",
                "Unit tests for authentication flow"
            ],
            metadatas=[
                {"repo": "frontend", "artifact_type": "code", "author": "jasonwarren"},
                {"repo": "backend", "artifact_type": "code", "author": "jasonwarren"},
                {"repo": "backend", "artifact_type": "code", "author": "jasonwarren"}
            ],
            ids=["fe1", "be1", "be2"]
        )
        print(f"      ✓ Documents added")

        # 3. Query
        print(f"  [3/5] Querying for 'authentication'...")
        results = query_collection(
            collection,
            query_text="authentication",
            n_results=2
        )
        print(f"      ✓ Found {len(results['documents'][0])} results")
        assert len(results["documents"][0]) == 2

        # 4. Get stats
        print(f"  [4/5] Getting collection stats...")
        stats = get_collection_stats(collection)
        print(f"      ✓ Collection has {stats['count']} documents")
        assert stats["count"] == 3

        # 5. Delete collection
        print(f"  [5/5] Deleting collection...")
        delete_collection(test_client, "workflow_test")
        print(f"      ✓ Collection deleted")

        # Verify deletion
        with pytest.raises(Exception):
            test_client.get_collection("workflow_test")
        print(f"  ✓ Workflow complete!")


if __name__ == "__main__":
    """
    Run tests directly with: python -m backend.test_vector_db
    Or use pytest: pytest backend/test_vector_db.py -v
    """
    pytest.main([__file__, "-v"])
