from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, comment="人员编码")
    name = Column(String(50), nullable=False, comment="姓名")
    person_type = Column(String(20), default="sales", comment="人员类型: sales=销售, warehouse=仓管, other=其他")
    department = Column(String(50), comment="部门/组别")
    phone = Column(String(20), comment="联系电话")
    is_active = Column(Boolean, default=True, comment="是否启用")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
