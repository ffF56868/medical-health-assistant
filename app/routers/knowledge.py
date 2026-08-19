from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas import KnowledgeRebuildResponse, KnowledgeStatusResponse
from app.vector_store import get_knowledge_status, rebuild_vector_store


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/status", response_model=KnowledgeStatusResponse)
def get_status(session: Session = Depends(get_session)):
    return get_knowledge_status(session)


@router.post("/rebuild", response_model=KnowledgeRebuildResponse)
def rebuild_knowledge(session: Session = Depends(get_session)):
    document_count, chunk_count = rebuild_vector_store(session)
    return KnowledgeRebuildResponse(
        message="知识库向量重建完成",
        document_count=document_count,
        chunk_count=chunk_count,
    )
