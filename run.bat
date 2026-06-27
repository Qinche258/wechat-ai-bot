@echo off
echo 正在启动微信AI陪伴机器人...
echo.

REM 安装依赖
pip install -r requirements.txt

REM 启动服务
python main.py

pause
