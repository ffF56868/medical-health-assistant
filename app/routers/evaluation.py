import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import KnowledgeIndexState, RAGEvaluationCase, RAGEvaluationRun
from app.routers.auth import require_admin
from app.schemas import (
    RAGEvaluationCaseCreate,
    RAGEvaluationCaseListResponse,
    RAGEvaluationCaseRead,
    RAGEvaluationCaseResult,
    RAGEvaluationCategoryMetric,
    RAGEvaluationHistoryRead,
    RAGEvaluationHistoryResponse,
    RAGEvaluationQualityGate,
    RAGEvaluationResponse,
    RetrievalDiagnosticCandidate,
    RetrievalDiagnosticCaseResult,
    RetrievalDiagnosticResponse,
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


router = APIRouter(
    prefix="/evaluation",
    tags=["evaluation"],
    dependencies=[Depends(require_admin)],
)
BASELINE_RETRIEVAL_COUNT = 3

# These cases intentionally verify retrieval only, not medical conclusions.
EVALUATION_CASES = (
    {
        "case_id": "drug-ibuprofen",
        "question": "布洛芬有什么作用？",
        "expected_name": "布洛芬",
        "expected_type": "drug",
        "category": "用药信息",
        "case_source": "默认题",
    },
    {
        "case_id": "sleep-guidance",
        "question": "睡眠不足时有哪些通用健康建议？",
        "expected_name": "睡眠健康提示",
        "expected_type": "document",
        "category": "生活方式",
        "case_source": "默认题",
    },
    {
        "case_id": "common-cold-symptoms",
        "question": "鼻塞、流鼻涕和打喷嚏的相关资料是什么？",
        "expected_name": "普通感冒",
        "expected_type": "condition",
        "category": "症状相关",
        "alternative_names": ["过敏性鼻炎"],
        "case_source": "默认题",
    },
    {
        "case_id": "urgent-warning-signs",
        "question": "呼吸困难或持续胸痛时有哪些警示信号？",
        "expected_name": "需要及时就医的警示信号",
        "expected_type": "document",
        "category": "紧急警示",
        "case_source": "默认题",
    },
    {
        "case_id": "drug-acetaminophen",
        "question": "对乙酰氨基酚常用于缓解什么不适？",
        "expected_name": "对乙酰氨基酚",
        "expected_type": "drug",
        "category": "用药信息",
        "case_source": "默认题",
    },
    {
        "case_id": "drug-loratadine",
        "question": "鼻痒、喷嚏和流清鼻涕的相关药物资料是什么？",
        "expected_name": "氯雷他定",
        "expected_type": "drug",
        "category": "用药信息",
        "case_source": "默认题",
    },
    {
        "case_id": "drug-amoxicillin-safety",
        "question": "阿莫西林对普通感冒有什么提示？",
        "expected_name": "阿莫西林",
        "expected_type": "drug",
        "category": "用药信息",
        "case_source": "默认题",
    },
    {
        "case_id": "drug-oseltamivir",
        "question": "奥司他韦主要用于什么情况？",
        "expected_name": "奥司他韦",
        "expected_type": "drug",
        "category": "用药信息",
        "case_source": "默认题",
    },
    {
        "case_id": "drug-diosmectite",
        "question": "急性腹泻的对症处理可参考什么药物资料？",
        "expected_name": "蒙脱石散",
        "expected_type": "drug",
        "category": "用药信息",
        "case_source": "默认题",
    },
    {
        "case_id": "influenza-symptoms",
        "question": "发热、肌肉酸痛和乏力的相关病症资料是什么？",
        "expected_name": "流行性感冒",
        "expected_type": "condition",
        "category": "症状相关",
        "case_source": "默认题",
    },
    {
        "case_id": "reflux-symptoms",
        "question": "反酸、烧心且饭后躺下加重的相关病症资料是什么？",
        "expected_name": "胃食管反流",
        "expected_type": "condition",
        "category": "症状相关",
        "case_source": "默认题",
    },
    {
        "case_id": "migraine-symptoms",
        "question": "反复搏动性头痛并伴随畏光的相关病症资料是什么？",
        "expected_name": "偏头痛",
        "expected_type": "condition",
        "category": "症状相关",
        "case_source": "默认题",
    },
)


def get_alternative_names(case: dict) -> list[str]:
    raw_names = case.get("alternative_names", [])
    if not isinstance(raw_names, list):
        return []
    return [name for name in raw_names if isinstance(name, str)]


def get_case_category(case: dict) -> str:
    category = case.get("category")
    return category.strip() if isinstance(category, str) and category.strip() else "未分类"


def normalize_evaluation_case(case: dict) -> dict:
    normalized_case = dict(case)
    normalized_case["category"] = get_case_category(case)
    normalized_case["alternative_names"] = get_alternative_names(case)
    return normalized_case


def get_acceptable_names(case: dict) -> set[str]:
    return {str(case["expected_name"]), *get_alternative_names(case)}


def build_strategy_result(
    matches: list[tuple[object, float]],
    case: dict,
) -> RetrievalStrategyResult:
    top_name = None
    top_type = None
    top_score = None
    expected_rank = None
    matched_name = None
    acceptable_names = get_acceptable_names(case)

    for rank, (document, score) in enumerate(matches, start=1):
        if rank == 1:
            top_name = document.metadata.get("name")
            top_type = document.metadata.get("type")
            top_score = round(score, 3)
        if (
            score >= MIN_RELEVANCE_SCORE
            and document.metadata.get("name") in acceptable_names
            and document.metadata.get("type") == case["expected_type"]
        ):
            expected_rank = rank
            matched_name = str(document.metadata.get("name"))
            break

    return RetrievalStrategyResult(
        passed=expected_rank is not None,
        expected_rank=expected_rank,
        matched_name=matched_name,
        top_name=top_name,
        top_type=top_type,
        top_score=top_score,
    )


def evaluate_baseline_case(
    vector_store: object,
    case: dict,
) -> RetrievalStrategyResult:
    matches = vector_store.similarity_search_with_relevance_scores(
        case["question"],
        k=BASELINE_RETRIEVAL_COUNT,
    )
    return build_strategy_result(matches, case)


def evaluate_current_case(
    vector_store: object,
    case: dict,
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


def evaluate_case(vector_store: object, case: dict) -> RAGEvaluationCaseResult:
    result = evaluate_current_case(vector_store, case)
    return RAGEvaluationCaseResult(**case, **result.model_dump())


def compare_case(
    vector_store: object,
    case: dict,
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


def get_match_name(document: object) -> str:
    return str(getattr(document, "metadata", {}).get("name", "未命名资料"))


def get_match_type(document: object) -> str:
    return str(getattr(document, "metadata", {}).get("type", "unknown"))


def build_diagnostic_case(
    vector_store: object,
    case: dict,
) -> RetrievalDiagnosticCaseResult:
    raw_matches = vector_store.similarity_search_with_relevance_scores(
        case["question"],
        k=RAG_RETRIEVAL_FETCH_COUNT,
    )
    selected_matches = select_distinct_relevant_matches(
        raw_matches,
        limit=RAG_RETRIEVAL_RESULT_COUNT,
    )
    strategy_result = build_strategy_result(selected_matches, case)
    candidates = [
        RetrievalDiagnosticCandidate(
            rank=rank,
            name=get_match_name(document),
            type=get_match_type(document),
            relevance_score=round(score, 3),
        )
        for rank, (document, score) in enumerate(selected_matches, start=1)
    ]
    acceptable_names = get_acceptable_names(case)
    expected_raw_match = next(
        (
            (rank, score, get_match_name(document))
            for rank, (document, score) in enumerate(raw_matches, start=1)
            if get_match_name(document) in acceptable_names
            and get_match_type(document) == case["expected_type"]
        ),
        None,
    )

    if strategy_result.expected_rank == 1:
        diagnostic_level = "healthy"
        diagnostic = (
            f"可接受资料“{strategy_result.matched_name}”位于首位，"
            "当前检索表现正常。"
        )
        suggested_action = "暂不需要为这道题调整资料或检索参数。"
    elif strategy_result.expected_rank is not None:
        diagnostic_level = "attention"
        diagnostic = (
            f"可接受资料“{strategy_result.matched_name}”命中第 "
            f"{strategy_result.expected_rank} 条，"
            "能被找到，但前面还有更相近的资料。"
        )
        suggested_action = (
            "可在目标资料标题或正文中补充用户会使用的关键词，"
            "再运行评测确认排名变化。"
        )
    elif expected_raw_match is None:
        diagnostic_level = "failed"
        diagnostic = "目标资料没有进入前 8 个向量候选，语义关联不足。"
        suggested_action = (
            "检查目标资料是否缺少问题中的核心词，或补充更直接对应的资料内容。"
        )
    elif expected_raw_match[1] < MIN_RELEVANCE_SCORE:
        diagnostic_level = "failed"
        diagnostic = (
            f"可接受资料“{expected_raw_match[2]}”进入候选的第 "
            f"{expected_raw_match[0]} 条，"
            f"但相关度 {expected_raw_match[1]:.3f} 低于阈值 {MIN_RELEVANCE_SCORE}。"
        )
        suggested_action = (
            "在资料标题和正文中补充问题常用的表达，再重建知识库并运行评测。"
        )
    else:
        diagnostic_level = "failed"
        diagnostic = (
            f"可接受资料“{expected_raw_match[2]}”进入候选的第 "
            f"{expected_raw_match[0]} 条，"
            "但被更高相关度的不同资料挤出了最终前 3 条。"
        )
        suggested_action = (
            "补充目标资料的关键词或内容；若业务确实需要更多来源，可再评估是否调整最终保留数量。"
        )

    return RetrievalDiagnosticCaseResult(
        **case,
        passed=strategy_result.passed,
        expected_rank=strategy_result.expected_rank,
        matched_name=strategy_result.matched_name,
        diagnostic_level=diagnostic_level,
        diagnostic=diagnostic,
        suggested_action=suggested_action,
        candidates=candidates,
    )


def get_record_alternative_names(record: RAGEvaluationCase) -> list[str]:
    try:
        parsed_names = json.loads(record.alternative_names_json)
    except json.JSONDecodeError:
        return []
    return parsed_names if isinstance(parsed_names, list) else []


def get_run_result_snapshot(run: RAGEvaluationRun) -> list[dict]:
    try:
        snapshot = json.loads(run.results_json)
    except (json.JSONDecodeError, TypeError):
        return []
    return snapshot if isinstance(snapshot, list) else []


def get_latest_result_snapshot(
    session: Session,
) -> tuple[RAGEvaluationRun | None, list[dict]]:
    runs = session.exec(
        select(RAGEvaluationRun).order_by(RAGEvaluationRun.created_at.desc())
    ).all()
    for run in runs:
        snapshot = get_run_result_snapshot(run)
        if snapshot:
            return run, snapshot
    return None, []


def build_result_snapshot(results: list[RAGEvaluationCaseResult]) -> list[dict]:
    return [
        {
            "case_id": result.case_id,
            "question": result.question,
            "category": result.category,
            "passed": result.passed,
            "expected_rank": result.expected_rank,
        }
        for result in results
    ]


def build_category_metrics(
    results: list[RAGEvaluationCaseResult],
) -> list[RAGEvaluationCategoryMetric]:
    totals: dict[str, int] = {}
    passed_counts: dict[str, int] = {}
    for result in results:
        category = result.category
        totals[category] = totals.get(category, 0) + 1
        passed_counts[category] = passed_counts.get(category, 0) + int(result.passed)

    return [
        RAGEvaluationCategoryMetric(
            category=category,
            total_count=total,
            passed_count=passed_counts[category],
            pass_rate=passed_counts[category] / total,
        )
        for category, total in totals.items()
    ]


def build_quality_gate(
    results: list[RAGEvaluationCaseResult],
    previous_run: RAGEvaluationRun | None,
    previous_snapshot: list[dict],
) -> RAGEvaluationQualityGate:
    if previous_run is None:
        return RAGEvaluationQualityGate(
            status="baseline",
            message="已保存本次评测明细，下一次运行时将自动检查检索能力是否回退。",
        )

    previous_results = {
        item.get("case_id"): item
        for item in previous_snapshot
        if isinstance(item, dict) and isinstance(item.get("case_id"), str)
    }
    regressed_questions: list[str] = []
    improved_questions: list[str] = []
    new_questions: list[str] = []
    rank_regressed_questions: list[str] = []
    rank_improved_questions: list[str] = []
    for result in results:
        previous_result = previous_results.get(result.case_id)
        if previous_result is None:
            new_questions.append(result.question)
            continue
        previous_passed = previous_result.get("passed")
        if previous_passed is True and not result.passed:
            regressed_questions.append(result.question)
        elif previous_passed is False and result.passed:
            improved_questions.append(result.question)
        else:
            previous_rank = previous_result.get("expected_rank")
            current_rank = result.expected_rank
            if (
                previous_passed is True
                and result.passed
                and isinstance(previous_rank, int)
                and current_rank is not None
            ):
                if current_rank > previous_rank:
                    rank_regressed_questions.append(result.question)
                elif current_rank < previous_rank:
                    rank_improved_questions.append(result.question)

    if regressed_questions:
        return RAGEvaluationQualityGate(
            status="warning",
            compared_history_id=previous_run.id,
            message=(
                f"发现 {len(regressed_questions)} 道题从通过变为未通过，"
                "建议检查本次知识库或检索改动。"
            ),
            regressed_questions=regressed_questions,
            improved_questions=improved_questions,
            new_questions=new_questions,
            rank_regressed_questions=rank_regressed_questions,
            rank_improved_questions=rank_improved_questions,
        )
    if rank_regressed_questions:
        return RAGEvaluationQualityGate(
            status="attention",
            compared_history_id=previous_run.id,
            message=(
                f"有 {len(rank_regressed_questions)} 道题仍然通过，"
                "但目标资料的排名下降了。"
            ),
            rank_regressed_questions=rank_regressed_questions,
            rank_improved_questions=rank_improved_questions,
            new_questions=new_questions,
        )
    if improved_questions or rank_improved_questions:
        message = (
            f"本次有 {len(improved_questions)} 道题从未通过变为通过，"
            "且没有发现回退。"
            if improved_questions
            else (
                f"本次有 {len(rank_improved_questions)} 道题的目标资料排名提升，"
                "且没有发现回退。"
            )
        )
        return RAGEvaluationQualityGate(
            status="improved",
            compared_history_id=previous_run.id,
            message=message,
            improved_questions=improved_questions,
            new_questions=new_questions,
            rank_improved_questions=rank_improved_questions,
        )
    if new_questions:
        return RAGEvaluationQualityGate(
            status="expanded",
            compared_history_id=previous_run.id,
            message=(
                f"本次新增 {len(new_questions)} 道评测题；"
                "已有题没有发现通过状态回退。"
            ),
            new_questions=new_questions,
        )
    return RAGEvaluationQualityGate(
        status="stable",
        compared_history_id=previous_run.id,
        message="与上一次保存的评测明细相比，没有发现通过状态回退。",
    )


def serialize_evaluation_case(record: RAGEvaluationCase) -> RAGEvaluationCaseRead:
    return RAGEvaluationCaseRead(
        id=record.id,
        question=record.question,
        expected_name=record.expected_name,
        expected_type=record.expected_type,
        category=record.category,
        alternative_names=get_record_alternative_names(record),
        created_at=record.created_at,
    )


def build_custom_case(record: RAGEvaluationCase) -> dict:
    return {
        "case_id": f"custom-{record.id}",
        "case_source": "自定义题",
        "question": record.question,
        "expected_name": record.expected_name,
        "expected_type": record.expected_type,
        "category": record.category,
        "alternative_names": get_record_alternative_names(record),
    }


def get_evaluation_cases(session: Session) -> tuple[list[dict], int]:
    custom_cases = session.exec(
        select(RAGEvaluationCase).order_by(RAGEvaluationCase.created_at)
    ).all()
    cases = [
        *(normalize_evaluation_case(case) for case in EVALUATION_CASES),
        *(normalize_evaluation_case(build_custom_case(case)) for case in custom_cases),
    ]
    return cases, len(custom_cases)


@router.get("/cases", response_model=RAGEvaluationCaseListResponse)
def list_evaluation_cases(session: Session = Depends(get_session)):
    cases = session.exec(
        select(RAGEvaluationCase).order_by(RAGEvaluationCase.created_at.desc())
    ).all()
    return RAGEvaluationCaseListResponse(
        total_count=len(cases),
        cases=[serialize_evaluation_case(case) for case in cases],
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
    payload_data = payload.model_dump()
    alternative_names = payload_data.pop("alternative_names")
    case = RAGEvaluationCase(
        **payload_data,
        alternative_names_json=json.dumps(alternative_names, ensure_ascii=False),
    )
    session.add(case)
    session.commit()
    session.refresh(case)
    return serialize_evaluation_case(case)


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
    previous_run, previous_snapshot = get_latest_result_snapshot(session)
    quality_gate = build_quality_gate(results, previous_run, previous_snapshot)
    run = RAGEvaluationRun(
        total_count=total_count,
        passed_count=passed_count,
        pass_rate=pass_rate,
        preset_count=len(EVALUATION_CASES),
        custom_count=custom_count,
        knowledge_document_count=knowledge_status.get("document_count", 0),
        knowledge_hash=knowledge_index.content_hash if knowledge_index else None,
        results_json=json.dumps(build_result_snapshot(results), ensure_ascii=False),
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
        category_metrics=build_category_metrics(results),
        quality_gate=quality_gate,
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


@router.post("/diagnose", response_model=RetrievalDiagnosticResponse)
def diagnose_retrieval(session: Session = Depends(get_session)):
    """Explain why each evaluation target did or did not reach the live top three."""
    knowledge_status = get_knowledge_status(session)
    if not knowledge_status["is_current"]:
        raise HTTPException(
            status_code=409,
            detail="知识库已过期，请先重建知识库后再运行检索诊断",
        )

    try:
        vector_store = get_vector_store()
        cases, _ = get_evaluation_cases(session)
        results = [build_diagnostic_case(vector_store, case) for case in cases]
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="检索诊断暂时不可用，请检查知识库和 Embedding 配置",
        ) from error

    return RetrievalDiagnosticResponse(
        total_count=len(results),
        healthy_count=sum(result.diagnostic_level == "healthy" for result in results),
        attention_count=sum(
            result.diagnostic_level == "attention" for result in results
        ),
        failed_count=sum(result.diagnostic_level == "failed" for result in results),
        results=results,
    )
