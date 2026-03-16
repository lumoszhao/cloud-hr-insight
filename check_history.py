import subprocess

# 查看 Git 提交历史
result = subprocess.run(
    ['C:\\Program Files\\Git\\bin\\git.exe', 'log', '--oneline', '-10'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore'
)
print(result.stdout)

# 查看最后一次提交的 diff
result2 = subprocess.run(
    ['C:\\Program Files\\Git\\bin\\git.exe', 'diff', 'HEAD~1', 'HEAD', '--', 'index.html'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore'
)
print("\n=== 上次提交的修改 ===")
print(result2.stdout[:2000])  # 只显示前2000字符
