---
name: github-actions-feishu-schedule
overview: 配置 GitHub Actions 定时任务，每天早上 9 点自动抓取热榜数据并推送到飞书
todos:
  - id: create-feishu-push-module
    content: 创建 push_to_feishu.py 飞书推送模块
    status: completed
  - id: modify-main-script
    content: 修改 hot_trending_daily.py 添加推送调用
    status: completed
    dependencies:
      - create-feishu-push-module
  - id: create-github-workflow
    content: 创建 .github/workflows/daily-report.yml 工作流
    status: completed
    dependencies:
      - modify-main-script
  - id: create-requirements
    content: 创建 requirements.txt
    status: completed
  - id: create-readme
    content: 创建 README.md 使用说明文档
    status: completed
---

## 需求概述

将每日热榜日报生成脚本部署到 GitHub Actions，实现每天早上 9:00 自动运行，生成 HTML 后通过飞书机器人 Webhook 推送给用户。

## 核心功能

1. **定时触发**: 每天北京时间 9:00 自动运行
2. **数据抓取**: 从 36氪、百度、抖音获取热榜数据
3. **HTML 生成**: 生成精美的热榜日报页面
4. **飞书推送**: 通过 Webhook 发送消息卡片，包含跳转链接

## 技术方案

### 技术栈

- **触发器**: GitHub Actions (cron: `0 1 * * *`，北京时间 9:00)
- **运行环境**: Python 3.x (GitHub-hosted runner)
- **推送方式**: 飞书自定义机器人 Webhook

### 目录结构

```
/Users/gulu/新闻网页/
├── hot_trending_daily.py          # [修改] 主脚本，添加飞书推送功能
├── push_to_feishu.py              # [新建] 飞书推送模块
├── .github/
│   └── workflows/
│       └── daily-report.yml       # [新建] GitHub Actions 工作流
├── requirements.txt               # [新建] Python 依赖
└── README.md                      # [新建] 使用说明
```

### 核心实现

#### 1. GitHub Actions 工作流 (.github/workflows/daily-report.yml)

```
name: Daily Hot Report
on:
  schedule:
    - cron: "0 1 * * *"  # 每天北京时间 9:00
  workflow_dispatch:      # 手动触发
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install requests
      - name: Generate report
        run: python hot_trending_daily.py
      - name: Push to Feishu
        env:
          FEISHU_WEBHOOK: ${{ secrets.FEISHU_WEBHOOK }}
        run: python push_to_feishu.py
```

#### 2. 飞书推送模块 (push_to_feishu.py)

- 调用飞书 Webhook API
- 发送富文本消息卡片，包含:
- 标题: 每日热榜日报
- 日期信息
- 各平台数据统计
- 跳转 HTML 的链接按钮

### 飞书消息卡片示例

```
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {"tag": "plain_text", "content": "每日热榜日报"},
      "template": "purple"
    },
    "elements": [
      {"tag": "markdown", "content": "**日期**: 2026-04-01\n**数据来源**: 36氪 | 百度 | 抖音"},
      {"tag": "action", "elements": [{"tag": "button", "text": {"tag": "plain_text", "content": "查看完整日报"}, "type": "primary"}]}
    ]
  }
}
```

### 用户需要提供的配置

1. `FEISHU_WEBHOOK`: 飞书机器人 Webhook 地址
2. `HTML_URL`: 生成的 HTML 页面托管地址（如 GitHub Pages）