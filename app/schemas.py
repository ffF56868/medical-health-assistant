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


class AskRequest(SQLModel):
    question: str = Field(min_length=1, max_length=1000)

    _strip_question = field_validator("question", mode="before")(
        strip_required_text
    )


class AskResponse(SQLModel):
    question: str
    answer: str
    source: str


class KnowledgeRebuildResponse(SQLModel):
    message: str
    document_count: int
