from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from app.database import get_db
from app.models.location import StorageLocation, GoodsLocation
from app.models.stock import Stock
from app.models.goods import Goods
from app.models.warehouse import Warehouse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/locations", tags=["货位管理"])


class LocationCreate(BaseModel):
    warehouse_id: int
    code: str
    name: Optional[str] = None


class LocationResponse(BaseModel):
    id: int
    warehouse_id: int
    code: str
    name: Optional[str]
    is_active: bool
    warehouse_name: Optional[str] = None

    class Config:
        from_attributes = True


class GoodsLocationResponse(BaseModel):
    id: int
    goods_id: int
    location_id: int
    quantity: int
    location_code: Optional[str] = None
    warehouse_name: Optional[str] = None


@router.get("/", response_model=List[LocationResponse])
def list_locations(
    warehouse_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(StorageLocation)
    if warehouse_id:
        query = query.filter(StorageLocation.warehouse_id == warehouse_id)
    locations = query.all()
    result = []
    for loc in locations:
        wh = db.query(Warehouse).filter(Warehouse.id == loc.warehouse_id).first()
        result.append(LocationResponse(
            id=loc.id,
            warehouse_id=loc.warehouse_id,
            code=loc.code,
            name=loc.name,
            is_active=loc.is_active,
            warehouse_name=wh.name if wh else None,
        ))
    return result


@router.post("/", response_model=LocationResponse)
def create_location(
    req: LocationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing = db.query(StorageLocation).filter(
        StorageLocation.code == req.code,
    ).first()
    if existing:
        wh_name = db.query(Warehouse.name).filter(Warehouse.id == existing.warehouse_id).scalar() or f"ID={existing.warehouse_id}"
        raise HTTPException(status_code=400, detail=f"编码「{req.code}」已被【{wh_name}】使用")

    loc = StorageLocation(warehouse_id=req.warehouse_id, code=req.code, name=req.name)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    wh = db.query(Warehouse).filter(Warehouse.id == loc.warehouse_id).first()
    return LocationResponse(
        id=loc.id,
        warehouse_id=loc.warehouse_id,
        code=loc.code,
        name=loc.name,
        is_active=loc.is_active,
        warehouse_name=wh.name if wh else None,
    )


@router.delete("/{location_id}")
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    loc = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="货位不存在")
    db.query(GoodsLocation).filter(GoodsLocation.location_id == location_id).delete()
    db.delete(loc)
    db.commit()
    return {"message": "已删除"}


@router.post("/goods-location")
def set_goods_location(
    goods_id: int = Query(...),
    location_id: int = Query(...),
    quantity: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    gl = db.query(GoodsLocation).filter(
        GoodsLocation.goods_id == goods_id,
        GoodsLocation.location_id == location_id,
    ).first()
    if gl:
        gl.quantity = quantity
    else:
        gl = GoodsLocation(goods_id=goods_id, location_id=location_id, quantity=quantity)
        db.add(gl)
    db.commit()
    return {"message": "ok"}


@router.get("/goods-location/{goods_id}", response_model=List[GoodsLocationResponse])
def get_goods_locations(
    goods_id: int,
    db: Session = Depends(get_db),
):
    records = db.query(GoodsLocation).filter(GoodsLocation.goods_id == goods_id).all()
    result = []
    for r in records:
        loc = db.query(StorageLocation).filter(StorageLocation.id == r.location_id).first()
        wh = db.query(Warehouse).filter(Warehouse.id == loc.warehouse_id).first() if loc else None
        result.append(GoodsLocationResponse(
            id=r.id,
            goods_id=r.goods_id,
            location_id=r.location_id,
            quantity=r.quantity,
            location_code=f"{wh.name}/{loc.code}" if wh and loc else loc.code if loc else "",
            warehouse_name=wh.name if wh else None,
        ))
    return result


@router.get("/scan/{barcode}")
def scan_barcode(
    barcode: str,
    db: Session = Depends(get_db),
):
    """扫码查询：返回商品信息、所有仓库库存、货位分布"""
    goods = db.query(Goods).filter(Goods.barcode == barcode).first()
    if not goods:
        raise HTTPException(status_code=404, detail="未找到该条码的商品")

    stocks = db.query(Stock).filter(Stock.goods_id == goods.id).all()
    warehouse_stocks = []
    for s in stocks:
        wh = db.query(Warehouse).filter(Warehouse.id == s.warehouse_id).first()
        locations = db.query(GoodsLocation).filter(
            GoodsLocation.goods_id == goods.id,
            GoodsLocation.location_id.in_(
                db.query(StorageLocation.id).filter(
                    StorageLocation.warehouse_id == s.warehouse_id
                )
            ),
        ).all()
        loc_list = []
        for gl in locations:
            loc = db.query(StorageLocation).filter(StorageLocation.id == gl.location_id).first()
            loc_list.append({"code": loc.code, "quantity": gl.quantity})
        warehouse_stocks.append({
            "warehouse_id": s.warehouse_id,
            "warehouse_name": wh.name if wh else "未知",
            "quantity": s.quantity,
            "locations": loc_list,
        })

    return {
        "goods_id": goods.id,
        "barcode": goods.barcode,
        "name": goods.name,
        "spec": goods.spec,
        "unit": goods.unit,
        "price": goods.price,
        "warehouse_stocks": warehouse_stocks,
    }
