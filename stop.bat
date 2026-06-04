@echo off
chcp 65001 >nul
echo ====================================================
echo 霍格沃茨 MIS 系统停止脚本
echo ====================================================
echo.
echo 正在查找并停止Flask进程...
echo.

REM 查找Python进程
for /f "tokens=2" %%i in ('tasklist ^| findstr "python.exe"') do (
    echo 找到进程 PID: %%i
    taskkill /PID %%i /F >nul 2>&1
)

echo.
echo ====================================================
echo 后端服务器已停止
echo ====================================================
pause