import os
from .base import LLMProvider, EmbeddingProvider
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiProvider(LLMProvider, EmbeddingProvider):
    def __init__(self, api_key=None, llm_model="gemini-2.5-flash", embed_model="gemini-embedding-2"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.llm_model = llm_model
        self.embed_model = embed_model
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            
    def call_json(self, prompt: str) -> dict:
        if not genai or not self.api_key:
            raise Exception("Gemini not configured.")
        import json
        model = genai.GenerativeModel(self.llm_model)
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        return json.loads(text.strip())
        
    def get_embedding(self, text: str) -> list:
        if not genai or not self.api_key:
            return []
        emb_res = genai.embed_content(
            model=self.embed_model,
            content=text
        )
        return emb_res["embedding"] if isinstance(emb_res, dict) else emb_res.get("embedding")
