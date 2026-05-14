from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base


class GoodsImportRecord(Base):
    __tablename__ = "goods_import_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False, comment="导入文件名")
    total_count = Column(Integer, default=0, comment="总记录数")
    success_count = Column(Integer, default=0, comment="成功导入数")
    fail_count = Column(Integer, default=0, comment="失败数")
    status = Column(String(20), default="processing", comment="状态: processing=处理中, completed=完成, failed=失败")
    error_message = Column(Text, comment="错误信息")
    operator = Column(String(50), comment="操作人")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), comment="完成时间")