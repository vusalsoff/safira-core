from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def call_json(self, prompt: str) -> dict:
        """Call the LLM and return a JSON dictionary."""
        pass

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> list:
        """Generate an embedding for the given text."""
        pass
