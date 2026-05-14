from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.warehouse import Warehouse
from app.models.stock import Stock
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/warehouses", tags=["仓库管理"])


class WarehouseCreate(BaseModel):
    code: str
    name: str
    warehouse_type: str = "entity"
    parent_id: int = 0
    remark: str = None


class WarehouseUpdate(BaseModel):
    name: str = None
    warehouse_type: str = None
    is_active: bool = None
    remark: str = None


class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str
    warehouse_type: str
    parent_id: int
    is_active: bool
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[WarehouseResponse])
def list_warehouses(skip: int = 0, limit: int = 100, warehouse_type: str = None, db: Session = Depends(get_db)):
    query = db.query(Warehouse)
    if warehouse_type:
        query = query.filter(Warehouse.warehouse_type == warehouse_type)
    warehouses = query.offset(skip).limit(limit).all()
    return warehouses


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return warehouse


@router.post("/", response_model=WarehouseResponse)
def create_warehouse(warehouse_data: WarehouseCreate, db: Session = Depends(get_db)):
    existing = db.query(Warehouse).filter(Warehouse.code == warehouse_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="仓库编码已存在")

    warehouse = Warehouse(**warehouse_data.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(warehouse_id: int, warehouse_data: WarehouseUpdate, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")

    update_data = warehouse_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(warehouse, key, value)

    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete("/{warehouse_id}")
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in ("admin",):
        raise HTTPException(status_code=403, detail="仅管理员可删除仓库")

    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")

    # 检查该仓库及所有虚拟子仓是否有库存
    warehouse_ids = [warehouse_id]
    sub_ids = db.query(Warehouse.id).filter(
        Warehouse.parent_id == warehouse_id,
        Warehouse.warehouse_type != "entity",
    ).all()
    warehouse_ids.extend([r[0] for r in sub_ids])

    has_stock = db.query(Stock).filter(Stock.warehouse_id.in_(warehouse_ids)).first()
    if has_stock:
        raise HTTPException(status_code=400, detail="该仓库或虚拟子仓中存在库存，无法删除")

    db.delete(warehouse)
    db.commit()
    return {"message": "删除成功"}
