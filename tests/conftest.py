from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.database import get_session
from app.routers import ask, conditions, conversations, documents, drugs, feedback, knowledge


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(test_engine) -> Generator[TestClient, None, None]:
    test_app = FastAPI()
    test_app.include_router(conditions.router)
    test_app.include_router(drugs.router)
    test_app.include_router(ask.router)
    test_app.include_router(knowledge.router)
    test_app.include_router(conversations.router)
    test_app.include_router(documents.router)
    test_app.include_router(feedback.router)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session
    with TestClient(test_app) as test_client:
        yield test_client
