from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.db import SessionLocal

router = APIRouter(prefix="/missions", tags=["missions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.MissionRead, status_code=status.HTTP_201_CREATED)
def create_mission(payload: schemas.MissionCreate, db: Session = Depends(get_db)):
    try:
        mission = crud.create_mission_with_targets(db, payload.targets)
    except ValueError as e:
        code = str(e)
        if code == "TARGETS_COUNT_OUT_OF_RANGE":
            raise HTTPException(status_code=400, detail="Targets must be between 1 and 3")
        if code == "TARGET_NAME_NOT_UNIQUE_IN_MISSION":
            raise HTTPException(status_code=400, detail="Target names must be unique within a mission")
        raise
    return mission


@router.get("/", response_model=List[schemas.MissionRead])
def list_missions(db: Session = Depends(get_db)):
    return crud.list_missions(db)


@router.get("/{mission_id}", response_model=schemas.MissionRead)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = crud.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    try:
        ok = crud.delete_mission(db, mission_id)
    except ValueError as e:
        if str(e) == "MISSION_ASSIGNED_CANNOT_DELETE":
            raise HTTPException(status_code=409, detail="Mission is assigned to a cat")
        raise
    if not ok:
        raise HTTPException(status_code=404, detail="Mission not found")
    return


@router.post("/{mission_id}/assign", response_model=schemas.MissionRead)
def assign(mission_id: int, payload: schemas.MissionAssign, db: Session = Depends(get_db)):
    try:
        mission = crud.assign_cat_to_mission(db, mission_id, payload.cat_id)
    except ValueError as e:
        code = str(e)
        if code == "MISSION_ALREADY_COMPLETE":
            raise HTTPException(status_code=409, detail="Mission already completed")
        if code == "CAT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Cat not found")
        if code == "CAT_ALREADY_HAS_ACTIVE_MISSION":
            raise HTTPException(status_code=409, detail="Cat already has an active mission")
        raise
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.patch("/{mission_id}/targets/{target_id}", response_model=schemas.MissionRead)
def update_target(mission_id: int, target_id: int, payload: schemas.TargetUpdate, db: Session = Depends(get_db)):
    try:
        target = crud.update_target(
            db,
            mission_id,
            target_id,
            notes=payload.notes,
            is_complete=payload.is_complete,
        )
    except ValueError as e:
        if str(e) == "NOTES_FROZEN":
            raise HTTPException(status_code=403, detail="Notes are frozen (mission or target completed)")
        raise

    if not target:
        raise HTTPException(status_code=404, detail="Mission or target not found")

    mission = crud.get_mission(db, mission_id)
    return mission
