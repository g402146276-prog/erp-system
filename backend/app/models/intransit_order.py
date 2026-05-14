from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class IntransitOrder(Base):
    """在途订单 - 直发客户/跨店调拨，货在途中先记录，参与库存计算"""
    __tablename__ = "intransit_orders"

    id = Column(Integer, primary_key=True, index=True)
    apply_no = Column(String(50), unique=True, nullable=False)  # ZT+时间戳
    order_type = Column(String(20), nullable=False)  # direct_shipping / cross_transfer
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    customer_name = Column(String(100), nullable=True)
    bojun_order_no = Column(String(50), nullable=True)
    bojun_order_status = Column(String(20), default="pending")  # pending/synced/completed
    status = Column(String(20), default="pending")  # pending / completed / cancelled
    # 关联链路：入库→调拨→出库
    inbound_record_id = Column(Integer, ForeignKey("inbound_records.id"), nullable=True)
    transfer_id = Column(Integer, ForeignKey("transfer_applies.id"), nullable=True)
    outbound_id = Column(Integer, ForeignKey("outbound_orders.id"), nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
