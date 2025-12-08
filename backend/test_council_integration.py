"""Integration tests for full council flow."""

import pytest
from backend.council import run_full_council


@pytest.mark.asyncio
async def test_full_council_flow():
    """Test the complete 3-stage council process end-to-end."""
    user_query = "What is the capital of France?"

    # Run the full council
    stage1_results, stage2_results, stage3_result, metadata = await run_full_council(user_query)

    # Verify Stage 1
    assert isinstance(stage1_results, list), "Stage 1 should return a list"
    assert len(stage1_results) > 0, "Stage 1 should have at least one response"

    for result in stage1_results:
        assert "model" in result, "Each Stage 1 result should have 'model' key"
        assert "response" in result, "Each Stage 1 result should have 'response' key"
        assert isinstance(result["response"], str), "Response should be a string"
        assert len(result["response"]) > 0, "Response should not be empty"

    print(f"✓ Stage 1: {len(stage1_results)} models responded")
    for result in stage1_results:
        print(f"  - {result['model']}: {result['response'][:50]}...")

    # Verify Stage 2
    assert isinstance(stage2_results, list), "Stage 2 should return a list"
    assert len(stage2_results) > 0, "Stage 2 should have at least one ranking"

    for result in stage2_results:
        assert "model" in result, "Each Stage 2 result should have 'model' key"
        assert "ranking" in result, "Each Stage 2 result should have 'ranking' key"
        assert "parsed_ranking" in result, "Each Stage 2 result should have 'parsed_ranking' key"
        assert isinstance(result["ranking"], str), "Ranking should be a string"
        assert isinstance(result["parsed_ranking"], list), "Parsed ranking should be a list"

    print(f"✓ Stage 2: {len(stage2_results)} rankings collected")
    for result in stage2_results:
        print(f"  - {result['model']}: parsed {len(result['parsed_ranking'])} responses")

    # Verify Stage 3
    assert isinstance(stage3_result, dict), "Stage 3 should return a dict"
    assert "model" in stage3_result, "Stage 3 result should have 'model' key"
    assert "response" in stage3_result, "Stage 3 result should have 'response' key"
    assert isinstance(stage3_result["response"], str), "Stage 3 response should be a string"
    assert len(stage3_result["response"]) > 0, "Stage 3 response should not be empty"

    print(f"✓ Stage 3: Chairman ({stage3_result['model']}) synthesized response")
    print(f"  - {stage3_result['response'][:100]}...")

    # Verify metadata
    assert isinstance(metadata, dict), "Metadata should be a dict"
    assert "label_to_model" in metadata, "Metadata should have 'label_to_model'"
    assert "aggregate_rankings" in metadata, "Metadata should have 'aggregate_rankings'"

    assert isinstance(metadata["label_to_model"], dict), "label_to_model should be a dict"
    assert isinstance(metadata["aggregate_rankings"], list), "aggregate_rankings should be a list"

    print(f"✓ Metadata complete:")
    print(f"  - {len(metadata['label_to_model'])} anonymized labels")
    print(f"  - {len(metadata['aggregate_rankings'])} aggregate rankings")

    # Verify aggregate rankings structure
    for ranking in metadata["aggregate_rankings"]:
        assert "model" in ranking, "Each aggregate ranking should have 'model'"
        assert "average_rank" in ranking, "Each aggregate ranking should have 'average_rank'"
        assert "rankings_count" in ranking, "Each aggregate ranking should have 'rankings_count'"
        print(f"  - {ranking['model']}: avg rank {ranking['average_rank']} ({ranking['rankings_count']} votes)")


@pytest.mark.asyncio
async def test_council_with_complex_query():
    """Test council with a more complex, open-ended query."""
    user_query = "Explain the concept of quantum entanglement in simple terms."

    stage1_results, stage2_results, stage3_result, metadata = await run_full_council(user_query)

    # Basic validation
    assert len(stage1_results) > 0, "Should have Stage 1 responses"
    assert len(stage2_results) > 0, "Should have Stage 2 rankings"
    assert stage3_result["response"], "Should have Stage 3 synthesis"
    assert metadata["label_to_model"], "Should have label mapping"
    assert metadata["aggregate_rankings"], "Should have aggregate rankings"

    print(f"✓ Complex query handled successfully")
    print(f"  - {len(stage1_results)} responses, {len(stage2_results)} rankings")
    print(f"  - Final answer length: {len(stage3_result['response'])} characters")
