import requests
import json
import re
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, endpoint="http://localhost:11434/api/generate", model="qwen2.5:3b"):
        self.endpoint = endpoint
        self.model = model

    def call_json(self, prompt: str) -> dict:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1}
        }
        res = requests.post(self.endpoint, json=payload, timeout=60)
        res.raise_for_status()
        text = res.json().get("response", "")
        # Robust JSON extraction
        match = re.search(r'\{.*\}', text.replace('\n', ''))
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
