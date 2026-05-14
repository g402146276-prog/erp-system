from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
from app.database import get_db
from app.models.inbound_apply import InboundApply

router = APIRouter(prefix="/api/inbound-apply", tags=["入库申请单"])


class InboundApplyCreate(BaseModel):
    apply_type: str
    applicant_id: int
    customer_name: str = None
    boniu_order_no: str = None
    goods_details: str
    expect_date: str = None
    remark: str = None


class InboundApplyUpdate(BaseModel):
    boniu_order_status: str = None
    status: str = None
    arrived_quantity: int = None
    remark: str = None


class InboundApplyResponse(BaseModel):
    id: int
    apply_no: str
    apply_type: str
    applicant_id: int
    customer_name: Optional[str] = None
    boniu_order_no: Optional[str] = None
    boniu_order_status: str
    goods_details: Optional[str] = None
    expect_date: Optional[str] = None
    status: str
    arrived_quantity: int
    total_quantity: int
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def generate_apply_no():
    now = datetime.now()
    return f"RK{now.strftime('%Y%m%d%H%M%S')}"


@router.get("/", response_model=List[InboundApplyResponse])
def list_inbound_applies(skip: int = 0, limit: int = 100, status: str = None, applicant_id: int = None, db: Session = Depends(get_db)):
    query = db.query(InboundApply)
    if status:
        query = query.filter(InboundApply.status == status)
    if applicant_id:
        query = query.filter(InboundApply.applicant_id == applicant_id)
    applies = query.order_by(InboundApply.created_at.desc()).offset(skip).limit(limit).all()
    return applies


@router.get("/{apply_id}", response_model=InboundApplyResponse)
def get_inbound_apply(apply_id: int, db: Session = Depends(get_db)):
    apply = db.query(InboundApply).filter(InboundApply.id == apply_id).first()
    if not apply:
        raise HTTPException(status_code=404, detail="入库申请单不存在")
    return apply


@router.post("/", response_model=InboundApplyResponse)
def create_inbound_apply(apply_data: InboundApplyCreate, db: Session = Depends(get_db)):
    try:
        goods_details_json = json.loads(apply_data.goods_details) if isinstance(apply_data.goods_details, str) else apply_data.goods_details
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"商品明细JSON格式错误: {str(e)}")
    if not isinstance(goods_details_json, list):
        raise HTTPException(status_code=400, detail="商品明细必须是数组格式")
    total_quantity = sum(item.get("quantity", 0) for item in goods_details_json)

    apply = InboundApply(
        apply_no=generate_apply_no(),
        applicant_id=apply_data.applicant_id,
        apply_type=apply_data.apply_type,
        customer_name=apply_data.customer_name,
        boniu_order_no=apply_data.boniu_order_no,
        goods_details=apply_data.goods_details,
        expect_date=apply_data.expect_date,
        total_quantity=total_quantity,
        status="pending"
    )
    db.add(apply)
    db.commit()
    db.refresh(apply)
    return apply


@router.put("/{apply_id}", response_model=InboundApplyResponse)
def update_inbound_apply(apply_id: int, apply_data: InboundApplyUpdate, db: Session = Depends(get_db)):
    apply = db.query(InboundApply).filter(InboundApply.id == apply_id).first()
    if not apply:
        raise HTTPException(status_code=404, detail="入库申请单不存在")

    update_data = apply_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(apply, key, value)

    db.commit()
    db.refresh(apply)
    return apply


@router.delete("/{apply_id}")
def delete_inbound_apply(apply_id: int, db: Session = Depends(get_db)):
    apply = db.query(InboundApply).filter(InboundApply.id == apply_id).first()
    if not apply:
        raise HTTPException(status_code=404, detail="入库申请单不存在")

    db.delete(apply)
    db.commit()
    return {"message": "删除成功"}
