import os

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlmodel import Session, select

from app.database import get_session
from app.models import ChatMessage
from app.schemas import AskRequest, AskResponse
from app.vector_store import get_knowledge_status, get_vector_store


router = APIRouter(prefix="/ask", tags=["ask"])


def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4.1-mini"),
        temperature=0,
    )


def save_message(session: Session, conversation_id: str, role: str, content: str):
    session.add(
        ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
    )


@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    session: Session = Depends(get_session),
):
    """根据语义相似度，从 Chroma 向量库检索医疗健康资料。"""
    history = session.exec(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == request.conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    ).all()
    history.reverse()
    history_text = "\n".join(
        f"{message.role}: {message.content}"
        for message in history
    ) or "暂无历史对话"
    retrieval_query = (
        f"{history_text}\n当前问题：{request.question}"
        if history
        else request.question
    )

    knowledge_status = get_knowledge_status(session)
    if not knowledge_status["is_current"]:
        raise HTTPException(
            status_code=409,
            detail="知识库已过期，请先执行 POST /knowledge/rebuild",
        )

    try:
        vector_store = get_vector_store()
        matches = vector_store.similarity_search_with_relevance_scores(
            retrieval_query,
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
        answer = "知识库中没有找到足够相关的内容。建议换一种更具体的说法。"
        save_message(session, request.conversation_id, "user", request.question)
        save_message(session, request.conversation_id, "assistant", answer)
        session.commit()
        return AskResponse(
            question=request.question,
            answer=answer,
            source="chroma-vector-search:no-match",
            conversation_id=request.conversation_id,
            references=[],
        )

    context = "\n\n".join(
        document.page_content
        for document in relevant_documents
    )
    references = [
        document.metadata.get("name", "未命名资料")
        for document in relevant_documents
    ]

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
                "历史对话：\n{history}\n\n"
                "参考资料：\n{context}\n\n用户问题：{question}",
            ),
        ]
    )

    try:
        response = get_chat_model().invoke(
            prompt.format_messages(
                context=context,
                history=history_text,
                question=request.question,
            )
        )
        answer = str(response.content)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="模型暂时不可用，请检查 CHAT_MODEL 和 API 配置",
        ) from error

    save_message(session, request.conversation_id, "user", request.question)
    save_message(session, request.conversation_id, "assistant", answer)
    session.commit()

    return AskResponse(
        question=request.question,
        answer=answer,
        source="chroma-retrieval-openai-generation",
        conversation_id=request.conversation_id,
        references=references,
    )
