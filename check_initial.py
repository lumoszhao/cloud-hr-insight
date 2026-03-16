import subprocess

# 查看初始版本的 HTML 文件
result = subprocess.run(
    ['C:\\Program Files\\Git\\bin\\git.exe', 'show', '13e23f0:index.html'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore'
)

lines = result.stdout.split('\n')
# 保存到文件
with open('initial_html_structure.txt', 'w', encoding='utf-8') as f:
    f.write(f'总行数: {len(lines)}\n\n')
    for i in range(580, min(650, len(lines))):
        f.write(f'{i+1}: {lines[i][:120]}\n')

print(f'已保存到 initial_html_structure.txt')
