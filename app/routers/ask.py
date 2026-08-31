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
from app.models import ChatMessage, User
from app.routers.auth import get_current_user
from app.schemas import AskRequest, AskResponse
from app.hybrid_search import (
    build_vector_filter,
    get_retrieval_method,
    hybrid_search,
)
from app.monitoring import record_request_metric
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

DIRECT_LOOKUP_KEYWORDS = (
    "哪份资料",
    "什么资料",
    "哪个资料",
    "哪篇资料",
    "哪个专科",
    "哪个科",
    "哪个概览",
    "查什么",
    "看什么",
    "哪里看",
    "什么说明",
    "使用前",
    "说明书",
)
DRUG_QUESTION_KEYWORDS = (
    "药物",
    "药品",
    "怎么用",
    "如何用",
    "服用",
    "使用说明",
    "注意事项",
    "药效",
    "作用",
)
SYMPTOM_QUESTION_KEYWORDS = (
    "怎么办",
    "怎么处理",
    "不舒服",
    "症状",
    "疼",
    "痛",
    "发热",
    "发烧",
    "咳嗽",
    "腹泻",
    "头晕",
    "恶心",
    "呕吐",
    "出血",
    "瘀斑",
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
    user_id: int | None = None,
) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id,
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


def search_knowledge(
    vector_store: object,
    query: str,
    knowledge_type: str,
    source_filter: str,
    current_user: User | None = None,
    session: Session | None = None,
    keyword_query: str | None = None,
):
    if session is not None:
        return hybrid_search(
            session,
            vector_store,
            query,
            knowledge_type,
            source_filter,
            current_user,
            RAG_RETRIEVAL_FETCH_COUNT,
            keyword_query=keyword_query,
        )

    search_options = {"k": RAG_RETRIEVAL_FETCH_COUNT}
    vector_filter = build_vector_filter(
        knowledge_type,
        source_filter,
        current_user,
    )


def build_answer_mode_instruction(question: str) -> str:
    """Choose a concise answer shape before asking the model to generate text.

    A single long medical template made document-location questions sound evasive.
    The rules intentionally remain small and transparent so they can be tuned from
    real evaluation failures without adding another model call.
    """
    normalized_question = question.replace(" ", "")
    if any(keyword in normalized_question for keyword in DIRECT_LOOKUP_KEYWORDS):
        return (
            "资料定位模式：第一句必须直接回答用户要找的资料标题、专科或说明，"
            "例如“建议优先查看《资料标题》”或“该问题对应某某专科”。"
            "随后最多补充 2 至 3 条和问题直接相关的资料要点。"
            "不要使用固定的“三个部分”标题，也不要先说泛化建议。"
        )
    if any(keyword in normalized_question for keyword in DRUG_QUESTION_KEYWORDS):
        return (
            "药物说明模式：第一句直接说明资料中该药物的作用或用户所问的核心结论，"
            "随后列出 2 至 4 条资料中已有的使用说明或注意事项。"
            "不要提供资料中没有的剂量、疗程或治疗方案。"
        )
    if any(keyword in normalized_question for keyword in SYMPTOM_QUESTION_KEYWORDS):
        return (
            "症状咨询模式：必须严格按三个部分回答："
            "一、资料内容；二、通用健康建议；三、就医提示。"
            "第一部分只能客观列出资料中的信息，不得把用户症状和疾病建立联系。"
        )
    return (
        "知识问答模式：第一句先直接回答问题，再用 2 至 4 条资料要点补充。"
        "不需要使用固定的“三个部分”标题；安全提示只在资料确有相关内容时简短给出。"
    )
    if vector_filter is not None:
        search_options["filter"] = vector_filter
    return vector_store.similarity_search_with_relevance_scores(query, **search_options)


def retrieval_labels(matches: list[tuple[object, float]]) -> tuple[str, str]:
    method = get_retrieval_method(matches)
    rerank_applied = any(
        bool(getattr(document, "metadata", {}).get("rerank_applied"))
        for document, _ in matches
    )
    if rerank_applied and method == "hybrid":
        return (
            "hybrid-rerank-retrieval-openai-generation",
            "rag-hybrid-rerank",
        )
    if rerank_applied and method == "keyword":
        return (
            "keyword-rerank-retrieval-openai-generation",
            "rag-keyword-rerank",
        )
    if rerank_applied:
        return (
            "vector-rerank-retrieval-openai-generation",
            "rag-vector-rerank",
        )
    if method == "hybrid":
        return (
            "hybrid-retrieval-openai-generation",
            "rag-hybrid-retrieval",
        )
    if method == "keyword":
        return (
            "mysql-keyword-retrieval-openai-generation",
            "rag-keyword-retrieval",
        )
    return (
        "milvus-retrieval-openai-generation",
        "rag-vector-retrieval",
    )


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


def parse_metadata_int(value: object, minimum: int = 0) -> int | None:
    try:
        parsed_value = int(value)
    except (TypeError, ValueError):
        return None
    return parsed_value if parsed_value >= minimum else None


def infer_source_kind(
    knowledge_type: str,
    source: str,
    source_url: str,
) -> str:
    """Return a human-readable source category for a stable citation."""
    if knowledge_type in {"condition", "drug"}:
        return "结构化资料"
    if "PDF" in source.upper():
        return "PDF 文件"
    if "WORD" in source.upper():
        return "Word 文件"
    if "EXCEL" in source.upper():
        return "Excel 文件"
    if "网页" in source or source_url:
        return "网页"
    if "上传文件" in source:
        return "文本文件"
    return "知识文档"


def build_citation_location(
    source_kind: str,
    page_number: int | None,
    chunk_index: int | None,
    chunk_count: int | None,
) -> str:
    location_parts: list[str] = []
    if page_number is not None:
        location_parts.append(f"第 {page_number} 页")
    elif source_kind == "网页":
        location_parts.append("网页正文")
    elif source_kind == "结构化资料":
        location_parts.append("结构化记录")
    else:
        location_parts.append("全文")

    if (
        chunk_index is not None
        and chunk_count is not None
        and chunk_count > 1
    ):
        location_parts.append(f"切块 {chunk_index + 1}/{chunk_count}")
    return " · ".join(location_parts)


def build_references(relevant_matches: list[tuple[object, float]]) -> list[dict]:
    references: list[dict] = []
    for document, score in relevant_matches:
        metadata = document.metadata
        knowledge_type = str(metadata.get("type", "unknown"))
        name = str(metadata.get("name", "未命名资料"))
        source_tier = str(metadata.get("source_tier", "unverified"))
        source = str(metadata.get("source", "未标注来源"))
        source_url = str(metadata.get("source_url", "") or "")
        page_number = parse_metadata_int(metadata.get("page_number"), 1)
        chunk_index = parse_metadata_int(metadata.get("chunk_index"), 0)
        chunk_count = parse_metadata_int(metadata.get("chunk_count"), 1)
        source_kind = infer_source_kind(knowledge_type, source, source_url)
        location = build_citation_location(
            source_kind,
            page_number,
            chunk_index,
            chunk_count,
        )
        citation = f"{name} | {source_kind} | {source} | {location}"
        updated_at = parse_metadata_datetime(metadata.get("updated_at"))
        initial_score = metadata.get("initial_score")
        try:
            initial_score_value = float(initial_score)
        except (TypeError, ValueError):
            initial_score_value = score
        references.append(
            {
                "name": name,
                "type": knowledge_type,
                "record_id": metadata.get("record_id"),
                "source": source,
                "source_url": source_url or None,
                "source_kind": source_kind,
                "location": location,
                "citation": citation,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "chunk_count": chunk_count,
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
                # Keep the original field stable; rerank_score is the new
                # second-stage score used for the final ordering.
                "relevance_score": round(initial_score_value, 3),
                "initial_score": metadata.get("initial_score"),
                "rerank_score": metadata.get("rerank_score", round(score, 3)),
                "rerank_text_score": metadata.get("rerank_text_score"),
                "rerank_title_score": metadata.get("rerank_title_score"),
                "retrieval_method": metadata.get("retrieval_method", "vector"),
                "vector_score": metadata.get("vector_score"),
                "keyword_score": metadata.get("keyword_score"),
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


def build_rag_answer_prompt() -> ChatPromptTemplate:
    """Return the common prompt used by synchronous, streaming, and RAGAS flows."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是医疗健康知识库助手。只能依据参考资料回答，"
                "不能编造资料中没有的内容。不得根据用户症状判断、推测或声明"
                "用户可能患有任何疾病或感染，也不要使用‘可能是’‘像是’等诊断性表达。"
                "绝不能说用户的症状‘符合’‘相符’‘指向’任何疾病。"
                "不能提供药物剂量或治疗方案。"
                "如果资料不足，要明确说资料不足，并建议咨询医生。"
                "资料可靠性提示：{source_limitations}\n"
                "本次检索到的资料标题：{reference_names}\n"
                "当前回答方式：{answer_mode}\n"
                "无论回答方式如何，结尾保留一条简短提醒：内容仅供健康信息参考，"
                "不代替医生诊断或处方。",
            ),
            (
                "human",
                "历史对话：\n{history}\n\n"
                "参考资料：\n{context}\n\n用户问题：{question}",
            ),
        ]
    )


def run_rag_answer_pipeline(
    session: Session,
    question: str,
    *,
    knowledge_type: str = "all",
    source_filter: str = "all",
    current_user: User | None = None,
    history_text: str = "暂无历史对话",
) -> dict:
    """Run the side-effect-free form of the normal first-turn RAG workflow.

    RAGAS calls this function so each sampled case uses the production hybrid
    retrieval, reranking, relevance filtering, prompt, and OpenAI generation
    path without creating user conversation messages.
    """
    started_at = perf_counter()
    urgent_answer = get_urgent_warning_response(question)
    if urgent_answer:
        references = build_safety_references()
        metadata = build_response_metadata(
            source="safety-keyword-guard",
            references=references,
            processing_path="safety-keyword-guard",
            retrieval_scope=knowledge_type,
            source_filter=source_filter,
            retrieved_count=0,
            started_at=started_at,
        )
        return {
            "answer": urgent_answer,
            "contexts": [reference["excerpt"] for reference in references],
            **metadata,
        }

    knowledge_status = get_knowledge_status(session)
    if not knowledge_status["is_current"]:
        raise RuntimeError("知识库已过期，请先执行 POST /knowledge/rebuild")

    try:
        vector_store = get_vector_store()
        matches = search_knowledge(
            vector_store,
            question,
            knowledge_type,
            source_filter,
            current_user,
            session,
            question,
        )
    except Exception as error:
        raise RuntimeError("知识库暂时不可用，请确认已执行 /knowledge/rebuild") from error

    relevant_matches = select_distinct_relevant_matches(matches)
    relevant_matches = select_title_matched_documents(question, relevant_matches)
    relevant_documents = [document for document, _ in relevant_matches]
    if not relevant_documents:
        metadata = build_response_metadata(
            source="milvus-vector-search:no-match",
            references=[],
            processing_path="vector-search-no-match",
            retrieval_scope=knowledge_type,
            source_filter=source_filter,
            retrieved_count=0,
            started_at=started_at,
        )
        return {
            "answer": "知识库中没有找到足够相关的内容。建议换一种更具体的说法。",
            "contexts": [],
            **metadata,
        }

    context = "\n\n".join(document.page_content for document in relevant_documents)
    references = build_references(relevant_matches)
    reference_names = "、".join(reference["name"] for reference in references)
    try:
        response = get_chat_model().invoke(
            build_rag_answer_prompt().format_messages(
                context=context,
                history=history_text,
                question=question,
                source_limitations=build_source_limitations(references),
                reference_names=reference_names,
                answer_mode=build_answer_mode_instruction(question),
            )
        )
    except Exception as error:
        raise RuntimeError("模型暂时不可用，请检查 CHAT_MODEL 和 API 配置") from error

    retrieval_source, retrieval_path = retrieval_labels(relevant_matches)
    metadata = build_response_metadata(
        source=retrieval_source,
        references=references,
        processing_path=retrieval_path,
        retrieval_scope=knowledge_type,
        source_filter=source_filter,
        retrieved_count=len(relevant_documents),
        started_at=started_at,
    )
    return {
        "answer": str(response.content),
        "contexts": [document.page_content for document in relevant_documents],
        **metadata,
    }


@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """同时使用 MySQL 关键词检索和 Milvus 向量检索获取资料。"""
    started_at = perf_counter()
    history = session.exec(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == request.conversation_id)
        .where(
            (ChatMessage.user_id == current_user.id)
            if not current_user.is_admin
            else True
        )
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
        save_message(
            session,
            request.conversation_id,
            "user",
            request.question,
            user_id=current_user.id,
        )
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            urgent_answer,
            metadata,
            user_id=current_user.id,
        )
        session.flush()
        record_request_metric(
            session,
            user_id=current_user.id,
            assistant_message_id=assistant_message.id,
            endpoint="ask",
            success=True,
            status_code=200,
            request_type="safety_guard",
            processing_path=metadata["processing_path"],
            retrieved_count=metadata["retrieved_count"],
            latency_ms=metadata["latency_ms"],
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
        record_request_metric(
            session,
            user_id=current_user.id,
            endpoint="ask",
            success=False,
            status_code=409,
            request_type="error",
            processing_path="knowledge-stale",
            latency_ms=round((perf_counter() - started_at) * 1000),
            error_type="knowledge_stale",
        )
        session.commit()
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
            current_user,
            session,
            request.question,
        )
    except Exception as error:
        record_request_metric(
            session,
            user_id=current_user.id,
            endpoint="ask",
            success=False,
            status_code=503,
            request_type="error",
            processing_path="retrieval-error",
            latency_ms=round((perf_counter() - started_at) * 1000),
            error_type="retrieval_error",
        )
        session.commit()
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
            source="milvus-vector-search:no-match",
            references=[],
            processing_path="vector-search-no-match",
            retrieval_scope=request.knowledge_type,
            source_filter=request.source_filter,
            retrieved_count=0,
            started_at=started_at,
        )
        save_message(
            session,
            request.conversation_id,
            "user",
            request.question,
            user_id=current_user.id,
        )
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            answer,
            metadata,
            user_id=current_user.id,
        )
        session.flush()
        record_request_metric(
            session,
            user_id=current_user.id,
            assistant_message_id=assistant_message.id,
            endpoint="ask",
            success=True,
            status_code=200,
            request_type="no_match",
            processing_path=metadata["processing_path"],
            retrieved_count=metadata["retrieved_count"],
            latency_ms=metadata["latency_ms"],
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
    reference_names = "、".join(reference["name"] for reference in references)

    prompt = build_rag_answer_prompt()

    try:
        response = get_chat_model().invoke(
            prompt.format_messages(
                context=context,
                history=history_text,
                question=request.question,
                source_limitations=build_source_limitations(references),
                reference_names=reference_names,
                answer_mode=build_answer_mode_instruction(request.question),
            )
        )
        answer = str(response.content)
    except Exception as error:
        record_request_metric(
            session,
            user_id=current_user.id,
            endpoint="ask",
            success=False,
            status_code=503,
            request_type="rag",
            processing_path="generation-error",
            retrieved_count=len(relevant_documents),
            latency_ms=round((perf_counter() - started_at) * 1000),
            error_type="generation_error",
        )
        session.commit()
        raise HTTPException(
            status_code=503,
            detail="模型暂时不可用，请检查 CHAT_MODEL 和 API 配置",
        ) from error

    retrieval_source, retrieval_path = retrieval_labels(relevant_matches)
    metadata = build_response_metadata(
        source=retrieval_source,
        references=references,
        processing_path=retrieval_path,
        retrieval_scope=request.knowledge_type,
        source_filter=request.source_filter,
        retrieved_count=len(relevant_documents),
        started_at=started_at,
    )
    save_message(
        session,
        request.conversation_id,
        "user",
        request.question,
        user_id=current_user.id,
    )
    assistant_message = save_message(
        session,
        request.conversation_id,
        "assistant",
        answer,
        metadata,
        user_id=current_user.id,
    )
    session.flush()
    record_request_metric(
        session,
        user_id=current_user.id,
        assistant_message_id=assistant_message.id,
        endpoint="ask",
        success=True,
        status_code=200,
        request_type="rag",
        processing_path=metadata["processing_path"],
        retrieved_count=metadata["retrieved_count"],
        latency_ms=metadata["latency_ms"],
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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Use SSE to return answer chunks while preserving the normal RAG rules."""
    started_at = perf_counter()
    history = session.exec(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == request.conversation_id)
        .where(
            (ChatMessage.user_id == current_user.id)
            if not current_user.is_admin
            else True
        )
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
            save_message(
                session,
                request.conversation_id,
                "user",
                request.question,
                user_id=current_user.id,
            )
            assistant_message = save_message(
                session,
                request.conversation_id,
                "assistant",
                urgent_answer,
                metadata,
                user_id=current_user.id,
            )
            session.flush()
            record_request_metric(
                session,
                user_id=current_user.id,
                assistant_message_id=assistant_message.id,
                endpoint="ask/stream",
                success=True,
                status_code=200,
                request_type="safety_guard",
                processing_path=metadata["processing_path"],
                retrieved_count=metadata["retrieved_count"],
                latency_ms=metadata["latency_ms"],
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
        record_request_metric(
            session,
            user_id=current_user.id,
            endpoint="ask/stream",
            success=False,
            status_code=409,
            request_type="error",
            processing_path="knowledge-stale",
            latency_ms=round((perf_counter() - started_at) * 1000),
            error_type="knowledge_stale",
        )
        session.commit()
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
            current_user,
            session,
            request.question,
        )
    except Exception as error:
        record_request_metric(
            session,
            user_id=current_user.id,
            endpoint="ask/stream",
            success=False,
            status_code=503,
            request_type="error",
            processing_path="retrieval-error",
            latency_ms=round((perf_counter() - started_at) * 1000),
            error_type="retrieval_error",
        )
        session.commit()
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
                source="milvus-vector-search:no-match",
                references=[],
                processing_path="vector-search-no-match",
                retrieval_scope=request.knowledge_type,
                source_filter=request.source_filter,
                retrieved_count=0,
                started_at=started_at,
            )
            save_message(
                session,
                request.conversation_id,
                "user",
                request.question,
                user_id=current_user.id,
            )
            assistant_message = save_message(
                session,
                request.conversation_id,
                "assistant",
                no_match_answer,
                metadata,
                user_id=current_user.id,
            )
            session.flush()
            record_request_metric(
                session,
                user_id=current_user.id,
                assistant_message_id=assistant_message.id,
                endpoint="ask/stream",
                success=True,
                status_code=200,
                request_type="no_match",
                processing_path=metadata["processing_path"],
                retrieved_count=metadata["retrieved_count"],
                latency_ms=metadata["latency_ms"],
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
    reference_names = "、".join(reference["name"] for reference in references)
    retrieval_source, retrieval_path = retrieval_labels(relevant_matches)
    prompt = build_rag_answer_prompt()
    messages = prompt.format_messages(
        context=context,
        history=history_text,
        question=request.question,
        source_limitations=build_source_limitations(references),
        reference_names=reference_names,
        answer_mode=build_answer_mode_instruction(request.question),
    )

    def answer_event_stream():
        initial_metadata = build_response_metadata(
            source=retrieval_source,
            references=references,
            processing_path=retrieval_path,
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
            record_request_metric(
                session,
                user_id=current_user.id,
                endpoint="ask/stream",
                success=False,
                status_code=503,
                request_type="rag",
                processing_path="generation-error",
                retrieved_count=len(relevant_documents),
                latency_ms=round((perf_counter() - started_at) * 1000),
                error_type="generation_error",
            )
            session.commit()
            yield format_sse_event(
                "error",
                {"detail": "模型暂时不可用，请检查 CHAT_MODEL 和 API 配置"},
            )
            return

        answer = "".join(answer_parts).strip()
        if not answer:
            record_request_metric(
                session,
                user_id=current_user.id,
                endpoint="ask/stream",
                success=False,
                status_code=502,
                request_type="rag",
                processing_path="generation-empty",
                retrieved_count=len(relevant_documents),
                latency_ms=round((perf_counter() - started_at) * 1000),
                error_type="empty_generation",
            )
            session.commit()
            yield format_sse_event("error", {"detail": "模型没有返回可用内容"})
            return
        metadata = build_response_metadata(
            source=retrieval_source,
            references=references,
            processing_path=retrieval_path,
            retrieval_scope=request.knowledge_type,
            source_filter=request.source_filter,
            retrieved_count=len(relevant_documents),
            started_at=started_at,
        )
        save_message(
            session,
            request.conversation_id,
            "user",
            request.question,
            user_id=current_user.id,
        )
        assistant_message = save_message(
            session,
            request.conversation_id,
            "assistant",
            answer,
            metadata,
            user_id=current_user.id,
        )
        session.flush()
        record_request_metric(
            session,
            user_id=current_user.id,
            assistant_message_id=assistant_message.id,
            endpoint="ask/stream",
            success=True,
            status_code=200,
            request_type="rag",
            processing_path=metadata["processing_path"],
            retrieved_count=metadata["retrieved_count"],
            latency_ms=metadata["latency_ms"],
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
