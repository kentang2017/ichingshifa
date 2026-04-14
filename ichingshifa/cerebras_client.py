# -*- coding: utf-8 -*-
"""Cerebras AI client wrapper for ichingshifa."""

from cerebras.cloud.sdk import Cerebras

DEFAULT_MODEL = "qwen-3-235b-a22b-instruct-2507"

CEREBRAS_MODEL_OPTIONS = [
    "qwen-3-235b-a22b-instruct-2507",
    "deepseek-r1-distill-llama-70b",
    "llama-4-scout-17b-16e-instruct",
    "llama3.3-70b",
    "llama3.1-8b",
]

CEREBRAS_MODEL_DESCRIPTIONS = {
    "qwen-3-235b-a22b-instruct-2507": "Qwen 3 235B (推薦)",
    "deepseek-r1-distill-llama-70b": "DeepSeek R1 Distill 70B",
    "llama-4-scout-17b-16e-instruct": "Llama 4 Scout 17B",
    "llama3.3-70b": "Llama 3.3 70B",
    "llama3.1-8b": "Llama 3.1 8B",
}


class CerebrasClient:
    """Thin wrapper around the Cerebras SDK for chat completions."""

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("CerebrasClient must be initialized with an API key.")
        self.client = Cerebras(api_key=api_key)

    def get_chat_completion(self, messages, model=DEFAULT_MODEL, **kwargs):
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            **kwargs,
        )
