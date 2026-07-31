# GitHub Trends Pusher — Design Spec

**Date:** 2026-07-31
**Status:** Implemented（已实现，本文反映实际状态）

---

## 1. 项目定位

轻量级多源热榜聚合推送工具。通过 GitHub Actions 定时抓取 GitHub Trending / Hacker News / 稀土掘金 / Product Hunt / 牛客等多个平台的热门内容，推送到飞书、微信（Server酱）等 IM 渠道。

命令行参数选择数据源：`--source github|hackernews|newsnow`，NewsNow 聚合 API 覆盖 30+ 平台。

---

## 2. 技术选型

| 维度 | 选择 |
|------|------|
| 语言 | Python 3.12+ |
| 包管理 | `uv`（`pyproject.toml` + `uv.lock`） |
| HTML 解析 | `beautifulsoup4`（仅 GitHub Trending） |
| RSS 解析 | 标准库 `re` 解析 XML（Hacker News） |
| 聚合 API | NewsNow（`newsnow.busiyi.world`，免费无需 Key） |
| HTTP 请求 | `requests` |
| 配置 | YAML + 环境变量覆盖 |
| 调度 | GitHub Actions，每个数据源独立 workflow 文件 |
| 敏感信息 | GitHub Secrets → 环境变量注入 |

---

## 3. 项目结构

```
github-trends-pusher/
├── .github/workflows/
│   ├── push-github.yml
│   ├── push-hackernews.yml
│   ├── push-juejin.yml
│   ├── push-producthunt.yml
│   └── push-nowcoder.yml
├── config/
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── __main__.py                 # --source github|hackernews|newsnow [--platform xxx]
│   ├── crawler/
│   │   ├── base.py                 # BaseCrawler ABC
│   │   ├── github/                 # GitHub Trending（HTML 解析）
│   │   │   ├── models.py          # Repo
│   │   │   └── crawler.py
│   │   ├── hackernews/             # Hacker News（RSS）
│   │   │   ├── models.py          # Story
│   │   │   └── crawler.py
│   │   └── newsnow/                # NewsNow 聚合（30+ 平台）
│   │       ├── models.py          # HotItem
│   │       └── crawler.py
│   └── notification/
│       ├── base.py                 # BaseSender ABC
│       ├── feishu.py               # 飞书（卡片 2.0，自动分批）
│       ├── wechat.py               # 微信（Server酱）
│       ├── dispatcher.py           # 遍历渠道，统一发送
│       └── formatter/              # 按数据源分文件
│           ├── github.py           # Repo → Markdown
│           ├── hackernews.py       # Story → Markdown
│           └── newsnow.py          # HotItem → Markdown
├── docs/
│   └── README-EN.md
├── pyproject.toml
├── README.md
├── .env.example
└── .gitignore
```

---

## 4. 模块设计

### 4.1 `crawler/base.py` — 爬虫抽象

```python
class BaseCrawler(ABC):
    @abstractmethod
    def crawl(self) -> list[Any]: ...
    @property
    @abstractmethod
    def name(self) -> str: ...
```

各数据源自己定义模型（`Repo` / `Story` / `HotItem`），不强求统一。

### 4.2 数据源

| 数据源 | 方式 | 模块 |
|--------|------|------|
| GitHub Trending | HTML 解析 | `crawler/github/` |
| Hacker News | RSS（hnrss.org） | `crawler/hackernews/` |
| 稀土掘金 / Product Hunt / 牛客等 | NewsNow API | `crawler/newsnow/` |

- NewsNow：`GET https://newsnow.busiyi.world/api/s?id={platform}&latest`，响应 JSON `{status, items: [{title, url, extra: {heat}}]}`
- 新增平台只需 `--source newsnow --platform {id}`，无需写抓取代码

### 4.3 `notification/formatter/` — 消息格式化

输入数据源模型，输出统一 Markdown 格式：

- `**列表项标题链接**` + 统计行 + `---` 分隔 + 底部斜体水印
- 飞书 sender 统一包裹为卡片 2.0（`msg_type: interactive`）
- 格式随数据源不同有差异（GitHub 日期+Dailt、HN 奖牌热度、NewsNow 平台 emoji）

### 4.4 通知渠道

| 渠道 | 模块 | 特点 |
|------|------|------|
| 飞书 | `feishu.py` | 卡片 2.0，超长自动分批（30KB），HMAC 签名 |
| 微信 | `wechat.py` | Server酱 HTTP POST，title + desp |

新增渠道：实现 `BaseSender`，在 `dispatcher.py` 中注册。

### 4.5 `__main__.py` — 入口

```bash
uv run python -m src --source github                       # GitHub Trending
uv run python -m src --source hackernews                   # Hacker News
uv run python -m src --source newsnow --platform juejin    # 稀土掘金
uv run python -m src --source newsnow --platform producthunt
```

流程：加载配置 → 按 `--source` 选择 Crawler → `crawl()` → 对应 Formatter → Dispatcher 分发。

---

## 5. 配置设计

`config/config.yaml`：抓取参数（`since`/`language`）、展示选项（`max_items`/颜色/描述）、通知渠道开关。

环境变量覆盖 YAML：`FEISHU_WEBHOOK_URL`、`WECHAT_SENDKEY` 等。

GitHub Secrets → workflow env → 程序读取。

---

## 6. GitHub Actions

每个数据源独立 workflow 文件，默认北京时间的上午时段错开推送：

| Workflow | 数据源 | 默认 cron (UTC) | 北京时间 |
|----------|--------|----------------|---------|
| `push-github.yml` | GitHub Trending | `3 2 * * *` | 10:03 |
| `push-hackernews.yml` | Hacker News | `33 2 * * *` | 10:33 |
| `push-juejin.yml` | 稀土掘金 | `8 2 * * *` | 10:08 |
| `push-producthunt.yml` | Product Hunt | `13 2 * * *` | 10:13 |
| `push-nowcoder.yml` | 牛客 | `18 2 * * *` | 10:18 |

均支持 `workflow_dispatch` 手动触发，共享同一套 Secrets。

---

## 7. 依赖 (`pyproject.toml`)

```toml
[project]
name = "github-trends-pusher"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.32",
    "beautifulsoup4>=4.12",
    "pyyaml>=6.0",
]

[tool.uv]
index-url = "https://mirrors.aliyun.com/pypi/simple/"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

---

## 8. 扩展点

| 扩展项 | 方式 |
|--------|------|
| 新通知渠道 | 实现 `BaseSender`，在 `dispatcher.py` 注册 |
| 新独立数据源 | 新建 `crawler/xxx/`（models + crawler）+ `formatter/xxx.py`，在 `__main__.py` 注册 |
| 新 NewsNow 平台 | 新建 workflow 文件，`--source newsnow --platform {id}` 即用 |
| Docker 部署 | 后期添加 `Dockerfile` + `docker-compose.yml` |

---

## 9. 暂不纳入一期

以下功能一期不实现，但不排除后续版本加入：

- AI 分析/翻译
- HTML 报告/网页展示
- 数据存储/历史记录
- 关键词过滤
- 调度系统（timeline）
- 多账号管理
