from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import KnowledgeIndexState, RAGEvaluationCase, RAGEvaluationRun
from app.schemas import (
    RAGEvaluationCaseCreate,
    RAGEvaluationCaseListResponse,
    RAGEvaluationCaseRead,
    RAGEvaluationCaseResult,
    RAGEvaluationHistoryRead,
    RAGEvaluationHistoryResponse,
    RAGEvaluationResponse,
    RetrievalComparisonCaseResult,
    RetrievalComparisonResponse,
    RetrievalStrategyResult,
    RetrievalStrategySummary,
)
from app.vector_store import (
    MIN_RELEVANCE_SCORE,
    RAG_RETRIEVAL_FETCH_COUNT,
    RAG_RETRIEVAL_RESULT_COUNT,
    get_knowledge_status,
    get_vector_store,
    select_distinct_relevant_matches,
)


router = APIRouter(prefix="/evaluation", tags=["evaluation"])
BASELINE_RETRIEVAL_COUNT = 3

# These cases intentionally verify retrieval only, not medical conclusions.
EVALUATION_CASES = (
    {
        "case_id": "drug-ibuprofen",
        "question": "布洛芬有什么作用？",
        "expected_name": "布洛芬",
        "expected_type": "drug",
        "case_source": "默认题",
    },
    {
        "case_id": "sleep-guidance",
        "question": "睡眠不足时有哪些通用健康建议？",
        "expected_name": "睡眠健康提示",
        "expected_type": "document",
        "case_source": "默认题",
    },
    {
        "case_id": "common-cold-symptoms",
        "question": "鼻塞、流鼻涕和打喷嚏的相关资料是什么？",
        "expected_name": "普通感冒",
        "expected_type": "condition",
        "case_source": "默认题",
    },
    {
        "case_id": "urgent-warning-signs",
        "question": "呼吸困难或持续胸痛时有哪些警示信号？",
        "expected_name": "需要及时就医的警示信号",
        "expected_type": "document",
        "case_source": "默认题",
    },
)


def build_strategy_result(
    matches: list[tuple[object, float]],
    case: dict[str, str],
) -> RetrievalStrategyResult:
    top_name = None
    top_type = None
    top_score = None
    expected_rank = None

    for rank, (document, score) in enumerate(matches, start=1):
        if rank == 1:
            top_name = document.metadata.get("name")
            top_type = document.metadata.get("type")
            top_score = round(score, 3)
        if (
            score >= MIN_RELEVANCE_SCORE
            and document.metadata.get("name") == case["expected_name"]
            and document.metadata.get("type") == case["expected_type"]
        ):
            expected_rank = rank
            break

    return RetrievalStrategyResult(
        passed=expected_rank is not None,
        expected_rank=expected_rank,
        top_name=top_name,
        top_type=top_type,
        top_score=top_score,
    )


def evaluate_baseline_case(
    vector_store: object,
    case: dict[str, str],
) -> RetrievalStrategyResult:
    matches = vector_store.similarity_search_with_relevance_scores(
        case["question"],
        k=BASELINE_RETRIEVAL_COUNT,
    )
    return build_strategy_result(matches, case)


def evaluate_current_case(
    vector_store: object,
    case: dict[str, str],
) -> RetrievalStrategyResult:
    matches = vector_store.similarity_search_with_relevance_scores(
        case["question"],
        k=RAG_RETRIEVAL_FETCH_COUNT,
    )
    return build_strategy_result(
        select_distinct_relevant_matches(
            matches,
            limit=RAG_RETRIEVAL_RESULT_COUNT,
        ),
        case,
    )


def evaluate_case(vector_store: object, case: dict[str, str]) -> RAGEvaluationCaseResult:
    result = evaluate_current_case(vector_store, case)
    return RAGEvaluationCaseResult(**case, **result.model_dump())


def compare_case(
    vector_store: object,
    case: dict[str, str],
) -> RetrievalComparisonCaseResult:
    baseline = evaluate_baseline_case(vector_store, case)
    current = evaluate_current_case(vector_store, case)
    baseline_rank = baseline.expected_rank or (RAG_RETRIEVAL_RESULT_COUNT + 1)
    current_rank = current.expected_rank or (RAG_RETRIEVAL_RESULT_COUNT + 1)
    if current_rank < baseline_rank:
        change = "improved"
    elif current_rank > baseline_rank:
        change = "regressed"
    else:
        change = "unchanged"
    return RetrievalComparisonCaseResult(
        **case,
        baseline=baseline,
        current=current,
        change=change,
    )


def build_custom_case(record: RAGEvaluationCase) -> dict[str, str]:
    return {
        "case_id": f"custom-{record.id}",
        "case_source": "自定义题",
        "question": record.question,
        "expected_name": record.expected_name,
        "expected_type": record.expected_type,
    }


def get_evaluation_cases(session: Session) -> tuple[list[dict[str, str]], int]:
    custom_cases = session.exec(
        select(RAGEvaluationCase).order_by(RAGEvaluationCase.created_at)
    ).all()
    return [*EVALUATION_CASES, *(build_custom_case(case) for case in custom_cases)], len(
        custom_cases
    )


@router.get("/cases", response_model=RAGEvaluationCaseListResponse)
def list_evaluation_cases(session: Session = Depends(get_session)):
    cases = session.exec(
        select(RAGEvaluationCase).order_by(RAGEvaluationCase.created_at.desc())
    ).all()
    return RAGEvaluationCaseListResponse(
        total_count=len(cases),
        cases=[RAGEvaluationCaseRead.model_validate(case) for case in cases],
    )


@router.post(
    "/cases",
    response_model=RAGEvaluationCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_evaluation_case(
    payload: RAGEvaluationCaseCreate,
    session: Session = Depends(get_session),
):
    case = RAGEvaluationCase(**payload.model_dump())
    session.add(case)
    session.commit()
    session.refresh(case)
    return RAGEvaluationCaseRead.model_validate(case)


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evaluation_case(case_id: int, session: Session = Depends(get_session)):
    case = session.get(RAGEvaluationCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="自定义评测题不存在")
    session.delete(case)
    session.commit()


@router.get("/history", response_model=RAGEvaluationHistoryResponse)
def list_evaluation_history(
    limit: int = 20,
    session: Session = Depends(get_session),
):
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="历史记录数量必须在 1 到 100 之间")
    runs = session.exec(
        select(RAGEvaluationRun)
        .order_by(RAGEvaluationRun.created_at.desc())
        .limit(limit)
    ).all()
    return RAGEvaluationHistoryResponse(
        total_count=len(session.exec(select(RAGEvaluationRun)).all()),
        runs=[RAGEvaluationHistoryRead.model_validate(run) for run in runs],
    )


@router.post("/run", response_model=RAGEvaluationResponse)
def run_rag_evaluation(session: Session = Depends(get_session)):
    knowledge_status = get_knowledge_status(session)
    if not knowledge_status["is_current"]:
        raise HTTPException(
            status_code=409,
            detail="知识库已过期，请先重建知识库后再运行评测",
        )

    try:
        vector_store = get_vector_store()
        cases, custom_count = get_evaluation_cases(session)
        results = [evaluate_case(vector_store, case) for case in cases]
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="RAG 评测暂时不可用，请检查知识库和 Embedding 配置",
        ) from error

    passed_count = sum(result.passed for result in results)
    total_count = len(results)
    pass_rate = passed_count / total_count if total_count else 0
    knowledge_index = session.get(KnowledgeIndexState, 1)
    run = RAGEvaluationRun(
        total_count=total_count,
        passed_count=passed_count,
        pass_rate=pass_rate,
        preset_count=len(EVALUATION_CASES),
        custom_count=custom_count,
        knowledge_document_count=knowledge_status.get("document_count", 0),
        knowledge_hash=knowledge_index.content_hash if knowledge_index else None,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return RAGEvaluationResponse(
        history_id=run.id,
        total_count=total_count,
        passed_count=passed_count,
        pass_rate=pass_rate,
        preset_count=len(EVALUATION_CASES),
        custom_count=custom_count,
        results=results,
    )


@router.post("/compare", response_model=RetrievalComparisonResponse)
def compare_retrieval_strategies(session: Session = Depends(get_session)):
    """Compare the pre-deduplication top-three search with the live RAG strategy."""
    knowledge_status = get_knowledge_status(session)
    if not knowledge_status["is_current"]:
        raise HTTPException(
            status_code=409,
            detail="知识库已过期，请先重建知识库后再运行检索对比",
        )

    try:
        vector_store = get_vector_store()
        cases, custom_count = get_evaluation_cases(session)
        results = [compare_case(vector_store, case) for case in cases]
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="检索对比暂时不可用，请检查知识库和 Embedding 配置",
        ) from error

    total_count = len(results)
    baseline_passed_count = sum(result.baseline.passed for result in results)
    current_passed_count = sum(result.current.passed for result in results)
    baseline_pass_rate = baseline_passed_count / total_count if total_count else 0
    current_pass_rate = current_passed_count / total_count if total_count else 0
    return RetrievalComparisonResponse(
        total_count=total_count,
        preset_count=len(EVALUATION_CASES),
        custom_count=custom_count,
        baseline=RetrievalStrategySummary(
            passed_count=baseline_passed_count,
            pass_rate=baseline_pass_rate,
        ),
        current=RetrievalStrategySummary(
            passed_count=current_passed_count,
            pass_rate=current_pass_rate,
        ),
        pass_rate_delta=current_pass_rate - baseline_pass_rate,
        improved_count=sum(result.change == "improved" for result in results),
        regressed_count=sum(result.change == "regressed" for result in results),
        unchanged_count=sum(result.change == "unchanged" for result in results),
        results=results,
    )
