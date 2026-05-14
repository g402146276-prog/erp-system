from app.database import SessionLocal, engine, Base
from app.models import Goods, Warehouse, Person, Stock

Base.metadata.create_all(bind=engine)


def init_sample_data():
    db = SessionLocal()

    if db.query(Warehouse).count() == 0:
        warehouses = [
            Warehouse(code="WH001", name="大仓库", warehouse_type="entity", remark="主仓库"),
            Warehouse(code="WH002", name="小仓库1", warehouse_type="entity", remark="副仓库1"),
            Warehouse(code="WH003", name="小仓库2", warehouse_type="entity", remark="副仓库2"),
            Warehouse(code="VS001", name="报损仓", warehouse_type="virtual_damage", remark="报损商品存放"),
        ]
        for w in warehouses:
            db.add(w)
        print("仓库数据初始化完成")

    if db.query(Person).count() == 0:
        persons = [
            Person(code="P001", name="仓管员", person_type="warehouse", department="仓储部"),
            Person(code="S001", name="销售A", person_type="sales", department="销售组A"),
            Person(code="S002", name="销售B", person_type="sales", department="销售组A"),
            Person(code="S003", name="销售C", person_type="sales", department="销售组B"),
        ]
        for p in persons:
            db.add(p)
        print("人员数据初始化完成")

    if db.query(Goods).count() == 0:
        goods_list = [
            Goods(barcode="C010114090155", name="和合璧鸳鸯炉", spec="约φ79*10mm/0.25kg", unit="个", category="铜摆件", price=500),
            Goods(barcode="C010114090156", name="铜香炉A款", spec="约φ60*8mm/0.2kg", unit="个", category="铜香炉", price=350),
            Goods(barcode="C010114090157", name="铜香炉B款", spec="约φ70*9mm/0.22kg", unit="个", category="铜香炉", price=400),
        ]
        for g in goods_list:
            db.add(g)
        print("商品数据初始化完成")

    db.commit()
    db.close()
    print("数据初始化完成！")


if __name__ == "__main__":
    init_sample_data()
