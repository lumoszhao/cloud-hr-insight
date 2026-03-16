import subprocess

# 提交所有修改
subprocess.run(['C:\\Program Files\\Git\\bin\\git.exe', 'add', '.'], check=True)
subprocess.run(['C:\\Program Files\\Git\\bin\\git.exe', 'commit', '-m ' + '修复自动更新逻辑: 正确处理本周观察和今日观察的更新时机'.encode('utf-8').decode('utf-8')], check=True)
subprocess.run(['C:\\Program Files\\Git\\bin\\git.exe', 'push'], check=True)

print("✅ 提交成功！")
