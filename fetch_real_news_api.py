#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 NewsAPI 获取真实的云行业新闻
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import codecs

# 修复 Windows 编码问题
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# NewsAPI 配置
NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # 请替换为您的 NewsAPI Key
NEWS_API_URL = "https://newsapi.org/v2/everything"

def fetch_news_from_api():
    """
    从 NewsAPI 获取云行业相关的真实新闻
    """
    print("=" * 60)
    print("云行业HR洞察 - NewsAPI 真实新闻抓取工具")
    print("=" * 60)
    print()

    # 搜索关键词
    keywords = [
        "云招聘 云计算招聘",
        "阿里云 腾讯云 华为云 招聘",
        "火山引擎 AWS 招聘",
        "云计算 人才招聘"
    ]

    # 时间范围（过去 7 天）
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")

    all_news = []

    for keyword in keywords:
        print(f"正在搜索关键词: {keyword}")

        params = {
            "q": keyword,
            "from": from_date,
            "to": to_date,
            "language": "zh",
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
            "pageSize": 10
        }

        try:
            response = requests.get(NEWS_API_URL, params=params)
            data = response.json()

            if data.get("status") == "ok":
                articles = data.get("articles", [])
                print(f"  找到 {len(articles)} 条新闻")

                for article in articles:
                    # 提取云厂商名称
                    title = article.get("title", "")
                    description = article.get("description", "")
                    url = article.get("url", "")
                    published_at = article.get("publishedAt", "")

                    # 过滤重复新闻
                    if not any(news["link"] == url for news in all_news):
                        company = extract_company_name(title, description)
                        if company:
                            news_item = {
                                "company": company,
                                "title": title,
                                "summary": description or title,
                                "link": url,
                                "timestamp": published_at.replace("T", " ").replace("Z", ""),
                                "priority": determine_priority(title, description),
                                "tags": extract_tags(title, description)
                            }
                            all_news.append(news_item)

            else:
                print(f"  API 错误: {data.get('message', '未知错误')}")

        except Exception as e:
            print(f"  请求失败: {str(e)}")

        # 避免请求过快
        import time
        time.sleep(1)

    # 按时间排序
    all_news.sort(key=lambda x: x["timestamp"], reverse=True)

    # 保存数据
    save_news_to_json(all_news)

def extract_company_name(title, description):
    """
    从标题和描述中提取云厂商名称
    """
    text = (title + " " + description).lower()

    companies = {
        "腾讯云": ["腾讯云", "腾讯"],
        "阿里云": ["阿里云", "阿里巴巴"],
        "华为云": ["华为云", "华为"],
        "火山引擎": ["火山引擎", "字节"],
        "AWS": ["aws", "亚马逊云"],
        "Azure": ["azure", "微软云"],
        "百度云": ["百度云", "百度"],
        "金山云": ["金山云"]
    }

    for company, keywords in companies.items():
        for keyword in keywords:
            if keyword in text:
                return company

    return "云行业"

def determine_priority(title, description):
    """
    根据关键词确定新闻优先级
    """
    text = (title + " " + description).lower()

    high_priority_keywords = ["招聘", "扩招", "校招", "人才", "岗位"]
    medium_priority_keywords = ["业务", "技术", "产品", "服务"]

    for keyword in high_priority_keywords:
        if keyword in text:
            return "高"

    for keyword in medium_priority_keywords:
        if keyword in text:
            return "中"

    return "低"

def extract_tags(title, description):
    """
    从标题和描述中提取标签
    """
    text = title + " " + description
    tags = []

    tag_keywords = [
        "招聘", "扩招", "校招", "实习生", "人才",
        "云计算", "AI", "人工智能", "大数据", "数据库",
        "架构师", "工程师", "销售", "产品",
        "腾讯云", "阿里云", "华为云", "火山引擎", "AWS", "Azure"
    ]

    for keyword in tag_keywords:
        if keyword in text:
            tags.append(keyword)

    return list(set(tags))[:5]  # 最多返回 5 个标签

def save_news_to_json(news_list):
    """
    保存新闻到 JSON 文件
    """
    today = datetime.now().strftime("%Y-%m-%d")

    data = {
        "date": today,
        "news": news_list[:20],  # 最多保存 20 条新闻
        "source": "NewsAPI",
        "note": "真实新闻数据，来源于 NewsAPI"
    }

    with open('daily_news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print(f"✅ 成功获取 {len(news_list)} 条真实新闻")
    print(f"✅ 数据已保存到 daily_news.json")
    print()
    print("=" * 60)
    print("抓取完成！")
    print("=" * 60)

    # 显示新闻预览
    if news_list:
        print("\n📰 新闻预览：")
        for i, news in enumerate(news_list[:5], 1):
            print(f"\n{i}. {news['company']} - {news['title']}")
            print(f"   链接: {news['link']}")

if __name__ == "__main__":
    # 检查 API Key
    if NEWS_API_KEY == "YOUR_NEWS_API_KEY":
        print("⚠️  请先设置 NEWS_API_KEY！")
        print("📝 获取免费 API Key: https://newsapi.org/")
        print()
        print("💡 在这个文件中，将 NEWS_API_KEY 替换为您的真实 API Key")
    else:
        fetch_news_from_api()
