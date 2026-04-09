#!/usr/bin/env python3
"""
每日热榜日报生成器
自动从36氪、百度、抖音热榜获取数据，生成静态HTML日报
"""

import json
import urllib.request
import urllib.error
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


# ============== 配置 ==============
API_URLS = {
    "36氪": "https://api.iyuns.com/api/hot36kr",
    "百度": "https://api.iyuns.com/api/baiduhot",
    "抖音": "https://api.iyuns.com/api/douyinhot"
}

OUTPUT_DIR = "./html"
DATA_DIR = "./data"

# 请求头，模拟浏览器访问
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://api.iyuns.com/"
}


# ============== 数据获取 ==============
def fetch_api(url: str) -> Optional[Dict]:
    """调用API获取数据"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠️ 请求失败: {e}")
        return None


# ============== 数据清洗 ==============
def clean_36kr(raw_data: List[Dict]) -> List[Dict]:
    """清洗36氪数据"""
    items = []
    for idx, item in enumerate(raw_data):
        tmpl = item.get("templateMaterial", {})
        item_id = item.get("itemId", "")

        # 拼接文章详情链接（正确格式：/p/ 而非 /detail/）
        if item_id:
            url = f"https://36kr.com/p/{item_id}"
        else:
            url = "https://36kr.com/"

        items.append({
            "rank": idx + 1,
            "title": tmpl.get("widgetTitle", ""),
            "hot_value": tmpl.get("statRead", 0),
            "hot_text": f"{tmpl.get('statRead', 0):,}阅读" if isinstance(tmpl.get('statRead'), int) else str(tmpl.get('statRead', '')),
            "summary": tmpl.get("authorName", ""),
            "cover": tmpl.get("widgetImage", ""),
            "url": url,
            "source": "36氪"
        })
    return items


def clean_baidu(raw_data: List[Dict]) -> List[Dict]:
    """清洗百度热搜数据"""
    items = []
    for item in raw_data:
        items.append({
            "rank": item.get("index", 0),
            "title": item.get("title", ""),
            "hot_value": item.get("hot", ""),
            "hot_text": str(item.get("hot", "")),
            "summary": item.get("desc", ""),
            "cover": item.get("img", ""),
            "url": item.get("url", ""),
            "source": "百度"
        })
    return items


def clean_douyin(raw_data: List[Dict]) -> List[Dict]:
    """清洗抖音热榜数据"""
    items = []
    for item in raw_data:
        cover_obj = item.get("word_cover", {}) or {}
        url_list = cover_obj.get("url_list", []) or []

        # 拼接抖音搜索链接
        word = item.get("word", "")
        search_url = f"https://www.douyin.com/search/{urllib.parse.quote(word)}" if word else ""

        items.append({
            "rank": item.get("position", 0),
            "title": word,
            "hot_value": item.get("hot_value", 0),
            "hot_text": format_hot_value(item.get("hot_value", 0)),
            "summary": get_douyin_label_text(item.get("label", 0)),
            "cover": url_list[0] if url_list else "",
            "url": search_url,
            "source": "抖音"
        })
    return items


def format_hot_value(value: int) -> str:
    """格式化热度值"""
    if value >= 100000000:
        return f"{value / 100000000:.1f}亿"
    elif value >= 10000:
        return f"{value / 10000:.1f}万"
    else:
        return str(value)


def get_douyin_label_text(label: int) -> str:
    """获取抖音标签文字"""
    labels = {
        0: "普通",
        1: "普通",
        3: "热榜",
        5: "娱乐",
        7: "社会",
        9: "知识",
        11: "体育",
        13: "数码"
    }
    return labels.get(label, "热榜")


# ============== HTML生成 ==============
def generate_html(data: Dict[str, List], date_str: str) -> str:
    """生成HTML日报"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{date_str} 每日热榜日报</title>
    <style>
        :root {{
            --primary: #1a73e8;
            --secondary: #5f6368;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --border: #e8eaed;
            --text: #202124;
            --text-light: #5f6368;
            --baidu-color: #2932e1;
            --kr-color: #f4503e;
            --douyin-color: #00f2ea;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        /* 头部 */
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-bottom: 40px;
            border-radius: 16px;
        }}

        .header h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 12px;
        }}

        .header .date {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 16px;
        }}

        .header .sources {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.9rem;
            opacity: 0.85;
        }}

        .header .source-item {{
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 20px;
        }}

        /* Tab 切换 */
        .tab-container {{
            margin-top: 30px;
        }}

        .tab-nav {{
            display: flex;
            gap: 8px;
            background: var(--card-bg);
            padding: 8px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }}

        .tab-btn {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 20px;
            border: none;
            background: transparent;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-light);
            transition: all 0.2s;
        }}

        .tab-btn:hover {{
            background: var(--bg);
            color: var(--text);
        }}

        .tab-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .tab-icon {{
            font-size: 1.2rem;
        }}

        .tab-name {{
            font-weight: 600;
        }}

        .tab-count {{
            background: rgba(255,255,255,0.3);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
        }}

        .tab-btn:not(.active) .tab-count {{
            background: var(--bg);
            color: var(--text-light);
        }}

        /* Tab 内容 */
        .tab-content {{
            min-height: 400px;
        }}

        .tab-panel {{
            display: none;
        }}

        .tab-panel.active {{
            display: block;
        }}

        /* 卡片 */
        .card {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 14px;
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
            display: flex;
            flex-direction: column;
        }}

        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: var(--primary);
        }}

        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }}

        .card-header {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .rank {{
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.95rem;
            color: white;
        }}

        .rank.top1 {{ background: linear-gradient(135deg, #f7971e, #f5af19); }}
        .rank.top2 {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .rank.top3 {{ background: linear-gradient(135deg, #11998e, #38ef7d); }}
        .rank.normal {{ background: var(--border); color: var(--text-light); }}

        .card-title {{
            flex: 1;
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.4;
            color: var(--text);
        }}

        .card-title a {{
            text-decoration: none;
            color: inherit;
        }}

        .card-title a:hover {{
            color: var(--primary);
        }}

        .card-body {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .card-cover {{
            width: 100%;
            height: 160px;
            border-radius: 8px;
            object-fit: cover;
            background: var(--bg);
        }}

        .card-summary {{
            font-size: 0.9rem;
            color: var(--text-light);
            line-height: 1.5;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid var(--border);
        }}

        .hot-value {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 600;
            color: #ea4335;
            font-size: 0.9rem;
        }}

        .hot-value::before {{
            content: "🔥";
            font-size: 0.85rem;
        }}

        .card-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .card-link:hover {{
            text-decoration: underline;
        }}

        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-light);
            font-size: 0.85rem;
        }}

        /* 卡片网格 */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }}

        /* 响应式 - 手机单列 */
        @media (max-width: 768px) {{
            .container {{
                padding: 12px;
            }}

            .header {{
                padding: 24px 16px;
                margin-bottom: 24px;
            }}

            .header h1 {{
                font-size: 1.6rem;
            }}

            .tab-nav {{
                flex-direction: column;
                gap: 6px;
            }}

            .tab-btn {{
                padding: 10px 16px;
            }}

            .card-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* 加载状态 */
        .loading {{
            text-align: center;
            padding: 40px;
            color: var(--text-light);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 每日热榜日报</h1>
            <div class="date">{date_str} · 早间版</div>
            <div class="sources">
                <span class="source-item">📰 36氪</span>
                <span class="source-item">🔍 百度</span>
                <span class="source-item">🎵 抖音</span>
            </div>
        </header>
"""

    # Tab切换布局
    source_config = {
        "36氪": {"icon": "📰", "id": "kr"},
        "百度": {"icon": "🔍", "id": "baidu"},
        "抖音": {"icon": "🎵", "id": "douyin"}
    }

    # Tab导航
    html += '''
        <div class="tab-container">
            <div class="tab-nav">
'''
    for idx, source_name in enumerate(["36氪", "百度", "抖音"]):
        items = data.get(source_name, [])
        config = source_config.get(source_name, {})
        active = "active" if idx == 0 else ""
        html += f'''
                <button class="tab-btn {active}" data-tab="{config.get("id", "")}" onclick="switchTab('{config.get("id", "")}')">
                    <span class="tab-icon">{config.get("icon", "")}</span>
                    <span class="tab-name">{source_name}</span>
                    <span class="tab-count">{len(items)}</span>
                </button>
'''

    html += '''
            </div>
            <div class="tab-content">
'''

    # Tab内容
    for idx, source_name in enumerate(["36氪", "百度", "抖音"]):
        items = data.get(source_name, [])
        config = source_config.get(source_name, {})
        active = "active" if idx == 0 else ""

        html += f'''
                <div class="tab-panel {active}" id="tab-{config.get("id", "")}">
                    <div class="card-grid">
'''

        for item in items:
            rank_class = "top1" if item["rank"] == 1 else "top2" if item["rank"] == 2 else "top3" if item["rank"] == 3 else "normal"

            # 封面图
            cover_html = ""
            if item.get("cover"):
                cover_html = f'<img class="card-cover" src="{item["cover"]}" alt="{item["title"]}" loading="lazy" onerror="this.style.display=\'none\'">'

            # 摘要
            summary_html = ""
            if item.get("summary"):
                summary_html = f'<div class="card-summary">{item["summary"]}</div>'

            html += f'''
                        <article class="card">
                            <div class="card-header">
                                <span class="rank {rank_class}">{item["rank"]}</span>
                                <h3 class="card-title">
                                    <a href="{item["url"]}" target="_blank" rel="noopener">{item["title"]}</a>
                                </h3>
                            </div>
                            <div class="card-body">
                                {cover_html}
                                {summary_html}
                            </div>
                            <div class="card-footer">
                                <span class="hot-value">{item["hot_text"]}</span>
                                <a class="card-link" href="{item["url"]}" target="_blank" rel="noopener">查看详情 →</a>
                            </div>
                        </article>
'''

        html += '''
                    </div>
                </div>
'''

    html += '''
            </div>
        </div>
'''

    # 页脚
    html += f'''
        <footer class="footer">
            <p>📅 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p style="margin-top: 8px;">数据来源: 36氪、百度热搜、抖音热榜 | 本页面为静态页面，可直接保存分享</p>
        </footer>
    </div>

    <script>
        function switchTab(tabId) {{
            var btns = document.querySelectorAll(".tab-btn");
            var panels = document.querySelectorAll(".tab-panel");
            for (var i = 0; i < btns.length; i++) {{
                btns[i].classList.remove("active");
            }}
            for (var j = 0; j < panels.length; j++) {{
                panels[j].classList.remove("active");
            }}
            document.querySelector("[data-tab=" + tabId + "]").classList.add("active");
            document.getElementById("tab-" + tabId).classList.add("active");
        }}
    </script>
</body>
</html>'''

    return html


# ============== 主程序 ==============
def main():
    import urllib.parse

    print("🚀 开始生成每日热榜日报...")

    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")

    # 确保目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    all_data = {}

    # 获取各平台数据
    for source_name, url in API_URLS.items():
        print(f"\n📡 正在获取 {source_name} 数据...")

        raw_data = fetch_api(url)
        if not raw_data or raw_data.get("code") != 200:
            print(f"  ⚠️ {source_name} 数据获取失败，跳过")
            all_data[source_name] = []
            continue

        raw_items = raw_data.get("data", [])
        print(f"  ✅ 获取到 {len(raw_items)} 条数据")

        # 根据来源清洗数据
        if source_name == "36氪":
            cleaned = clean_36kr(raw_items)
        elif source_name == "百度":
            cleaned = clean_baidu(raw_items)
        elif source_name == "抖音":
            cleaned = clean_douyin(raw_items)
        else:
            cleaned = []

        all_data[source_name] = cleaned
        print(f"  ✅ 清洗完成，保留 {len(cleaned)} 条")

    # 保存JSON数据（同时保存到 html/data/ 供动态首页使用）
    json_data = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "sources": list(API_URLS.keys()),
        "data": all_data
    }
    # 保存到 html/data/ 目录（动态首页需要）
    html_data_dir = os.path.join(OUTPUT_DIR, "data")
    os.makedirs(html_data_dir, exist_ok=True)
    json_path = os.path.join(html_data_dir, f"{date_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON数据已保存: {json_path}")

    # 生成HTML
    print("🎨 正在生成HTML页面...")
    html_content = generate_html(all_data, date_str)

    html_path = os.path.join(OUTPUT_DIR, f"{date_str}-热榜日报.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ HTML日报已生成: {html_path}")

    # 统计
    total = sum(len(v) for v in all_data.values())
    print(f"\n📊 完成! 共获取 {total} 条热榜内容")

    # 准备推送数据
    report_data = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "sources": list(API_URLS.keys()),
        "data": all_data
    }

    # 尝试推送飞书消息（仅在配置了 Webhook 时）
    webhook_url = os.environ.get("FEISHU_WEBHOOK", "")
    if webhook_url:
        print("\n📤 正在推送飞书消息...")
        from push_to_feishu import send_feishu_message

        # 构建 GitHub Pages URL（使用正确的仓库名 hot-trending-daily）
        html_filename = os.path.basename(html_path)
        # 用户的 GitHub Pages: rougulu21-afk.github.io/hot-trending-daily/
        github_pages_url = f"https://rougulu21-afk.github.io/hot-trending-daily/{urllib.parse.quote(html_filename)}"

        report_data["html_url"] = github_pages_url
        send_feishu_message(webhook_url, report_data)
    else:
        print("\n💡 提示: 设置 FEISHU_WEBHOOK 环境变量可自动推送飞书消息")

    # 更新 manifest.json，指向最新日报 JSON
    update_manifest(OUTPUT_DIR, date_str)

    return html_path


def update_manifest(output_dir: str, date: str):
    """更新 manifest.json，指向最新日报 JSON"""
    import json
    manifest = {
        "latest": f"data/{date}.json",
        "date": date
    }
    manifest_path = os.path.join(output_dir, "data", "manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"✅ manifest.json 已更新: {date}")


if __name__ == "__main__":
    main()
