import subprocess

git_path = r'C:\Program Files\Git\bin\git.exe'
subprocess.run([git_path, 'add', '.'], check=True)
subprocess.run([git_path, 'commit', '-m', '修复自动更新HTML脚本，成功删除本周观察中的旧新闻'], check=True)
subprocess.run([git_path, 'push'], check=True)
print("✅ Git 推送成功")
