@echo off
REM 云行业HR洞察 - 定时更新脚本
REM 每天自动运行此脚本，更新今日观察和报告时间
REM 每周日晚20:00运行时，还会生成本周观察（上周的周报）

cd /d "c:\Users\赵梓菡\WorkBuddy\Claw\netlify-deploy"

echo [%date% %time%] 开始自动更新...

REM 运行自动更新HTML脚本 v3（正确版）
python auto_update_v3.py

echo [%date% %time%] 自动更新完成

pause
