from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import Condition, Drug
from app.schemas import AskRequest, AskResponse


router = APIRouter(prefix="/ask", tags=["ask"])


def text_bigrams(text: str) -> set[str]:
    """把中文文本切成连续的两个字，作为轻量级关键词。"""
    normalized = "".join(character for character in text if character.isalnum())
    return {
        normalized[index : index + 2]
        for index in range(len(normalized) - 1)
    }


def relevance_score(question: str, content: str, name: str) -> int:
    """名称完全命中优先，其余情况按问题与内容的共同关键词计分。"""
    if name in question:
        return 100

    return len(text_bigrams(question) & text_bigrams(content))


@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    session: Session = Depends(get_session),
):
    """根据问题中出现的名称，从当前 SQLite 知识库检索内容。"""
    question = request.question
    answer_parts: list[str] = []

    condition_matches: list[tuple[int, Condition]] = []
    conditions = session.exec(select(Condition).order_by(Condition.id)).all()
    for condition in conditions:
        content = f"{condition.name}{condition.symptoms}{condition.treatment}"
        score = relevance_score(question, content, condition.name)
        if score > 0:
            condition_matches.append((score, condition))

    for _, condition in sorted(condition_matches, reverse=True, key=lambda item: item[0])[:3]:
        answer_parts.append(
            f"病症：{condition.name}\n"
            f"常见症状：{condition.symptoms}\n"
            f"处理建议：{condition.treatment}"
        )

    drug_matches: list[tuple[int, Drug]] = []
    drugs = session.exec(select(Drug).order_by(Drug.id)).all()
    for drug in drugs:
        content = f"{drug.name}{drug.effects}{drug.instructions}"
        score = relevance_score(question, content, drug.name)
        if score > 0:
            drug_matches.append((score, drug))

    for _, drug in sorted(drug_matches, reverse=True, key=lambda item: item[0])[:3]:
        answer_parts.append(
            f"药物：{drug.name}\n"
            f"作用：{drug.effects}\n"
            f"使用说明：{drug.instructions}"
        )

    if answer_parts:
        answer = "\n\n".join(answer_parts)
        answer += "\n\n提醒：以上是知识库中的通用信息，不代替医生诊断或处方。"
        source = "sqlite-knowledge-base"
    else:
        answer = (
            "当前知识库没有找到与问题直接匹配的病症或药物。"
            "你可以先在问题中写出具体名称，例如“普通感冒有哪些症状？”"
        )
        source = "sqlite-knowledge-base:no-match"

    return AskResponse(
        question=question,
        answer=answer,
        source=source,
    )
