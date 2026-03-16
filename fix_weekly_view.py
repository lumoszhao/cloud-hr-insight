#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全重写本周观察部分，使用正确的结构
"""

from bs4 import BeautifulSoup
import subprocess

# Git 路径
GIT_PATH = r'C:\Program Files\Git\bin\git.exe'

# 上周日期范围
WEEK_START = "2026-03-09"
WEEK_END = "2026-03-15"

# 上周新闻数据
WEEKLY_NEWS = [
    {
        "title": "华为云发布Q1组织架构调整，成立AI算力事业部",
        "date": "2026-03-10",
        "tags": ["组织架构调整", "AI算力", "华为云"],
        "summary": "华为云宣布成立AI算力事业部，强化AI算力业务，从服务提供者转向AI时代算力黑土地和卖水人。",
        "priority": "high",
        "hr_impact": "•招聘需求激增:AI算力事业部新增岗位200+，重点招聘AI算力产品经理、解决方案架构师\n•人才竞争:与阿里云、腾讯云形成三足鼎立，从华为ICT产品线挖人成功率更高\n•薪资竞争力:AI算力相关岗位薪资提升30-40%，核心岗位年薪可达200万+",
        "key_data": "•成立时间:2026年3月10日\n•新增岗位:200+\n•重点岗位:AI算力产品经理(60人)、解决方案架构师(80人)、销售经理(60人)\n•薪资涨幅:30-40%"
    },
    {
        "title": "腾讯云启动大规模校招，目标院校33所",
        "date": "2026-03-12",
        "tags": ["校招", "腾讯云", "目标院校"],
        "summary": "腾讯云启动2026年春季校园招聘，计划访问33所目标高校，重点招聘技术岗和销售岗，转正率超50%。",
        "priority": "medium",
        "hr_impact": "•招聘策略:提前2-3个月布局，目标院校包括985/211院校\n•转正率提升:实习生转正率超50%，高于行业平均水平\n•人才培养:重点培养云计算、AI、大数据方向人才",
        "key_data": "•目标院校:33所\n•招聘岗位:技术岗(60%)、销售岗(40%)\n•转正率:50%+\n•招聘规模:2000+"
    },
    {
        "title": "阿里云华东华南重点招聘，新增岗位800+",
        "date": "2026-03-11",
        "tags": ["社招", "阿里云", "区域招聘"],
        "summary": "阿里云在华东华南地区启动大规模招聘，新增岗位超过800个，重点招聘销售和解决方案架构师。",
        "priority": "medium",
        "hr_impact": "•招聘区域:华东(上海、杭州、南京)、华南(广州、深圳、东莞)\n•岗位需求:销售岗位(400人)、解决方案架构师(250人)、产品经理(150人)\n•薪资水平:销售岗年包40-100万，技术岗年包60-150万",
        "key_data": "•新增岗位:800+\n•招聘重点:华东华南地区\n•核心岗位:销售岗(400人)、解决方案架构师(250人)\n•启动时间:2026年3月11日"
    },
    {
        "title": "火山引擎校招7000+实习生，转正率超50%",
        "date": "2026-03-13",
        "tags": ["校招", "火山引擎", "实习生招聘"],
        "summary": "字节跳动旗下火山引擎启动大规模实习生招聘，计划招聘7000+实习生，转正率超50%。",
        "priority": "medium",
        "hr_impact": "•招聘策略:提前半年布局，目标院校包括985/211院校\n•转正优势:实习生转正率超50%，有转正机会的实习生更具竞争力\n•人才培养:重点培养云计算、AI、大数据方向人才",
        "key_data": "•招聘规模:7000+\n•转正率:50%+\n•启动时间:2026年3月13日\n•目标院校:985/211院校"
    },
    {
        "title": "AWS中国区启动春季社招，重点招聘AI算力人才",
        "date": "2026-03-14",
        "tags": ["社招", "AWS", "AI算力"],
        "summary": "AWS中国区启动春季社会招聘，重点招聘AI算力相关人才，包括解决方案架构师、销售经理等岗位。",
        "priority": "medium",
        "hr_impact": "•招聘重点:AI算力解决方案架构师(50人)、AI算力销售(40人)、产品经理(30人)\n•人才竞争:与华为云、阿里云、腾讯云形成竞争，从国内云厂商挖人成功率较高\n•薪资水平:年包60-200万，核心岗位可达200万+",
        "key_data": "•新增岗位:120+\n•招聘重点:AI算力人才\n•启动时间:2026年3月14日\n•薪资范围:60-200万"
    },
    {
        "title": "Azure中国区发布Q1招聘计划，目标500+岗位",
        "date": "2026-03-15",
        "tags": ["社招", "Azure", "招聘计划"],
        "summary": "微软Azure中国区发布2026年Q1招聘计划，目标招聘500+岗位，重点招聘云架构师和销售。",
        "priority": "medium",
        "hr_impact": "•招聘重点:云解决方案架构师(200人)、云销售(180人)、产品经理(120人)\n•人才策略:从阿里云、华为云、腾讯云挖人，重视AI和云计算背景\n•薪资竞争力:年包50-180万，核心岗位可达180万+",
        "key_data": "•招聘规模:500+\n•重点岗位:架构师(200人)、销售(180人)\n•启动时间:2026年3月15日\n•薪资范围:50-180万"
    },
    {
        "title": "科锐国际发布云计算行业薪酬报告，跳槽涨幅创新高",
        "date": "2026-03-11",
        "tags": ["薪酬报告", "跳槽涨幅", "科锐国际"],
        "summary": "科锐国际发布云计算行业薪酬报告，显示技术岗跳槽涨幅达到20-50%，创历史新高，AI算力相关岗位涨幅最高。",
        "priority": "high",
        "hr_impact": "•招聘时机:3-4月是关键期，提前2-3个月布局\n•薪资策略:技术岗必须提供20-50%涨幅，核心岗位可谈包和期权\n•人才流向:向头部大厂集中，中型云厂商可以挖人",
        "key_data": "•技术岗涨幅:20-50%\n•AI算力岗位涨幅:30-60%\n•销售岗涨幅:15-30%\n•跳槽高峰期:3-4月"
    }
]

def create_news_card(news):
    """创建新闻卡片的 HTML"""
    priority_class = "priority-high" if news['priority'] == "high" else "priority-medium"
    priority_text = "高优先级" if news['priority'] == "high" else "中优先级"

    # 创建标签 HTML，包括日期标签
    all_tags = news['tags'] + [f"📅 {news['date']}"]
    tags_html = "\n                        ".join([f'<span class="tag">{tag}</span>' for tag in all_tags])

    html = f'''                <div class="news-card">
                    <span class="priority-badge {priority_class}">{priority_text}</span>
                    <h3>{news['title']}</h3>
                    <div class="tags">
                        {tags_html}
                    </div>
                    <p class="summary">{news['summary']}</p>
                    <div class="meta">📅 发布时间: {news['date']} | 📌 信息来源: 示例数据</div>
                    <button class="expand-btn" onclick="toggleExpand(this)">📖 展开招聘视角</button>
                    <div class="expand-content">
                        <div class="key-data">
                            <strong>📊 核心数据:</strong><br>
                            {news['key_data'].replace('•', '<br>•')}
                        </div>
                        <div class="hr-impact">
                            <strong>💡 招聘视角:</strong><br>
                            {news['hr_impact'].replace('•', '<br>•')}
                        </div>
                        <div class="info-source">
                            <strong>🔗 原始链接:</strong>
                            <div class="source-links">
                                <a href="#" target="_blank">查看原文</a>
                            </div>
                        </div>
                    </div>
                </div>
'''
    return html

def main():
    # 读取 HTML 文件
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找本周观察 section
    weekly_section = soup.find('div', {'id': 'weekly-view'})
    if not weekly_section:
        print("错误：找不到本周观察 section")
        return

    # 获取信息来源部分（保留）
    info_sources = weekly_section.find('div', class_='info-sources')

    # 清空本周观察的所有内容
    weekly_section.clear()

    # 创建 header
    header = soup.new_tag('header')
    h1 = soup.new_tag('h1')
    h1.string = f"📅 {WEEK_START} ~ {WEEK_END} 周观察记录"
    header.append(h1)

    subtitle = soup.new_tag('div', **{'class': 'subtitle'})
    subtitle.string = "云行业HR每周洞察 - 上周新闻汇总与趋势分析"
    header.append(subtitle)

    update_time = soup.new_tag('div', **{'class': 'update-time'})
    from datetime import datetime
    now = datetime.now()
    update_time.string = f"更新时间: {now.strftime('%Y-%m-%d %H:%M')}"
    header.append(update_time)

    weekly_section.append(header)

    # 创建标题
    title_comment = soup.new_string('<!-- Weekly News -->')
    weekly_section.append(title_comment)

    section_title = soup.new_tag('h2', **{'class': 'section-title', 'style': 'color: white; margin-top: 40px;'})
    section_title.string = f"🔥 上周重点新闻 ({WEEK_START}) (招聘视角)"
    weekly_section.append(section_title)

    # 创建新闻网格
    news_grid = soup.new_tag('div', **{'class': 'news-grid'})

    # 插入新闻
    for news in WEEKLY_NEWS:
        news_card = BeautifulSoup(create_news_card(news), 'html.parser')
        news_grid.append(news_card)

    weekly_section.append(news_grid)

    # 添加信息来源（如果存在）
    if info_sources:
        weekly_section.append(info_sources)

    # 保存更新后的 HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"本周观察已完全重写！插入了 {len(WEEKLY_NEWS)} 条新闻")

    # 提交到 GitHub
    try:
        subprocess.run([GIT_PATH, 'add', '.'], check=True)
        subprocess.run([GIT_PATH, 'commit', '-m', f'修复本周观察排版: {WEEK_START} ~ {WEEK_END}'], check=True)
        subprocess.run([GIT_PATH, 'push'], check=True)
        print("Git 推送成功！")
    except Exception as e:
        print(f"Git 推送失败: {e}")

if __name__ == '__main__':
    main()
