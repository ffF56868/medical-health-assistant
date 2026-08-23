def register_user(client, account="user@example.com"):
    response = client.post(
        "/auth/register",
        json={
            "account": account,
            "password": "health123",
            "confirm_password": "health123",
        },
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_knowledge_requires_login(auth_client):
    response = auth_client.get("/conditions")

    assert response.status_code == 401


def test_regular_user_can_query_but_cannot_change_knowledge(auth_client):
    headers = register_user(auth_client)

    listed = auth_client.get("/conditions", headers=headers)
    assert listed.status_code == 200

    created = auth_client.post(
        "/conditions",
        headers=headers,
        json={
            "name": "普通用户不应新增的病症",
            "symptoms": "测试症状",
            "treatment": "测试建议",
        },
    )
    assert created.status_code == 403
    assert created.json()["detail"] == "需要管理员权限"


def test_admin_can_change_knowledge(client):
    response = client.post(
        "/conditions",
        json={
            "name": "管理员可以新增的病症",
            "symptoms": "测试症状",
            "treatment": "测试建议",
        },
    )

    assert response.status_code == 201
