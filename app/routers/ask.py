from fastapi import APIRouter, HTTPException

from app.schemas import AskRequest, AskResponse
from app.vector_store import get_vector_store


router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse)
def ask_question(request: AskRequest):
    """根据语义相似度，从 Chroma 向量库检索医疗健康资料。"""
    try:
        vector_store = get_vector_store()
        matches = vector_store.similarity_search_with_relevance_scores(
            request.question,
            k=3,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="知识库暂时不可用，请确认已执行 /knowledge/rebuild",
        ) from error

    relevant_documents = [
        document
        for document, score in matches
        if score >= 0.3
    ]

    if not relevant_documents:
        return AskResponse(
            question=request.question,
            answer="知识库中没有找到足够相关的内容。建议换一种更具体的说法。",
            source="chroma-vector-search:no-match",
        )

    answer = "\n\n".join(
        document.page_content
        for document in relevant_documents
    )
    answer += "\n\n提醒：以上是知识库中的通用信息，不代替医生诊断或处方。"

    return AskResponse(
        question=request.question,
        answer=answer,
        source="chroma-vector-search",
    )
