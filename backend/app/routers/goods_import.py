from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import csv
import io
from app.database import get_db
from app.models.goods import Goods
from app.models.goods_import import GoodsImportRecord

router = APIRouter(prefix="/api/goods-import", tags=["档案管理"])


class ImportResponse(BaseModel):
    id: int
    file_name: str
    total_count: int
    success_count: int
    fail_count: int
    status: str
    error_message: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoodsItem(BaseModel):
    barcode: str
    name: str
    spec: str = None
    unit: str = "个"
    category: str = None
    price: float = 0
    remark: str = None


@router.get("/", response_model=List[ImportResponse])
def list_import_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    records = db.query(GoodsImportRecord).order_by(GoodsImportRecord.created_at.desc()).offset(skip).limit(limit).all()
    return records


@router.get("/{record_id}", response_model=ImportResponse)
def get_import_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(GoodsImportRecord).filter(GoodsImportRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="导入记录不存在")
    return record


@router.post("/upload")
async def upload_goods_file(
    file: UploadFile = File(...),
    operator: str = None,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="只支持CSV文件")

    # 创建导入记录
    record = GoodsImportRecord(
        file_name=file.filename,
        status="processing",
        operator=operator
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    try:
        # 读取CSV文件（自动识别编码）
        contents = await file.read()
        try:
            raw = contents.decode('utf-8-sig')
        except UnicodeDecodeError:
            raw = contents.decode('gbk', errors='replace')
        csv_file = io.StringIO(raw)
        reader = csv.DictReader(csv_file)

        total_count = 0
        success_count = 0
        fail_count = 0
        errors = []
        seen_barcodes = set()  # 跟踪本次CSV内已出现的条码

        for row in reader:
            total_count += 1
            try:
                barcode = row.get('barcode') or row.get('条码')
                name = row.get('name') or row.get('名称')
                spec = row.get('spec') or row.get('规格', '')
                unit = row.get('unit') or row.get('单位', '个')
                category = row.get('category') or row.get('分类', '')
                price = row.get('price') or row.get('单价', 0)
                remark = row.get('remark') or row.get('备注', '')

                if not barcode or not name:
                    fail_count += 1
                    errors.append(f"第{total_count}行: 条码和名称不能为空")
                    continue

                # 检查CSV内重复条码
                if barcode in seen_barcodes:
                    fail_count += 1
                    errors.append(f"第{total_count}行: 条码'{barcode}'在文件中重复")
                    continue
                seen_barcodes.add(barcode)

                existing = db.query(Goods).filter(Goods.barcode == barcode).first()
                if existing:
                    existing.name = name
                    existing.spec = spec
                    existing.unit = unit
                    existing.category = category
                    existing.price = float(price or 0)
                    existing.remark = remark
                else:
                    goods = Goods(
                        barcode=barcode,
                        name=name,
                        spec=spec,
                        unit=unit,
                        category=category,
                        price=float(price or 0),
                        remark=remark
                    )
                    db.add(goods)

                success_count += 1

            except Exception as e:
                fail_count += 1
                errors.append(f"第{total_count}行: {str(e)}")

        # 更新导入记录（与商品变更在同一事务中提交）
        record.total_count = total_count
        record.success_count = success_count
        record.fail_count = fail_count
        record.status = "completed" if fail_count == 0 else "partial"
        record.error_message = "\n".join(errors) if errors else None
        record.completed_at = datetime.now()
        db.commit()
        db.refresh(record)

        return {
            "message": "导入完成",
            "record_id": record.id,
            "total": total_count,
            "success": success_count,
            "fail": fail_count
        }

    except Exception as e:
        db.rollback()  # 先回滚损坏的事务
        record = db.query(GoodsImportRecord).filter(GoodsImportRecord.id == record.id).first()
        if record:
            record.status = "failed"
            record.error_message = str(e)
            record.completed_at = datetime.now()
            db.commit()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/template/download")
def download_template():
    template_content = "条码,名称,规格,单位,分类,单价,备注\n"
    template_content += "C010114090155,和合璧鸳鸯炉,约φ79*10mm/0.25kg,个,香炉,299,精品\n"
    template_content += "C010114090156,铜香炉A款,约φ60*8mm/0.2kg,个,香炉,199,\n"
    
    return {
        "filename": "商品档案导入模板.csv",
        "content": template_content,
        "headers": ["条码", "名称", "规格", "单位", "分类", "单价", "备注"],
        "description": "条码和名称为必填项"
    }