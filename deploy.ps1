# ERP系统 - 一键部署脚本
# 用法：右键 -> 使用 PowerShell 运行

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ERP系统 - 一键部署到服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 编译前端
Write-Host "[1/3] 编译前端..." -ForegroundColor Yellow
Set-Location "$ROOT\frontend"
cmd /c "npx vite build 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 编译失败！" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}
Write-Host "[完成] 前端编译成功" -ForegroundColor Green
Write-Host ""

# 2. 提交到 Git
Write-Host "[2/3] 提交代码到 Git..." -ForegroundColor Yellow
Set-Location $ROOT
git add .
git commit -m "auto deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 推送失败，请检查 GitHub 配置！" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}
Write-Host "[完成] 代码已推送到 GitHub" -ForegroundColor Green
Write-Host ""

# 3. 触发服务器更新
Write-Host "[3/3] 通知服务器更新..." -ForegroundColor Yellow
Write-Host "服务器将自动拉取并重启" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "按回车退出"
