from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel


def strip_required_text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("内容不能为空")
    return value.strip()


class ConditionCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    symptoms: str = Field(min_length=1, max_length=5000)
    treatment: str = Field(min_length=1, max_length=5000)

    _strip_name = field_validator("name", mode="before")(strip_required_text)
    _strip_symptoms = field_validator("symptoms", mode="before")(
        strip_required_text
    )
    _strip_treatment = field_validator("treatment", mode="before")(
        strip_required_text
    )


class ConditionRead(ConditionCreate):
    id: int


class DrugCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    effects: str = Field(min_length=1, max_length=5000)
    instructions: str = Field(min_length=1, max_length=5000)

    _strip_name = field_validator("name", mode="before")(strip_required_text)
    _strip_effects = field_validator("effects", mode="before")(
        strip_required_text
    )
    _strip_instructions = field_validator("instructions", mode="before")(
        strip_required_text
    )


class DrugRead(DrugCreate):
    id: int


class KnowledgeDocumentCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    source: str = Field(default="manual", min_length=1, max_length=200)

    _strip_title = field_validator("title", mode="before")(strip_required_text)
    _strip_content = field_validator("content", mode="before")(strip_required_text)
    _strip_source = field_validator("source", mode="before")(strip_required_text)


class KnowledgeDocumentRead(KnowledgeDocumentCreate):
    id: int


class AskRequest(SQLModel):
    question: str = Field(min_length=1, max_length=1000)
    conversation_id: str = Field(default="default", min_length=1, max_length=100)

    _strip_question = field_validator("question", mode="before")(
        strip_required_text
    )
    _strip_conversation_id = field_validator("conversation_id", mode="before")(
        strip_required_text
    )


class ReferenceRead(SQLModel):
    name: str
    type: str
    source: str | None = None
    excerpt: str
    relevance_score: float


class AskResponse(SQLModel):
    question: str
    answer: str
    source: str
    conversation_id: str
    assistant_message_id: int
    references: list[ReferenceRead] = Field(default_factory=list)


class ChatMessageRead(SQLModel):
    id: int
    conversation_id: str
    role: str
    content: str
    created_at: datetime


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


class FeedbackCreate(SQLModel):
    assistant_message_id: int = Field(gt=0)
    helpful: bool
    reason: str | None = Field(default=None, max_length=1000)

    _normalize_reason = field_validator("reason", mode="before")(
        normalize_optional_text
    )


class FeedbackRead(FeedbackCreate):
    id: int
    created_at: datetime


class FeedbackSummary(SQLModel):
    total_count: int
    helpful_count: int
    not_helpful_count: int
    helpful_rate: float | None = None


class KnowledgeRebuildResponse(SQLModel):
    message: str
    document_count: int
    chunk_count: int


class KnowledgeStatusResponse(SQLModel):
    is_current: bool
    document_count: int
    chunk_count: int
    indexed_document_count: int | None = None
    indexed_at: datetime | None = None


class HealthResponse(SQLModel):
    status: str
    service: str
    database: str
    knowledge_base_current: bool
    document_count: int
    chunk_count: int
