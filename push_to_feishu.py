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

    # 读取 HTML 文件路径（由主脚本传入）
    html_file = os.environ.get("HTML_FILE", "")

    today = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    sources = data.get("sources", [])

    # 统计各平台数据条数
    stats = []
    for source in sources:
        count = len(data.get("data", {}).get(source, []))
        if source == "36氪":
            stats.append(f"📰 36氪: {count}条")
        elif source == "百度":
            stats.append(f"🔍 百度: {count}条")
        elif source == "抖音":
            stats.append(f"🎵 抖音: {count}条")

    stats_text = "\n".join(stats) if stats else "暂无数据"

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

**🔥 今日热榜已更新**

{stats_text}

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

    # 在 GitHub Actions 环境中，使用 rawgit 或 jsdelivr 托管 HTML
    html_url = os.environ.get("HTML_URL", "")
    if html_url:
        # 在 GitHub Actions 中，HTML 文件会被保存到 html/ 目录
        # 可以通过 GitHub Pages 访问，或者直接在消息中说明本地路径
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
