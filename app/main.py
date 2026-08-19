import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlmodel import Session

load_dotenv()
if not os.getenv("OPENAI_BASE_URL", "").strip():
    os.environ.pop("OPENAI_BASE_URL", None)

from app.database import create_db_and_tables, get_session
from app.routers import (
    ask,
    conditions,
    conversations,
    documents,
    drugs,
    feedback,
    knowledge,
)
from app.schemas import HealthResponse
from app.vector_store import get_knowledge_status


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="医疗健康助手",
    description="基于 RAG 的医疗健康知识库问答系统",
    version="0.1.0",
    lifespan=lifespan,
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def application_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["system"], response_model=HealthResponse)
def health_check(session: Session = Depends(get_session)):
    try:
        session.exec(text("SELECT 1"))
        knowledge_status = get_knowledge_status(session)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="服务健康检查失败，请检查数据库和知识库配置",
        ) from error

    return HealthResponse(
        status="ok" if knowledge_status["is_current"] else "degraded",
        service="medical-health-assistant",
        database="connected",
        knowledge_base_current=knowledge_status["is_current"],
        document_count=knowledge_status["document_count"],
        chunk_count=knowledge_status["chunk_count"],
    )


app.include_router(conditions.router)
app.include_router(drugs.router)
app.include_router(ask.router)
app.include_router(knowledge.router)
app.include_router(conversations.router)
app.include_router(documents.router)
app.include_router(feedback.router)
