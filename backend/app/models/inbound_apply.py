from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class InboundApply(Base):
    __tablename__ = "inbound_applies"

    id = Column(Integer, primary_key=True, index=True)
    apply_no = Column(String(50), unique=True, nullable=False, comment="申请单号")
    apply_type = Column(String(20), nullable=False, comment="申请类型: direct=直发客户, transfer=调拨订单")
    applicant_id = Column(Integer, ForeignKey("persons.id"), nullable=False, comment="申请人ID")
    customer_name = Column(String(100), comment="客户姓名")
    boniu_order_no = Column(String(50), comment="伯俊订单号")
    boniu_order_status = Column(String(20), default="pending", comment="伯俊订单状态: pending=待入库, synced=数据已同步, completed=已完成, cancelled=已取消")
    goods_details = Column(Text, comment="商品明细JSON: [{goods_id, barcode, name, quantity}]")
    expect_date = Column(String(20), comment="期望到货日期")
    status = Column(String(20), default="pending", comment="状态: pending=待入库, part=部分到货, completed=已完成, cancelled=已取消")
    arrived_quantity = Column(Integer, default=0, comment="已到货数量")
    total_quantity = Column(Integer, default=0, comment="总数量")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
