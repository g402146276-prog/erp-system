from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class InboundRecord(Base):
    __tablename__ = "inbound_records"

    id = Column(Integer, primary_key=True, index=True)
    inbound_apply_id = Column(Integer, ForeignKey("inbound_applies.id"), nullable=True, comment="入库申请单ID")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="入库仓库ID")
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, comment="商品ID")
    quantity = Column(Integer, nullable=False, comment="入库数量")
    boniu_order_no = Column(String(50), comment="伯俊订单号")
    operator = Column(String(50), comment="操作人")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
