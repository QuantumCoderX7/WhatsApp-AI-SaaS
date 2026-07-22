from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from datetime import datetime

from app.api.dependencies import get_db_session, get_current_user, get_current_tenant_id
from app.domain.tenant.models import User
from app.domain.rag.models import KnowledgeDocument, KnowledgeChunk
from app.domain.rag.parser import DocumentParser
from app.domain.rag.chunker import SemanticChunker
from app.domain.rag.embedder import EmbeddingGenerator

router = APIRouter()

class DocumentOut(BaseModel):
    id: UUID
    tenant_id: UUID
    filename: str
    mime_type: str
    chunk_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Uploads a PDF, DOCX, or TXT document, parses, chunks, and generates pgvector embeddings."""
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 1. Create Document Record
    doc = KnowledgeDocument(
        tenant_id=current_user.tenant_id,
        filename=file.filename or "uploaded_document.txt",
        file_path=f"storage/{current_user.tenant_id}/{file.filename}",
        mime_type=file.content_type or "text/plain",
        status="PROCESSING"
    )
    db.add(doc)
    await db.flush()

    # 2. Parse Text
    text_content = DocumentParser.parse(doc.filename, content_bytes, doc.mime_type)
    if not text_content.strip():
        doc.status = "FAILED"
        await db.commit()
        raise HTTPException(status_code=400, detail="Could not extract text content from file.")

    # 3. Chunk Text
    chunker = SemanticChunker(chunk_size=400, overlap=50)
    chunks_text = chunker.split_text(text_content)

    # 4. Generate Embeddings & Save Vector Chunks
    embedder = EmbeddingGenerator()
    for idx, chunk_str in enumerate(chunks_text):
        vector = await embedder.generate_embedding(chunk_str)
        chunk_model = KnowledgeChunk(
            tenant_id=current_user.tenant_id,
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_str,
            embedding=vector,
            metadata_json={"filename": doc.filename, "chunk_index": idx}
        )
        db.add(chunk_model)

    doc.chunk_count = len(chunks_text)
    doc.status = "READY"
    await db.commit()
    await db.refresh(doc)

    return doc

@router.get("/documents", response_model=List[DocumentOut])
async def list_documents(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists knowledge documents uploaded for active tenant."""
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.tenant_id == tenant_id).order_by(KnowledgeDocument.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Deletes document and cascades deletion of vector chunks."""
    stmt = select(KnowledgeDocument).where(
        KnowledgeDocument.id == document_id,
        KnowledgeDocument.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(doc)
    await db.commit()
    return None
