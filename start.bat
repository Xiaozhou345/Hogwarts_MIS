@echo off
chcp 65001 >nul
echo ====================================================
echo 霍格沃茨 MIS 系统启动脚本
echo ====================================================
echo.
echo 正在启动后端服务器...
echo.
cd /d "%~dp0py"
python app.py
if %errorlevel% neq 0 (
    echo.
    echo ====================================================
    echo 启动失败！可能的原因：
    echo 1. Python未安装或未添加到PATH
    echo 2. 缺少依赖包（请运行: pip install flask flask-cors mysql-connector-python python-dotenv）
    echo 3. 数据库未启动
    echo ====================================================
    pause
)