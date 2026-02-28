@echo off
chcp 65001 >nul
echo ========================================
echo   启动前端服务
echo ========================================
echo.

cd /d "%~dp0frontend"

echo 正在检查 Node.js...
node --version
if errorlevel 1 (
    echo [错误] 未安装 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
call npm install

echo.
echo 启动前端服务...
echo 地址: http://localhost:3000
echo.
call npm start

pause
