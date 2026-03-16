import subprocess
import re

# 查看初始版本的 HTML 文件（13e23f0）
result = subprocess.run(
    ['C:\\Program Files\\Git\\bin\\git.exe', 'show', '13e23f0:index.html'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore'
)

html_content = result.stdout

# 提取本周观察部分
lines = html_content.split('\n')
in_weekly_section = False
weekly_news = []

for i, line in enumerate(lines):
    if '<!-- Weekly View -->' in line or '本周观察' in line:
        in_weekly_section = True
        print(f"找到本周观察部分，从第 {i+1} 行开始")

    if in_weekly_section:
        weekly_news.append(line)

        # 检查是否到达本周观察的结束位置（比如下一个 section 开始）
        if '<!-- Daily View -->' in line or '<div class="view-section"' in line and len(weekly_news) > 10:
            break

        # 限制行数，避免过多
        if len(weekly_news) > 50:
            break

# 保存到文件
with open('recovered_weekly_news.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(weekly_news))

print(f"\n=== 本周观察部分已保存到 recovered_weekly_news.txt（共 {len(weekly_news)} 行）===")
