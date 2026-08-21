from types import SimpleNamespace

from langchain_core.documents import Document
from sqlmodel import Session, create_engine

from app.database import create_db_and_tables
from app.main import health_check
from app.routers import ask as ask_router
from app.routers import evaluation as evaluation_router
from app.routers import knowledge as knowledge_router


class FakeVectorStore:
    def __init__(self, matches):
        self.matches = matches
        self.last_query = None
        self.last_k = None

    def similarity_search_with_relevance_scores(self, query, k):
        self.last_query = query
        self.last_k = k
        return self.matches


class FakeChatModel:
    def __init__(self, answer="这是测试模型回答。"):
        self.answer = answer
        self.call_count = 0

    def invoke(self, _messages):
        self.call_count += 1
        return SimpleNamespace(content=self.answer)

    def stream(self, _messages):
        self.call_count += 1
        midpoint = max(1, len(self.answer) // 2)
        yield SimpleNamespace(content=self.answer[:midpoint])
        yield SimpleNamespace(content=self.answer[midpoint:])


class FakeEvaluationVectorStore:
    def __init__(self):
        self.queries = []

    def similarity_search_with_relevance_scores(self, query, k):
        self.queries.append((query, k))
        case = next(
            item
            for item in evaluation_router.EVALUATION_CASES
            if item["question"] == query
        )
        return [
            (
                Document(
                    page_content="评测用资料",
                    metadata={
                        "name": case["expected_name"],
                        "type": case["expected_type"],
                    },
                ),
                0.9,
            )
        ]


class FakeComparisonVectorStore:
    def __init__(self, matches):
        self.matches = matches
        self.queries = []

    def similarity_search_with_relevance_scores(self, query, k):
        self.queries.append((query, k))
        return self.matches[:k]


def mock_current_knowledge_base(monkeypatch):
    monkeypatch.setattr(
        ask_router,
        "get_knowledge_status",
        lambda session: {"is_current": True},
    )


def test_condition_can_be_created_and_listed(client):
    create_response = client.post(
        "/conditions",
        json={
            "name": "测试病症",
            "symptoms": "测试症状",
            "treatment": "测试处理建议",
            "source": "测试卫生机构",
            "source_tier": "professional",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/conditions", params={"keyword": "测试"})
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "测试病症"
    assert list_response.json()[0]["source_tier"] == "professional"
    assert list_response.json()[0]["updated_at"] is not None


def test_existing_sqlite_data_receives_metadata_columns_without_data_loss():
    old_database = create_engine("sqlite://")
    with old_database.begin() as connection:
        connection.exec_driver_sql(
            'CREATE TABLE "condition" ('
            'id INTEGER PRIMARY KEY, name VARCHAR(100), '
            'symptoms VARCHAR(5000), treatment VARCHAR(5000))'
        )
        connection.exec_driver_sql(
            "INSERT INTO \"condition\" (id, name, symptoms, treatment) "
            "VALUES (1, '旧资料', '旧症状', '旧建议')"
        )

    create_db_and_tables(old_database)

    with old_database.connect() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql('PRAGMA table_info("condition")')
        }
        migrated_row = connection.exec_driver_sql(
            'SELECT source, source_tier, updated_at FROM "condition" WHERE id = 1'
        ).one()

    assert {"source", "source_tier", "updated_at"}.issubset(columns)
    assert migrated_row.source == "未标注来源"
    assert migrated_row.source_tier == "unverified"
    assert migrated_row.updated_at is None


def test_blank_knowledge_search_is_rejected(client):
    response = client.get("/knowledge/search", params={"q": " "})
    assert response.status_code == 422
    assert response.json()["detail"] == "搜索关键词不能为空"


def test_review_queue_lists_only_knowledge_that_needs_human_review(client):
    needs_review = client.post(
        "/conditions",
        json={
            "name": "待核验病症",
            "symptoms": "测试症状",
            "treatment": "测试处理建议",
        },
    )
    ready = client.post(
        "/drugs",
        json={
            "name": "已标注药物",
            "effects": "测试作用",
            "instructions": "测试说明",
            "source": "测试专业机构",
            "source_tier": "professional",
        },
    )
    assert needs_review.status_code == 201
    assert ready.status_code == 201

    response = client.get("/knowledge/review-queue")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["results"][0]["title"] == "待核验病症"
    assert "可信度等级为待核实" in data["results"][0]["review_reasons"]
    assert "未标注具体资料来源" in data["results"][0]["review_reasons"]


def test_knowledge_versions_can_restore_a_previous_snapshot(client, monkeypatch):
    def fake_rebuild_vector_store(session):
        session.commit()
        return 1, 1

    monkeypatch.setattr(
        knowledge_router,
        "rebuild_vector_store",
        fake_rebuild_vector_store,
    )
    created = client.post(
        "/conditions",
        json={
            "name": "版本测试病症",
            "symptoms": "第一版症状",
            "treatment": "第一版建议",
        },
    )
    assert created.status_code == 201
    condition_id = created.json()["id"]

    first_rebuild = client.post("/knowledge/rebuild")
    assert first_rebuild.status_code == 200
    first_version_id = first_rebuild.json()["snapshot_id"]

    updated = client.put(
        f"/conditions/{condition_id}",
        json={
            "name": "版本测试病症",
            "symptoms": "第二版症状",
            "treatment": "第二版建议",
        },
    )
    assert updated.status_code == 200
    second_rebuild = client.post("/knowledge/rebuild")
    assert second_rebuild.status_code == 200
    assert second_rebuild.json()["snapshot_id"] != first_version_id

    restored = client.post(f"/knowledge/versions/{first_version_id}/restore")
    assert restored.status_code == 200
    assert restored.json()["restored_version_id"] == first_version_id
    assert restored.json()["backup_version_id"] == second_rebuild.json()["snapshot_id"]

    condition = client.get(f"/conditions/{condition_id}")
    assert condition.status_code == 200
    assert condition.json()["symptoms"] == "第一版症状"

    versions = client.get("/knowledge/versions")
    assert versions.status_code == 200
    restored_version = next(
        version
        for version in versions.json()["versions"]
        if version["id"] == first_version_id
    )
    assert restored_version["is_current"] is True


def test_rag_evaluation_reports_hits_in_the_top_three(client, monkeypatch):
    vector_store = FakeEvaluationVectorStore()
    monkeypatch.setattr(
        evaluation_router,
        "get_knowledge_status",
        lambda session: {"is_current": True},
    )
    monkeypatch.setattr(
        evaluation_router,
        "get_vector_store",
        lambda: vector_store,
    )

    response = client.post("/evaluation/run")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == len(evaluation_router.EVALUATION_CASES)
    assert data["passed_count"] == data["total_count"]
    assert data["pass_rate"] == 1
    assert all(item["expected_rank"] == 1 for item in data["results"])
    assert all(k == 8 for _, k in vector_store.queries)


def test_retrieval_comparison_reports_deduplication_improvement(client, monkeypatch):
    case = {
        "case_id": "deduplication-case",
        "case_source": "默认题",
        "question": "目标资料在哪里？",
        "expected_name": "目标资料",
        "expected_type": "document",
    }
    vector_store = FakeComparisonVectorStore(
        [
            (
                Document(
                    page_content="同一资料的第一个切块",
                    metadata={"name": "重复资料", "type": "document", "record_id": 1},
                ),
                0.99,
            ),
            (
                Document(
                    page_content="同一资料的第二个切块",
                    metadata={"name": "重复资料", "type": "document", "record_id": 1},
                ),
                0.98,
            ),
            (
                Document(
                    page_content="另一份资料",
                    metadata={"name": "另一份资料", "type": "document", "record_id": 2},
                ),
                0.97,
            ),
            (
                Document(
                    page_content="目标资料内容",
                    metadata={"name": "目标资料", "type": "document", "record_id": 3},
                ),
                0.96,
            ),
        ]
    )
    monkeypatch.setattr(evaluation_router, "EVALUATION_CASES", (case,))
    monkeypatch.setattr(
        evaluation_router,
        "get_knowledge_status",
        lambda session: {"is_current": True},
    )
    monkeypatch.setattr(
        evaluation_router,
        "get_vector_store",
        lambda: vector_store,
    )

    response = client.post("/evaluation/compare")

    assert response.status_code == 200
    data = response.json()
    assert data["baseline"]["passed_count"] == 0
    assert data["current"]["passed_count"] == 1
    assert data["pass_rate_delta"] == 1
    assert data["improved_count"] == 1
    assert data["regressed_count"] == 0
    assert data["results"][0]["baseline"]["expected_rank"] is None
    assert data["results"][0]["current"]["expected_rank"] == 3
    assert data["results"][0]["change"] == "improved"
    assert [k for _, k in vector_store.queries] == [3, 8]


def test_rag_evaluation_saves_and_lists_history(client, monkeypatch):
    vector_store = FakeEvaluationVectorStore()
    monkeypatch.setattr(
        evaluation_router,
        "get_knowledge_status",
        lambda session: {
            "is_current": True,
            "document_count": 13,
        },
    )
    monkeypatch.setattr(
        evaluation_router,
        "get_vector_store",
        lambda: vector_store,
    )

    run_response = client.post("/evaluation/run")

    assert run_response.status_code == 200
    run_data = run_response.json()
    assert run_data["history_id"] > 0

    history_response = client.get("/evaluation/history")

    assert history_response.status_code == 200
    history_data = history_response.json()
    assert history_data["total_count"] == 1
    assert history_data["runs"][0]["id"] == run_data["history_id"]
    assert history_data["runs"][0]["passed_count"] == 4
    assert history_data["runs"][0]["knowledge_document_count"] == 13


def test_evaluation_history_limit_is_validated(client):
    response = client.get("/evaluation/history", params={"limit": 0})

    assert response.status_code == 422


def test_custom_evaluation_cases_can_be_created_listed_and_deleted(client):
    created = client.post(
        "/evaluation/cases",
        json={
            "question": "布洛芬有什么作用？",
            "expected_name": "布洛芬",
            "expected_type": "drug",
        },
    )

    assert created.status_code == 201
    case_id = created.json()["id"]
    assert created.json()["expected_type"] == "drug"

    listed = client.get("/evaluation/cases")
    assert listed.status_code == 200
    assert listed.json()["total_count"] == 1
    assert listed.json()["cases"][0]["id"] == case_id

    deleted = client.delete(f"/evaluation/cases/{case_id}")
    assert deleted.status_code == 204
    assert client.get("/evaluation/cases").json()["cases"] == []


def test_custom_evaluation_case_rejects_unknown_knowledge_type(client):
    response = client.post(
        "/evaluation/cases",
        json={
            "question": "测试问题",
            "expected_name": "测试资料",
            "expected_type": "unknown",
        },
    )

    assert response.status_code == 422


def test_condition_can_be_updated_and_deleted(client):
    created = client.post(
        "/conditions",
        json={
            "name": "待编辑病症",
            "symptoms": "旧症状",
            "treatment": "旧建议",
        },
    )
    condition_id = created.json()["id"]

    updated = client.put(
        f"/conditions/{condition_id}",
        json={
            "name": "已编辑病症",
            "symptoms": "新症状",
            "treatment": "新建议",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "已编辑病症"

    deleted = client.delete(f"/conditions/{condition_id}")
    assert deleted.status_code == 204
    assert client.get(f"/conditions/{condition_id}").status_code == 404


def test_text_document_can_be_uploaded(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "睡眠提示.txt",
                "保持规律作息，睡前避免长时间使用电子设备。".encode("utf-8"),
                "text/plain",
            )
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "睡眠提示"


def test_conversation_can_be_listed_read_and_deleted(client):
    ask_response = client.post(
        "/ask",
        json={
            "conversation_id": "test-conversation-history",
            "question": "我出现持续胸痛怎么办？",
        },
    )
    assert ask_response.status_code == 200

    summaries = client.get("/conversations")
    assert summaries.status_code == 200
    assert summaries.json()[0]["conversation_id"] == "test-conversation-history"
    assert summaries.json()[0]["message_count"] == 2

    messages = client.get("/conversations/test-conversation-history/messages")
    assert messages.status_code == 200
    assert len(messages.json()) == 2

    deleted = client.delete("/conversations/test-conversation-history/messages")
    assert deleted.status_code == 204
    assert client.get("/conversations").json() == []


def test_urgent_warning_bypasses_model_and_can_receive_feedback(client):
    ask_response = client.post(
        "/ask",
        json={
            "conversation_id": "test-urgent-feedback",
            "question": "我现在感觉呼吸困难，怎么办？",
        },
    )
    assert ask_response.status_code == 200
    ask_data = ask_response.json()
    assert ask_data["source"] == "safety-keyword-guard"
    assert "立即寻求紧急医疗帮助" in ask_data["answer"]

    feedback_response = client.post(
        "/feedback",
        json={
            "assistant_message_id": ask_data["assistant_message_id"],
            "helpful": False,
            "reason": "资料不足，没有回答这个问题",
        },
    )
    assert feedback_response.status_code == 200

    suggestions_response = client.get("/feedback/improvement-suggestions")
    assert suggestions_response.status_code == 200
    suggestions = suggestions_response.json()
    assert suggestions["not_helpful_count"] == 1
    assert suggestions["repeated_questions"][0]["text"] == "我现在感觉呼吸困难，怎么办？"


def test_health_check_reports_database_and_knowledge_state(test_engine, monkeypatch):
    expected_status = {
        "is_current": True,
        "document_count": 0,
        "chunk_count": 0,
    }
    monkeypatch.setattr(
        "app.main.get_knowledge_status",
        lambda session: expected_status,
    )
    with Session(test_engine) as session:
        response = health_check(session)

    assert response.status == "ok"
    assert response.database == "connected"
    assert response.knowledge_base_current is True


def test_rag_keeps_the_best_chunk_and_returns_structured_references(
    client,
    monkeypatch,
):
    mock_current_knowledge_base(monkeypatch)
    vector_store = FakeVectorStore(
        [
            (
                Document(
                    page_content="睡眠资料的低分切块",
                    metadata={
                        "type": "document",
                        "record_id": 1,
                        "name": "睡眠健康提示",
                        "source": "测试文档",
                        "chunk_index": 0,
                    },
                ),
                0.5,
            ),
            (
                Document(
                    page_content="睡眠资料的高分切块",
                    metadata={
                        "type": "document",
                        "record_id": 1,
                        "name": "睡眠健康提示",
                        "source": "测试文档",
                        "chunk_index": 1,
                    },
                ),
                0.9,
            ),
            (
                Document(
                    page_content="布洛芬可用于缓解发热和疼痛。",
                    metadata={
                        "type": "drug",
                        "record_id": 2,
                        "name": "布洛芬",
                        "chunk_index": 0,
                    },
                ),
                0.7,
            ),
        ]
    )
    chat_model = FakeChatModel()
    monkeypatch.setattr(ask_router, "get_vector_store", lambda: vector_store)
    monkeypatch.setattr(ask_router, "get_chat_model", lambda: chat_model)

    response = client.post(
        "/ask",
        json={"conversation_id": "test-rag-references", "question": "睡眠问题"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "这是测试模型回答。"
    assert data["source"] == "chroma-retrieval-openai-generation"
    assert vector_store.last_k == 8
    assert chat_model.call_count == 1
    assert [item["name"] for item in data["references"]] == [
        "睡眠健康提示",
        "布洛芬",
    ]
    assert data["references"][0]["relevance_score"] == 0.9
    assert "高分切块" in data["references"][0]["excerpt"]
    assert data["references"][0]["source"] == "测试文档"
    assert data["references"][0]["source_tier"] == "unverified"
    assert data["references"][0]["needs_review"] is True
    assert data["processing_path"] == "rag-vector-retrieval"
    assert data["retrieved_count"] == 2
    assert data["latency_ms"] >= 0


def test_rag_returns_no_match_without_calling_the_chat_model(client, monkeypatch):
    mock_current_knowledge_base(monkeypatch)
    vector_store = FakeVectorStore(
        [
            (
                Document(
                    page_content="不相关资料",
                    metadata={"type": "document", "record_id": 1, "name": "资料"},
                ),
                0.19,
            )
        ]
    )
    monkeypatch.setattr(ask_router, "get_vector_store", lambda: vector_store)
    monkeypatch.setattr(
        ask_router,
        "get_chat_model",
        lambda: (_ for _ in ()).throw(AssertionError("不应调用模型")),
    )

    response = client.post(
        "/ask",
        json={"conversation_id": "test-rag-no-match", "question": "无关问题"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "chroma-vector-search:no-match"
    assert data["references"] == []


def test_rag_rejects_requests_when_the_knowledge_base_is_outdated(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        ask_router,
        "get_knowledge_status",
        lambda session: {"is_current": False},
    )

    response = client.post(
        "/ask",
        json={"conversation_id": "test-rag-stale", "question": "布洛芬的作用"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "知识库已过期，请先执行 POST /knowledge/rebuild"


def test_rag_streams_tokens_and_saves_the_completed_answer(client, monkeypatch):
    mock_current_knowledge_base(monkeypatch)
    vector_store = FakeVectorStore(
        [
            (
                Document(
                    page_content="布洛芬可用于缓解发热和疼痛。",
                    metadata={"type": "drug", "record_id": 2, "name": "布洛芬"},
                ),
                0.9,
            )
        ]
    )
    chat_model = FakeChatModel(answer="这是分段返回的测试回答。")
    monkeypatch.setattr(ask_router, "get_vector_store", lambda: vector_store)
    monkeypatch.setattr(ask_router, "get_chat_model", lambda: chat_model)

    response = client.post(
        "/ask/stream",
        json={
            "conversation_id": "test-streaming-answer",
            "question": "布洛芬有什么作用？",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: metadata" in response.text
    assert response.text.count("event: token") == 2
    assert '"text": "这是分段返回"' in response.text
    assert '"text": "的测试回答。"' in response.text
    assert '"processing_path": "rag-vector-retrieval"' in response.text
    assert '"retrieved_count": 1' in response.text
    assert "event: done" in response.text
    assert chat_model.call_count == 1

    messages = client.get("/conversations/test-streaming-answer/messages")
    assert [message["content"] for message in messages.json()] == [
        "布洛芬有什么作用？",
        "这是分段返回的测试回答。",
    ]
