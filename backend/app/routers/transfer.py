from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.transfer import TransferRecord
from app.models.stock import Stock

router = APIRouter(prefix="/api/transfer", tags=["调拨管理"])


class TransferCreate(BaseModel):
    transfer_type: str
    from_warehouse_id: int
    to_warehouse_id: int
    from_person_id: int = None
    to_person_id: int = None
    goods_id: int
    quantity: int
    sales_tag: str = None
    remark: str = None
    operator: str = None


class TransferUpdate(BaseModel):
    status: str = None
    approved_by: str = None
    remark: str = None
    reversed_remark: str = None


class TransferResponse(BaseModel):
    id: int
    transfer_no: str
    transfer_type: str
    from_warehouse_id: int
    to_warehouse_id: int
    from_person_id: Optional[int] = None
    to_person_id: Optional[int] = None
    goods_id: int
    quantity: int
    sales_tag: Optional[str] = None
    status: str
    remark: Optional[str] = None
    operator: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def generate_transfer_no(db: Session = None):
    now = datetime.now()
    ts = now.strftime('%Y%m%d%H%M%S')
    if db:
        last = db.query(TransferRecord).filter(
            TransferRecord.transfer_no.like(f"DB{ts}%")
        ).order_by(TransferRecord.id.desc()).first()
        if last:
            seq = int(last.transfer_no[-3:]) + 1
            return f"DB{ts}{seq:03d}"
    return f"DB{ts}000"


@router.get("/", response_model=List[TransferResponse])
def list_transfers(skip: int = 0, limit: int = 100, transfer_type: str = None, status: str = None, db: Session = Depends(get_db)):
    query = db.query(TransferRecord)
    if transfer_type:
        query = query.filter(TransferRecord.transfer_type == transfer_type)
    if status:
        query = query.filter(TransferRecord.status == status)
    transfers = query.order_by(TransferRecord.created_at.desc()).offset(skip).limit(limit).all()
    return transfers


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(TransferRecord).filter(TransferRecord.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨记录不存在")
    return transfer


@router.post("/", response_model=TransferResponse)
def create_transfer(transfer_data: TransferCreate, db: Session = Depends(get_db)):
    transfer = TransferRecord(
        transfer_no=generate_transfer_no(db),
        **transfer_data.model_dump()
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


@router.put("/{transfer_id}/approve", response_model=TransferResponse)
def approve_transfer(transfer_id: int, approved_by: str = None, db: Session = Depends(get_db)):
    transfer = db.query(TransferRecord).filter(TransferRecord.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨记录不存在")

    if transfer.status != "pending":
        raise HTTPException(status_code=400, detail="只能审批待审批状态的调拨单")

    transfer.status = "approved"
    transfer.approved_by = approved_by
    transfer.approved_at = datetime.now()

    # 扣减源仓库存
    src_stock = db.query(Stock).filter(
        Stock.warehouse_id == transfer.from_warehouse_id,
        Stock.goods_id == transfer.goods_id,
    ).first()
    if not src_stock or src_stock.quantity < transfer.quantity:
        raise HTTPException(status_code=400, detail=f"源仓库库存不足，当前库存: {src_stock.quantity if src_stock else 0}")
    src_stock.quantity -= transfer.quantity

    # 增加目标仓库库存
    dst_stock = db.query(Stock).filter(
        Stock.warehouse_id == transfer.to_warehouse_id,
        Stock.goods_id == transfer.goods_id,
    ).first()
    if dst_stock:
        dst_stock.quantity += transfer.quantity
    else:
        dst_stock = Stock(
            warehouse_id=transfer.to_warehouse_id,
            goods_id=transfer.goods_id,
            quantity=transfer.quantity,
        )
        db.add(dst_stock)

    transfer.status = "completed"
    db.commit()
    db.refresh(transfer)

    return transfer


@router.put("/{transfer_id}/reverse", response_model=TransferResponse)
def reverse_transfer(transfer_id: int, reversed_remark: str = None, db: Session = Depends(get_db)):
    transfer = db.query(TransferRecord).filter(TransferRecord.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨记录不存在")

    if transfer.status == "reversed":
        raise HTTPException(status_code=400, detail="该单据已被红冲")

    # 恢复源仓库库存
    src_stock = db.query(Stock).filter(
        Stock.warehouse_id == transfer.from_warehouse_id,
        Stock.goods_id == transfer.goods_id,
    ).first()
    if src_stock:
        src_stock.quantity += transfer.quantity
    else:
        src_stock = Stock(
            warehouse_id=transfer.from_warehouse_id,
            goods_id=transfer.goods_id,
            quantity=transfer.quantity,
        )
        db.add(src_stock)

    # 扣减目标仓库库存
    dst_stock = db.query(Stock).filter(
        Stock.warehouse_id == transfer.to_warehouse_id,
        Stock.goods_id == transfer.goods_id,
    ).first()
    if dst_stock:
        dst_stock.quantity -= transfer.quantity

    transfer.status = "reversed"
    transfer.reversed_remark = reversed_remark
    transfer.reversed_at = datetime.now()

    db.commit()
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}")
def delete_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(TransferRecord).filter(TransferRecord.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨记录不存在")

    db.delete(transfer)
    db.commit()
    return {"message": "删除成功"}
