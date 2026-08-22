def test_register_phone_normalizes_to_china_country_code(client):
    response = client.post(
        "/auth/register",
        json={
            "account": "18242643780",
            "password": "health123",
            "confirm_password": "health123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["account"] == "+8618242643780"
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_register_email_is_case_insensitive(client):
    response = client.post(
        "/auth/register",
        json={
            "account": "Health.Example@Example.COM",
            "password": "health123",
            "confirm_password": "health123",
        },
    )

    assert response.status_code == 201
    assert response.json()["user"]["account"] == "health.example@example.com"


def test_register_rejects_password_without_letters_or_digits(client):
    no_letter = client.post(
        "/auth/register",
        json={
            "account": "18242643780",
            "password": "12345678",
            "confirm_password": "12345678",
        },
    )
    no_digit = client.post(
        "/auth/register",
        json={
            "account": "test@example.com",
            "password": "abcdefgh",
            "confirm_password": "abcdefgh",
        },
    )

    assert no_letter.status_code == 422
    assert "英文字母" in no_letter.text
    assert no_digit.status_code == 422
    assert "数字" in no_digit.text


def test_register_rejects_mismatched_passwords(client):
    response = client.post(
        "/auth/register",
        json={
            "account": "test@example.com",
            "password": "health123",
            "confirm_password": "health456",
        },
    )

    assert response.status_code == 422
    assert "两次输入的密码不一致" in response.text


def test_duplicate_account_is_rejected(client):
    payload = {
        "account": "18242643780",
        "password": "health123",
        "confirm_password": "health123",
    }
    assert client.post("/auth/register", json=payload).status_code == 201

    duplicate = client.post("/auth/register", json=payload)

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "该账号已经注册"


def test_login_me_and_logout_manage_one_session(client):
    register = client.post(
        "/auth/register",
        json={
            "account": "test@example.com",
            "password": "health123",
            "confirm_password": "health123",
        },
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["account"] == "test@example.com"

    login = client.post(
        "/auth/login",
        json={"account": "TEST@EXAMPLE.COM", "password": "health123"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["account"] == "test@example.com"

    logout = client.post("/auth/logout", headers=headers)
    assert logout.status_code == 204
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_auth_does_not_require_a_captcha_field(client):
    response = client.post(
        "/auth/register",
        json={
            "account": "test@example.com",
            "password": "health123",
            "confirm_password": "health123",
        },
    )

    assert response.status_code == 201
