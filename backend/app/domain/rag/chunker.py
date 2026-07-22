from typing import List

class SemanticChunker:
    """Splits plain text into overlapping semantic chunks optimized for embedding."""

    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """Splits raw text into a list of chunk strings."""
        cleaned_text = " ".join(text.split())
        if not cleaned_text:
            return []

        words = cleaned_text.split()
        if len(words) <= self.chunk_size:
            return [cleaned_text]

        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + self.chunk_size])
            chunks.append(chunk)
            i += self.chunk_size - self.overlap
        return chunks
