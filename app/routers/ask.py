import os

from fastapi import APIRouter, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.schemas import AskRequest, AskResponse
from app.vector_store import get_vector_store


router = APIRouter(prefix="/ask", tags=["ask"])


def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4.1-mini"),
        temperature=0,
    )


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

    context = "\n\n".join(
        document.page_content
        for document in relevant_documents
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是医疗健康知识库助手。只能依据参考资料回答，"
                "不能编造资料中没有的诊断、药物剂量或治疗方案。"
                "如果资料不足，要明确说资料不足，并建议咨询医生。"
                "回答最后必须提醒：内容仅供健康信息参考，不代替医生诊断或处方。",
            ),
            (
                "human",
                "参考资料：\n{context}\n\n用户问题：{question}",
            ),
        ]
    )

    try:
        response = get_chat_model().invoke(
            prompt.format_messages(
                context=context,
                question=request.question,
            )
        )
        answer = str(response.content)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="模型暂时不可用，请检查 CHAT_MODEL 和 API 配置",
        ) from error

    return AskResponse(
        question=request.question,
        answer=answer,
        source="chroma-retrieval-openai-generation",
    )
