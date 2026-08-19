from types import SimpleNamespace

from langchain_core.documents import Document
from sqlmodel import Session

from app.main import health_check
from app.routers import ask as ask_router


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
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/conditions", params={"keyword": "测试"})
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "测试病症"


def test_blank_knowledge_search_is_rejected(client):
    response = client.get("/knowledge/search", params={"q": " "})
    assert response.status_code == 422
    assert response.json()["detail"] == "搜索关键词不能为空"


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
    assert "event: done" in response.text
    assert chat_model.call_count == 1

    messages = client.get("/conversations/test-streaming-answer/messages")
    assert [message["content"] for message in messages.json()] == [
        "布洛芬有什么作用？",
        "这是分段返回的测试回答。",
    ]
