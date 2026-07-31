# GitHub Trends Pusher — Design Spec

**Date:** 2026-07-31
**Status:** Draft

---

## 1. 项目定位

轻量级 GitHub Trending 定时推送工具。通过 GitHub Actions 定时抓取 GitHub Trending 页面，解析项目列表，推送到飞书、微信（Server酱）等多个 IM 渠道。

**不做什么：** 不聚合其他平台（微博、知乎等），不做 AI 分析，不做 HTML 报告，不做存储。专注一件事 —— 把 GitHub Trending 送到聊天窗口。

---

## 2. 技术选型

| 维度 | 选择 |
|------|------|
| 语言 | Python 3.12+ |
| 包管理 | `uv`（`pyproject.toml` + `uv.lock`） |
| HTML 解析 | `beautifulsoup4` |
| HTTP 请求 | `requests` |
| 配置 | YAML + 环境变量覆盖 |
| 调度 | GitHub Actions (`cron` + `workflow_dispatch`) |
| 敏感信息 | GitHub Secrets → 环境变量注入 |

---

## 3. 项目结构

```
github-trends-pusher/
├── .github/workflows/
│   └── push.yml
├── config/
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── __main__.py                 # 入口，编排流程
│   ├── formatter.py                # 数据结构 → 渠道 Markdown
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── base.py                 # Repo 数据类 + BaseCrawler 抽象
│   │   └── github_trending.py      # HTML 抓取实现
│   └── notification/
│       ├── __init__.py
│       ├── base.py                 # BaseSender 抽象接口
│       ├── feishu.py                # 飞书 webhook
│       ├── wechat.py                # 微信 Server酱 推送
│       └── dispatcher.py           # 遍历渠道，统一发送
├── docs/
│   └── README-EN.md
├── pyproject.toml
├── README.md
├── .env.example
└── .gitignore
```

---

## 4. 模块设计

### 4.1 `crawler/base.py` — 爬虫抽象 + 数据模型

```python
@dataclass
class Repo:
    owner: str           # 仓库所有者
    name: str            # 仓库名
    description: str     # 项目描述
    language: str        # 编程语言（可为空）
    language_color: str  # 语言颜色 hex（可为空）
    stars: str           # 总 Star 数（格式化字符串，如 "42.3k"）
    stars_today: str     # 今日新增 Star（格式化字符串）
    url: str             # 仓库 URL

class BaseCrawler(ABC):
    @abstractmethod
    def crawl(self) -> list[Repo]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...
```

### 4.2 `crawler/github_trending.py` — GitHub Trending 实现

- 请求 `https://github.com/trending?since={daily|weekly|monthly}&spoken_language_code={code}`
- BeautifulSoup 解析 HTML，提取每个 `.Box-row` 元素
- 解析每个仓库的：owner/name、description、language、stars、stars_today、url
- 语言颜色从 GitHub 的 `style` 属性中提取（`background-color: #xxx`）
- 返回 `list[Repo]`

### 4.3 `formatter.py` — 消息格式化

- 输入：`list[Repo]`
- 输出：Markdown 格式的推送消息（字符串）
- 按渠道可能需要微调（飞书和微信的 Markdown 略有差异），通过 `channel` 参数控制
- 语言颜色渲染为 Markdown 色块：`🟢 Python`（使用预定义映射）
- 支持 `max_items` 截断
- 消息头部包含日期和 `since` 类型

### 4.4 `notification/base.py` — 通知抽象

```python
class BaseSender(ABC):
    @abstractmethod
    def send(self, content: str) -> bool: ...

    @classmethod
    @abstractmethod
    def validate_config(cls, config: dict) -> bool: ...

    @property
    @abstractmethod
    def channel_name(self) -> str: ...
```

### 4.5 `notification/wechat.py` — 微信发送器（基于 Server酱）

- 用户注册 [Server酱](https://sct.ftqq.com/) 获得 SendKey
- 调用 `https://sctapi.ftqq.com/{SendKey}.send` 推送消息到微信
- 参数：`title`（消息标题）、`desp`（消息内容，支持 Markdown）
- 简单直接，无需签名校验，无消息长度限制问题

### 4.6 `notification/feishu.py` — 飞书发送器

- 支持飞书自定义机器人 webhook
- 支持签名校验（`secret` 字段，HMAC-SHA256 + Base64）
- 消息过长时自动分批（每批不超过 30KB）
- 消息类型：`interactive`（卡片）或 `text`（Markdown）

### 4.7 `notification/dispatcher.py` — 分发器

- 遍历 `config.yaml` 中 `enabled: true` 的渠道
- 跳过配置校验失败或 `enabled: false` 的渠道
- 统计发送成功/失败数量，输出日志
- 新增渠道只需：实现 `BaseSender` + 在 dispatcher 中注册

### 4.8 `__main__.py` — 入口

流程编排：

1. 加载配置（YAML + 环境变量覆盖）
2. 根据配置实例化 Crawler
3. 调用 `crawler.crawl()` 获取 `list[Repo]`
4. 调用 `formatter.format(repos, channel)` 生成消息
5. 调用 `dispatcher.dispatch(messages)` 发送到所有渠道

---

## 5. 配置设计

### 5.1 `config/config.yaml`

```yaml
crawler:
  since: "daily"           # daily / weekly / monthly
  language: ""             # 留空=全部，可选 python/go/javascript/...
  spoken_language: ""      # 留空=全部，可选 zh/en/...

display:
  max_items: 25
  show_language_color: true
  show_description: true

notification:
  feishu:
    enabled: false
    webhook_url: ""
    secret: ""
  wechat:
    enabled: false
    sendkey: ""
```

### 5.2 `.env.example`

```bash
# ===== 飞书 =====
FEISHU_ENABLED=false
FEISHU_WEBHOOK_URL=
FEISHU_SECRET=

# ===== 微信（Server酱）=====
WECHAT_ENABLED=false
WECHAT_SENDKEY=

# ===== 抓取选项 =====
CRAWLER_SINCE=daily
CRAWLER_LANGUAGE=
CRAWLER_SPOKEN_LANGUAGE=

# ===== 展示选项 =====
DISPLAY_MAX_ITEMS=25
```

### 5.3 配置优先级

环境变量 > config.yaml。加载顺序：先读 YAML，再用环境变量覆盖对应字段。

### 5.4 GitHub Secrets 映射

| Secret | 环境变量 |
|--------|---------|
| `FEISHU_WEBHOOK_URL` | `FEISHU_WEBHOOK_URL` |
| `FEISHU_SECRET` | `FEISHU_SECRET` |
| `WECHAT_SENDKEY` | `WECHAT_SENDKEY` |

---

## 6. GitHub Actions 工作流

```yaml
# .github/workflows/push.yml
name: Push GitHub Trending

on:
  schedule:
    # 默认 UTC 01:00 = 北京时间 09:00
    # 用户可 fork 后修改 cron 表达式
    - cron: "0 1 * * *"
  workflow_dispatch:

jobs:
  push:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - uses: astral-sh/setup-uv@v7
      - run: uv sync --frozen --no-dev
      - run: uv run python -m src
        env:
          FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
          FEISHU_SECRET: ${{ secrets.FEISHU_SECRET }}
          WECHAT_SENDKEY: ${{ secrets.WECHAT_SENDKEY }}
```

---

## 7. 依赖 (`pyproject.toml`)

```toml
[project]
name = "github-trends-pusher"
version = "0.1.0"
description = "定期拉取 GitHub Trending 并推送到飞书、微信等渠道"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.32",
    "beautifulsoup4>=4.12",
    "pyyaml>=6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 8. 推送效果预览

```
🔥 GitHub Trending · 2026-07-31 · Daily

━━━━━━━━━━━━━━━━━━━━━━━━

1. 🟢 cli/cli
   GitHub's official command line tool
   ⭐ 42.3k  |  📈 +128 today
   🔗 https://github.com/cli/cli

2. 🟡 anthropics/claude-code
   Anthropic's official CLI for Claude
   ⭐ 18.9k  |  📈 +356 today
   🔗 https://github.com/anthropics/claude-code

3. ⚪ slimtoolkit/slim
   Don't change anything in your container image and minify it by up to 30x
   ⭐ 20.1k  |  📈 +89 today
   🔗 https://github.com/slimtoolkit/slim

━━━━━━━━━━━━━━━━━━━━━━━━
共 25 个项目 · Powered by GitHub Trends Pusher
```

---

## 9. 扩展点

| 扩展项 | 方式 |
|--------|------|
| 新通知渠道 | 实现 `BaseSender`，在 dispatcher 注册 |
| 新数据源 | 实现 `BaseCrawler`，在 config 中切换 |
| 更多展示模式 | 扩展 `formatter.py`，通过 config 控制 |
| Docker 部署 | 后期添加 `Dockerfile` + `docker-compose.yml` |

---

## 10. 暂不纳入一期

以下功能一期不实现，但不排除后续版本加入：

- AI 分析/翻译
- HTML 报告/网页展示
- 数据存储/历史记录
- RSS 订阅
- 关键词过滤
- 调度系统（timeline）
- 多账号管理