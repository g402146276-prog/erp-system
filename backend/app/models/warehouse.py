from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, comment="仓库编码")
    name = Column(String(50), nullable=False, comment="仓库名称")
    warehouse_type = Column(String(20), default="entity", comment="仓库类型: entity=实体仓, virtual_sales=销售虚拟仓, virtual_exhibit=展台虚拟仓, virtual_damage=报损仓")
    parent_id = Column(Integer, default=0, comment="父级ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
