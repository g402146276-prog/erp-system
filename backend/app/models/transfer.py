from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class TransferRecord(Base):
    __tablename__ = "transfer_records"

    id = Column(Integer, primary_key=True, index=True)
    transfer_no = Column(String(50), unique=True, nullable=False, comment="调拨单号")
    transfer_type = Column(String(20), nullable=False, comment="调拨类型: outbound=借出, return=还货, direct=直接出库")
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="调出仓库ID")
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="调入仓库ID")
    from_person_id = Column(Integer, ForeignKey("persons.id"), comment="调出负责人ID")
    to_person_id = Column(Integer, ForeignKey("persons.id"), comment="调入负责人ID")
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, comment="商品ID")
    quantity = Column(Integer, nullable=False, comment="调拨数量")
    sales_tag = Column(String(100), comment="销售线索标签")
    status = Column(String(20), default="pending", comment="状态: pending=待审批, approved=已审批, rejected=已驳回, completed=已完成, reversed=已红冲")
    remark = Column(Text, comment="备注")
    reversed_remark = Column(Text, comment="红冲备注")
    operator = Column(String(50), comment="操作人")
    approved_by = Column(String(50), comment="审批人")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), comment="审批时间")
    reversed_at = Column(DateTime(timezone=True), comment="红冲时间")
