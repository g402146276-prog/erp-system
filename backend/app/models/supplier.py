from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, comment="供应商编码")
    name = Column(String(100), nullable=False, comment="供应商名称")
    short_name = Column(String(50), comment="简称")
    contact = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    mobile = Column(String(20), comment="手机")
    email = Column(String(100), comment="邮箱")
    address = Column(Text, comment="地址")
    bank_info = Column(String(200), comment="银行信息")
    tax_no = Column(String(50), comment="税号")
    is_active = Column(Boolean, default=True, comment="是否启用")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())