from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.source_metadata import SOURCE_TIERS


def strip_required_text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("内容不能为空")
    return value.strip()


def validate_source_tier(value: str) -> str:
    normalized_value = strip_required_text(value)
    if normalized_value not in SOURCE_TIERS:
        raise ValueError("可信度等级必须是 authority、professional、general 或 unverified")
    return normalized_value


class SourceMetadataCreate(SQLModel):
    source: str = Field(default="未标注来源", min_length=1, max_length=200)
    source_tier: str = Field(default="unverified", min_length=1, max_length=20)

    _strip_source = field_validator("source", mode="before")(strip_required_text)
    _validate_source_tier = field_validator("source_tier", mode="before")(
        validate_source_tier
    )


class ConditionCreate(SourceMetadataCreate):
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
    updated_at: datetime | None = None


class DrugCreate(SourceMetadataCreate):
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
    updated_at: datetime | None = None


class KnowledgeDocumentCreate(SourceMetadataCreate):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)

    _strip_title = field_validator("title", mode="before")(strip_required_text)
    _strip_content = field_validator("content", mode="before")(strip_required_text)


class KnowledgeDocumentRead(KnowledgeDocumentCreate):
    id: int
    updated_at: datetime | None = None


KNOWLEDGE_TYPES = {"all", "condition", "drug", "document"}


def validate_knowledge_type(value: str) -> str:
    normalized_value = strip_required_text(value)
    if normalized_value not in KNOWLEDGE_TYPES:
        raise ValueError("检索范围必须是 all、condition、drug 或 document")
    return normalized_value


class AskRequest(SQLModel):
    question: str = Field(min_length=1, max_length=1000)
    conversation_id: str = Field(default="default", min_length=1, max_length=100)
    knowledge_type: str = Field(default="all", min_length=1, max_length=20)

    _strip_question = field_validator("question", mode="before")(
        strip_required_text
    )
    _strip_conversation_id = field_validator("conversation_id", mode="before")(
        strip_required_text
    )
    _validate_knowledge_type = field_validator("knowledge_type", mode="before")(
        validate_knowledge_type
    )


class ReferenceRead(SQLModel):
    name: str
    type: str
    source: str | None = None
    source_tier: str = "unverified"
    updated_at: datetime | None = None
    needs_review: bool = True
    excerpt: str
    relevance_score: float


class AskResponse(SQLModel):
    question: str
    answer: str
    source: str
    conversation_id: str
    assistant_message_id: int
    references: list[ReferenceRead] = Field(default_factory=list)
    processing_path: str
    retrieval_scope: str
    retrieved_count: int
    latency_ms: int


class ChatMessageRead(SQLModel):
    id: int
    conversation_id: str
    role: str
    content: str
    created_at: datetime


class ConversationSummary(SQLModel):
    conversation_id: str
    preview: str
    message_count: int
    updated_at: datetime


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


class FeedbackDetail(SQLModel):
    id: int
    assistant_message_id: int
    conversation_id: str
    question: str | None = None
    answer: str
    helpful: bool
    reason: str | None = None
    created_at: datetime


class FeedbackGroup(SQLModel):
    text: str
    count: int


class FeedbackImprovementSuggestions(SQLModel):
    not_helpful_count: int
    common_reasons: list[FeedbackGroup] = Field(default_factory=list)
    repeated_questions: list[FeedbackGroup] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class KnowledgeSearchItem(SQLModel):
    type: str
    record_id: int
    title: str
    source: str | None = None
    source_tier: str = "unverified"
    updated_at: datetime | None = None
    needs_review: bool = True
    matched_fields: list[str]
    excerpt: str


class KnowledgeSearchResponse(SQLModel):
    query: str
    total_count: int
    results: list[KnowledgeSearchItem] = Field(default_factory=list)


class KnowledgeReviewItem(SQLModel):
    type: str
    record_id: int
    title: str
    source: str
    source_tier: str
    updated_at: datetime | None = None
    review_reasons: list[str] = Field(default_factory=list)


class KnowledgeReviewResponse(SQLModel):
    total_count: int
    results: list[KnowledgeReviewItem] = Field(default_factory=list)


class RAGEvaluationCaseResult(SQLModel):
    case_id: str
    case_source: str
    question: str
    expected_name: str
    expected_type: str
    category: str
    alternative_names: list[str] = Field(default_factory=list)
    passed: bool
    expected_rank: int | None = None
    matched_name: str | None = None
    top_name: str | None = None
    top_type: str | None = None
    top_score: float | None = None


class RetrievalStrategyResult(SQLModel):
    passed: bool
    expected_rank: int | None = None
    matched_name: str | None = None
    top_name: str | None = None
    top_type: str | None = None
    top_score: float | None = None


class RetrievalComparisonCaseResult(SQLModel):
    case_id: str
    case_source: str
    question: str
    expected_name: str
    expected_type: str
    category: str
    alternative_names: list[str] = Field(default_factory=list)
    baseline: RetrievalStrategyResult
    current: RetrievalStrategyResult
    change: str


class RetrievalStrategySummary(SQLModel):
    passed_count: int
    pass_rate: float


class RetrievalComparisonResponse(SQLModel):
    total_count: int
    preset_count: int
    custom_count: int
    baseline: RetrievalStrategySummary
    current: RetrievalStrategySummary
    pass_rate_delta: float
    improved_count: int
    regressed_count: int
    unchanged_count: int
    results: list[RetrievalComparisonCaseResult] = Field(default_factory=list)


class RetrievalDiagnosticCandidate(SQLModel):
    rank: int
    name: str
    type: str
    relevance_score: float


class RetrievalDiagnosticCaseResult(SQLModel):
    case_id: str
    case_source: str
    question: str
    expected_name: str
    expected_type: str
    category: str
    alternative_names: list[str] = Field(default_factory=list)
    passed: bool
    expected_rank: int | None = None
    matched_name: str | None = None
    diagnostic_level: str
    diagnostic: str
    suggested_action: str
    candidates: list[RetrievalDiagnosticCandidate] = Field(default_factory=list)


class RetrievalDiagnosticResponse(SQLModel):
    total_count: int
    healthy_count: int
    attention_count: int
    failed_count: int
    results: list[RetrievalDiagnosticCaseResult] = Field(default_factory=list)


class RAGEvaluationCategoryMetric(SQLModel):
    category: str
    total_count: int
    passed_count: int
    pass_rate: float


class RAGEvaluationQualityGate(SQLModel):
    status: str
    compared_history_id: int | None = None
    message: str
    regressed_questions: list[str] = Field(default_factory=list)
    improved_questions: list[str] = Field(default_factory=list)
    new_questions: list[str] = Field(default_factory=list)
    rank_regressed_questions: list[str] = Field(default_factory=list)
    rank_improved_questions: list[str] = Field(default_factory=list)


class RAGEvaluationResponse(SQLModel):
    history_id: int
    total_count: int
    passed_count: int
    pass_rate: float
    preset_count: int
    custom_count: int
    category_metrics: list[RAGEvaluationCategoryMetric] = Field(default_factory=list)
    quality_gate: RAGEvaluationQualityGate
    results: list[RAGEvaluationCaseResult] = Field(default_factory=list)


class RAGEvaluationHistoryRead(SQLModel):
    id: int
    total_count: int
    passed_count: int
    pass_rate: float
    preset_count: int
    custom_count: int
    knowledge_document_count: int
    knowledge_hash: str | None = None
    created_at: datetime


class RAGEvaluationHistoryResponse(SQLModel):
    total_count: int
    runs: list[RAGEvaluationHistoryRead] = Field(default_factory=list)


EVALUATION_EXPECTED_TYPES = {"condition", "drug", "document"}


def validate_evaluation_expected_type(value: str) -> str:
    normalized_value = strip_required_text(value)
    if normalized_value not in EVALUATION_EXPECTED_TYPES:
        raise ValueError("目标资料类型必须是 condition、drug 或 document")
    return normalized_value


def normalize_alternative_names(value: list[str] | None) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("可接受资料名称必须是列表")

    names: list[str] = []
    for name in value:
        normalized_name = strip_required_text(name)
        if normalized_name not in names:
            names.append(normalized_name)

    if len(names) > 10:
        raise ValueError("最多可填写 10 个可接受资料名称")
    return names


class RAGEvaluationCaseCreate(SQLModel):
    question: str = Field(min_length=1, max_length=1000)
    expected_name: str = Field(min_length=1, max_length=200)
    expected_type: str = Field(min_length=1, max_length=20)
    category: str = Field(default="自定义", min_length=1, max_length=50)
    alternative_names: list[str] = Field(default_factory=list)

    _strip_question = field_validator("question", mode="before")(strip_required_text)
    _strip_expected_name = field_validator("expected_name", mode="before")(
        strip_required_text
    )
    _validate_expected_type = field_validator("expected_type", mode="before")(
        validate_evaluation_expected_type
    )
    _strip_category = field_validator("category", mode="before")(strip_required_text)
    _normalize_alternative_names = field_validator(
        "alternative_names", mode="before"
    )(normalize_alternative_names)


class RAGEvaluationCaseRead(RAGEvaluationCaseCreate):
    id: int
    created_at: datetime


class RAGEvaluationCaseListResponse(SQLModel):
    total_count: int
    cases: list[RAGEvaluationCaseRead] = Field(default_factory=list)


class KnowledgeRebuildResponse(SQLModel):
    message: str
    document_count: int
    chunk_count: int
    snapshot_id: int
    snapshot_created: bool


class KnowledgeVersionRead(SQLModel):
    id: int
    document_count: int
    reason: str
    created_at: datetime
    is_current: bool


class KnowledgeVersionListResponse(SQLModel):
    total_count: int
    versions: list[KnowledgeVersionRead] = Field(default_factory=list)


class KnowledgeRestoreResponse(SQLModel):
    message: str
    restored_version_id: int
    backup_version_id: int
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
