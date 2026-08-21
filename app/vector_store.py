import os
from hashlib import sha256
import json
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session, select

from app.models import Condition, Drug, KnowledgeDocument, KnowledgeIndexState
from app.source_metadata import get_source_tier_label, needs_source_review


COLLECTION_NAME = "medical_health_knowledge"
MIN_RELEVANCE_SCORE = 0.2
RAG_RETRIEVAL_FETCH_COUNT = 8
RAG_RETRIEVAL_RESULT_COUNT = 3
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", ""],
)


def select_distinct_relevant_matches(
    matches: list[tuple[object, float]],
    min_relevance_score: float = MIN_RELEVANCE_SCORE,
    limit: int = RAG_RETRIEVAL_RESULT_COUNT,
) -> list[tuple[object, float]]:
    """Keep the strongest relevant chunk from each knowledge record."""
    best_matches: dict[tuple[str, str], tuple[object, float]] = {}
    for document, score in matches:
        if score < min_relevance_score:
            continue
        metadata = getattr(document, "metadata", {})
        source_key = (
            str(metadata.get("type", "unknown")),
            str(metadata.get("record_id", metadata.get("name"))),
        )
        previous_match = best_matches.get(source_key)
        if previous_match is None or score > previous_match[1]:
            best_matches[source_key] = (document, score)

    return sorted(
        best_matches.values(),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]


def get_vector_store() -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    persist_directory = Path(
        os.getenv("CHROMA_DIR", "chroma_db")
    ).resolve()
    persist_directory.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )


def build_source_metadata(record: object) -> dict[str, str | bool]:
    source = str(getattr(record, "source", "未标注来源") or "未标注来源")
    source_url = str(getattr(record, "source_url", "") or "")
    source_tier = str(getattr(record, "source_tier", "unverified") or "unverified")
    updated_at = getattr(record, "updated_at", None)
    return {
        "source": source,
        "source_url": source_url,
        "source_tier": source_tier,
        "updated_at": updated_at.isoformat() if updated_at else "",
        "needs_review": needs_source_review(
            source_tier,
            updated_at,
            source,
            source_url,
        ),
    }


def build_knowledge_documents(session: Session) -> list[Document]:
    documents: list[Document] = []

    conditions = session.exec(select(Condition).order_by(Condition.id)).all()
    for condition in conditions:
        documents.append(
            Document(
                page_content=(
                    f"病症名称：{condition.name}\n"
                    f"常见症状：{condition.symptoms}\n"
                    f"处理建议：{condition.treatment}\n"
                    f"资料来源：{condition.source}\n"
                    f"来源链接：{condition.source_url or '未提供'}\n"
                    f"可信度：{get_source_tier_label(condition.source_tier)}\n"
                    f"最后更新：{condition.updated_at.isoformat() if condition.updated_at else '未记录'}"
                ),
                metadata={
                    "type": "condition",
                    "record_id": condition.id,
                    "name": condition.name,
                    **build_source_metadata(condition),
                },
            )
        )

    drugs = session.exec(select(Drug).order_by(Drug.id)).all()
    for drug in drugs:
        documents.append(
            Document(
                page_content=(
                    f"药物名称：{drug.name}\n"
                    f"药物作用：{drug.effects}\n"
                    f"使用说明：{drug.instructions}\n"
                    f"资料来源：{drug.source}\n"
                    f"来源链接：{drug.source_url or '未提供'}\n"
                    f"可信度：{get_source_tier_label(drug.source_tier)}\n"
                    f"最后更新：{drug.updated_at.isoformat() if drug.updated_at else '未记录'}"
                ),
                metadata={
                    "type": "drug",
                    "record_id": drug.id,
                    "name": drug.name,
                    **build_source_metadata(drug),
                },
            )
        )

    knowledge_documents = session.exec(
        select(KnowledgeDocument).order_by(KnowledgeDocument.id)
    ).all()
    for knowledge_document in knowledge_documents:
        documents.append(
            Document(
                page_content=(
                    f"资料标题：{knowledge_document.title}\n"
                    f"资料来源：{knowledge_document.source}\n"
                    f"来源链接：{knowledge_document.source_url or '未提供'}\n"
                    f"可信度：{get_source_tier_label(knowledge_document.source_tier)}\n"
                    f"最后更新：{knowledge_document.updated_at.isoformat() if knowledge_document.updated_at else '未记录'}\n"
                    f"资料内容：{knowledge_document.content}"
                ),
                metadata={
                    "type": "document",
                    "record_id": knowledge_document.id,
                    "name": knowledge_document.title,
                    **build_source_metadata(knowledge_document),
                },
            )
        )

    chunks: list[Document] = []
    for document in documents:
        split_documents = TEXT_SPLITTER.split_documents([document])
        for chunk_index, chunk in enumerate(split_documents):
            chunk.metadata["chunk_index"] = chunk_index
            chunks.append(chunk)

    return chunks


def get_knowledge_fingerprint(documents: list[Document]) -> str:
    content = [
        {
            "page_content": document.page_content,
            "metadata": document.metadata,
        }
        for document in documents
    ]
    serialized = json.dumps(content, ensure_ascii=False, sort_keys=True)
    return sha256(serialized.encode("utf-8")).hexdigest()


def get_knowledge_status(session: Session) -> dict:
    documents = build_knowledge_documents(session)
    current_hash = get_knowledge_fingerprint(documents)
    index_state = session.get(KnowledgeIndexState, 1)
    source_document_count = sum(
        len(records)
        for records in (
            session.exec(select(Condition)).all(),
            session.exec(select(Drug)).all(),
            session.exec(select(KnowledgeDocument)).all(),
        )
    )

    return {
        "is_current": (
            index_state is not None
            and index_state.content_hash == current_hash
        ),
        "document_count": source_document_count,
        "chunk_count": len(documents),
        "indexed_document_count": (
            index_state.document_count if index_state is not None else None
        ),
        "indexed_at": index_state.indexed_at if index_state is not None else None,
    }


def rebuild_vector_store(session: Session) -> tuple[int, int]:
    documents = build_knowledge_documents(session)
    vector_store = get_vector_store()

    vector_store.delete_collection()
    vector_store = get_vector_store()

    if documents:
        ids = [
            "-".join(
                [
                    document.metadata["type"],
                    str(document.metadata["record_id"]),
                    str(document.metadata["chunk_index"]),
                ]
            )
            for document in documents
        ]
        vector_store.add_documents(documents=documents, ids=ids)

    index_state = KnowledgeIndexState(
        id=1,
        content_hash=get_knowledge_fingerprint(documents),
        document_count=len(documents),
    )
    session.merge(index_state)
    session.commit()

    source_document_count = sum(
        len(records)
        for records in (
            session.exec(select(Condition)).all(),
            session.exec(select(Drug)).all(),
            session.exec(select(KnowledgeDocument)).all(),
        )
    )
    return source_document_count, len(documents)
