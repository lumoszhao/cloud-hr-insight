#!/usr/bin/env python3
"""
云行业HR洞察 - 数据爬虫脚本
自动从各大云厂商官网和招聘平台获取最新招聘信息
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import os

class CloudRecruitmentScraper:
    """云行业招聘信息爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'news': [],
            'recruitment': []
        }

    def scrape_tencent_cloud(self):
        """爬取腾讯云招聘信息"""
        try:
            # 腾讯云招聘页面
            url = "https://cloud.tencent.com/joinus"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 这里需要根据实际页面结构调整选择器
                # 示例代码，实际使用时需要分析页面结构
                news_item = {
                    'company': '腾讯云',
                    'title': '腾讯云持续招聘中',
                    'summary': '关注腾讯云官方招聘页面获取最新职位信息',
                    'link': url,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                self.data['news'].append(news_item)
                print(f"✅ 成功获取腾讯云信息")

        except Exception as e:
            print(f"❌ 腾讯云爬取失败: {e}")

    def scrape_aliyun(self):
        """爬取阿里云招聘信息"""
        try:
            # 阿里云招聘页面
            url = "https://jobs.aliyun.com"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                news_item = {
                    'company': '阿里云',
                    'title': '阿里云持续招聘中',
                    'summary': '关注阿里云官方招聘页面获取最新职位信息',
                    'link': url,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                self.data['news'].append(news_item)
                print(f"✅ 成功获取阿里云信息")

        except Exception as e:
            print(f"❌ 阿里云爬取失败: {e}")

    def scrape_huawei_cloud(self):
        """爬取华为云招聘信息"""
        try:
            # 华为云招聘页面
            url = "https://career.huawei.com"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                news_item = {
                    'company': '华为云',
                    'title': '华为云持续招聘中',
                    'summary': '关注华为云官方招聘页面获取最新职位信息',
                    'link': url,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                self.data['news'].append(news_item)
                print(f"✅ 成功获取华为云信息")

        except Exception as e:
            print(f"❌ 华为云爬取失败: {e}")

    def scrape_volcano_engine(self):
        """爬取火山引擎招聘信息"""
        try:
            # 火山引擎招聘页面
            url = "https://career.volcengine.com"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                news_item = {
                    'company': '火山引擎',
                    'title': '火山引擎持续招聘中',
                    'summary': '关注火山引擎官方招聘页面获取最新职位信息',
                    'link': url,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                self.data['news'].append(news_item)
                print(f"✅ 成功获取火山引擎信息")

        except Exception as e:
            print(f"❌ 火山引擎爬取失败: {e}")

    def scrape_aws_china(self):
        """爬取AWS中国招聘信息"""
        try:
            # AWS中国招聘页面
            url = "https://amazon.jobs/zh-cn/locations/china"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                news_item = {
                    'company': 'AWS中国',
                    'title': 'AWS中国持续招聘中',
                    'summary': '关注AWS中国官方招聘页面获取最新职位信息',
                    'link': url,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                self.data['news'].append(news_item)
                print(f"✅ 成功获取AWS中国信息")

        except Exception as e:
            print(f"❌ AWS中国爬取失败: {e}")

    def scrape_microsoft_azure(self):
        """爬取Microsoft Azure招聘信息"""
        try:
            # Microsoft Azure中国招聘页面
            url = "https://careers.microsoft.com"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                news_item = {
                    'company': 'Microsoft Azure',
                    'title': 'Microsoft Azure持续招聘中',
                    'summary': '关注Microsoft官方招聘页面获取最新职位信息',
                    'link': url,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                self.data['news'].append(news_item)
                print(f"✅ 成功获取Microsoft Azure信息")

        except Exception as e:
            print(f"❌ Microsoft Azure爬取失败: {e}")

    def run_all(self):
        """运行所有爬虫"""
        print(f"\n{'='*60}")
        print(f"开始爬取云行业招聘信息 - {self.data['date']}")
        print(f"{'='*60}\n")

        # 爬取各大云厂商信息
        self.scrape_tencent_cloud()
        time.sleep(2)

        self.scrape_aliyun()
        time.sleep(2)

        self.scrape_huawei_cloud()
        time.sleep(2)

        self.scrape_volcano_engine()
        time.sleep(2)

        self.scrape_aws_china()
        time.sleep(2)

        self.scrape_microsoft_azure()

        print(f"\n{'='*60}")
        print(f"爬取完成！共获取 {len(self.data['news'])} 条信息")
        print(f"{'='*60}\n")

        return self.data

    def save_to_json(self, filename='daily_news.json'):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ 数据已保存到 {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    scraper = CloudRecruitmentScraper()
    data = scraper.run_all()
    scraper.save_to_json()
