"""Langchain-based model abstraction for querying LLMs."""

import asyncio
from typing import List, Dict, Optional, Any

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from .config import ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY


def _get_model_instance(model_config: Dict[str, str]) -> Any:
    """
    Create Langchain model instance from config.

    Args:
        model_config: Dict with 'provider' and 'model' keys

    Returns:
        Initialized Langchain chat model instance

    Raises:
        ValueError: If provider is not supported
    """
    provider = model_config.get("provider")
    model_name = model_config.get("model")

    if provider == "anthropic":
        return ChatAnthropic(model=model_name, anthropic_api_key=ANTHROPIC_API_KEY)
    elif provider == "openai":
        return ChatOpenAI(model=model_name, openai_api_key=OPENAI_API_KEY)
    # elif provider == "google":
    #     return ChatGoogleGenerativeAI(model=model_name, google_api_key=GOOGLE_API_KEY)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _convert_messages_to_langchain(messages: List[Dict[str, str]]) -> List:
    """
    Convert message dicts to Langchain message objects.

    Args:
        messages: List of dicts with 'role' and 'content' keys

    Returns:
        List of Langchain message objects (SystemMessage, HumanMessage, AIMessage)
    """
    langchain_messages = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "system":
            langchain_messages.append(SystemMessage(content=content))
        elif role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))
        else:
            # Default to HumanMessage for unknown roles
            langchain_messages.append(HumanMessage(content=content))

    return langchain_messages


async def query_model(
    model_config: Dict[str, str],
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    timeout: float = 120.0
) -> Optional[Dict[str, str]]:
    """
    Query a single model via Langchain.

    Args:
        model_config: Dict with 'provider' and 'model' keys
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0.0 to 1.0)
        timeout: Request timeout in seconds (currently not enforced)

    Returns:
        Response dict with 'content' key, or None if failed
    """
    try:
        # Get the appropriate model instance
        model = _get_model_instance(model_config)

        # Convert messages to Langchain format
        langchain_messages = _convert_messages_to_langchain(messages)

        # Query the model asynchronously
        response = await model.ainvoke(langchain_messages, config={"temperature": temperature})

        # Extract text content from AIMessage response
        return {
            'content': response.content,
            'reasoning_details': None  # Langchain doesn't provide reasoning_details by default
        }

    except Exception as e:
        # Graceful error handling: log and return None
        model_id = f"{model_config.get('provider')}/{model_config.get('model')}"
        print(f"Error querying model {model_id}: {e}")
        return None


async def query_models_parallel(
    model_configs: List[Dict[str, str]],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Query multiple models in parallel via Langchain.

    Args:
        model_configs: List of model config dicts with 'provider' and 'model' keys
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier string to response dict (or None if failed)
        Model identifier format: "provider/model"
    """
    # Create tasks for all models
    tasks = [query_model(config, messages) for config in model_configs]

    # Wait for all to complete (return_exceptions=True for graceful degradation)
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Map model configs to their responses
    results = {}
    for config, response in zip(model_configs, responses):
        # Create readable model identifier
        model_id = f"{config['provider']}/{config['model']}"

        # Handle exceptions from gather
        if isinstance(response, Exception):
            print(f"Exception for model {model_id}: {response}")
            results[model_id] = None
        else:
            results[model_id] = response

    return results
