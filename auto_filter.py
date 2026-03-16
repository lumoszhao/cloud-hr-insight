#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云行业HR洞察 - 自动筛选新闻脚本
功能：从 index.html 提取新闻，根据时间自动筛选今日/本周新闻
"""

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import logging
import subprocess
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_filter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 文件路径
HTML_FILE = 'index.html'
DAILY_JSON = 'daily_news.json'
WEEKLY_JSON = 'weekly_news.json'

# 时间范围配置
def get_today_date():
    """获取今天的日期"""
    return datetime.now().date()

def get_this_week_range():
    """获取本周时间范围（周一到周日）"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.date(), sunday.date()

def parse_news_date(date_str, today_date):
    """解析新闻日期字符串，返回 datetime.date 对象"""
    try:
        # 情况1: "今日 10:00" → 今天
        if '今日' in date_str:
            return today_date

        # 情况2: "昨日" → 昨天
        if '昨日' in date_str:
            return today_date - timedelta(days=1)

        # 情况3: "2026-03-10"
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            date_part = date_str.split(' ')[0]  # 去掉时间部分
            return datetime.strptime(date_part, '%Y-%m-%d').date()

        # 情况4: "2026年3月10日"
        if '年' in date_str and '月' in date_str and '日' in date_str:
            date_clean = re.sub(r'[^\d-]', '-', date_str)  # 统一格式
            date_clean = re.sub(r'-+', '-', date_clean).strip('-')
            return datetime.strptime(date_clean, '%Y-%m-%d').date()

        # 情况5: "3月10日"（当年）
        if '月' in date_str and '日' in date_str and '年' not in date_str:
            year = today_date.year
            date_str_with_year = f"{year}年{date_str}"
            date_clean = re.sub(r'[^\d-]', '-', date_str_with_year)
            date_clean = re.sub(r'-+', '-', date_clean).strip('-')
            return datetime.strptime(date_clean, '%Y-%m-%d').date()

        logging.warning(f"无法解析日期: {date_str}")
        return None

    except Exception as e:
        logging.warning(f"解析日期失败 '{date_str}': {e}")
        return None

def is_within_this_week(news_date, week_range):
    """判断日期是否在本周范围内"""
    if news_date is None:
        return False
    monday, sunday = week_range
    return monday <= news_date <= sunday

def is_today(news_date, today_date):
    """判断日期是否是今天"""
    if news_date is None:
        return False
    return news_date == today_date

# 提取新闻卡片
def extract_news_cards(soup, view_type='daily'):
    """从 HTML 中提取新闻卡片

    Args:
        soup: BeautifulSoup 对象
        view_type: 'daily' 或 'weekly'

    Returns:
        list: 新闻卡片列表
    """
    news_cards = []

    # 根据视图类型找到对应的 section
    view_id = f"{view_type}-view"
    view_section = soup.find(id=view_id)

    if not view_section:
        logging.error(f"找不到 {view_id} section")
        return news_cards

    # 找到所有新闻卡片
    cards = view_section.find_all(class_='news-card')

    for card in cards:
        try:
            # 提取 tag
            tag_elem = card.find(class_='tag')
            tag = tag_elem.get_text(strip=True) if tag_elem else ''

            # 提取标题
            title_elem = card.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # 提取摘要
            summary_elem = card.find(class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''

            # 提取发布时间
            # 两种格式：
            # 格式1: <div class="meta">📅 发布时间: 今日 10:00 | 📌 信息来源: 腾讯云官网</div>
            # 格式2: <p>📅 2026-03-10 | 📌 腾讯新闻 | 🔗 <a href="#">查看详情</a></p>

            date_str = ''
            source = ''
            link = ''

            # 尝试格式1（meta标签）
            meta_elem = card.find(class_='meta')
            if meta_elem:
                meta_text = meta_elem.get_text(strip=True)
                # 提取日期
                date_match = re.search(r'发布时间:\s*(.+?)\s*\|', meta_text)
                if date_match:
                    date_str = date_match.group(1).strip()
                # 提取来源
                source_match = re.search(r'信息来源:\s*(.+)', meta_text)
                if source_match:
                    source = source_match.group(1).strip()

            # 尝试格式2（source标签）
            if not date_str:
                source_elem = card.find(class_='source')
                if source_elem:
                    source_text = source_elem.get_text(strip=True)
                    # 提取日期
                    date_match = re.search(r'📅\s*(.+?)\s*\|', source_text)
                    if date_match:
                        date_str = date_match.group(1).strip()
                    # 提取来源
                    source_match = re.search(r'📌\s*(.+?)\s*\|', source_text)
                    if source_match:
                        source = source_match.group(1).strip()
                    # 提取链接
                    link_elem = source_elem.find('a')
                    if link_elem:
                        link = link_elem.get('href', '')

            # 提取关键词
            keywords = []
            keywords_elem = card.find(class_='keywords')
            if keywords_elem:
                for kw in keywords_elem.find_all('span'):
                    keywords.append(kw.get_text(strip=True))

            # 提取详细内容
            detail_content = ''
            expand_content = card.find(class_='expand-content') or card.find(class_='detail-content')
            if expand_content:
                detail_content = str(expand_content)

            # 构建新闻数据
            news_data = {
                'tag': tag,
                'title': title,
                'summary': summary,
                'date_str': date_str,
                'date': parse_news_date(date_str, get_today_date()),
                'source': source,
                'link': link,
                'keywords': keywords,
                'detail_content': detail_content,
                'html': str(card)  # 保存原始HTML
            }

            news_cards.append(news_data)
            logging.info(f"  ✓ 提取: {title} ({date_str})")

        except Exception as e:
            logging.warning(f"提取新闻卡片失败: {e}")
            continue

    return news_cards

# 筛选新闻
def filter_news_by_time(news_list, time_range='week'):
    """根据时间范围筛选新闻

    Args:
        news_list: 新闻列表
        time_range: 'today' 或 'week'

    Returns:
        list: 筛选后的新闻列表
    """
    today = get_today_date()
    week_range = get_this_week_range()

    filtered = []

    if time_range == 'today':
        for news in news_list:
            if is_today(news['date'], today):
                filtered.append(news)
                logging.info(f"  ✓ 今日新闻: {news['title']}")

    elif time_range == 'week':
        for news in news_list:
            if is_within_this_week(news['date'], week_range):
                filtered.append(news)
                logging.info(f"  ✓ 本周新闻: {news['title']}")

    return filtered

# 保存新闻数据
def save_news_json(news_list, filename, title):
    """保存新闻数据到 JSON 文件

    Args:
        news_list: 新闻列表
        filename: JSON 文件名
        title: 日志标题
    """
    # 转换 datetime.date 为字符串
    for news in news_list:
        if news['date']:
            news['date'] = news['date'].strftime('%Y-%m-%d')

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

    logging.info(f"{title}: {len(news_list)} 条新闻")
    logging.info(f"✅ 已保存到 {filename}")

# 主函数
def main():
    logging.info("=" * 50)
    logging.info("云行业HR洞察 - 自动筛选新闻脚本")
    logging.info("=" * 50)

    # 获取时间范围
    today = get_today_date()
    monday, sunday = get_this_week_range()

    logging.info(f"📅 今天: {today}")
    logging.info(f"📅 本周: {monday} 至 {sunday}")

    # 检查 HTML 文件是否存在
    if not os.path.exists(HTML_FILE):
        logging.error(f"❌ 找不到文件: {HTML_FILE}")
        return

    # 读取 HTML 文件
    logging.info(f"📖 正在读取 {HTML_FILE}...")
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取所有新闻（今日观察）
    logging.info("\n🔍 提取今日观察新闻...")
    daily_cards = extract_news_cards(soup, 'daily')
    logging.info(f"✓ 共提取 {len(daily_cards)} 条新闻")

    # 提取所有新闻（本周观察）
    logging.info("\n🔍 提取本周观察新闻...")
    weekly_cards = extract_news_cards(soup, 'weekly')
    logging.info(f"✓ 共提取 {len(weekly_cards)} 条新闻")

    # 筛选今日新闻
    logging.info("\n⏰ 筛选今日新闻...")
    today_news = filter_news_by_time(daily_cards, 'today')
    save_news_json(today_news, DAILY_JSON, "今日新闻")

    # 筛选本周新闻
    logging.info("\n⏰ 筛选本周新闻...")
    week_news = filter_news_by_time(weekly_cards, 'week')
    save_news_json(week_news, WEEKLY_JSON, "本周新闻")

    # 显示统计信息
    logging.info("\n📊 统计信息:")
    logging.info(f"  - 今日观察总数: {len(daily_cards)} 条")
    logging.info(f"  - 今日新闻（今日）: {len(today_news)} 条")
    logging.info(f"  - 本周观察总数: {len(weekly_cards)} 条")
    logging.info(f"  - 本周新闻（本周）: {len(week_news)} 条")

    # 推送到 GitHub
    logging.info("\n📤 推送到 GitHub...")
    try:
        git_path = r'C:\Program Files\Git\bin\git.exe'
        subprocess.run([git_path, 'add', '.'], check=True)
        subprocess.run([git_path, 'commit', '-m', f'自动筛选: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'], check=True)
        subprocess.run([git_path, 'push'], check=True)
        logging.info("✅ Git 推送成功")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git 推送失败: {e}")

    logging.info("\n" + "=" * 50)
    logging.info("✅ 自动筛选完成！")
    logging.info("=" * 50)

if __name__ == '__main__':
    main()
