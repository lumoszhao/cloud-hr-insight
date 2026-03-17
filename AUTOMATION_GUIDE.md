# 云行业HR洞察 - 自动化更新指南

## 概述

本项目已实现以下自动化功能：

### ✅ 已完成功能

1. **自动日期显示** - 使用JavaScript动态获取当前日期，无需手动更新
2. **数据爬虫脚本** - 从各大云厂商官网获取招聘信息
3. **新闻数据更新** - 自动获取云计算行业最新新闻
4. **GitHub Actions定时任务** - 每天自动更新数据

## 使用说明

### 方式一：自动更新（推荐）

项目已配置GitHub Actions，会每天自动运行更新脚本：

- **运行时间**：每天北京时间 8:00 (UTC 0:00)
- **自动执行**：无需任何操作，自动获取最新数据
- **自动推送**：更新后自动提交并推送到GitHub

### 方式二：手动更新

如果需要立即更新，可以手动运行：

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 运行新闻数据获取脚本
python fetch_news.py

# 3. 运行招聘信息爬虫
python scraper.py

# 4. 提交更改
git add .
git commit -m "chore: 手动更新数据"
git push
```

### 方式三：在GitHub上手动触发

1. 进入GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "Daily News Update" 工作流
4. 点击 "Run workflow" 按钮
5. 选择分支并运行

## 文件说明

### 核心文件

- `index.html` - 主页面，包含自动日期显示功能
- `fetch_news.py` - 新闻数据获取脚本
- `scraper.py` - 招聘信息爬虫脚本
- `requirements.txt` - Python依赖列表
- `.github/workflows/daily-update.yml` - GitHub Actions配置

### 数据文件

- `daily_news.json` - 每日新闻数据（自动生成）
- `weekly_news.json` - 每周报告数据（自动生成）

## 技术实现

### 1. 自动日期显示

JavaScript代码自动计算：
- 今天日期
- 昨天日期
- 前天日期
- 本周日期范围
- 上周日期范围
- 下个周日

```javascript
// 自动获取当前日期
function getTodayDate() {
    const today = new Date();
    return formatDate(today);
}

// 页面加载时自动初始化
window.addEventListener('DOMContentLoaded', function() {
    initializeDates();
});
```

### 2. 数据爬虫

爬虫脚本会访问以下来源：

- 腾讯云招聘页面
- 阿里云招聘页面
- 华为云招聘页面
- 火山引擎招聘页面
- AWS中国招聘页面
- Microsoft Azure招聘页面

### 3. GitHub Actions

工作流程：

1. 每天定时触发
2. 检出代码
3. 设置Python环境
4. 安装依赖
5. 运行数据更新脚本
6. 提交更改并推送

## 注意事项

### API密钥配置

如果需要使用真实的新闻API，请：

1. 申请免费API密钥（如NewsAPI）
2. 在GitHub仓库设置中添加Secrets：
   - `NEWS_API_KEY`
3. 在脚本中引用：
   ```python
   api_key = os.environ.get('NEWS_API_KEY')
   ```

### 反爬虫措施

某些网站可能有反爬虫机制：

- 已添加User-Agent头
- 已设置请求间隔
- 如遇到问题，可能需要：
  - 使用代理IP
  - 添加随机延迟
  - 使用Selenium等工具

### 数据准确性

- 当前版本使用演示数据结构
- 真实数据需要接入实际API
- 建议定期验证数据来源的可靠性

## 扩展功能建议

### 1. 添加更多数据源

- LinkedIn招聘信息
- Boss直聘数据
- 猎聘网数据
- 各大公司官方公告

### 2. 数据可视化

- 添加图表展示趋势
- 招聘数量统计
- 薪资水平对比

### 3. 邮件通知

- 发送每日简报
- 重要职位提醒
- 薪资变动通知

### 4. 移动端适配

- 响应式设计优化
- PWA支持
- 离线浏览

## 故障排查

### GitHub Actions运行失败

1. 检查Workflow日志
2. 确认Python版本兼容性
3. 验证依赖是否正确安装

### 数据未更新

1. 检查网络连接
2. 验证目标网站是否可访问
3. 查看脚本错误日志

### 日期显示错误

1. 检查JavaScript控制台
2. 验证浏览器时区设置
3. 清除浏览器缓存

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请通过以下方式联系：

- 提交Issue
- 发送邮件
- 在GitHub上联系

---

**更新日期**：2025-03-17
**版本**：v2.0.0
