from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.stock import Stock
from app.models.warehouse import Warehouse
from app.models.goods import Goods
from app.models.inbound import InboundRecord
from app.models.inbound_apply import InboundApply
from app.models.transfer import TransferRecord
from app.models.adjustment import GoodsAdjustment
from app.models.location import StorageLocation, GoodsLocation
from app.models.person import Person

router = APIRouter(prefix="/api/stock", tags=["库存管理"])


class StockResponse(BaseModel):
    id: int
    warehouse_id: int
    goods_id: int
    quantity: int
    warehouse_name: str = None
    goods_name: str = None
    goods_barcode: str = None

    class Config:
        from_attributes = True


class StockQueryResponse(BaseModel):
    goods_id: int
    barcode: str
    name: str
    spec: str = None
    total_quantity: int
    warehouse_stocks: List[dict]


@router.get("/", response_model=List[StockResponse])
def list_stocks(skip: int = 0, limit: int = 100, warehouse_id: int = None, goods_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Stock)
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if goods_id:
        query = query.filter(Stock.goods_id == goods_id)
    stocks = query.offset(skip).limit(limit).all()
    return stocks


@router.get("/query", response_model=List[StockQueryResponse])
def query_stock_summary(goods_name: str = None, barcode: str = None, db: Session = Depends(get_db)):
    query = db.query(Stock)

    stocks = query.all()
    result = []

    goods_map = {}
    for stock in stocks:
        if stock.goods_id not in goods_map:
            goods = db.query(Goods).filter(Goods.id == stock.goods_id).first()
            if not goods:
                continue
            if goods_name and goods_name not in goods.name:
                continue
            if barcode and barcode not in goods.barcode:
                continue
            goods_map[stock.goods_id] = {
                "goods_id": goods.id,
                "barcode": goods.barcode,
                "name": goods.name,
                "spec": goods.spec,
                "total_quantity": 0,
                "warehouse_stocks": []
            }

        warehouse = db.query(Warehouse).filter(Warehouse.id == stock.warehouse_id).first()
        warehouse_name = warehouse.name if warehouse else "未知仓库"

        goods_map[stock.goods_id]["total_quantity"] += stock.quantity
        goods_map[stock.goods_id]["warehouse_stocks"].append({
            "warehouse_id": stock.warehouse_id,
            "warehouse_name": warehouse_name,
            "quantity": stock.quantity
        })

    return list(goods_map.values())


@router.get("/{stock_id}", response_model=StockResponse)
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    return stock


@router.get("/detail/{goods_id}")
def get_goods_detail(goods_id: int, db: Session = Depends(get_db)):
    """商品详情聚合：库存、货位、最近业务记录、差异分析"""
    goods = db.query(Goods).filter(Goods.id == goods_id).first()
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 各仓库库存
    stocks = db.query(Stock).filter(Stock.goods_id == goods_id).all()
    warehouse_stocks = []
    for s in stocks:
        wh = db.query(Warehouse).filter(Warehouse.id == s.warehouse_id).first()
        locs = db.query(GoodsLocation).filter(
            GoodsLocation.goods_id == goods_id,
            GoodsLocation.location_id.in_(
                db.query(StorageLocation.id).filter(
                    StorageLocation.warehouse_id == s.warehouse_id
                )
            ),
        ).all()
        location_list = []
        for gl in locs:
            loc = db.query(StorageLocation).filter(StorageLocation.id == gl.location_id).first()
            location_list.append({"code": loc.code, "quantity": gl.quantity})
        warehouse_stocks.append({
            "warehouse_id": s.warehouse_id,
            "warehouse_name": wh.name if wh else "未知",
            "quantity": s.quantity,
            "locations": location_list,
        })

    # 最近30天业务记录
    recent_records = []
    now = datetime.now()

    inbound_records = db.query(InboundRecord).filter(
        InboundRecord.goods_id == goods_id
    ).order_by(InboundRecord.created_at.desc()).limit(20).all()
    for r in inbound_records:
        wh = db.query(Warehouse).filter(Warehouse.id == r.warehouse_id).first()
        recent_records.append({
            "type": "入库",
            "date": r.created_at,
            "quantity": r.quantity,
            "warehouse": wh.name if wh else "",
            "ref_no": r.boniu_order_no or "",
            "operator": r.operator or "",
            "detail": f"入库 +{r.quantity}",
        })

    transfers = db.query(TransferRecord).filter(
        TransferRecord.goods_id == goods_id
    ).order_by(TransferRecord.created_at.desc()).limit(20).all()
    for t in transfers:
        from_wh = db.query(Warehouse).filter(Warehouse.id == t.from_warehouse_id).first()
        to_wh = db.query(Warehouse).filter(Warehouse.id == t.to_warehouse_id).first()
        to_person = db.query(Person).filter(Person.id == t.to_person_id).first()
        transfer_type_map = {"outbound": "借出", "return": "还货", "direct": "直接出库"}
        sign = "+" if t.transfer_type == "return" else "-"
        target = to_person.name if to_person else (to_wh.name if to_wh else "")
        recent_records.append({
            "type": transfer_type_map.get(t.transfer_type, "调拨"),
            "date": t.created_at,
            "quantity": t.quantity,
            "warehouse": f"{from_wh.name if from_wh else ''} → {target}",
            "ref_no": t.transfer_no,
            "operator": t.operator or "",
            "detail": f"{transfer_type_map.get(t.transfer_type, '调拨')} {sign}{t.quantity}",
            "status": t.status,
        })

    adjustments = db.query(GoodsAdjustment).filter(
        GoodsAdjustment.goods_id == goods_id
    ).order_by(GoodsAdjustment.id.desc()).limit(20).all()
    for a in adjustments:
        wh = db.query(Warehouse).filter(Warehouse.id == a.warehouse_id).first()
        recent_records.append({
            "type": "盘点调整",
            "date": a.created_at,
            "quantity": a.diff_qty,
            "warehouse": wh.name if wh else "",
            "ref_no": a.adjust_no,
            "operator": a.operator,
            "detail": f"调整 {a.system_qty}→{a.actual_qty} ({a.status})",
        })

    recent_records.sort(key=lambda x: x["date"] if x["date"] else now, reverse=True)

    return {
        "goods_id": goods.id,
        "barcode": goods.barcode,
        "name": goods.name,
        "spec": goods.spec,
        "unit": goods.unit,
        "price": goods.price,
        "warehouse_stocks": warehouse_stocks,
        "total_quantity": sum(s.quantity for s in stocks),
        "recent_records": recent_records[:50],
    }
