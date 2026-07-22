import httpx
from typing import List
from app.core.config import settings

class EmbeddingGenerator:
    """Async Client wrapper for Google text-embedding-004 API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_EMBEDDING_MODEL
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent"

    async def generate_embedding(self, text_chunk: str) -> List[float]:
        """Generates a 768-dimensional embedding vector for a text chunk."""
        # Fallback vector for local dev when API key is not set
        if not self.api_key or self.api_key == "mock_gemini_api_key":
            return self._generate_mock_vector(text_chunk)

        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "model": f"models/{self.model}",
            "content": {
                "parts": [{"text": text_chunk}]
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                values = response.json().get("embedding", {}).get("values", [])
                if len(values) == 768:
                    return values

            print(f"Embedding API Error ({response.status_code}): {response.text}")
            return self._generate_mock_vector(text_chunk)

    def _generate_mock_vector(self, text_chunk: str) -> List[float]:
        """Deterministic 768-dimensional mock vector for testing without external API key."""
        seed = sum(ord(c) for c in text_chunk[:20]) % 100
        return [(seed + i) / 1000.0 for i in range(768)]
