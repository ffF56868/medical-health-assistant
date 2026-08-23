import os
import json
from datetime import datetime
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlmodel import Session, select

from app.database import get_session
from app.models import ChatMessage
from app.routers.auth import get_current_user
from app.schemas import AskRequest, AskResponse
from app.source_metadata import needs_source_review
from app.vector_store import (
    RAG_RETRIEVAL_FETCH_COUNT,
    get_knowledge_status,
    get_vector_store,
    select_distinct_relevant_matches,
)


router = APIRouter(
    prefix="/ask",
    tags=["ask"],
    dependencies=[Depends(get_current_user)],
)
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
    response_metadata: dict | None = None,
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        response_metadata_json=json.dumps(
            response_metadata or {},
            ensure_ascii=False,
            default=str,
        ),
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
    data = json.dumps(payload, ensure_ascii=False, default=str)
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


def build_vector_filter(knowledge_type: str, source_filter: str) -> dict | None:
    conditions: list[dict] = []
    if knowledge_type != "all":
        conditions.append({"type": knowledge_type})
    if source_filter == "reviewed":
        conditions.append({"needs_review": False})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def search_knowledge(
    vector_store: object,
    query: str,
    knowledge_type: str,
    source_filter: str,
):
    search_options = {"k": RAG_RETRIEVAL_FETCH_COUNT}
    vector_filter = build_vector_filter(knowledge_type, source_filter)
    if vector_filter is not None:
        search_options["filter"] = vector_filter
    return vector_store.similarity_search_with_relevance_scores(query, **search_options)


def select_title_matched_documents(
    question: str,
    relevant_matches: list[tuple[object, float]],
) -> list[tuple[object, float]]:
    """Prefer documents whose explicit disease title appears in the question.

    Vector similarity can group together unrelated documents that share terms
    such as "warning" or "seek medical care".  A direct title match is a
    stronger intent signal, while questions without such a match keep the
    normal multi-document retrieval behavior.
    """
    normalized_question = question.casefold()
    title_matches = [
        match
        for match in relevant_matches
        if str(match[0].metadata.get("type", "")) == "document"
        and str(match[0].metadata.get("name", "")).split("：", 1)[0].casefold()
        in normalized_question
    ]
    return title_matches or relevant_matches


def parse_metadata_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_references(relevant_matches: list[tuple[object, float]]) -> list[dict]:
    references: list[dict] = []
    for document, score in relevant_matches:
        metadata = document.metadata
        source_tier = str(metadata.get("source_tier", "unverified"))
        source = str(metadata.get("source", "未标注来源"))
        source_url = str(metadata.get("source_url", "") or "")
        updated_at = parse_metadata_datetime(metadata.get("updated_at"))
        references.append(
            {
                "name": metadata.get("name", "未命名资料"),
                "type": metadata.get("type", "unknown"),
                "record_id": metadata.get("record_id"),
                "source": source,
                "source_url": source_url or None,
                "source_tier": source_tier,
                "updated_at": updated_at,
                "needs_review": bool(
                    metadata.get(
                        "needs_review",
                        needs_source_review(
                            source_tier,
                            updated_at,
                            source,
                            source_url,
                        ),
                    )
                ),
                "excerpt": document.page_content.replace("\n", " ")[:180],
                "relevance_score": round(score, 3),
            }
        )
    return references


def build_source_limitations(references: list[dict]) -> str:
    if any(reference["needs_review"] for reference in references):
        return (
            "部分参考资料的来源待核实、未记录更新时间或已超过一年未更新。"
            "回答中必须明确提示这项限制，不能把这些资料表述为确定的医疗结论。"
        )
    return "参考资料已标注来源和更新时间，但仍只能作为健康信息参考。"


def build_response_metadata(
    *,
    source: str,
    references: list[dict],
    processing_path: str,
    retrieval_scope: str,
    source_filter: str,
    retrieved_count: int,
    started_at: float,
) -> dict:
    """Keep the evidence used for an answer available after the page reloads."""
    return {
        "source": source,
        "references": references,
        "processing_path": processing_path,
        "retrieval_scope": retrieval_scope,
        "source_filter": source_filter,
        "retrieved_count": retrieved_count,
        "latency_ms": round((perf_counter() - started_at) * 1000),
    }


def build_safety_references() -> list[dict]:
    return [
        {
            "name": "需要及时就医的警示信号",
            "type": "safety_guard",
            "source": "系统安全规则",
            "source_tier": "professional",
            "updated_at": None,
            "needs_review": False,
            "excerpt": (
                "呼吸困难、持续或加重的胸痛、意识改变、抽搐、"
                "单侧肢体无力、言语含糊或严重过敏表现时，"
                "应立即寻求紧急医疗帮助。"
            ),
            "relevance_score": 1.0,
        }
    ]


@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    session: Session = Depends(get_session),
):
    """根据语义相似度，从 Chroma 向量库检索医疗健康资料。"""
    started_at = perf_counter()
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
        references = build_safety_references()
        metadata = build_response_metadata(
            source="safety-keyword-guard",
            references=references,
            processing_path="safety-keyword-guard",
            retrieval_scope=request.knowledge_type,
            source_filter=request.source_filter,
            retrieved_count=0,
            started_at=started_at,
        )
        save_message(session, request.conversation_id, "user", request.question)
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            urgent_answer,
            metadata,
        )
        session.commit()
        session.refresh(assistant_message)
        return AskResponse(
            question=request.question,
            answer=urgent_answer,
            source=metadata["source"],
            conversation_id=request.conversation_id,
            assistant_message_id=assistant_message.id,
            references=metadata["references"],
            processing_path=metadata["processing_path"],
            retrieval_scope=metadata["retrieval_scope"],
            source_filter=metadata["source_filter"],
            retrieved_count=metadata["retrieved_count"],
            latency_ms=metadata["latency_ms"],
        )

    knowledge_status = get_knowledge_status(session)
    if not knowledge_status["is_current"]:
        raise HTTPException(
            status_code=409,
            detail="知识库已过期，请先执行 POST /knowledge/rebuild",
        )

    try:
        vector_store = get_vector_store()
        matches = search_knowledge(
            vector_store,
            retrieval_query,
            request.knowledge_type,
            request.source_filter,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="知识库暂时不可用，请确认已执行 /knowledge/rebuild",
        ) from error

    relevant_matches = select_distinct_relevant_matches(matches)
    relevant_matches = select_title_matched_documents(
        request.question,
        relevant_matches,
    )
    relevant_documents = [document for document, _ in relevant_matches]

    if not relevant_documents:
        answer = "知识库中没有找到足够相关的内容。建议换一种更具体的说法。"
        metadata = build_response_metadata(
            source="chroma-vector-search:no-match",
            references=[],
            processing_path="vector-search-no-match",
            retrieval_scope=request.knowledge_type,
            source_filter=request.source_filter,
            retrieved_count=0,
            started_at=started_at,
        )
        save_message(session, request.conversation_id, "user", request.question)
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            answer,
            metadata,
        )
        session.commit()
        session.refresh(assistant_message)
        return AskResponse(
            question=request.question,
            answer=answer,
            source=metadata["source"],
            conversation_id=request.conversation_id,
            assistant_message_id=assistant_message.id,
            references=metadata["references"],
            processing_path=metadata["processing_path"],
            retrieval_scope=metadata["retrieval_scope"],
            source_filter=metadata["source_filter"],
            retrieved_count=metadata["retrieved_count"],
            latency_ms=metadata["latency_ms"],
        )

    context = "\n\n".join(
        document.page_content
        for document in relevant_documents
    )
    references = build_references(relevant_matches)

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
                "资料可靠性提示：{source_limitations}"
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
                source_limitations=build_source_limitations(references),
            )
        )
        answer = str(response.content)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="模型暂时不可用，请检查 CHAT_MODEL 和 API 配置",
        ) from error

    metadata = build_response_metadata(
        source="chroma-retrieval-openai-generation",
        references=references,
        processing_path="rag-vector-retrieval",
        retrieval_scope=request.knowledge_type,
        source_filter=request.source_filter,
        retrieved_count=len(relevant_documents),
        started_at=started_at,
    )
    save_message(session, request.conversation_id, "user", request.question)
    assistant_message = save_message(
        session,
        request.conversation_id,
        "assistant",
        answer,
        metadata,
    )
    session.commit()
    session.refresh(assistant_message)

    return AskResponse(
        question=request.question,
        answer=answer,
        source=metadata["source"],
        conversation_id=request.conversation_id,
        assistant_message_id=assistant_message.id,
        references=metadata["references"],
        processing_path=metadata["processing_path"],
        retrieval_scope=metadata["retrieval_scope"],
        source_filter=metadata["source_filter"],
        retrieved_count=metadata["retrieved_count"],
        latency_ms=metadata["latency_ms"],
    )


@router.post("/stream")
def stream_answer(
    request: AskRequest,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Use SSE to return answer chunks while preserving the normal RAG rules."""
    started_at = perf_counter()
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
            metadata = build_response_metadata(
                source="safety-keyword-guard",
                references=build_safety_references(),
                processing_path="safety-keyword-guard",
                retrieval_scope=request.knowledge_type,
                source_filter=request.source_filter,
                retrieved_count=0,
                started_at=started_at,
            )
            save_message(session, request.conversation_id, "user", request.question)
            assistant_message = save_message(
                session,
                request.conversation_id,
                "assistant",
                urgent_answer,
                metadata,
            )
            session.commit()
            session.refresh(assistant_message)
            yield format_sse_event(
                "metadata",
                metadata,
            )
            yield format_sse_event("token", {"text": urgent_answer})
            yield format_sse_event(
                "done",
                {"assistant_message_id": assistant_message.id, **metadata},
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
        matches = search_knowledge(
            vector_store,
            retrieval_query,
            request.knowledge_type,
            request.source_filter,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="知识库暂时不可用，请确认已执行 /knowledge/rebuild",
        ) from error

    relevant_matches = select_distinct_relevant_matches(matches)
    relevant_matches = select_title_matched_documents(
        request.question,
        relevant_matches,
    )
    relevant_documents = [document for document, _ in relevant_matches]

    if not relevant_documents:
        no_match_answer = "知识库中没有找到足够相关的内容。建议换一种更具体的说法。"

        def no_match_event_stream():
            metadata = build_response_metadata(
                source="chroma-vector-search:no-match",
                references=[],
                processing_path="vector-search-no-match",
                retrieval_scope=request.knowledge_type,
                source_filter=request.source_filter,
                retrieved_count=0,
                started_at=started_at,
            )
            save_message(session, request.conversation_id, "user", request.question)
            assistant_message = save_message(
                session,
                request.conversation_id,
                "assistant",
                no_match_answer,
                metadata,
            )
            session.commit()
            session.refresh(assistant_message)
            yield format_sse_event(
                "metadata",
                metadata,
            )
            yield format_sse_event("token", {"text": no_match_answer})
            yield format_sse_event(
                "done",
                {"assistant_message_id": assistant_message.id, **metadata},
            )

        return StreamingResponse(
            no_match_event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    context = "\n\n".join(document.page_content for document in relevant_documents)
    references = build_references(relevant_matches)
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
                "资料可靠性提示：{source_limitations}"
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
        source_limitations=build_source_limitations(references),
    )

    def answer_event_stream():
        initial_metadata = build_response_metadata(
            source="chroma-retrieval-openai-generation",
            references=references,
            processing_path="rag-vector-retrieval",
            retrieval_scope=request.knowledge_type,
            source_filter=request.source_filter,
            retrieved_count=len(relevant_documents),
            started_at=started_at,
        )
        yield format_sse_event(
            "metadata",
            initial_metadata,
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
        metadata = build_response_metadata(
            source="chroma-retrieval-openai-generation",
            references=references,
            processing_path="rag-vector-retrieval",
            retrieval_scope=request.knowledge_type,
            source_filter=request.source_filter,
            retrieved_count=len(relevant_documents),
            started_at=started_at,
        )
        save_message(session, request.conversation_id, "user", request.question)
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            answer,
            metadata,
        )
        session.commit()
        session.refresh(assistant_message)
        yield format_sse_event(
            "done",
            {"assistant_message_id": assistant_message.id, **metadata},
        )

    return StreamingResponse(
        answer_event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
