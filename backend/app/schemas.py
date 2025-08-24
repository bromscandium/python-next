from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CatBase(BaseModel):
    name: str = Field(..., max_length=120)
    years_of_experience: int = Field(ge=0)
    breed: str
    salary: int = Field(ge=0)


class CatCreate(CatBase):
    pass


class CatRead(CatBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CatSalaryUpdate(BaseModel):
    salary: int = Field(ge=0)


class TargetBase(BaseModel):
    name: str = Field(..., max_length=120)
    country: str = Field(..., max_length=80)
    notes: Optional[str] = None


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    notes: Optional[str] = None
    is_complete: Optional[bool] = None


class TargetRead(TargetBase):
    id: int
    is_complete: bool
    model_config = ConfigDict(from_attributes=True)


class MissionCreate(BaseModel):
    targets: List[TargetCreate] = Field(min_length=1, max_length=3)


class MissionAssign(BaseModel):
    cat_id: int


class MissionRead(BaseModel):
    id: int
    assigned_cat_id: Optional[int]
    is_complete: bool
    targets: List[TargetRead]
    model_config = ConfigDict(from_attributes=True)
