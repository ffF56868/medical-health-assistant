from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import Drug
from app.schemas import DrugCreate, DrugRead


router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.post("", response_model=DrugRead, status_code=201)
def create_drug(
    drug_data: DrugCreate,
    session: Session = Depends(get_session),
):
    existing_drug = session.exec(
        select(Drug).where(Drug.name == drug_data.name)
    ).first()

    if existing_drug is not None:
        raise HTTPException(status_code=409, detail="药物已经存在")

    drug = Drug.model_validate(drug_data)
    session.add(drug)
    session.commit()
    session.refresh(drug)
    return drug


@router.get("", response_model=list[DrugRead])
def list_drugs(
    keyword: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_session),
):
    statement = select(Drug).order_by(Drug.id)

    if keyword and keyword.strip():
        statement = statement.where(Drug.name.contains(keyword.strip()))

    return session.exec(statement).all()


@router.get("/{drug_id}", response_model=DrugRead)
def get_drug(
    drug_id: int,
    session: Session = Depends(get_session),
):
    drug = session.get(Drug, drug_id)

    if drug is None:
        raise HTTPException(status_code=404, detail="药物不存在")

    return drug


@router.put("/{drug_id}", response_model=DrugRead)
def update_drug(
    drug_id: int,
    drug_data: DrugCreate,
    session: Session = Depends(get_session),
):
    drug = session.get(Drug, drug_id)

    if drug is None:
        raise HTTPException(status_code=404, detail="药物不存在")

    duplicate = session.exec(
        select(Drug).where(
            Drug.name == drug_data.name,
            Drug.id != drug_id,
        )
    ).first()

    if duplicate is not None:
        raise HTTPException(status_code=409, detail="药物名称已经存在")

    drug.name = drug_data.name
    drug.effects = drug_data.effects
    drug.instructions = drug_data.instructions
    session.add(drug)
    session.commit()
    session.refresh(drug)
    return drug


@router.delete("/{drug_id}", status_code=204)
def delete_drug(
    drug_id: int,
    session: Session = Depends(get_session),
):
    drug = session.get(Drug, drug_id)

    if drug is None:
        raise HTTPException(status_code=404, detail="药物不存在")

    session.delete(drug)
    session.commit()
