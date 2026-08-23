from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, UserSession
from app.schemas import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthResponse,
    UserRead,
)
from app.security import (
    create_access_token,
    hash_access_token,
    hash_password,
    is_expired,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def to_user_read(user: User) -> UserRead:
    return UserRead.model_validate(user)


def create_auth_response(session: Session, user: User) -> AuthResponse:
    access_token, expires_at = create_access_token()
    session.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_access_token(access_token),
            expires_at=expires_at,
        )
    )
    session.commit()
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=to_user_read(user),
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_session = session.exec(
        select(UserSession).where(
            UserSession.token_hash == hash_access_token(credentials.credentials)
        )
    ).first()
    if (
        user_session is None
        or user_session.revoked_at is not None
        or is_expired(user_session.expires_at)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已失效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号不可用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: AuthRegisterRequest,
    session: Session = Depends(get_session),
):
    if session.exec(select(User).where(User.account == payload.account)).first():
        raise HTTPException(status_code=409, detail="该账号已经注册")

    user = User(
        account=payload.account,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="该账号已经注册") from error
    session.refresh(user)
    return create_auth_response(session, user)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: AuthLoginRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.account == payload.account)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号不可用")
    return create_auth_response(session, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    user_session = session.exec(
        select(UserSession).where(
            UserSession.token_hash == hash_access_token(credentials.credentials)
        )
    ).first()
    if user_session is not None and user_session.revoked_at is None:
        from datetime import UTC, datetime

        user_session.revoked_at = datetime.now(UTC)
        session.add(user_session)
        session.commit()
    return None


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return to_user_read(current_user)
