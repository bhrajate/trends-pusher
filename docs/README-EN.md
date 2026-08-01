# Trends Pusher

[中文](../README.md)

> Multi-source trending aggregator. Periodically fetches hot content from GitHub Trending, Hacker News, Juejin, Product Hunt, Nowcoder and more, pushing to Feishu and WeChat.

## Supported Sources

| Source | Method | Default Schedule |
|--------|--------|-----------------|
| 🔥 GitHub Trending | Direct scraping | Daily 09:00 |
| ⛏️ Juejin | NewsNow API | Daily 12:00 |
| 💻 Nowcoder | NewsNow API | Daily 14:00 |
| 🦄 Product Hunt | NewsNow API | Daily 16:00 |
| 🔶 Hacker News | RSS | Daily 18:00 |

> The NewsNow API supports 30+ platforms. Adding a new platform is just `--source newsnow --platform {id}`.

## Features

- 📊 Multi-source: GitHub Trending (HTML), Hacker News (RSS), NewsNow aggregator (Zhihu, Douyin, Weibo, etc.)
- 📮 Multi-channel: **Feishu bot** (Card 2.0) + **WeChat** (ServerChan)
- ⏰ GitHub Actions scheduled, independent workflow per source
- 🎨 Rich Feishu cards with markdown layout, language colors, medals, heat indicators
- 🔌 Extensible: add source = `crawler/xxx/` + `formatter/xxx.py`, add channel = implement `BaseSender`

## Quick Start

### 1. Fork this repo

### 2. Configure channels

#### Feishu Bot

1. Add a "Custom Bot" in your Feishu group to get the Webhook URL
2. (Optional) Enable signature verification and get the Secret
3. Add to **Settings → Secrets and variables → Actions**:
   - `FEISHU_WEBHOOK_URL`: Webhook URL
   - `FEISHU_SECRET`: Signature secret (leave empty if not enabled)

#### WeChat (ServerChan)

1. Register at [ServerChan](https://sct.ftqq.com/) to get your SendKey
2. Add to GitHub Secrets:
   - `WECHAT_SENDKEY`: Your SendKey

### 3. Enable/disable sources

Each data source has its own workflow in the Actions tab — enable or disable individually.

### 4. Adjust schedule

Edit the `cron` expression in each workflow file (UTC, Beijing = UTC + 8).

## Local Development

```bash
# Install
uv sync

# GitHub Trending
uv run python -m src --source github

# Hacker News
uv run python -m src --source hackernews

# NewsNow platforms
uv run python -m src --source newsnow --platform juejin
uv run python -m src --source newsnow --platform producthunt

# With proxy
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897

# With channels configured
export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
export WECHAT_SENDKEY=SCTxxxxx
```

## Configuration

`config/config.yaml`:

| Option | Default | Description |
|--------|---------|-------------|
| `crawler.since` | `daily` | GitHub trending period: `daily` / `weekly` / `monthly` |
| `crawler.language` | `""` | Filter by language, e.g. `python` |
| `display.max_items` | `25` | Max items to display |
| `display.show_language_color` | `true` | Show language emoji |
| `display.show_description` | `true` | Show repo description |

## Project Structure

```
src/
├── __main__.py                    # --source github|hackernews|newsnow
├── crawler/
│   ├── base.py                    # BaseCrawler ABC
│   ├── github/                    # GitHub Trending (HTML)
│   │   ├── models.py             # Repo
│   │   └── crawler.py
│   ├── hackernews/                # Hacker News (RSS)
│   │   ├── models.py             # Story
│   │   └── crawler.py
│   └── newsnow/                   # NewsNow aggregator (30+ platforms)
│       ├── models.py             # HotItem
│       └── crawler.py
└── notification/
    ├── base.py                    # BaseSender ABC
    ├── feishu.py                  # Feishu (Card 2.0)
    ├── wechat.py                  # WeChat (ServerChan)
    ├── dispatcher.py
    └── formatter/
        ├── github.py              # Repo → Markdown
        ├── hackernews.py          # Story → Markdown
        └── newsnow.py             # HotItem → Markdown
```

## Extending

- **New channel**: Implement `BaseSender`, register in `dispatcher.py`
- **New source**: Implement `BaseCrawler` + models + formatter, register in `__main__.py`
- **New NewsNow platform**: Just add a workflow file with `--source newsnow --platform {id}`

## Reference

Design inspired by [TrendRadar](https://github.com/sansan0/TrendRadar). Data aggregation powered by [NewsNow](https://github.com/ourongxing/newsnow).

## License

MIT
