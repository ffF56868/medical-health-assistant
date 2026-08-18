import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sqlmodel import Session, select

from app.models import Condition, Drug


COLLECTION_NAME = "medical_health_knowledge"


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


def build_knowledge_documents(session: Session) -> list[Document]:
    documents: list[Document] = []

    conditions = session.exec(select(Condition).order_by(Condition.id)).all()
    for condition in conditions:
        documents.append(
            Document(
                page_content=(
                    f"病症名称：{condition.name}\n"
                    f"常见症状：{condition.symptoms}\n"
                    f"处理建议：{condition.treatment}"
                ),
                metadata={"type": "condition", "record_id": condition.id},
            )
        )

    drugs = session.exec(select(Drug).order_by(Drug.id)).all()
    for drug in drugs:
        documents.append(
            Document(
                page_content=(
                    f"药物名称：{drug.name}\n"
                    f"药物作用：{drug.effects}\n"
                    f"使用说明：{drug.instructions}"
                ),
                metadata={"type": "drug", "record_id": drug.id},
            )
        )

    return documents


def rebuild_vector_store(session: Session) -> int:
    documents = build_knowledge_documents(session)
    vector_store = get_vector_store()

    vector_store.delete_collection()
    vector_store = get_vector_store()

    if documents:
        ids = [
            f"{document.metadata['type']}-{document.metadata['record_id']}"
            for document in documents
        ]
        vector_store.add_documents(documents=documents, ids=ids)

    return len(documents)
