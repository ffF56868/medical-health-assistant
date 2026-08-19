from datetime import datetime

from sqlmodel import Field, SQLModel


class Condition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    symptoms: str = Field(max_length=5000)
    treatment: str = Field(max_length=5000)


class Drug(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    effects: str = Field(max_length=5000)
    instructions: str = Field(max_length=5000)


class KnowledgeDocument(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    content: str = Field(max_length=20000)
    source: str = Field(default="manual", max_length=200)


class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True, max_length=100)
    role: str = Field(max_length=20)
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class AnswerFeedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    assistant_message_id: int = Field(index=True, unique=True)
    helpful: bool
    reason: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class KnowledgeIndexState(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    content_hash: str = Field(max_length=64)
    document_count: int
    indexed_at: datetime = Field(default_factory=datetime.utcnow)
