from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import AnswerFeedback, ChatMessage
from app.schemas import ChatMessageRead


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conversation_id}/messages", response_model=list[ChatMessageRead])
def list_messages(
    conversation_id: str,
    session: Session = Depends(get_session),
):
    return session.exec(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at, ChatMessage.id)
    ).all()


@router.delete("/{conversation_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
def clear_messages(
    conversation_id: str,
    session: Session = Depends(get_session),
):
    messages = session.exec(
        select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
    ).all()

    if not messages:
        raise HTTPException(status_code=404, detail="会话记录不存在")

    message_ids = [message.id for message in messages if message.id is not None]
    feedback_items = session.exec(
        select(AnswerFeedback).where(
            AnswerFeedback.assistant_message_id.in_(message_ids)
        )
    ).all()
    for feedback in feedback_items:
        session.delete(feedback)

    for message in messages:
        session.delete(message)

    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
