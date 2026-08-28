"""
Universal OpenAI API Compatible Client for AoE2 LLM Coaching:
Supports llama.cpp server, Ollama, vLLM, LocalAI, LM Studio, OpenAI, and OpenRouter endpoints.
"""

import json
import re
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
import requests

from aoe2_coach.explanation.schemas import LLMConfig

logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Robustly extract and parse a JSON object from text that may contain markdown code fences,
    preambles, or trailing commentary.
    """
    cleaned = text.strip()

    # 1. Try direct parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Try stripping markdown code block: ```json ... ``` or ``` ... ```
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Try finding outer balanced braces { ... }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse valid JSON object from LLM response:\n{text}")


class OpenAICompatibleLLMClient:
    """
    Client for any OpenAI API compatible LLM server (llama.cpp, Ollama, vLLM, OpenAI, etc.).
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config_override: Optional[LLMConfig] = None,
    ) -> Tuple[Dict[str, Any], str, float]:
        """
        Execute synchronous chat completion request.
        Returns (parsed_json_dict, raw_completion_text, latency_ms).
        """
        cfg = config_override or self.config
        endpoint = f"{cfg.base_url.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.api_key}",
        }

        payload: Dict[str, Any] = {
            "model": cfg.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
        }

        if cfg.response_format:
            payload["response_format"] = {"type": cfg.response_format}

        start_time = time.perf_counter()
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=cfg.timeout_sec,
            )
            response.raise_for_status()
            res_data = response.json()
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            raw_text = res_data["choices"][0]["message"]["content"]
            parsed_json = extract_json_from_text(raw_text)
            return parsed_json, raw_text, latency_ms

        except requests.exceptions.RequestException as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.warning(f"LLM API request failed ({endpoint}): {e}")
            raise RuntimeError(f"LLM API connection error: {e}") from e

    async def async_generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config_override: Optional[LLMConfig] = None,
    ) -> Tuple[Dict[str, Any], str, float]:
        """
        Asynchronously execute chat completion request in thread pool without blocking event loop.
        """
        return await asyncio.to_thread(
            self.generate,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config_override=config_override,
        )
