from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.person import Person

router = APIRouter(prefix="/api/persons", tags=["人员档案"])


class PersonCreate(BaseModel):
    code: str
    name: str
    person_type: str = "sales"
    department: str = None
    phone: str = None
    remark: str = None


class PersonUpdate(BaseModel):
    name: str = None
    person_type: str = None
    department: str = None
    phone: str = None
    is_active: bool = None
    remark: str = None


class PersonResponse(BaseModel):
    id: int
    code: str
    name: str
    person_type: str
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    remark: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PersonResponse])
def list_persons(
    skip: int = 0,
    limit: int = 100,
    keyword: str = None,
    person_type: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Person)
    if keyword:
        query = query.filter(Person.name.contains(keyword) | Person.code.contains(keyword))
    if person_type:
        query = query.filter(Person.person_type == person_type)
    if is_active is not None:
        query = query.filter(Person.is_active == is_active)
    return query.order_by(Person.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    return person


@router.post("/", response_model=PersonResponse)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    existing = db.query(Person).filter(Person.code == person.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="人员编码已存在")
    
    db_person = Person(**person.model_dump())
    db.add(db_person)
    try:
        db.commit()
        db.refresh(db_person)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="人员编码已存在")
    return db_person


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(person_id: int, person: PersonUpdate, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    update_data = person.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_person, key, value)
    
    db.commit()
    db.refresh(db_person)
    return db_person


@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    db.delete(person)
    db.commit()
    return {"message": "删除成功"}