#!/bin/bash
# ERP系统 - 服务器端更新脚本
# 将此脚本上传到服务器，每次 git push 后执行

PROJECT_DIR="/www/wwwroot/erp-system"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "========================================"
echo "  开始更新 ERP 系统..."
echo "========================================"
echo ""

# 1. 拉取最新代码
echo "[1/4] 拉取最新代码..."
cd $PROJECT_DIR
git pull
echo ""

# 2. 安装后端依赖（如果有更新）
echo "[2/4] 更新后端依赖..."
cd $BACKEND_DIR
source venv/bin/activate
pip install -r requirements.txt -q
echo ""

# 3. 编译前端
echo "[3/4] 编译前端..."
cd $FRONTEND_DIR
npm install --silent
npm run build
echo ""

# 4. 重启后端服务
echo "[4/4] 重启服务..."
# 查找并杀掉旧进程
PID=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    kill -9 $PID
    echo "已停止旧进程: $PID"
fi

# 启动新服务
cd $BACKEND_DIR
nohup venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 >/dev/null 2>&1 &
echo "服务已重启"

echo ""
echo "========================================"
echo "  更新完成！"
echo "========================================"
