from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.supplier import Supplier

router = APIRouter(prefix="/api/suppliers", tags=["供应商档案"])


class SupplierCreate(BaseModel):
    code: str
    name: str
    short_name: str = None
    contact: str = None
    phone: str = None
    mobile: str = None
    email: str = None
    address: str = None
    bank_info: str = None
    tax_no: str = None
    remark: str = None


class SupplierUpdate(BaseModel):
    name: str = None
    short_name: str = None
    contact: str = None
    phone: str = None
    mobile: str = None
    email: str = None
    address: str = None
    bank_info: str = None
    tax_no: str = None
    is_active: bool = None
    remark: str = None


class SupplierResponse(BaseModel):
    id: int
    code: str
    name: str
    short_name: str = None
    contact: str = None
    phone: str = None
    mobile: str = None
    email: str = None
    address: str = None
    bank_info: str = None
    tax_no: str = None
    is_active: bool
    remark: str = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SupplierResponse])
def list_suppliers(
    skip: int = 0,
    limit: int = 100,
    keyword: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)
    if keyword:
        query = query.filter(Supplier.name.contains(keyword) | Supplier.code.contains(keyword))
    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)
    return query.order_by(Supplier.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


@router.post("/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    existing = db.query(Supplier).filter(Supplier.code == supplier.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="供应商编码已存在")
    
    db_supplier = Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    update_data = supplier.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_supplier, key, value)
    
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    db.delete(supplier)
    db.commit()
    return {"message": "删除成功"}