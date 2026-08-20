from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import Condition, Drug, KnowledgeDocument
from app.schemas import (
    KnowledgeRebuildResponse,
    KnowledgeSearchItem,
    KnowledgeSearchResponse,
    KnowledgeStatusResponse,
)
from app.source_metadata import needs_source_review
from app.vector_store import get_knowledge_status, rebuild_vector_store


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def find_matching_fields(query: str, fields: dict[str, str]) -> list[str]:
    normalized_query = query.casefold()
    return [
        field_name
        for field_name, value in fields.items()
        if normalized_query in value.casefold()
    ]


def build_excerpt(query: str, text: str, max_length: int = 240) -> str:
    normalized_text = text.casefold()
    match_start = normalized_text.find(query.casefold())
    if match_start == -1 or len(text) <= max_length:
        return text[:max_length]

    start = max(0, match_start - 80)
    end = min(len(text), start + max_length)
    prefix = "..." if start else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{text[start:end]}{suffix}"


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


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    q: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
): 
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="搜索关键词不能为空")

    results: list[KnowledgeSearchItem] = []

    for condition in session.exec(select(Condition).order_by(Condition.id)).all():
        fields = {
            "名称": condition.name,
            "症状": condition.symptoms,
            "处理建议": condition.treatment,
        }
        matched_fields = find_matching_fields(query, fields)
        if matched_fields:
            results.append(
                KnowledgeSearchItem(
                    type="condition",
                    record_id=condition.id,
                    title=condition.name,
                    source=condition.source,
                    source_tier=condition.source_tier,
                    updated_at=condition.updated_at,
                    needs_review=needs_source_review(
                        condition.source_tier,
                        condition.updated_at,
                    ),
                    matched_fields=matched_fields,
                    excerpt=build_excerpt(query, "\n".join(fields.values())),
                )
            )

    for drug in session.exec(select(Drug).order_by(Drug.id)).all():
        fields = {
            "名称": drug.name,
            "作用": drug.effects,
            "使用说明": drug.instructions,
        }
        matched_fields = find_matching_fields(query, fields)
        if matched_fields:
            results.append(
                KnowledgeSearchItem(
                    type="drug",
                    record_id=drug.id,
                    title=drug.name,
                    source=drug.source,
                    source_tier=drug.source_tier,
                    updated_at=drug.updated_at,
                    needs_review=needs_source_review(
                        drug.source_tier,
                        drug.updated_at,
                    ),
                    matched_fields=matched_fields,
                    excerpt=build_excerpt(query, "\n".join(fields.values())),
                )
            )

    for document in session.exec(
        select(KnowledgeDocument).order_by(KnowledgeDocument.id)
    ).all():
        fields = {
            "标题": document.title,
            "内容": document.content,
            "来源": document.source,
        }
        matched_fields = find_matching_fields(query, fields)
        if matched_fields:
            results.append(
                KnowledgeSearchItem(
                    type="document",
                    record_id=document.id,
                    title=document.title,
                    source=document.source,
                    source_tier=document.source_tier,
                    updated_at=document.updated_at,
                    needs_review=needs_source_review(
                        document.source_tier,
                        document.updated_at,
                    ),
                    matched_fields=matched_fields,
                    excerpt=build_excerpt(query, "\n".join(fields.values())),
                )
            )

    limited_results = results[:limit]
    return KnowledgeSearchResponse(
        query=query,
        total_count=len(results),
        results=limited_results,
    )
