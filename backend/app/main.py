from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import (
    goods, warehouse, inbound, inbound_apply, transfer, stock,
    goods_import, person, supplier, auth, location, adjustment,
    warehouse_manager, transfer_apply as transfer_apply_router,
    purchase_inbound, intransit_order, outbound, gift,
    approval_rule, reconciliation,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="仓库ERP系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 生产模式：提供前端静态文件 =====
import os
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

@app.middleware("http")
async def add_charset_and_spa(request, call_next):
    # 生产模式下，非API请求返回前端页面
    if os.path.isdir(frontend_dist):
        path = request.url.path
        if path.startswith("/assets/"):
            from fastapi.staticfiles import StaticFiles
            static = StaticFiles(directory=os.path.join(frontend_dist, "assets"))
            return await static(request, call_next)
        if not path.startswith("/api/") and not path.startswith("/docs") and not path.startswith("/openapi"):
            index_path = os.path.join(frontend_dist, "index.html")
            if os.path.isfile(index_path):
                return FileResponse(index_path)

    response = await call_next(request)
    ct = response.headers.get("content-type", "")
    if ct.startswith(("text/", "application/json")):
        if "charset" not in ct:
            response.headers["content-type"] = ct + "; charset=utf-8"
    return response

# 原有路由（保持兼容）
app.include_router(goods.router)
app.include_router(warehouse.router)
app.include_router(inbound.router)
app.include_router(inbound_apply.router)
app.include_router(transfer.router)
app.include_router(stock.router)
app.include_router(goods_import.router)
app.include_router(person.router)
app.include_router(supplier.router)
app.include_router(auth.router)
app.include_router(location.router)
app.include_router(adjustment.router)

# 新路由
app.include_router(warehouse_manager.router)
app.include_router(transfer_apply_router.router)
app.include_router(purchase_inbound.router)
app.include_router(intransit_order.router)
app.include_router(outbound.router)
app.include_router(gift.router)
app.include_router(approval_rule.router)
app.include_router(reconciliation.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
