from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class GoodsAdjustment(Base):
    __tablename__ = "goods_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    adjust_no = Column(String(50), unique=True, nullable=False, comment="调整单号 TZ+时间戳")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, comment="商品ID")

    system_qty = Column(Integer, nullable=False, comment="调整前系统数量")
    actual_qty = Column(Integer, nullable=False, comment="实际清点数量")
    diff_qty = Column(Integer, nullable=False, comment="差异 = actual - system")

    borrowed_qty = Column(Integer, default=0, comment="其中已借出数量")
    pending_pickup_qty = Column(Integer, default=0, comment="其中已出库未取")
    gifted_qty = Column(Integer, default=0, comment="其中已赠送")
    unexplained_qty = Column(Integer, default=0, comment="无法解释的差异")

    operator = Column(String(50), nullable=False, comment="操作人")
    status = Column(String(20), default="pending", comment="draft/pending/applied/cancelled")
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_at = Column(DateTime(timezone=True), nullable=True)
    applied_by = Column(String(50), nullable=True, comment="审核人")
