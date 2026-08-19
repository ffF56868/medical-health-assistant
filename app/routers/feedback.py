from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import AnswerFeedback, ChatMessage
from app.schemas import FeedbackCreate, FeedbackRead, FeedbackSummary


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackRead)
def create_or_update_feedback(
    feedback_data: FeedbackCreate,
    session: Session = Depends(get_session),
):
    message = session.get(ChatMessage, feedback_data.assistant_message_id)
    if message is None or message.role != "assistant":
        raise HTTPException(status_code=404, detail="助手回答记录不存在")

    feedback = session.exec(
        select(AnswerFeedback).where(
            AnswerFeedback.assistant_message_id
            == feedback_data.assistant_message_id
        )
    ).first()
    if feedback is None:
        feedback = AnswerFeedback(**feedback_data.model_dump())
    else:
        feedback.helpful = feedback_data.helpful
        feedback.reason = feedback_data.reason

    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


@router.get("/summary", response_model=FeedbackSummary)
def get_feedback_summary(session: Session = Depends(get_session)):
    feedback_items = session.exec(select(AnswerFeedback)).all()
    total_count = len(feedback_items)
    helpful_count = sum(item.helpful for item in feedback_items)
    return FeedbackSummary(
        total_count=total_count,
        helpful_count=helpful_count,
        not_helpful_count=total_count - helpful_count,
        helpful_rate=(round(helpful_count / total_count, 3) if total_count else None),
    )
