import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
if not os.getenv("OPENAI_BASE_URL", "").strip():
    os.environ.pop("OPENAI_BASE_URL", None)

from app.database import create_db_and_tables
from app.routers import ask, conditions, drugs, knowledge


app = FastAPI(
    title="医疗健康助手",
    description="基于 RAG 的医疗健康知识库问答系统",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": "medical-health-assistant",
    }


app.include_router(conditions.router)
app.include_router(drugs.router)
app.include_router(ask.router)
app.include_router(knowledge.router)
