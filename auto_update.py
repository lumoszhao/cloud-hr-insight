#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云行业HR洞察 - 自动更新脚本
功能：自动抓取云行业新闻，筛选时间范围，生成HTML报告，自动部署
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import subprocess
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 新闻源配置
# 注意：这些是示例URL，实际需要根据真实新闻源调整
NEWS_SOURCES = [
    {
        'name': '示例新闻源1',
        'url': 'https://example.com/news',
        'selector': '.news-item',
        'title_selector': '.title',
        'date_selector': '.date',
        'link_selector': 'a'
    }
    # 实际使用时，需要替换为真实的云厂商新闻源URL和选择器
]

# 时间范围配置
def get_this_week_range():
    """获取本周时间范围（周一到周日）"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def is_within_this_week(date_str):
    """判断日期是否在本周范围内"""
    try:
        news_date = datetime.strptime(date_str, '%Y-%m-%d')
        monday, sunday = get_this_week_range()
        return monday <= news_date <= sunday
    except:
        return False

def is_today(date_str):
    """判断日期是否是今天"""
    try:
        news_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().date()
        return news_date.date() == today
    except:
        return False

# 抓取新闻
def fetch_news(url, selector, title_selector, date_selector, link_selector):
    """抓取单个新闻源"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = []
        items = soup.select(selector)

        for item in items:
            try:
                title_elem = item.select_one(title_selector)
                date_elem = item.select_one(date_selector)
                link_elem = item.select_one(link_selector)

                if not title_elem or not date_elem:
                    continue

                title = title_elem.get_text(strip=True)
                date_str = date_elem.get_text(strip=True)
                link = link_elem.get('href', '') if link_elem else ''

                # 标准化日期格式
                try:
                    if '年' in date_str:
                        date_str = datetime.strptime(date_str, '%Y年%m月%d日').strftime('%Y-%m-%d')
                    elif '-' in date_str:
                        date_str = date_str.split(' ')[0]  # 去掉时间部分
                except:
                    continue

                news_items.append({
                    'title': title,
                    'date': date_str,
                    'link': link,
                    'source': url
                })
            except Exception as e:
                logging.warning(f"解析新闻项失败: {e}")
                continue

        return news_items
    except Exception as e:
        logging.error(f"抓取 {url} 失败: {e}")
        return []

# 筛选新闻
def filter_news_by_time(news_list, time_range='week'):
    """根据时间范围筛选新闻"""
    filtered = []
    for news in news_list:
        if time_range == 'week':
            if is_within_this_week(news['date']):
                filtered.append(news)
        elif time_range == 'today':
            if is_today(news['date']):
                filtered.append(news)
    return filtered

# 生成HTML
def generate_html_report(daily_news, weekly_news):
    """生成HTML报告"""
    template_path = 'index.html.template'
    output_path = 'index.html'

    # 读取模板（如果有）
    # 这里简化处理，直接使用现有的 index.html 作为基础

    logging.info(f"今日新闻: {len(daily_news)} 条")
    logging.info(f"本周新闻: {len(weekly_news)} 条")

    # 保存新闻数据
    with open('daily_news.json', 'w', encoding='utf-8') as f:
        json.dump(daily_news, f, ensure_ascii=False, indent=2)

    with open('weekly_news.json', 'w', encoding='utf-8') as f:
        json.dump(weekly_news, f, ensure_ascii=False, indent=2)

    return output_path

# Git 操作
def git_commit_and_push(message):
    """提交并推送代码"""
    try:
        # 使用 git 的完整路径，避免找不到命令
        git_path = r'C:\Program Files\Git\bin\git.exe'

        subprocess.run([git_path, 'add', '.'], check=True)
        subprocess.run([git_path, 'commit', '-m', message], check=True)
        subprocess.run([git_path, 'push'], check=True)
        logging.info("Git 推送成功")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Git 操作失败: {e}")
        return False

# 主函数
def main():
    logging.info("=" * 50)
    logging.info("云行业HR洞察 - 自动更新脚本启动")
    logging.info("=" * 50)

    # 获取本周时间范围
    monday, sunday = get_this_week_range()
    logging.info(f"本周时间范围: {monday.strftime('%Y-%m-%d')} 至 {sunday.strftime('%Y-%m-%d')}")

    # 抓取所有新闻源
    all_news = []
    for source in NEWS_SOURCES:
        logging.info(f"正在抓取: {source['name']}...")
        news = fetch_news(
            source['url'],
            source['selector'],
            source['title_selector'],
            source['date_selector'],
            source['link_selector']
        )
        logging.info(f"  -> 抓取到 {len(news)} 条新闻")
        all_news.extend(news)

    # 筛选今日新闻和本周新闻
    daily_news = filter_news_by_time(all_news, 'today')
    weekly_news = filter_news_by_time(all_news, 'week')

    # 生成报告
    report_file = generate_html_report(daily_news, weekly_news)

    # 推送到 GitHub
    commit_message = f"自动更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if git_commit_and_push(commit_message):
        logging.info("✅ 自动更新完成！")
    else:
        logging.error("❌ 自动更新失败")

    logging.info("=" * 50)

if __name__ == '__main__':
    main()
