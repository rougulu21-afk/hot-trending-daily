# 📊 每日热榜日报

自动抓取 36氪、百度、抖音 三大平台热榜数据，生成精美的 HTML 日报，并通过飞书机器人推送。

## ✨ 功能特点

- 🔄 **自动更新** - 每天北京时间 9:00 自动抓取最新热榜
- 📱 **响应式设计** - 支持桌面端和移动端浏览
- 🏷️ **Tab 切换** - 36氪 / 百度 / 抖音 三个平台快速切换
- 🔔 **飞书推送** - 自动推送消息卡片到飞书群
- ☁️ **云端运行** - 基于 GitHub Actions，无需本地电脑

## 🚀 快速开始

### 1. 准备飞书机器人

1. 在飞书群中点击「设置」→「群机器人」
2. 添加「自定义机器人」
3. 复制 Webhook 地址（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）

### 2. 上传到 GitHub

1. 创建新的 GitHub 仓库
2. 上传本项目所有文件：
   ```
   hot_trending_daily.py
   push_to_feishu.py
   requirements.txt
   .github/workflows/daily-report.yml
   ```

### 3. 配置 Secrets

在 GitHub 仓库中依次点击：
**Settings → Secrets and variables → Actions → New repository secret**

添加一个 Secret：
- **Name**: `FEISHU_WEBHOOK`
- **Secret**: 你的飞书机器人 Webhook 地址

### 4. 启用 Actions

1. 进入仓库的 **Actions** 页面
2. 点击 "I understand my workflows, go ahead and enable them"
3. 每天北京时间 9:00 会自动运行

### 5. 手动测试

在 Actions 页面点击左侧 "Daily Hot Report"，然后点击 "Run workflow" 手动触发一次测试。

## 📁 项目结构

```
├── hot_trending_daily.py      # 主脚本：抓取数据并生成 HTML
├── push_to_feishu.py          # 飞书推送模块
├── requirements.txt           # Python 依赖
├── .github/
│   └── workflows/
│       └── daily-report.yml  # GitHub Actions 工作流配置
└── README.md                  # 本说明文档
```

## ⏰ 定时任务说明

| 时区 | 执行时间 | 说明 |
|------|---------|------|
| 北京时间 | 每天 09:00 | 自动抓取并推送 |
| UTC | 每天 01:00 | GitHub Actions 实际执行时间 |

## 🔧 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置飞书 Webhook（可选）
export FEISHU_WEBHOOK="你的Webhook地址"

# 运行脚本
python hot_trending_daily.py
```

生成的 HTML 文件保存在 `html/` 目录，数据 JSON 保存在 `data/` 目录。

## 📬 飞书消息样式

每天 9:00 你会收到类似这样的飞书卡片：

```
┌─────────────────────────────────────┐
│ 📊 每日热榜日报                      │
│                                     │
│ 📅 日期: 2026-04-02 早间版          │
│                                     │
│ 🔥 今日热榜已更新                    │
│    📰 36氪: 50条                    │
│    🔍 百度: 51条                    │
│    🎵 抖音: 48条                    │
│                                     │
│     [📖 查看完整日报]                │
└─────────────────────────────────────┘
```

## ⚙️ 自定义配置

### 修改推送时间

编辑 `.github/workflows/daily-report.yml`，修改 cron 表达式：

```yaml
schedule:
  - cron: "0 1 * * *"  # 北京时间 9:00
```

### 修改数据源

编辑 `hot_trending_daily.py` 中的 `API_URLS` 配置。

## ❓ 常见问题

**Q: 飞书没有收到消息？**
- 检查 GitHub Secrets 中的 Webhook 地址是否正确
- 查看 Actions 运行日志是否有报错
- 确认机器人没有被移出群聊

**Q: 想推送给多个群？**
- 飞书不支持一个 Webhook 发给多个群
- 可以创建多个 Secret，在脚本中循环发送

## 📄 License

MIT License - 随意使用和修改
