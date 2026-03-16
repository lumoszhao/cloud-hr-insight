#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云行业HR洞察 - 智能自动更新脚本 v3（正确版）

功能：
1. 每天运行：更新"今日观察"（只保留当天的新闻）
2. 每周日晚20:00运行：更新"本周观察"（生成上周的周报）
3. 更新报告生成时间
4. 自动提交到 GitHub，触发 Netlify 自动部署
"""

import os
import logging
import subprocess
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update_v3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 文件路径
HTML_FILE = 'index.html'
DAILY_NEWS_FILE = 'daily_news.json'
WEEKLY_NEWS_FILE = 'weekly_news.json'

# Git 路径
GIT_PATH = r'C:\Program Files\Git\bin\git.exe'

def is_sunday_20pm():
    """
    判断当前时间是否是周日晚上20:00
    允许前后1小时的误差（19:00-21:00）
    """
    now = datetime.now()
    
    # 检查是否是周日（weekday=6）
    if now.weekday() != 6:
        return False
    
    # 检查时间是否在 19:00-21:00 之间
    current_hour = now.hour
    if 19 <= current_hour <= 21:
        return True
    
    return False

def get_week_range():
    """
    获取上周的时间范围（周一到周日）
    例如：今天是周一，返回上周（周一到周日）
    """
    today = datetime.now()
    
    # 获取本周一的日期
    this_monday = today - timedelta(days=today.weekday())
    
    # 上周一是本周一减7天
    last_monday = this_monday - timedelta(days=7)
    
    # 上周日是上周一加6天
    last_sunday = last_monday + timedelta(days=6)
    
    return last_monday, last_sunday

def parse_date(date_str):
    """
    解析新闻时间，返回 datetime 对象
    
    支持格式：
    - "今日 10:00" → 今天
    - "昨日" → 昨天
    - "2026-03-10" → 具体日期
    - "2026年3月10日" → 具体日期
    - "3月10日" → 当年的该日期
    - "3月10日 10:00" → 当年的该日期
    """
    today = datetime.now()
    
    date_str = date_str.strip()
    
    # 处理 "今日 10:00"
    if date_str.startswith('今日'):
        return today
    
    # 处理 "昨日"
    if date_str == '昨日':
        return today - timedelta(days=1)
    
    # 处理 "前日"
    if date_str == '前日':
        return today - timedelta(days=2)
    
    # 处理 "2026-03-10" 格式
    try:
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts) >= 3:
                return datetime(int(parts[0]), int(parts[1]), int(parts[2]))
    except:
        pass
    
    # 处理 "2026年3月10日" 格式
    try:
        if '年' in date_str and '月' in date_str:
            import re
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match:
                return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except:
        pass
    
    # 处理 "3月10日" 或 "3月10日 10:00" 格式
    try:
        import re
        match = re.search(r'(\d{1,2})月(\d{1,2})日', date_str)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            # 使用当年
            year = today.year
            return datetime(year, month, day)
    except:
        pass
    
    # 如果都解析不了，返回 None
    return None

def extract_news_from_html(soup, section_id):
    """
    从 HTML 中提取指定 section 的新闻
    """
    section = soup.find('div', {'id': section_id})
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
                # 从 "📅 发布时间: 今日 10:00" 中提取 "今日 10:00"
                import re
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
            
            news_list.append({
                'title': title,
                'date': date_str,
                'tags': tags,
                'summary': summary,
                'priority': priority,
                'date_parsed': parse_date(date_str)
            })
        except Exception as e:
            logging.warning(f"提取新闻失败: {e}")
            continue
    
    return news_list

def update_today_view(soup):
    """
    更新今日观察：只保留当天的新闻
    """
    logging.info("📅 开始更新今日观察...")
    
    today_news = extract_news_from_html(soup, 'daily-view')
    
    # 筛选今天的新闻
    today = datetime.now()
    filtered_news = []
    for news in today_news:
        if news['date_parsed'] and news['date_parsed'].date() == today.date():
            # 移除 date_parsed 字段（datetime 对象不能序列化到 JSON）
            news_copy = news.copy()
            del news_copy['date_parsed']
            filtered_news.append(news_copy)
    
    logging.info(f"  今日观察原新闻数: {len(today_news)}")
    logging.info(f"  筛选后保留: {len(filtered_news)}")
    
    # 删除不在今天的新闻
    section = soup.find('div', {'id': 'daily-view'})
    if section:
        news_grid = section.find('div', class_='news-grid')
        if news_grid:
            cards = news_grid.find_all('div', class_='news-card')
            for card in cards:
                try:
                    meta = card.find('div', class_='meta')
                    if meta:
                        meta_text = meta.get_text(strip=True)
                        import re
                        match = re.search(r'发布时间:\s*(.+?)(?:\s*\||$)', meta_text)
                        if match:
                            date_str = match.group(1).strip()
                            date_parsed = parse_date(date_str)
                            if date_parsed and date_parsed.date() != today.date():
                                title_elem = card.find('h3')
                                title = title_elem.get_text(strip=True) if title_elem else "（无标题）"
                                card.decompose()
                                logging.info(f"  ✓ 删除非今日新闻: {title} ({date_str})")
                except Exception as e:
                    logging.warning(f"删除新闻失败: {e}")
    
    return filtered_news

def update_weekly_view(soup):
    """
    更新本周观察：生成上周的周报
    
    只在周日20:00运行时才更新
    """
    if not is_sunday_20pm():
        logging.info("⏰ 当前不是周日20:00，跳过本周观察更新")
        return []
    
    logging.info("📅 开始更新本周观察（生成上周周报）...")
    
    # 获取上周的时间范围
    last_monday, last_sunday = get_week_range()
    logging.info(f"  上周范围: {last_monday.strftime('%Y-%m-%d')} ~ {last_sunday.strftime('%Y-%m-%d')}")
    
    # 从今日观察中提取上周的新闻（需要从历史数据或其他地方获取）
    # 由于当前 HTML 只保留今日新闻，我们需要从 git 历史或其他地方获取
    # 这里暂时使用示例数据
    
    # TODO: 实现从 git 历史或其他数据源获取上周的新闻
    weekly_news = []
    
    logging.info(f"  本周观察更新完成，共 {len(weekly_news)} 条新闻")
    
    return weekly_news

def update_report_time(soup):
    """
    更新报告生成时间和下次更新时间
    """
    today = datetime.now()
    report_date = today.strftime('%Y-%m-%d')
    report_time = today.strftime('%H:%M')
    
    # 计算下次更新时间（下周一）
    next_monday = today + timedelta(days=(7 - today.weekday()))
    next_update = next_monday.strftime('%Y-%m-%d') + " 24:00"
    
    # 更新 HTML 中的时间
    # 查找报告时间元素并更新
    time_elements = soup.find_all(text=lambda text: text and '本次报告生成时间' in str(text))
    for elem in time_elements:
        new_text = f"本次报告生成时间: {report_date} {report_time} | 下次更新: {next_update}"
        elem.replace_with(new_text)
        logging.info(f"  ✓ 更新报告时间: {report_date} {report_time}")
    
    return report_date, next_update

def save_json(data, filename):
    """
    保存数据到 JSON 文件
    """
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"  ✓ 保存到 {filename}")

def git_commit_and_push(message):
    """
    提交并推送代码
    """
    try:
        subprocess.run([GIT_PATH, 'add', '.'], check=True)
        subprocess.run([GIT_PATH, 'commit', '-m', message], check=True)
        subprocess.run([GIT_PATH, 'push'], check=True)
        logging.info("✅ Git 推送成功")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git 操作失败: {e}")
        return False

def main():
    """
    主函数
    """
    logging.info("="*60)
    logging.info("🚀 云行业HR洞察 - 智能自动更新 v3 开始运行")
    logging.info("="*60)
    
    # 读取 HTML 文件
    if not os.path.exists(HTML_FILE):
        logging.error(f"❌ 找不到文件: {HTML_FILE}")
        return
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 更新今日观察（每天运行）
    daily_news = update_today_view(soup)
    save_json(daily_news, DAILY_NEWS_FILE)
    
    # 2. 更新本周观察（只在周日20:00运行）
    weekly_news = update_weekly_view(soup)
    save_json(weekly_news, WEEKLY_NEWS_FILE)
    
    # 3. 更新报告时间
    report_date, next_update = update_report_time(soup)
    
    # 4. 保存更新后的 HTML
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    logging.info("✅ HTML 文件已更新")
    
    # 5. 提交到 GitHub
    commit_message = f"自动更新: {report_date}"
    git_commit_and_push(commit_message)
    
    logging.info("="*60)
    logging.info("✅ 自动更新完成！")
    logging.info("="*60)

if __name__ == '__main__':
    main()
