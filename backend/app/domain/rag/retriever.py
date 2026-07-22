from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.rag.models import KnowledgeChunk
from app.domain.rag.embedder import EmbeddingGenerator
from app.core.config import settings

class RAGRetriever:
    """Multi-tenant hybrid vector search engine using pgvector HNSW distance queries."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.embedder = EmbeddingGenerator()

    async def search_relevant_chunks(
        self,
        tenant_id: UUID,
        query: str,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Performs tenant-isolated vector similarity search."""
        query_vector = await self.embedder.generate_embedding(query)

        is_sqlite = settings.DATABASE_URL.startswith("sqlite")
        
        if is_sqlite:
            # Fallback text query for SQLite local dev mode
            stmt = (
                select(KnowledgeChunk.content, KnowledgeChunk.metadata_json)
                .where(KnowledgeChunk.tenant_id == tenant_id)
                .limit(top_k)
            )
        else:
            # pgvector Cosine Distance Query hard-filtered by tenant_id
            stmt = (
                select(KnowledgeChunk.content, KnowledgeChunk.metadata_json)
                .where(KnowledgeChunk.tenant_id == tenant_id)
                .order_by(KnowledgeChunk.embedding.cosine_distance(query_vector))
                .limit(top_k)
            )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "content": row[0],
                "metadata": row[1]
            }
            for row in rows
        ]
