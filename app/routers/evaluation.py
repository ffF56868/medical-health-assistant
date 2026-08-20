from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas import RAGEvaluationCaseResult, RAGEvaluationResponse
from app.vector_store import get_knowledge_status, get_vector_store


router = APIRouter(prefix="/evaluation", tags=["evaluation"])
MIN_RELEVANCE_SCORE = 0.2

# These cases intentionally verify retrieval only, not medical conclusions.
EVALUATION_CASES = (
    {
        "case_id": "drug-ibuprofen",
        "question": "布洛芬有什么作用？",
        "expected_name": "布洛芬",
        "expected_type": "drug",
    },
    {
        "case_id": "sleep-guidance",
        "question": "睡眠不足时有哪些通用健康建议？",
        "expected_name": "睡眠健康提示",
        "expected_type": "document",
    },
    {
        "case_id": "common-cold-symptoms",
        "question": "鼻塞、流鼻涕和打喷嚏的相关资料是什么？",
        "expected_name": "普通感冒",
        "expected_type": "condition",
    },
    {
        "case_id": "urgent-warning-signs",
        "question": "呼吸困难或持续胸痛时有哪些警示信号？",
        "expected_name": "需要及时就医的警示信号",
        "expected_type": "document",
    },
)


def evaluate_case(vector_store: object, case: dict[str, str]) -> RAGEvaluationCaseResult:
    matches = vector_store.similarity_search_with_relevance_scores(
        case["question"],
        k=3,
    )
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

    return RAGEvaluationCaseResult(
        **case,
        passed=expected_rank is not None,
        expected_rank=expected_rank,
        top_name=top_name,
        top_type=top_type,
        top_score=top_score,
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
        results = [evaluate_case(vector_store, case) for case in EVALUATION_CASES]
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="RAG 评测暂时不可用，请检查知识库和 Embedding 配置",
        ) from error

    passed_count = sum(result.passed for result in results)
    return RAGEvaluationResponse(
        total_count=len(results),
        passed_count=passed_count,
        pass_rate=passed_count / len(results),
        results=results,
    )
