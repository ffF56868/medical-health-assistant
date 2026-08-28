from langchain_core.documents import Document
from sqlmodel import Session

from app.hybrid_search import (
    KeywordMatch,
    extract_keyword_terms,
    keyword_search,
    merge_retrieval_matches,
)
from app.models import Drug, KnowledgeDocument, User


def test_extract_keyword_terms_keeps_a_chinese_medical_name():
    terms = extract_keyword_terms("布洛芬有什么作用？")

    assert "布洛芬" in terms
    assert "什么" not in terms


def test_extract_keyword_terms_ignores_generic_specialty_overview_title_parts():
    terms = extract_keyword_terms("眼科常见病概览中有哪些就医警示？")

    assert "眼科" in terms
    assert "专科概览" not in terms
    assert "科概览" not in terms
    assert "就医警示" not in terms


def test_keyword_search_respects_type_and_private_document_access(test_engine):
    with Session(test_engine) as session:
        session.add(
            Drug(
                name="布洛芬",
                effects="缓解发热和疼痛",
                instructions="请阅读说明书并咨询医生",
            )
        )
        session.add(
            KnowledgeDocument(
                title="用户二的私有资料",
                content="只有用户二可以看到的布洛芬资料",
                owner_user_id=2,
                visibility="private",
            )
        )
        session.commit()

        regular_user = User(id=1, account="reader@example.com", is_admin=False)
        drug_matches = keyword_search(
            session,
            "布洛芬有什么作用",
            knowledge_type="drug",
            source_filter="all",
            current_user=regular_user,
        )
        private_matches = keyword_search(
            session,
            "用户二私有资料",
            knowledge_type="document",
            source_filter="all",
            current_user=regular_user,
        )

    assert [match.document.metadata["name"] for match in drug_matches] == [
        "布洛芬"
    ]
    assert private_matches == []


def test_merge_retrieval_matches_deduplicates_a_record_and_marks_hybrid():
    vector_document = Document(
        page_content="布洛芬的向量切块",
        metadata={"type": "drug", "record_id": 1, "name": "布洛芬"},
    )
    keyword_document = Document(
        page_content="布洛芬的关键词资料",
        metadata={"type": "drug", "record_id": 1, "name": "布洛芬"},
    )
    another_document = Document(
        page_content="感冒资料",
        metadata={"type": "condition", "record_id": 2, "name": "感冒"},
    )

    merged = merge_retrieval_matches(
        [(vector_document, 0.8)],
        [
            KeywordMatch(document=keyword_document, score=1.0),
            KeywordMatch(document=another_document, score=0.8),
        ],
    )

    assert len(merged) == 2
    assert merged[0][0].metadata["name"] == "布洛芬"
    assert merged[0][0].metadata["retrieval_method"] == "hybrid"
    assert merged[0][0].metadata["vector_score"] == 0.8
    assert merged[0][0].metadata["keyword_score"] == 1.0
    assert {item[0].metadata["record_id"] for item in merged} == {1, 2}
