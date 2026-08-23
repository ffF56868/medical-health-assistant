from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlmodel import Session, select

from app.access import accessible_documents_statement, can_access_document
from app.database import get_session
from app.models import KnowledgeDocument, User
from app.routers.auth import get_current_user, require_admin
from app.schemas import (
    DocumentUploadBatchResponse,
    DocumentUploadError,
    DocumentUploadItem,
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)

ALLOWED_SUFFIXES = {".md", ".txt"}
MAX_DOCUMENT_BYTES = 200_000
MAX_BATCH_FILES = 20
MAX_BATCH_BYTES = 2_000_000


def validate_upload_file(filename: str, content_type: str | None) -> None:
    suffix = Path(filename).suffix.lower()
    text_content_types = {"text/markdown", "text/plain"}
    if suffix not in ALLOWED_SUFFIXES and content_type not in text_content_types:
        raise ValueError("只支持上传 .md 或 .txt 文本文件")


def get_document_title(filename: str) -> str:
    title = Path(filename).stem.strip()
    if not title:
        raise ValueError("文件名不能为空")
    return title


async def read_upload_content(upload: UploadFile) -> tuple[str, str]:
    filename = (upload.filename or "").strip()
    validate_upload_file(filename, upload.content_type)
    raw_content = await upload.read()
    if len(raw_content) > MAX_DOCUMENT_BYTES:
        raise ValueError("文件不能超过 200KB")

    try:
        content = raw_content.decode("utf-8-sig").strip()
    except UnicodeDecodeError as error:
        raise ValueError("文件必须使用 UTF-8 编码保存") from error
    if not content:
        raise ValueError("上传的文件内容不能为空")
    return filename, content


def build_uploaded_document(filename: str, content: str) -> KnowledgeDocument:
    return KnowledgeDocument(
        title=get_document_title(filename),
        content=content,
        source=f"上传文件：{filename}",
        source_tier="unverified",
        updated_at=datetime.now(UTC),
    )


@router.post("", response_model=KnowledgeDocumentRead, status_code=201)
def create_document(
    document_data: KnowledgeDocumentCreate,
    current_user: User = Depends(require_admin),
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
    if document.visibility == "private":
        document.owner_user_id = current_user.id
    else:
        document.owner_user_id = None
    document.updated_at = datetime.now(UTC)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.post("/upload", response_model=KnowledgeDocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    try:
        filename, content = await read_upload_content(file)
        document = build_uploaded_document(filename, content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    duplicate = session.exec(
        select(KnowledgeDocument).where(
            KnowledgeDocument.title == document.title
        )
    ).first()
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="同名知识文档已经存在")

    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.post(
    "/upload-batch",
    response_model=DocumentUploadBatchResponse,
    status_code=201,
)
async def upload_documents(
    files: list[UploadFile] = File(...),
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """Import several text files and report per-file validation failures."""
    if not files:
        raise HTTPException(status_code=400, detail="至少选择一个文件")
    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=413,
            detail=f"一次最多上传 {MAX_BATCH_FILES} 个文件",
        )

    created_documents: list[tuple[str, KnowledgeDocument]] = []
    errors: list[DocumentUploadError] = []
    total_bytes = 0
    seen_titles: set[str] = set()

    for upload in files:
        filename = (upload.filename or "未命名文件").strip() or "未命名文件"
        try:
            filename, content = await read_upload_content(upload)
            total_bytes += len(content.encode("utf-8"))
            if total_bytes > MAX_BATCH_BYTES:
                raise ValueError("批量上传文件总大小不能超过 2MB")

            document = build_uploaded_document(filename, content)
            if document.title in seen_titles:
                raise ValueError("本次上传中存在同名文件")
            duplicate = session.exec(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.title == document.title
                )
            ).first()
            if duplicate is not None:
                raise ValueError("同名知识文档已经存在")

            seen_titles.add(document.title)
            session.add(document)
            created_documents.append((filename, document))
        except ValueError as error:
            errors.append(DocumentUploadError(filename=filename, detail=str(error)))

    session.commit()
    items: list[DocumentUploadItem] = []
    for filename, document in created_documents:
        session.refresh(document)
        items.append(
            DocumentUploadItem(
                filename=filename,
                title=document.title,
                document_id=document.id,
            )
        )

    return DocumentUploadBatchResponse(
        created_count=len(items),
        failed_count=len(errors),
        items=items,
        errors=errors,
    )


@router.get("", response_model=list[KnowledgeDocumentRead])
def list_documents(
    keyword: str | None = Query(default=None, max_length=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    statement = accessible_documents_statement(current_user).order_by(
        KnowledgeDocument.id
    )

    if keyword and keyword.strip():
        statement = statement.where(
            KnowledgeDocument.title.contains(keyword.strip())
        )

    return session.exec(statement).all()


@router.get("/{document_id}", response_model=KnowledgeDocumentRead)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = session.get(KnowledgeDocument, document_id)

    if document is None or not can_access_document(document, current_user):
        raise HTTPException(status_code=404, detail="知识文档不存在")

    return document


@router.put("/{document_id}", response_model=KnowledgeDocumentRead)
def update_document(
    document_id: int,
    document_data: KnowledgeDocumentCreate,
    current_user: User = Depends(require_admin),
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
    document.knowledge_base_id = document_data.knowledge_base_id
    document.visibility = document_data.visibility
    document.page_number = document_data.page_number
    document.owner_user_id = (
        current_user.id if document_data.visibility == "private" else None
    )
    document.updated_at = datetime.now(UTC)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    document = session.get(KnowledgeDocument, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="知识文档不存在")

    session.delete(document)
    session.commit()
