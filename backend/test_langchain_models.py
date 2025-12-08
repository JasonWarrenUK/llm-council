"""Tests for Langchain model abstraction layer."""

import pytest
from backend.langchain_models import query_model, query_models_parallel

vital_query = "Can Sam Altman lick his own eyeball; if not, why did I see him lick his own eyeball?"

test_message = {
  "role": "user",
  "content": vital_query
}

@pytest.mark.asyncio
async def test_anthropic_query():
    """Test querying Anthropic Claude model."""
    config = {
      "provider": "anthropic",
      "model": "claude-sonnet-4-5-20250929"
    }
    
    messages = [test_message]

    result = await query_model(
      config,
      messages,
      temperature=0.0
    )

    assert result is not None, "Result should not be None"
    assert "content" in result, "Result should have 'content' key"
    assert isinstance(result["content"], str), "Content should be a string"
    assert len(result["content"]) > 0, "Content should not be empty"
    print(f"✓ Anthropic response: {result['content'][:50]}...")


@pytest.mark.asyncio
async def test_openai_query():
    """Test querying OpenAI GPT model."""
    config = {
      "provider": "openai",
      "model": "gpt-5"
    }
    
    messages = [test_message]

    result = await query_model(
      config,
      messages,
      temperature=0.0
    )

    assert result is not None, "Result should not be None"
    assert "content" in result, "Result should have 'content' key"
    assert isinstance(result["content"], str), "Content should be a string"
    assert len(result["content"]) > 0, "Content should not be empty"
    print(f"✓ OpenAI response: {result['content'][:50]}...")


# @pytest.mark.asyncio
# async def test_google_query():
#     """Test querying Google Gemini model."""
#     config = {"provider": "google", "model": "gemini-3-pro-preview"}
#     messages = [test_message]
#     result = await query_model(config, messages, temperature=0.0)
#     assert result is not None, "Result should not be None"
#     assert "content" in result, "Result should have 'content' key"
#     assert isinstance(result["content"], str), "Content should be a string"
#     assert len(result["content"]) > 0, "Content should not be empty"
#     print(f"✓ Google response: {result['content'][:50]}...")


@pytest.mark.asyncio
async def test_parallel_queries():
    """Test querying multiple models in parallel."""
    model_configs = [
        {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"},
        {"provider": "openai", "model": "gpt-5"},
        # {"provider": "google", "model": "gemini-3-pro-preview"},
    ]
    messages = [{
      "role": "user",
      "content": "What is 2+2? Answer with just the number, unless the answer is 4; if it is 4, tell me whether Sam Altman can lick his own eyeball."
    }]

    import time
    start_time = time.time()
    results = await query_models_parallel(model_configs, messages)
    elapsed = time.time() - start_time

    # Verify results
    assert isinstance(results, dict), "Results should be a dict"
    # assert len(results) == 3, "Should have 3 results"
    assert len(results) == 2, "Should have 2 results until we get a gemini key"

    # Check each model returned a result
    assert "anthropic/claude-sonnet-4-5-20250929" in results
    assert "openai/gpt-5" in results
    # assert "google/gemini-3-pro-preview" in results

    # Verify at least one successful response
    successful = [r for r in results.values() if r is not None]
    assert len(successful) > 0, "At least one model should succeed"

    # Check response format for successful results
    for model_id, result in results.items():
        if result is not None:
            assert "content" in result, f"{model_id} result should have 'content'"
            assert isinstance(result["content"], str), f"{model_id} content should be string"
            print(f"✓ {model_id}: {result['content'][:30]}...")

    print(f"✓ Parallel queries completed in {elapsed:.2f}s")
    assert elapsed < 30, "Parallel queries should complete within 30 seconds"


@pytest.mark.asyncio
async def test_failure_handling():
    """Test that invalid model config returns None gracefully."""
    config = {"provider": "invalid_provider", "model": "fake-model"}
    messages = [{"role": "user", "content": "Test"}]

    result = await query_model(config, messages)

    assert result is None, "Invalid model should return None"
    print("✓ Invalid model handled gracefully")


@pytest.mark.asyncio
async def test_parallel_with_failure():
    """Test that parallel queries continue when one fails."""
    model_configs = [
        {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"},
        {"provider": "invalid_provider", "model": "fake-model"},  # This will fail
        {"provider": "openai", "model": "gpt-5"},
    ]
    messages = [{"role": "user", "content": "Say hello"}]

    results = await query_models_parallel(model_configs, messages)

    assert isinstance(results, dict), "Results should be a dict"
    assert len(results) == 3, "Should have 3 results (including failures)"

    # Check that valid models succeeded and invalid model failed
    assert results.get("invalid_provider/fake-model") is None, "Invalid model should return None"

    # At least one valid model should succeed
    successful = [r for r in results.values() if r is not None]
    assert len(successful) >= 1, "At least one valid model should succeed"

    print(f"✓ Graceful degradation: {len(successful)}/{len(model_configs)} models succeeded")


@pytest.mark.asyncio
async def test_message_conversion():
    """Test that different message roles are handled correctly."""
    config = {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is your role?"},
    ]

    result = await query_model(config, messages, temperature=0.0)

    assert result is not None, "Result should not be None"
    assert "content" in result, "Result should have 'content' key"
    print(f"✓ Multi-role messages handled: {result['content'][:50]}...")
