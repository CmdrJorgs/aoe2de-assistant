"""
Unit tests for OpenAICompatibleLLMClient and JSON extraction utilities.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
import requests

from aoe2_coach.explanation.schemas import LLMConfig
from aoe2_coach.explanation.client import (
    OpenAICompatibleLLMClient,
    extract_json_from_text,
)


def test_extract_json_pure_json():
    text = '{"primary_directive": "CASTLE AGE KNIGHT PUSH", "status": "ok"}'
    data = extract_json_from_text(text)
    assert data["primary_directive"] == "CASTLE AGE KNIGHT PUSH"
    assert data["status"] == "ok"


def test_extract_json_markdown_block():
    text = """
    Here is the coaching advice:
    ```json
    {
        "primary_directive": "FEUDAL ARCHER RUSH",
        "score": 95
    }
    ```
    Good luck!
    """
    data = extract_json_from_text(text)
    assert data["primary_directive"] == "FEUDAL ARCHER RUSH"
    assert data["score"] == 95


def test_extract_json_raw_braces():
    text = """
    Some preliminary text...
    {
        "directive": "DEFEND NOW",
        "units": ["spearman", "skirmisher"]
    }
    Hope this helps!
    """
    data = extract_json_from_text(text)
    assert data["directive"] == "DEFEND NOW"
    assert "spearman" in data["units"]


def test_extract_json_invalid_raises():
    with pytest.raises(ValueError, match="Could not parse valid JSON"):
        extract_json_from_text("This is just plain conversational text without any JSON.")


@patch("requests.post")
def test_openai_client_generate(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "primary_directive": "CASTLE CAVALRY PUSH",
                        "coach_summary": "Produce knights from 3 stables",
                    })
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    config = LLMConfig(base_url="http://localhost:11434/v1", model="llama3.2")
    client = OpenAICompatibleLLMClient(config)

    parsed, raw, latency = client.generate("system prompt", "user prompt")
    assert parsed["primary_directive"] == "CASTLE CAVALRY PUSH"
    assert latency >= 0.0

    # Verify request payload
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:11434/v1/chat/completions"
    assert kwargs["json"]["model"] == "llama3.2"


@pytest.mark.asyncio
@patch("requests.post")
async def test_openai_client_async_generate(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"primary_directive": "FAST IMPERIAL", "target": "trebuchet"}'
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    client = OpenAICompatibleLLMClient()
    parsed, raw, latency = await client.async_generate("sys", "usr")
    assert parsed["primary_directive"] == "FAST IMPERIAL"
    assert parsed["target"] == "trebuchet"


@patch("requests.post")
def test_openai_client_error_handling(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect to local server")

    client = OpenAICompatibleLLMClient()
    with pytest.raises(RuntimeError, match="LLM API connection error"):
        client.generate("sys", "usr")
