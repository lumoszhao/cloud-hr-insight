@echo off
REM 云行业HR洞察 - 定时更新脚本
REM 每天自动运行此脚本，筛选新闻并自动部署

cd /d "c:\Users\赵梓菡\WorkBuddy\Claw\netlify-deploy"

echo [%date% %time%] 开始自动更新...

REM 运行自动更新HTML脚本
python auto_update_html.py

echo [%date% %time%] 自动更新完成

pause
