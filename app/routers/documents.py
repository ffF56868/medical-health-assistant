from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlmodel import Session, select

from app.database import get_session
from app.models import KnowledgeDocument
from app.schemas import KnowledgeDocumentCreate, KnowledgeDocumentRead


router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_SUFFIXES = {".md", ".txt"}
MAX_DOCUMENT_BYTES = 200_000


@router.post("", response_model=KnowledgeDocumentRead, status_code=201)
def create_document(
    document_data: KnowledgeDocumentCreate,
    session: Session = Depends(get_session),
):
    duplicate = session.exec(
        select(KnowledgeDocument).where(
            KnowledgeDocument.title == document_data.title
        )
    ).first()

    if duplicate is not None:
        raise HTTPException(status_code=409, detail="知识文档标题已经存在")

    document = KnowledgeDocument.model_validate(document_data)
    document.updated_at = datetime.now(UTC)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.post("/upload", response_model=KnowledgeDocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    text_content_types = {"text/markdown", "text/plain"}
    if suffix not in ALLOWED_SUFFIXES and file.content_type not in text_content_types:
        raise HTTPException(
            status_code=400,
            detail="只支持上传 .md 或 .txt 文本文件",
        )

    raw_content = await file.read()
    if len(raw_content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="文件不能超过 200KB")

    try:
        content = raw_content.decode("utf-8-sig").strip()
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="文件必须使用 UTF-8 编码保存",
        ) from error

    if not content:
        raise HTTPException(status_code=400, detail="上传的文件内容不能为空")

    title = Path(filename).stem.strip() or "未命名知识文档"
    if not title:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    duplicate = session.exec(
        select(KnowledgeDocument).where(KnowledgeDocument.title == title)
    ).first()
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="同名知识文档已经存在")

    document = KnowledgeDocument(
        title=title,
        content=content,
        source=f"上传文件：{filename}",
        source_tier="unverified",
        updated_at=datetime.now(UTC),
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.get("", response_model=list[KnowledgeDocumentRead])
def list_documents(
    keyword: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_session),
):
    statement = select(KnowledgeDocument).order_by(KnowledgeDocument.id)

    if keyword and keyword.strip():
        statement = statement.where(
            KnowledgeDocument.title.contains(keyword.strip())
        )

    return session.exec(statement).all()


@router.get("/{document_id}", response_model=KnowledgeDocumentRead)
def get_document(
    document_id: int,
    session: Session = Depends(get_session),
):
    document = session.get(KnowledgeDocument, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="知识文档不存在")

    return document


@router.put("/{document_id}", response_model=KnowledgeDocumentRead)
def update_document(
    document_id: int,
    document_data: KnowledgeDocumentCreate,
    session: Session = Depends(get_session),
):
    document = session.get(KnowledgeDocument, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="知识文档不存在")

    duplicate = session.exec(
        select(KnowledgeDocument).where(
            KnowledgeDocument.title == document_data.title,
            KnowledgeDocument.id != document_id,
        )
    ).first()

    if duplicate is not None:
        raise HTTPException(status_code=409, detail="知识文档标题已经存在")

    document.title = document_data.title
    document.content = document_data.content
    document.source = document_data.source
    document.source_url = document_data.source_url
    document.source_tier = document_data.source_tier
    document.updated_at = datetime.now(UTC)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    session: Session = Depends(get_session),
):
    document = session.get(KnowledgeDocument, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="知识文档不存在")

    session.delete(document)
    session.commit()
