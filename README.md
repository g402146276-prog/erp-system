# 仓库ERP系统

## 项目简介

这是一个基于Vue3 + FastAPI的仓库ERP系统，专门为卖场型仓库设计，支持：

- 入库登记（扫条码入库）
- 入库申请单（直发客户订单追踪）
- 调拨管理（借出/还货/直接出库）
- 库存查询（三仓分布）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Element Plus |
| 后端 | Python + FastAPI |
| 数据库 | SQLite |
| 构建工具 | Vite |

## 项目结构

```
erp-system/
├── backend/                 # 后端
│   ├── app/
│   │   ├── main.py         # FastAPI入口
│   │   ├── database.py     # 数据库配置
│   │   ├── models/         # 数据模型
│   │   └── routers/        # API路由
│   ├── init_data.py        # 初始化数据
│   └── requirements.txt    # Python依赖
│
└── frontend/               # 前端
    ├── src/
    │   ├── views/         # 页面组件
    │   ├── api/           # API调用
    │   └── router/        # 路由配置
    └── package.json
```

## 快速启动

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库和示例数据
python init_data.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后访问：http://localhost:8000

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问：http://localhost:3000

## 初始数据

运行 `init_data.py` 后会自动创建以下示例数据：

### 仓库
| 编码 | 名称 | 类型 |
|------|------|------|
| WH001 | 大仓库 | 实体仓 |
| WH002 | 小仓库1 | 实体仓 |
| WH003 | 小仓库2 | 实体仓 |
| VS001 | 报损仓 | 虚拟仓 |

### 人员
| 编码 | 姓名 | 类型 |
|------|------|------|
| P001 | 仓管员 | 仓管 |
| S001 | 销售A | 销售 |
| S002 | 销售B | 销售 |
| S003 | 销售C | 销售 |

### 商品
| 条码 | 名称 | 规格 |
|------|------|------|
| C010114090155 | 和合璧鸳鸯炉 | 约φ79*10mm/0.25kg |
| C010114090156 | 铜香炉A款 | 约φ60*8mm/0.2kg |
| C010114090157 | 铜香炉B款 | 约φ70*9mm/0.22kg |

## 功能说明

### 入库登记
1. 扫描或输入商品条码
2. 选择入库仓库
3. 输入入库数量
4. 可选填伯俊订单号用于关联

### 入库申请单
- 追踪直发客户订单
- 支持超时提醒
- 可标记到货状态

### 调拨管理
- 借出：仓库货物借给销售
- 还货：销售归还货物
- 直接出库：直接销售出库
- 支持销售标签（记录客户/用途）

### 库存查询
- 按商品名称/条码查询
- 显示各仓库库存分布

## 后续扩展

如需添加更多功能，可扩展：

- [ ] 报损管理模块
- [ ] 账务调拨记录（欠数据追踪）
- [ ] 审批流程优化
- [ ] 数据报表
- [ ] 移动端APP（UniApp）

## 注意事项

1. 本系统数据存储在本地SQLite文件 `erp.db`
2. 定期备份数据库文件防止数据丢失
3. 如需外网访问，使用内网穿透工具（如ngrok）
