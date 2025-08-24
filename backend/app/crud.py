from __future__ import annotations
from typing import List, Optional, Iterable, Tuple
import os
import threading
import time

import requests
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app import models, schemas

_BREED_CACHE_LOCK = threading.Lock()
_BREED_CACHE: Optional[Tuple[float, set, set]] = None
_BREED_TTL_SEC = 60 * 60


def _fetch_breeds_from_api() -> Tuple[set, set]:
    url = "https://api.thecatapi.com/v1/breeds"
    headers = {}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    ids = {item["id"].strip().lower() for item in data if "id" in item}
    names = {item["name"].strip().lower() for item in data if "name" in item}
    return ids, names


def _get_breed_cache() -> Tuple[set, set]:
    global _BREED_CACHE
    ts_now = time.time()
    with _BREED_CACHE_LOCK:
        if _BREED_CACHE and (ts_now - _BREED_CACHE[0]) < _BREED_TTL_SEC:
            return _BREED_CACHE[1], _BREED_CACHE[2]

        try:
            ids, names = _fetch_breeds_from_api()
        except Exception:

            ids = {"beng", "siam", "mcoo", "sibe", "rblu"}
            names = {"bengal", "siamese", "maine coon", "siberian", "russian blue"}
        _BREED_CACHE = (ts_now, ids, names)
        return ids, names


def validate_breed(breed: str) -> bool:
    if not breed or not breed.strip():
        return False
    b = breed.strip().lower()
    ids, names = _get_breed_cache()
    return b in ids or b in names


def create_cat(db: Session, cat: schemas.CatCreate) -> models.Cat:
    db_cat = models.Cat(
        name=cat.name.strip(),
        years_of_experience=cat.years_of_experience,
        breed=cat.breed.strip(),
        salary=cat.salary,
    )
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


def list_cats(db: Session, skip: int = 0, limit: int = 100) -> List[models.Cat]:
    stmt = select(models.Cat).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def get_cat(db: Session, cat_id: int) -> Optional[models.Cat]:
    return db.get(models.Cat, cat_id)


def update_cat_salary(db: Session, cat_id: int, salary: int) -> Optional[models.Cat]:
    cat = db.get(models.Cat, cat_id)
    if not cat:
        return None
    cat.salary = salary
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def cat_has_active_mission(db: Session, cat_id: int) -> bool:
    stmt = select(func.count(models.Mission.id)).where(
        and_(models.Mission.assigned_cat_id == cat_id, models.Mission.is_complete.is_(False))
    )
    return db.execute(stmt).scalar_one() > 0


def delete_cat(db: Session, cat_id: int) -> bool:
    cat = db.get(models.Cat, cat_id)
    if not cat:
        return False

    if cat_has_active_mission(db, cat_id):
        raise ValueError("CAT_HAS_ACTIVE_MISSION")
    db.delete(cat)
    db.commit()
    return True


def create_mission_with_targets(
        db: Session,
        targets: Iterable[schemas.TargetCreate]
) -> models.Mission:

    t_list = list(targets)
    if not (1 <= len(t_list) <= 3):
        raise ValueError("TARGETS_COUNT_OUT_OF_RANGE")

    mission = models.Mission(is_complete=False, assigned_cat_id=None)
    db.add(mission)
    db.flush()

    seen_names = set()
    for t in t_list:
        name_key = t.name.strip().lower()
        if name_key in seen_names:
            raise ValueError("TARGET_NAME_NOT_UNIQUE_IN_MISSION")
        seen_names.add(name_key)

        db_target = models.Target(
            mission_id=mission.id,
            name=t.name.strip(),
            country=t.country.strip(),
            notes=(t.notes or None),
            is_complete=False,
        )
        db.add(db_target)

    db.commit()
    db.refresh(mission)
    mission = db.get(models.Mission, mission.id)
    return mission


def list_missions(db: Session) -> List[models.Mission]:
    stmt = select(models.Mission)
    return db.execute(stmt).scalars().all()


def get_mission(db: Session, mission_id: int) -> Optional[models.Mission]:
    return db.get(models.Mission, mission_id)


def delete_mission(db: Session, mission_id: int) -> bool:
    mission = db.get(models.Mission, mission_id)
    if not mission:
        return False
    if mission.assigned_cat_id is not None:
        raise ValueError("MISSION_ASSIGNED_CANNOT_DELETE")
    db.delete(mission)
    db.commit()
    return True


def assign_cat_to_mission(db: Session, mission_id: int, cat_id: int) -> Optional[models.Mission]:
    mission = db.get(models.Mission, mission_id)
    if not mission:
        return None
    if mission.is_complete:
        raise ValueError("MISSION_ALREADY_COMPLETE")
    cat = db.get(models.Cat, cat_id)
    if not cat:
        raise ValueError("CAT_NOT_FOUND")
    if cat_has_active_mission(db, cat_id):
        raise ValueError("CAT_ALREADY_HAS_ACTIVE_MISSION")
    mission.assigned_cat_id = cat_id
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


def update_target(
        db: Session,
        mission_id: int,
        target_id: int,
        *,
        notes: Optional[str] = None,
        is_complete: Optional[bool] = None
) -> Optional[models.Target]:
    mission = db.get(models.Mission, mission_id)
    if not mission:
        return None
    target = db.get(models.Target, target_id)
    if not target or target.mission_id != mission_id:
        return None

    if mission.is_complete or target.is_complete:
        if notes is not None:
            raise ValueError("NOTES_FROZEN")

    changed = False
    if notes is not None and not target.is_complete and not mission.is_complete:
        target.notes = notes
        changed = True

    if is_complete is True and not target.is_complete:
        target.is_complete = True
        changed = True

    if changed:
        db.add(target)
        db.commit()
        db.refresh(target)
        _maybe_complete_mission(db, mission_id)

    return target


def _maybe_complete_mission(db: Session, mission_id: int) -> None:
    mission = db.get(models.Mission, mission_id)
    if not mission or mission.is_complete:
        return
    stmt_total = select(func.count(models.Target.id)).where(models.Target.mission_id == mission_id)
    stmt_done = select(func.count(models.Target.id)).where(
        and_(models.Target.mission_id == mission_id, models.Target.is_complete.is_(True))
    )
    total = db.execute(stmt_total).scalar_one()
    done = db.execute(stmt_done).scalar_one()
    if total > 0 and total == done:
        mission.is_complete = True
        db.add(mission)
        db.commit()
