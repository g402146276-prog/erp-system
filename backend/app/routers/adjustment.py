from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from app.database import get_db
from app.models.adjustment import GoodsAdjustment
from app.models.stock import Stock
from app.models.goods import Goods
from app.models.warehouse import Warehouse
from app.models.transfer import TransferRecord
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/adjustments", tags=["调整单管理"])


class AdjustmentCreate(BaseModel):
    warehouse_id: int
    goods_id: int
    actual_qty: int
    remark: Optional[str] = None


class AdjustmentResponse(BaseModel):
    id: int
    adjust_no: str
    warehouse_id: int
    goods_id: int
    system_qty: int
    actual_qty: int
    diff_qty: int
    borrowed_qty: int
    pending_pickup_qty: int
    gifted_qty: int
    unexplained_qty: int
    operator: str
    status: str
    remark: Optional[str]
    created_at: Optional[datetime]
    applied_at: Optional[datetime]
    applied_by: Optional[str]
    goods_name: Optional[str] = None
    goods_barcode: Optional[str] = None
    warehouse_name: Optional[str] = None

    class Config:
        from_attributes = True


def generate_adjust_no(db: Session) -> str:
    from datetime import datetime
    now = datetime.now()
    prefix = f"TZ{now.strftime('%Y%m%d')}"
    last = db.query(GoodsAdjustment).filter(
        GoodsAdjustment.adjust_no.like(f"{prefix}%")
    ).order_by(GoodsAdjustment.id.desc()).first()
    seq = 1
    if last:
        seq = int(last.adjust_no[-4:]) + 1
    return f"{prefix}{seq:04d}"


@router.post("/", response_model=AdjustmentResponse)
def create_adjustment(
    req: AdjustmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建单品调整单（只记录差异，不修改库存）"""
    stock = db.query(Stock).filter(
        Stock.warehouse_id == req.warehouse_id,
        Stock.goods_id == req.goods_id,
    ).first()
    if not stock:
        raise HTTPException(status_code=404, detail="该仓库下无此商品的库存记录")

    system_qty = stock.quantity
    diff_qty = req.actual_qty - system_qty

    # 自动分析差异原因：查询当前借出数量总和
    borrowed = db.query(func.coalesce(func.sum(TransferRecord.quantity), 0)).filter(
        TransferRecord.goods_id == req.goods_id,
        TransferRecord.from_warehouse_id == req.warehouse_id,
        TransferRecord.status.in_(["pending", "approved", "completed"]),
        TransferRecord.transfer_type == "outbound",
    ).scalar()

    adjust = GoodsAdjustment(
        adjust_no=generate_adjust_no(db),
        warehouse_id=req.warehouse_id,
        goods_id=req.goods_id,
        system_qty=system_qty,
        actual_qty=req.actual_qty,
        diff_qty=diff_qty,
        borrowed_qty=borrowed,
        pending_pickup_qty=0,
        gifted_qty=0,
        unexplained_qty=diff_qty - borrowed,
        operator=user.display_name,
        status="pending",
        remark=req.remark,
    )
    db.add(adjust)
    db.commit()
    db.refresh(adjust)
    return _format_adjustment(adjust, db)


@router.get("/", response_model=List[AdjustmentResponse])
def list_adjustments(
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(GoodsAdjustment)
    if status:
        query = query.filter(GoodsAdjustment.status == status)
    if warehouse_id:
        query = query.filter(GoodsAdjustment.warehouse_id == warehouse_id)
    query = query.order_by(GoodsAdjustment.id.desc()).limit(100)
    return [_format_adjustment(a, db) for a in query.all()]


@router.get("/{adjust_id}", response_model=AdjustmentResponse)
def get_adjustment(adjust_id: int, db: Session = Depends(get_db)):
    adjust = db.query(GoodsAdjustment).filter(GoodsAdjustment.id == adjust_id).first()
    if not adjust:
        raise HTTPException(status_code=404, detail="调整单不存在")
    return _format_adjustment(adjust, db)


@router.put("/{adjust_id}/apply")
def apply_adjustment(
    adjust_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """审核通过调整单，按实际数量更新库存"""
    adjust = db.query(GoodsAdjustment).filter(GoodsAdjustment.id == adjust_id).first()
    if not adjust:
        raise HTTPException(status_code=404, detail="调整单不存在")
    if adjust.status != "pending":
        raise HTTPException(status_code=400, detail="只有待审核的调整单才能审核")

    stock = db.query(Stock).filter(
        Stock.warehouse_id == adjust.warehouse_id,
        Stock.goods_id == adjust.goods_id,
    ).first()
    if not stock:
        raise HTTPException(status_code=404, detail="库存记录不存在")

    stock.quantity = adjust.actual_qty
    adjust.status = "applied"
    adjust.applied_at = datetime.now(timezone.utc)
    adjust.applied_by = user.display_name
    db.commit()
    return {"message": "调整单已审核，库存已更新", "adjust_no": adjust.adjust_no}


@router.put("/{adjust_id}/cancel")
def cancel_adjustment(
    adjust_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    adjust = db.query(GoodsAdjustment).filter(GoodsAdjustment.id == adjust_id).first()
    if not adjust:
        raise HTTPException(status_code=404, detail="调整单不存在")
    if adjust.status != "pending":
        raise HTTPException(status_code=400, detail="只能作废待审核的调整单")
    adjust.status = "cancelled"
    db.commit()
    return {"message": "调整单已作废"}


def _format_adjustment(adjust: GoodsAdjustment, db: Session):
    goods = db.query(Goods).filter(Goods.id == adjust.goods_id).first()
    wh = db.query(Warehouse).filter(Warehouse.id == adjust.warehouse_id).first()
    return AdjustmentResponse(
        id=adjust.id,
        adjust_no=adjust.adjust_no,
        warehouse_id=adjust.warehouse_id,
        goods_id=adjust.goods_id,
        system_qty=adjust.system_qty,
        actual_qty=adjust.actual_qty,
        diff_qty=adjust.diff_qty,
        borrowed_qty=adjust.borrowed_qty,
        pending_pickup_qty=adjust.pending_pickup_qty,
        gifted_qty=adjust.gifted_qty,
        unexplained_qty=adjust.unexplained_qty,
        operator=adjust.operator,
        status=adjust.status,
        remark=adjust.remark,
        created_at=adjust.created_at,
        applied_at=adjust.applied_at,
        applied_by=adjust.applied_by,
        goods_name=goods.name if goods else None,
        goods_barcode=goods.barcode if goods else None,
        warehouse_name=wh.name if wh else None,
    )
