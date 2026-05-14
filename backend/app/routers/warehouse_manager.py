from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.warehouse_manager import WarehouseManager
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/warehouse-managers", tags=["仓库管理人"])


class ManagerAssign(BaseModel):
    warehouse_id: int
    user_ids: List[int]


@router.get("/{warehouse_id}")
def get_managers(warehouse_id: int, db: Session = Depends(get_db)):
    records = db.query(WarehouseManager).filter(
        WarehouseManager.warehouse_id == warehouse_id
    ).all()
    return [{"id": r.id, "warehouse_id": r.warehouse_id, "user_id": r.user_id} for r in records]


@router.post("/")
def assign_managers(
    data: ManagerAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="无权限")
    db.query(WarehouseManager).filter(
        WarehouseManager.warehouse_id == data.warehouse_id
    ).delete()
    for uid in data.user_ids:
        db.add(WarehouseManager(warehouse_id=data.warehouse_id, user_id=uid))
    db.commit()
    return {"message": "管理人已更新"}


@router.get("/user/{user_id}/warehouses")
def get_user_warehouses(user_id: int, db: Session = Depends(get_db)):
    records = db.query(WarehouseManager).filter(
        WarehouseManager.user_id == user_id
    ).all()
    return [{"id": r.id, "warehouse_id": r.warehouse_id, "user_id": r.user_id} for r in records]
