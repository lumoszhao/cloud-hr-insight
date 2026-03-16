#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Git 历史中提取上周（3.9-3.15）的新闻
"""

import subprocess
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Git 路径
GIT_PATH = r'C:\Program Files\Git\bin\git.exe'

# 上周日期范围
WEEK_START = datetime(2026, 3, 9)   # 周一
WEEK_END = datetime(2026, 3, 15)     # 周日

def extract_news_from_commit(commit_hash):
    """
    从指定提交中提取今日观察的新闻
    """
    try:
        result = subprocess.run(
            [GIT_PATH, 'show', f'{commit_hash}:index.html'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        html_content = result.stdout
    except:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取今日观察的新闻
    section = soup.find('div', {'id': 'daily-view'})
    if not section:
        return []
    
    news_cards = section.find_all('div', class_='news-card')
    news_list = []
    
    for card in news_cards:
        try:
            # 提取标题
            h3 = card.find('h3')
            title = h3.get_text(strip=True) if h3 else ""
            
            # 提取发布时间
            meta = card.find('div', class_='meta')
            date_str = ""
            if meta:
                meta_text = meta.get_text(strip=True)
                match = re.search(r'发布时间:\s*(.+?)(?:\s*\||$)', meta_text)
                if match:
                    date_str = match.group(1).strip()
            
            # 提取标签
            tags_div = card.find('div', class_='tags')
            tags = []
            if tags_div:
                tag_elements = tags_div.find_all('span', class_='tag')
                tags = [tag.get_text(strip=True) for tag in tag_elements]
            
            # 提取摘要
            summary_p = card.find('p', class_='summary')
            summary = summary_p.get_text(strip=True) if summary_p else ""
            
            # 提取优先级
            priority_badge = card.find('span', class_='priority-badge')
            priority = "中"
            if priority_badge:
                if 'high' in priority_badge.get('class', []):
                    priority = "高"
                elif 'medium' in priority_badge.get('class', []):
                    priority = "中"
                elif 'low' in priority_badge.get('class', []):
                    priority = "低"
            
            # 提取招聘视角内容
            expand_content = card.find('div', class_='expand-content')
            hr_impact = ""
            key_data = ""
            if expand_content:
                hr_div = expand_content.find('div', class_='hr-impact')
                if hr_div:
                    hr_impact = hr_div.get_text(strip=True)
                data_div = expand_content.find('div', class_='key-data')
                if data_div:
                    key_data = data_div.get_text(strip=True)
            
            news_list.append({
                'title': title,
                'date': date_str,
                'tags': tags,
                'summary': summary,
                'priority': priority,
                'hr_impact': hr_impact,
                'key_data': key_data,
                'commit': commit_hash
            })
        except Exception as e:
            print(f"提取新闻失败: {e}")
            continue
    
    return news_list

def get_commits_in_date_range(start_date, end_date):
    """
    获取指定日期范围内的提交
    """
    try:
        # 获取指定日期范围内的提交
        result = subprocess.run(
            [GIT_PATH, 'log', '--after', start_date.strftime('%Y-%m-%d'),
             '--before', end_date.strftime('%Y-%m-%d'),
             '--pretty=format:%H|%cd',
             '--date=short'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 2:
                    commits.append({
                        'hash': parts[0],
                        'date': parts[1]
                    })
        
        return commits
    except:
        return []

def main():
    """
    主函数
    """
    print("="*60)
    print(f"提取上周（{WEEK_START.strftime('%Y-%m-%d')} ~ {WEEK_END.strftime('%Y-%m-%d')}）的新闻")
    print("="*60)
    
    # 获取指定日期范围内的提交
    print("\n正在获取 Git 提交历史...")
    commits = get_commits_in_date_range(WEEK_START, WEEK_END)
    
    if not commits:
        print("没有找到该日期范围内的提交")
        print("\n尝试获取所有提交...")
        result = subprocess.run(
            [GIT_PATH, 'log', '--pretty=format:%H|%cd', '--date=short', '-20'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 2:
                    commits.append({
                        'hash': parts[0],
                        'date': parts[1]
                    })
        
        print(f"找到 {len(commits)} 个提交:")
        for commit in commits:
            print(f"  - {commit['date']}: {commit['hash']}")
    
    # 从每个提交中提取新闻
    all_news = []
    for commit in commits:
        print(f"\n处理提交: {commit['date']} - {commit['hash']}")
        news = extract_news_from_commit(commit['hash'])
        print(f"  提取到 {len(news)} 条新闻")
        all_news.extend(news)
    
    # 输出结果
    print("\n" + "="*60)
    print(f"总共提取到 {len(all_news)} 条新闻")
    print("="*60)
    
    for i, news in enumerate(all_news, 1):
        print(f"\n【{i}】{news['title']}")
        print(f"  日期: {news['date']}")
        print(f"  优先级: {news['priority']}")
        print(f"  标签: {', '.join(news['tags'])}")
        print(f"  摘要: {news['summary'][:100]}...")
    
    # 保存到 JSON
    import json
    with open('weekly_news_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n新闻已保存到 weekly_news_extracted.json")

if __name__ == '__main__':
    main()
