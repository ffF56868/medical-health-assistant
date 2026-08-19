import os
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlmodel import Session, select

from app.database import get_session
from app.models import ChatMessage
from app.schemas import AskRequest, AskResponse
from app.vector_store import get_knowledge_status, get_vector_store


router = APIRouter(prefix="/ask", tags=["ask"])
# Multi-symptom questions often spread their similarity across several records.
# Scores below 0.2 have been checked to be unrelated to this knowledge base.
MIN_RELEVANCE_SCORE = 0.2
URGENT_WARNING_KEYWORDS = (
    "呼吸困难",
    "持续胸痛",
    "加重的胸痛",
    "意识改变",
    "抽搐",
    "单侧肢体无力",
    "言语含糊",
    "严重过敏",
    "头痛突然剧烈",
)


def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4.1-mini"),
        temperature=0,
    )


def save_message(
    session: Session,
    conversation_id: str,
    role: str,
    content: str,
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    session.add(message)
    return message


def get_urgent_warning_response(question: str) -> str | None:
    matched_keywords = [
        keyword
        for keyword in URGENT_WARNING_KEYWORDS
        if keyword in question
    ]
    if not matched_keywords:
        return None

    keywords_text = "、".join(matched_keywords)
    return (
        f"你的描述包含需要及时就医的警示词：{keywords_text}。"
        "这不代表任何具体诊断，但如果这些症状正在发生、持续或加重，"
        "请立即寻求紧急医疗帮助或联系当地急救服务。"
        "不要依赖本系统的在线回答来延误线下评估。\n\n"
        "内容仅供健康信息参考，不代替医生诊断或处方。"
    )


def format_sse_event(event: str, payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False)
    return f"event: {event}\ndata: {data}\n\n"


def get_stream_text(chunk: object) -> str:
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )
    return str(content)


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

    urgent_answer = get_urgent_warning_response(request.question)
    if urgent_answer:
        save_message(session, request.conversation_id, "user", request.question)
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            urgent_answer,
        )
        session.commit()
        session.refresh(assistant_message)
        return AskResponse(
            question=request.question,
            answer=urgent_answer,
            source="safety-keyword-guard",
            conversation_id=request.conversation_id,
            assistant_message_id=assistant_message.id,
            references=[
                {
                    "name": "需要及时就医的警示信号",
                    "type": "safety_guard",
                    "source": "系统安全规则",
                    "excerpt": (
                        "呼吸困难、持续或加重的胸痛、意识改变、抽搐、"
                        "单侧肢体无力、言语含糊或严重过敏表现时，"
                        "应立即寻求紧急医疗帮助。"
                    ),
                    "relevance_score": 1.0,
                }
            ],
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
            k=8,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="知识库暂时不可用，请确认已执行 /knowledge/rebuild",
        ) from error

    # Each source may have several chunks. Keep only its best matching chunk.
    best_matches: dict[tuple[str, str], tuple[object, float]] = {}
    for document, score in matches:
        if score < MIN_RELEVANCE_SCORE:
            continue
        source_key = (
            str(document.metadata.get("type", "unknown")),
            str(document.metadata.get("record_id", document.metadata.get("name"))),
        )
        previous_match = best_matches.get(source_key)
        if previous_match is None or score > previous_match[1]:
            best_matches[source_key] = (document, score)

    relevant_matches = sorted(
        best_matches.values(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    relevant_documents = [document for document, _ in relevant_matches]

    if not relevant_documents:
        answer = "知识库中没有找到足够相关的内容。建议换一种更具体的说法。"
        save_message(session, request.conversation_id, "user", request.question)
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            answer,
        )
        session.commit()
        session.refresh(assistant_message)
        return AskResponse(
            question=request.question,
            answer=answer,
            source="chroma-vector-search:no-match",
            conversation_id=request.conversation_id,
            assistant_message_id=assistant_message.id,
            references=[],
        )

    context = "\n\n".join(
        document.page_content
        for document in relevant_documents
    )
    references = [
        {
            "name": document.metadata.get("name", "未命名资料"),
            "type": document.metadata.get("type", "unknown"),
            "source": document.metadata.get("source"),
            "excerpt": document.page_content.replace("\n", " ")[:180],
            "relevance_score": round(score, 3),
        }
        for document, score in relevant_matches
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是医疗健康知识库助手。只能依据参考资料回答，"
                "不能编造资料中没有的内容。不得根据用户症状判断、推测或声明"
                "用户可能患有任何疾病或感染，也不要使用‘可能是’‘像是’等诊断性表达。"
                "绝不能说用户的症状‘符合’‘相符’‘指向’任何疾病。"
                "当用户描述症状时，必须严格按三个部分回答："
                "一、资料内容：仅客观列出参考资料中各病症的常见症状；"
                "二、通用健康建议：只给资料中已有的休息、补水或观察建议；"
                "三、就医提示：只列出资料中的警示信号或建议咨询医生的情况。"
                "第一部分不得把用户症状与任何病症建立联系。"
                "不能提供药物剂量或治疗方案。"
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
    assistant_message = save_message(
        session,
        request.conversation_id,
        "assistant",
        answer,
    )
    session.commit()
    session.refresh(assistant_message)

    return AskResponse(
        question=request.question,
        answer=answer,
        source="chroma-retrieval-openai-generation",
        conversation_id=request.conversation_id,
        assistant_message_id=assistant_message.id,
        references=references,
    )


@router.post("/stream")
def stream_answer(
    request: AskRequest,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Use SSE to return answer chunks while preserving the normal RAG rules."""
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

    urgent_answer = get_urgent_warning_response(request.question)
    if urgent_answer:
        def urgent_event_stream():
            save_message(session, request.conversation_id, "user", request.question)
            assistant_message = save_message(
                session,
                request.conversation_id,
                "assistant",
                urgent_answer,
            )
            session.commit()
            session.refresh(assistant_message)
            yield format_sse_event(
                "metadata",
                {
                    "source": "safety-keyword-guard",
                    "references": [
                        {
                            "name": "需要及时就医的警示信号",
                            "type": "safety_guard",
                            "source": "系统安全规则",
                            "excerpt": (
                                "呼吸困难、持续或加重的胸痛、意识改变、抽搐、"
                                "单侧肢体无力、言语含糊或严重过敏表现时，"
                                "应立即寻求紧急医疗帮助。"
                            ),
                            "relevance_score": 1.0,
                        }
                    ],
                },
            )
            yield format_sse_event("token", {"text": urgent_answer})
            yield format_sse_event(
                "done",
                {"assistant_message_id": assistant_message.id},
            )

        return StreamingResponse(
            urgent_event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
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
            k=8,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="知识库暂时不可用，请确认已执行 /knowledge/rebuild",
        ) from error

    best_matches: dict[tuple[str, str], tuple[object, float]] = {}
    for document, score in matches:
        if score < MIN_RELEVANCE_SCORE:
            continue
        source_key = (
            str(document.metadata.get("type", "unknown")),
            str(document.metadata.get("record_id", document.metadata.get("name"))),
        )
        previous_match = best_matches.get(source_key)
        if previous_match is None or score > previous_match[1]:
            best_matches[source_key] = (document, score)

    relevant_matches = sorted(
        best_matches.values(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    relevant_documents = [document for document, _ in relevant_matches]

    if not relevant_documents:
        no_match_answer = "知识库中没有找到足够相关的内容。建议换一种更具体的说法。"

        def no_match_event_stream():
            save_message(session, request.conversation_id, "user", request.question)
            assistant_message = save_message(
                session,
                request.conversation_id,
                "assistant",
                no_match_answer,
            )
            session.commit()
            session.refresh(assistant_message)
            yield format_sse_event(
                "metadata",
                {"source": "chroma-vector-search:no-match", "references": []},
            )
            yield format_sse_event("token", {"text": no_match_answer})
            yield format_sse_event(
                "done",
                {"assistant_message_id": assistant_message.id},
            )

        return StreamingResponse(
            no_match_event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    context = "\n\n".join(document.page_content for document in relevant_documents)
    references = [
        {
            "name": document.metadata.get("name", "未命名资料"),
            "type": document.metadata.get("type", "unknown"),
            "source": document.metadata.get("source"),
            "excerpt": document.page_content.replace("\n", " ")[:180],
            "relevance_score": round(score, 3),
        }
        for document, score in relevant_matches
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是医疗健康知识库助手。只能依据参考资料回答，"
                "不能编造资料中没有的内容。不得根据用户症状判断、推测或声明"
                "用户可能患有任何疾病或感染，也不要使用‘可能是’‘像是’等诊断性表达。"
                "绝不能说用户的症状‘符合’‘相符’‘指向’任何疾病。"
                "当用户描述症状时，必须严格按三个部分回答："
                "一、资料内容：仅客观列出参考资料中各病症的常见症状；"
                "二、通用健康建议：只给资料中已有的休息、补水或观察建议；"
                "三、就医提示：只列出资料中的警示信号或建议咨询医生的情况。"
                "第一部分不得把用户症状与任何病症建立联系。"
                "不能提供药物剂量或治疗方案。"
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
    messages = prompt.format_messages(
        context=context,
        history=history_text,
        question=request.question,
    )

    def answer_event_stream():
        yield format_sse_event(
            "metadata",
            {
                "source": "chroma-retrieval-openai-generation",
                "references": references,
            },
        )
        answer_parts: list[str] = []
        try:
            for chunk in get_chat_model().stream(messages):
                text = get_stream_text(chunk)
                if not text:
                    continue
                answer_parts.append(text)
                yield format_sse_event("token", {"text": text})
        except Exception:
            yield format_sse_event(
                "error",
                {"detail": "模型暂时不可用，请检查 CHAT_MODEL 和 API 配置"},
            )
            return

        answer = "".join(answer_parts).strip()
        if not answer:
            yield format_sse_event("error", {"detail": "模型没有返回可用内容"})
            return
        save_message(session, request.conversation_id, "user", request.question)
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            answer,
        )
        session.commit()
        session.refresh(assistant_message)
        yield format_sse_event(
            "done",
            {"assistant_message_id": assistant_message.id},
        )

    return StreamingResponse(
        answer_event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
