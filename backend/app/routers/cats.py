from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.db import SessionLocal

router = APIRouter(prefix="/cats", tags=["cats"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.CatRead, status_code=status.HTTP_201_CREATED)
def create_cat(cat: schemas.CatCreate, db: Session = Depends(get_db)):
    if not crud.validate_breed(cat.breed):
        raise HTTPException(status_code=400, detail="Breed not found in TheCatAPI")
    return crud.create_cat(db, cat)


@router.get("/", response_model=List[schemas.CatRead])
def list_cats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_cats(db, skip=skip, limit=limit)


@router.get("/{cat_id}", response_model=schemas.CatRead)
def get_cat(cat_id: int, db: Session = Depends(get_db)):
    cat = crud.get_cat(db, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat


@router.patch("/{cat_id}/salary", response_model=schemas.CatRead)
def update_salary(cat_id: int, payload: schemas.CatSalaryUpdate, db: Session = Depends(get_db)):
    cat = crud.update_cat_salary(db, cat_id, payload.salary)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cat(cat_id: int, db: Session = Depends(get_db)):
    try:
        ok = crud.delete_cat(db, cat_id)
    except ValueError as e:
        if str(e) == "CAT_HAS_ACTIVE_MISSION":
            raise HTTPException(status_code=409, detail="Cat has an active mission")
        raise
    if not ok:
        raise HTTPException(status_code=404, detail="Cat not found")
    return
