from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.intransit_order import IntransitOrder
from app.models.goods import Goods
from app.models.warehouse import Warehouse
from app.models.stock import Stock
from app.models.inbound import InboundRecord
from app.models.transfer_apply import TransferApply
from app.models.outbound_order import OutboundOrder
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/intransit-orders", tags=["在途订单"])


class IntransitCreate(BaseModel):
    order_type: str  # direct_shipping / cross_transfer
    goods_id: int
    quantity: int
    warehouse_id: int  # 入库仓库
    customer_name: Optional[str] = None
    bojun_order_no: Optional[str] = None
    remark: Optional[str] = None


def generate_apply_no(db: Session) -> str:
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    prefix = f"ZT{date_str}"
    last = db.query(IntransitOrder).filter(
        IntransitOrder.apply_no.like(f"{prefix}%")
    ).order_by(IntransitOrder.id.desc()).first()
    if last:
        seq = int(last.apply_no[-4:]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


@router.post("/")
def create_intransit(
    data: IntransitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建在途订单，自动生成入库→调拨→出库链路"""
    apply_no = generate_apply_no(db)

    # 1. 创建在途订单记录
    order = IntransitOrder(
        apply_no=apply_no,
        order_type=data.order_type,
        applicant_id=current_user.id,
        goods_id=data.goods_id,
        quantity=data.quantity,
        customer_name=data.customer_name,
        bojun_order_no=data.bojun_order_no,
        status="pending",
        remark=data.remark,
    )

    # 2. 增加库存（在途即算实物库存）
    stock = db.query(Stock).filter(
        Stock.warehouse_id == data.warehouse_id,
        Stock.goods_id == data.goods_id,
    ).first()
    if stock:
        stock.quantity += data.quantity
    else:
        stock = Stock(
            warehouse_id=data.warehouse_id,
            goods_id=data.goods_id,
            quantity=data.quantity,
        )
        db.add(stock)

    # 3. 创建入库记录
    inbound_rec = InboundRecord(
        warehouse_id=data.warehouse_id,
        goods_id=data.goods_id,
        quantity=data.quantity,
        bojun_order_no=data.bojun_order_no,
        operator=current_user.display_name,
        remark=f"在途订单[{apply_no}]自动入库",
    )
    db.add(inbound_rec)
    db.flush()
    order.inbound_record_id = inbound_rec.id

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/transfer")
def link_transfer(
    order_id: int,
    transfer_apply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """关联在途订单到调拨申请单"""
    order = db.query(IntransitOrder).filter(IntransitOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="在途订单不存在")
    order.transfer_id = transfer_apply_id
    db.commit()
    return {"message": "已关联"}


@router.post("/{order_id}/outbound")
def link_outbound(
    order_id: int,
    outbound_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """关联在途订单到出库单"""
    order = db.query(IntransitOrder).filter(IntransitOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="在途订单不存在")
    order.outbound_id = outbound_id
    order.status = "completed"
    db.commit()
    return {"message": "已关联，在途订单已完成"}


@router.get("/")
def list_intransit(
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(IntransitOrder)
    if status:
        query = query.filter(IntransitOrder.status == status)
    if order_type:
        query = query.filter(IntransitOrder.order_type == order_type)
    records = query.order_by(IntransitOrder.created_at.desc()).limit(200).all()
    result = []
    for r in records:
        goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
        applicant = db.query(User).filter(User.id == r.applicant_id).first()
        result.append({
            "id": r.id,
            "apply_no": r.apply_no,
            "order_type": r.order_type,
            "goods_name": goods.name if goods else "",
            "goods_barcode": goods.barcode if goods else "",
            "quantity": r.quantity,
            "customer_name": r.customer_name,
            "bojun_order_no": r.bojun_order_no,
            "status": r.status,
            "applicant": applicant.display_name if applicant else "",
            "inbound_record_id": r.inbound_record_id,
            "transfer_id": r.transfer_id,
            "outbound_id": r.outbound_id,
            "remark": r.remark,
            "created_at": r.created_at,
        })
    return result


@router.get("/{order_id}")
def get_intransit(order_id: int, db: Session = Depends(get_db)):
    r = db.query(IntransitOrder).filter(IntransitOrder.id == order_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="在途订单不存在")
    goods = db.query(Goods).filter(Goods.id == r.goods_id).first()
    applicant = db.query(User).filter(User.id == r.applicant_id).first()
    return {
        "id": r.id,
        "apply_no": r.apply_no,
        "order_type": r.order_type,
        "goods_id": r.goods_id,
        "goods_name": goods.name if goods else "",
        "goods_barcode": goods.barcode if goods else "",
        "quantity": r.quantity,
        "customer_name": r.customer_name,
        "bojun_order_no": r.bojun_order_no,
        "bojun_order_status": r.bojun_order_status,
        "status": r.status,
        "applicant": applicant.display_name if applicant else "",
        "inbound_record_id": r.inbound_record_id,
        "transfer_id": r.transfer_id,
        "outbound_id": r.outbound_id,
        "remark": r.remark,
        "created_at": r.created_at,
    }


@router.put("/{order_id}/cancel")
def cancel_intransit(order_id: int, db: Session = Depends(get_db)):
    order = db.query(IntransitOrder).filter(IntransitOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="在途订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只能作废待处理的订单")
    order.status = "cancelled"
    # 扣回库存
    if order.inbound_record_id:
        rec = db.query(InboundRecord).filter(
            InboundRecord.id == order.inbound_record_id
        ).first()
        if rec:
            stock = db.query(Stock).filter(
                Stock.warehouse_id == rec.warehouse_id,
                Stock.goods_id == rec.goods_id,
            ).first()
            if stock:
                stock.quantity -= rec.quantity
    db.commit()
    return {"message": "已作废"}
