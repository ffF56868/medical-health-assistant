from langchain_core.documents import Document

from app.reranker import rerank_matches


def test_reranker_can_move_an_exactly_relevant_candidate_up():
    loosely_related = Document(
        page_content="高血压资料介绍和健康建议。",
        metadata={"type": "condition", "record_id": 1, "name": "高血压"},
    )
    exact_match = Document(
        page_content="布洛芬可用于缓解发热和疼痛。",
        metadata={"type": "drug", "record_id": 2, "name": "布洛芬"},
    )

    matches = rerank_matches(
        "布洛芬有什么作用？",
        [(loosely_related, 0.95), (exact_match, 0.60)],
    )

    assert matches[0][0].metadata["name"] == "布洛芬"
    assert matches[0][0].metadata["rerank_applied"] is True
    assert matches[0][0].metadata["initial_score"] == 0.6
    assert matches[0][0].metadata["rerank_score"] == matches[0][1]
    assert matches[0][0].metadata["rerank_title_score"] > 0


def test_reranker_preserves_original_order_when_question_has_no_terms():
    first = Document(page_content="资料一", metadata={"name": "资料一"})
    second = Document(page_content="资料二", metadata={"name": "资料二"})

    matches = rerank_matches("？", [(first, 0.4), (second, 0.8)])

    assert [match[0].metadata["name"] for match in matches] == ["资料二", "资料一"]
    assert matches[0][1] == 0.8
