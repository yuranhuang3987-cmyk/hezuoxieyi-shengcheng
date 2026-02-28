@echo off
chcp 65001 >nul
echo ========================================
echo   启动后端服务
echo ========================================
echo.

cd /d "%~dp0backend"

echo 正在检查 Python...
python --version
if errorlevel 1 (
    echo [错误] 未安装 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 启动后端服务...
echo 地址: http://localhost:5000
echo.
python app.py

pause
