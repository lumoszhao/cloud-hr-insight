#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云行业HR洞察 - 自动更新HTML脚本
功能：从 index.html 提取新闻，根据时间筛选，自动更新 HTML，推送到 GitHub
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
        logging.FileHandler('auto_update_html.log', encoding='utf-8'),
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
            date_part = date_str.split(' ')[0]
            return datetime.strptime(date_part, '%Y-%m-%d').date()

        # 情况4: "2026年3月10日"
        if '年' in date_str and '月' in date_str and '日' in date_str:
            date_clean = re.sub(r'[^\d-]', '-', date_str)
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
    """从 HTML 中提取新闻卡片"""
    news_cards = []
    view_id = f"{view_type}-view"
    view_section = soup.find(id=view_id)

    if not view_section:
        logging.error(f"找不到 {view_id} section")
        return news_cards

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
            date_str = ''
            source = ''
            link = ''

            # 尝试格式1（meta标签）
            meta_elem = card.find(class_='meta')
            if meta_elem:
                meta_text = meta_elem.get_text(strip=True)
                date_match = re.search(r'发布时间:\s*(.+?)\s*\|', meta_text)
                if date_match:
                    date_str = date_match.group(1).strip()
                source_match = re.search(r'信息来源:\s*(.+)', meta_text)
                if source_match:
                    source = source_match.group(1).strip()

            # 尝试格式2（source标签）
            if not date_str:
                source_elem = card.find(class_='source')
                if source_elem:
                    source_text = source_elem.get_text(strip=True)
                    date_match = re.search(r'📅\s*(.+?)\s*\|', source_text)
                    if date_match:
                        date_str = date_match.group(1).strip()
                    source_match = re.search(r'📌\s*(.+?)\s*\|', source_text)
                    if source_match:
                        source = source_match.group(1).strip()

            # 提取关键词
            keywords = []
            keywords_elem = card.find(class_='keywords')
            if keywords_elem:
                for kw in keywords_elem.find_all('span'):
                    keywords.append(kw.get_text(strip=True))

            news_data = {
                'tag': tag,
                'title': title,
                'summary': summary,
                'date_str': date_str,
                'date': parse_news_date(date_str, get_today_date()),
                'source': source,
                'link': link,
                'keywords': keywords,
                'html': str(card)  # 保存原始HTML
            }

            news_cards.append(news_data)

        except Exception as e:
            logging.warning(f"提取新闻卡片失败: {e}")
            continue

    return news_cards

# 筛选新闻
def filter_news_by_time(news_list, time_range='week'):
    """根据时间范围筛选新闻"""
    today = get_today_date()
    week_range = get_this_week_range()
    filtered = []

    if time_range == 'today':
        for news in news_list:
            if is_today(news['date'], today):
                filtered.append(news)

    elif time_range == 'week':
        for news in news_list:
            if is_within_this_week(news['date'], week_range):
                filtered.append(news)

    return filtered

# 更新 HTML 中的新闻
def update_html_news(soup, news_list, view_type='daily'):
    """更新 HTML 中的新闻卡片

    Args:
        soup: BeautifulSoup 对象
        news_list: 筛选后的新闻列表
        view_type: 'daily' 或 'weekly'

    Returns:
        bool: 是否有更新
    """
    view_id = f"{view_type}-view"
    view_section = soup.find(id=view_id)

    if not view_section:
        logging.error(f"找不到 {view_id} section")
        return False

    # 找到新闻标题（如"本周重点新闻"）
    section_title = None
    if view_type == 'daily':
        # 今日观察的新闻在 news-grid 中
        news_grid = view_section.find(class_='news-grid')
        if news_grid:
            # 清空所有新闻卡片
            for card in news_grid.find_all(class_='news-card'):
                card.decompose()
            # 插入新的新闻卡片
            for news in news_list:
                news_grid.append(BeautifulSoup(news['html'], 'html.parser'))
    else:
        # 本周观察的新闻在标题之后
        # 找到"本周重点新闻"标题
        section_title = view_section.find(string=lambda text: text and '本周重点新闻' in text)
        if section_title:
            # 找到下一个标题或 section
            next_elem = section_title.parent.find_next_sibling()
            if next_elem and next_elem.name == 'h2':
                # 找到所有新闻卡片
                cards = []
                sibling = next_elem.find_next_sibling()
                while sibling:
                    if sibling.name == 'div' and 'news-card' in sibling.get('class', []):
                        cards.append(sibling)
                        sibling = sibling.find_next_sibling()
                    elif sibling.name == 'h2':
                        break
                    else:
                        sibling = sibling.find_next_sibling()

                # 删除所有新闻卡片
                for card in cards:
                    card.decompose()

                # 插入新的新闻卡片
                if news_list:
                    for i, news in enumerate(news_list):
                        card_soup = BeautifulSoup(news['html'], 'html.parser')
                        section_title.parent.insert_after(card_soup)
        else:
            # 找到所有 news-card 并删除
            for card in view_section.find_all(class_='news-card'):
                card.decompose()
            # 插入新的新闻卡片
            for news in news_list:
                view_section.append(BeautifulSoup(news['html'], 'html.parser'))

    return len(news_list) > 0

# 更新报告生成时间
def update_report_time(soup):
    """更新报告生成时间"""
    today = get_today_date()
    next_week = today + timedelta(days=7)

    # 更新本周观察的生成时间
    weekly_header = soup.find(id='weekly-view').find('header')
    update_time_div = weekly_header.find(class_='update-time')
    if update_time_div:
        new_time = f"本次报告生成时间: {today.strftime('%Y-%m-%d')} | 下次更新: {next_week.strftime('%Y-%m-%d')} 24:00"
        update_time_div.string = new_time
        logging.info(f"✓ 更新报告时间: {new_time}")

    # 更新今日观察的更新时间
    daily_header = soup.find(id='daily-view').find('header')
    update_time_div = daily_header.find(class_='update-time')
    if update_time_div:
        now = datetime.now()
        new_time = f"更新时间: {now.strftime('%Y-%m-%d %H:%M')}"
        update_time_div.string = new_time
        logging.info(f"✓ 更新今日时间: {new_time}")

# 主函数
def main():
    logging.info("=" * 50)
    logging.info("云行业HR洞察 - 自动更新HTML脚本")
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
    logging.info(f"✓ 筛选出 {len(today_news)} 条今日新闻")

    # 筛选本周新闻
    logging.info("\n⏰ 筛选本周新闻...")
    week_news = filter_news_by_time(weekly_cards, 'week')
    logging.info(f"✓ 筛选出 {len(week_news)} 条本周新闻")

    # 更新 HTML 中的新闻
    logging.info("\n📝 更新 HTML 中的新闻...")
    daily_updated = update_html_news(soup, today_news, 'daily')
    weekly_updated = update_html_news(soup, week_news, 'weekly')

    if daily_updated:
        logging.info(f"✓ 今日观察: 已更新 {len(today_news)} 条新闻")
    else:
        logging.info(f"✓ 今日观察: 无需更新（{len(today_news)} 条新闻）")

    if weekly_updated:
        logging.info(f"✓ 本周观察: 已更新 {len(week_news)} 条新闻")
    else:
        logging.info(f"✓ 本周观察: 无需更新（{len(week_news)} 条新闻）")

    # 更新报告时间
    logging.info("\n🕒 更新报告生成时间...")
    update_report_time(soup)

    # 保存更新后的 HTML
    logging.info(f"\n💾 保存更新后的 {HTML_FILE}...")
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    logging.info(f"✓ 已保存")

    # 保存 JSON 数据
    logging.info(f"\n💾 保存 JSON 数据...")

    # 转换 datetime.date 为字符串
    for news in today_news:
        if news['date']:
            news['date'] = news['date'].strftime('%Y-%m-%d')
    for news in week_news:
        if news['date']:
            news['date'] = news['date'].strftime('%Y-%m-%d')

    with open(DAILY_JSON, 'w', encoding='utf-8') as f:
        json.dump(today_news, f, ensure_ascii=False, indent=2)
    logging.info(f"✓ 已保存 {DAILY_JSON} ({len(today_news)} 条)")

    with open(WEEKLY_JSON, 'w', encoding='utf-8') as f:
        json.dump(week_news, f, ensure_ascii=False, indent=2)
    logging.info(f"✓ 已保存 {WEEKLY_JSON} ({len(week_news)} 条)")

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
        subprocess.run([git_path, 'commit', '-m', f'自动更新HTML: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'], check=True)
        subprocess.run([git_path, 'push'], check=True)
        logging.info("✅ Git 推送成功")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git 推送失败: {e}")

    logging.info("\n" + "=" * 50)
    logging.info("✅ 自动更新完成！")
    logging.info("=" * 50)

if __name__ == '__main__':
    main()
