#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 HTML 中的重复内容
"""

from bs4 import BeautifulSoup

# 读取 HTML 文件
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 查找本周观察 section
weekly_section = soup.find('div', {'id': 'weekly-view'})
if not weekly_section:
    print("错误：找不到本周观察 section")
    exit(1)

# 查找 header
header = weekly_section.find('header')
if not header:
    print("错误：找不到 header")
    exit(1)

# 找到 header 之后的第一个 div，检查是否是错误的 news-grid
next_sibling = header.find_next_sibling()
if next_sibling and 'news-grid' in next_sibling.get('class', []) if next_sibling else False:
    # 检查 class 属性是否正确
    if 'class_' in str(next_sibling):
        print("删除错误的 news-grid")
        next_sibling.decompose()

# 保存清理后的 HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print("HTML 清理完成！")
