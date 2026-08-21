from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Condition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    symptoms: str = Field(max_length=5000)
    treatment: str = Field(max_length=5000)
    source: str = Field(default="未标注来源", max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    source_tier: str = Field(default="unverified", max_length=20)
    updated_at: datetime | None = Field(default=None)


class Drug(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    effects: str = Field(max_length=5000)
    instructions: str = Field(max_length=5000)
    source: str = Field(default="未标注来源", max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    source_tier: str = Field(default="unverified", max_length=20)
    updated_at: datetime | None = Field(default=None)


class KnowledgeDocument(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    content: str = Field(max_length=20000)
    source: str = Field(default="未标注来源", max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    source_tier: str = Field(default="unverified", max_length=20)
    updated_at: datetime | None = Field(default=None)


class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True, max_length=100)
    role: str = Field(max_length=20)
    content: str = Field(max_length=10000)
    response_metadata_json: str = Field(default="{}", max_length=30000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
    )


class AnswerFeedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    assistant_message_id: int = Field(index=True, unique=True)
    helpful: bool
    reason: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
    )


class KnowledgeIndexState(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    content_hash: str = Field(max_length=64)
    document_count: int
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class KnowledgeSnapshot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content_hash: str = Field(index=True, max_length=64)
    document_count: int
    reason: str = Field(default="rebuild", max_length=50)
    payload_json: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
    )


class RAGEvaluationCase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question: str = Field(max_length=1000)
    expected_name: str = Field(max_length=200)
    expected_type: str = Field(max_length=20)
    category: str = Field(default="自定义", max_length=50)
    alternative_names_json: str = Field(default="[]", max_length=2000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
    )


class RAGEvaluationRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    total_count: int
    passed_count: int
    pass_rate: float
    preset_count: int
    custom_count: int
    knowledge_document_count: int
    knowledge_hash: str | None = Field(default=None, max_length=64)
    results_json: str = Field(default="[]")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
    )
