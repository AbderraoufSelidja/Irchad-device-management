from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db_setup import get_db
from typing import List
from db.models.maintainers import Intervention, Failure
from schemas import (
    InterventionCreate,
    Intervention as InterventionOut,
    FailureCreate,
    FailureUpdate,
    Failure as FailureOut,
)


router = APIRouter()



@router.post("/interventions/", response_model=InterventionOut, status_code=201)
def create_intervention(
    intervention: InterventionCreate, db: Session = Depends(get_db)
):
    db_intervention = Intervention(
        device_serial_number=intervention.device_serial_number,
        type=intervention.type,
        date=intervention.date,
        note=intervention.note,
        status=intervention.status,
        estimated_duration=intervention.estimated_duration,
    )
    db.add(db_intervention)
    db.commit()
    db.refresh(db_intervention)

    # Add related failures
    for fail in intervention.failures:
        db_failure = Failure(
            intervention_id=db_intervention.id,
            failure_type=fail.failure_type,
            status=fail.status,
        )
        db.add(db_failure)
    db.commit()

    db.refresh(db_intervention)
    return db_intervention


@router.get("/interventions/", response_model=list[InterventionOut])
def get_all_interventions(db: Session = Depends(get_db)):
    return db.query(Intervention).all()


@router.get("/interventions/{intervention_id}", response_model=InterventionOut)
def get_intervention(intervention_id: int, db: Session = Depends(get_db)):
    intervention = (
        db.query(Intervention).filter(Intervention.id == intervention_id).first()
    )
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return intervention


@router.put("/interventions/{intervention_id}", response_model=InterventionOut)
def update_intervention(
    intervention_id: int, update: InterventionCreate, db: Session = Depends(get_db)
):
    db_intervention = (
        db.query(Intervention).filter(Intervention.id == intervention_id).first()
    )
    if not db_intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(db_intervention, key, value)

    db.commit()
    db.refresh(db_intervention)
    return db_intervention


@router.delete("/interventions/{intervention_id}", response_model=InterventionOut)
def delete_intervention(intervention_id: int, db: Session = Depends(get_db)):
    intervention = (
        db.query(Intervention).filter(Intervention.id == intervention_id).first()
    )
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    db.delete(intervention)
    db.commit()
    return intervention



@router.post("/failures/", response_model=FailureOut, status_code=201)
def create_failure(failure: FailureCreate, db: Session = Depends(get_db)):
    intervention = (
        db.query(Intervention)
        .filter(Intervention.id == failure.intervention_id)
        .first()
    )
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    db_failure = Failure(
        failure_type=failure.failure_type,
        status=failure.status,
        intervention_id=failure.intervention_id,
    )
    db.add(db_failure)
    db.commit()
    db.refresh(db_failure)
    return db_failure


@router.get("/failures/", response_model=List[FailureOut])
def get_all_failures(db: Session = Depends(get_db)):
    return db.query(Failure).all()


@router.get("/failures/{failure_id}", response_model=FailureOut)
def get_failure(failure_id: int, db: Session = Depends(get_db)):
    failure = db.query(Failure).filter(Failure.id == failure_id).first()
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    return failure


@router.put("/failures/{failure_id}", response_model=FailureOut)
def update_failure(
    failure_id: int, failure_update: FailureUpdate, db: Session = Depends(get_db)
):
    db_failure = db.query(Failure).filter(Failure.id == failure_id).first()
    if not db_failure:
        raise HTTPException(status_code=404, detail="Failure not found")

    for key, value in failure_update.model_dump(exclude_unset=True).items():
        setattr(db_failure, key, value)

    db.commit()
    db.refresh(db_failure)
    return db_failure


@router.delete("/failures/{failure_id}", response_model=FailureOut)
def delete_failure(failure_id: int, db: Session = Depends(get_db)):
    failure = db.query(Failure).filter(Failure.id == failure_id).first()
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    db.delete(failure)
    db.commit()
    return failure
