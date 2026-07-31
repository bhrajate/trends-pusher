# GitHub Trends Pusher

> 多源热榜聚合推送工具，定时抓取 GitHub Trending / Hacker News / 稀土掘金 / Product Hunt / 牛客等平台热门内容，推送到飞书、微信。

## 支持的数据源

| 数据源 | 方式 | 默认推送时间 |
|--------|------|-------------|
| 🔥 GitHub Trending | 直接抓取 | 每天 10:03 |
| 🔶 Hacker News | RSS | 每天 10:33 |
| ⛏️ 稀土掘金 | NewsNow API | 每天 10:08 |
| 🦄 Product Hunt | NewsNow API | 每天 10:13 |
| 💻 牛客 | NewsNow API | 每天 10:18 |

> NewsNow 聚合 API 支持 30+ 平台，新增平台只需 `--source newsnow --platform {id}`，无需写抓取代码。

## 功能

- 📊 多数据源：GitHub Trending（HTML 解析）、Hacker News（RSS）、NewsNow 聚合（知乎/抖音/微博等 30+ 平台）
- 📮 多渠道推送：**飞书群机器人**（卡片 2.0）+ **微信个人号**（Server酱）
- ⏰ GitHub Actions 定时运行，每个数据源独立 workflow，cron 自由配置
- 🎨 飞书富文本卡片，Markdown 分隔线布局，语言颜色/奖牌/热度标识
- 🔌 可扩展：加数据源 = 加 `crawler/xxx/` + `formatter/xxx.py`，加渠道 = 实现 `BaseSender`

## 快速开始

### 1. Fork 本项目

### 2. 配置通知渠道

#### 飞书群机器人

1. 在飞书群中添加「自定义机器人」，获取 Webhook URL
2. （可选）设置签名校验，获取 Secret
3. 在 GitHub 仓库 **Settings → Secrets and variables → Actions** 中添加：
   - `FEISHU_WEBHOOK_URL`：Webhook 地址
   - `FEISHU_SECRET`：签名密钥（未开启则留空）

#### 微信个人号（Server酱）

1. 注册 [Server酱](https://sct.ftqq.com/)，获取 SendKey
2. 在 GitHub Secrets 中添加：
   - `WECHAT_SENDKEY`：你的 SendKey

### 3. 启用/禁用数据源

在 GitHub Actions 页面，每个数据源有独立的 workflow，可以手动 enable/disable。

### 4. 调整推送时间

编辑对应 workflow 文件的 `cron` 表达式（UTC 时间，北京时间 = UTC + 8）。

## 本地运行

```bash
# 安装依赖
uv sync

# GitHub Trending
uv run python -m src --source github

# Hacker News
uv run python -m src --source hackernews

# NewsNow 平台（如掘金、Product Hunt 等）
uv run python -m src --source newsnow --platform juejin
uv run python -m src --source newsnow --platform producthunt

# 需要代理时
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897

# 配置飞书/微信后可直接推送
export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
export WECHAT_SENDKEY=SCTxxxxx
```

## 配置说明

`config/config.yaml`：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `crawler.since` | `daily` | GitHub 榜单类型：`daily` / `weekly` / `monthly` |
| `crawler.language` | `""` | 编程语言过滤，如 `python` |
| `display.max_items` | `25` | 最大展示条数 |
| `display.show_language_color` | `true` | 是否显示语言 emoji |
| `display.show_description` | `true` | 是否显示项目描述 |

## 项目结构

```
src/
├── __main__.py                    # --source github|hackernews|newsnow
├── crawler/
│   ├── base.py                    # BaseCrawler ABC
│   ├── github/                    # GitHub Trending（HTML 解析）
│   │   ├── models.py             # Repo
│   │   └── crawler.py
│   ├── hackernews/                # Hacker News（RSS）
│   │   ├── models.py             # Story
│   │   └── crawler.py
│   └── newsnow/                   # NewsNow 聚合（30+ 平台）
│       ├── models.py             # HotItem
│       └── crawler.py
└── notification/
    ├── base.py                    # BaseSender ABC
    ├── feishu.py                  # 飞书（卡片 2.0）
    ├── wechat.py                  # 微信（Server酱）
    ├── dispatcher.py              # 分发器
    └── formatter/
        ├── github.py              # Repo → Markdown
        ├── hackernews.py          # Story → Markdown
        └── newsnow.py             # HotItem → Markdown
```

## 扩展

- **新通知渠道**：实现 `BaseSender`，在 `dispatcher.py` 中注册
- **新数据源**：实现 `BaseCrawler` + models + formatter，在 `__main__.py` 中注册
- **新 NewsNow 平台**：只需新建 workflow 文件，`--source newsnow --platform {id}` 即用

## 参考

设计参考了 [TrendRadar](https://github.com/sansan0/TrendRadar)，数据聚合基于 [NewsNow](https://github.com/ourongxing/newsnow)。

## License

MIT
