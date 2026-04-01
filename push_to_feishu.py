#!/usr/bin/env python3
"""
飞书 Webhook 推送模块
通过飞书群机器人发送每日热榜日报卡片
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional


def build_trending_list(data: Dict, source: str, max_items: int = 5) -> str:
    """
    构建热榜列表的 Markdown 内容

    Args:
        data: 完整数据字典
        source: 平台名称（36氪/百度/抖音）
        max_items: 最大条目数

    Returns:
        Markdown 格式的热榜列表
    """
    items = data.get("data", {}).get(source, [])
    if not items:
        return "暂无数据"

    lines = []
    for i, item in enumerate(items[:max_items]):
        title = item.get("title", "无标题")
        url = item.get("url", "")
        hot_text = item.get("hot_text", "")

        # 转义 Markdown 特殊字符（主要转义中括号避免解析问题）
        title_escaped = title.replace("[", "\\[").replace("]", "\\]")

        # 构建可点击链接
        if url:
            lines.append(f"🔝 {i+1}. [{title_escaped}]({url})")
            if hot_text:
                lines[-1] += f" 🔥{hot_text}"
        else:
            lines.append(f"🔝 {i+1}. {title_escaped}")
            if hot_text:
                lines[-1] += f" 🔥{hot_text}"

    return "\n".join(lines)


def send_feishu_message(webhook_url: str, data: Dict) -> bool:
    """
    发送飞书消息卡片

    Args:
        webhook_url: 飞书 Webhook 地址
        data: 包含 date, sources, data 等字段的字典

    Returns:
        是否发送成功
    """
    if not webhook_url:
        print("⚠️ 未配置飞书 Webhook，跳过推送")
        return False

    today = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    # 平台配置
    platform_config = {
        "36氪": {"icon": "📰", "max_items": 5},
        "百度": {"icon": "🔍", "max_items": 5},
        "抖音": {"icon": "🎵", "max_items": 5}
    }

    # 构建各平台热榜内容
    trending_sections = []
    for source in data.get("sources", []):
        config = platform_config.get(source, {"icon": "📋", "max_items": 5})
        max_items = config["max_items"]
        icon = config["icon"]

        trending_list = build_trending_list(data, source, max_items)
        count = len(data.get("data", {}).get(source, []))

        section = f"**{icon} {source} Top {min(max_items, count)}**\n{trending_list}"
        trending_sections.append(section)

    trending_content = "\n\n---\n\n".join(trending_sections) if trending_sections else "暂无数据"

    # 构建飞书消息卡片
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 每日热榜日报"
                },
                "template": "purple"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"""**📅 日期**: {today} 早间版

**🔥 今日热榜速览**

{trending_content}

---
*由 GitHub Actions 自动生成*"""
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"生成时间: {datetime.now().strftime('%H:%M:%S')}"
                        }
                    ]
                }
            ]
        }
    }

    # 在 GitHub Actions 环境中，添加完整日报按钮
    html_url = os.environ.get("HTML_URL", "")
    if html_url:
        message["card"]["elements"].insert(1, {
            "tag": "action",
            "elements": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "📖 查看完整日报"
                    },
                    "type": "primary",
                    "url": html_url
                }
            ]
        })

    # 发送请求
    try:
        data_bytes = json.dumps(message).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))

            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print("✅ 飞书消息发送成功!")
                return True
            else:
                print(f"❌ 飞书消息发送失败: {result}")
                return False

    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


def main():
    """从命令行参数或环境变量读取配置"""
    # 从环境变量获取 Webhook URL
    webhook_url = os.environ.get("FEISHU_WEBHOOK", "")

    if not webhook_url:
        print("⚠️ 请设置 FEISHU_WEBHOOK 环境变量")
        sys.exit(1)

    # 读取数据文件（可选）
    data_file = os.environ.get("DATA_FILE", "")
    if data_file and os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # 使用默认数据
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sources": ["36氪", "百度", "抖音"],
            "data": {}
        }

    success = send_feishu_message(webhook_url, data)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
