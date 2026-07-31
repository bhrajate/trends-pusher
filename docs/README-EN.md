# GitHub Trends Pusher

> Periodically fetch [GitHub Trending](https://github.com/trending) projects and push them to Feishu, WeChat (via ServerChan), and other IM channels.

## Features

- 📊 Scrapes the GitHub Trending page for daily/weekly/monthly popular repositories
- 📮 Pushes to **Feishu group bot** and **WeChat** (via ServerChan)
- ⏰ Scheduled via GitHub Actions, defaults to 09:00 Beijing time daily
- 🎨 Language color emoji indicators with stars and descriptions
- 🔌 Extensible: add new channels or data sources by implementing interfaces

## Quick Start

### 1. Fork this repo

### 2. Configure notification channels

#### Feishu Group Bot

1. Add a "Custom Bot" in your Feishu group to get the Webhook URL
2. (Optional) Enable signature verification and get the Secret
3. Add to **Settings → Secrets and variables → Actions**:
   - `FEISHU_WEBHOOK_URL`: Webhook URL
   - `FEISHU_SECRET`: Signature secret (leave empty if not enabled)

#### WeChat (via ServerChan)

1. Register at [ServerChan](https://sct.ftqq.com/) to get your SendKey
2. Add to GitHub Secrets:
   - `WECHAT_SENDKEY`: Your SendKey

### 3. (Optional) Adjust schedule

Edit `.github/workflows/push.yml` cron expression:

```yaml
on:
  schedule:
    - cron: "0 1 * * *"   # UTC 01:00 = Beijing 09:00
```

### 4. Test with manual trigger

Go to Actions → `Push GitHub Trending` → `Run workflow`.

## Local Development

```bash
# Install dependencies
uv sync

# Run with proxy
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897

# Configure channels
export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
export WECHAT_SENDKEY=SCTxxxxx

uv run python -m src
```

## Configuration

Edit `config/config.yaml` or override via environment variables.

| Option | Default | Description |
|--------|---------|-------------|
| `crawler.since` | `daily` | Trending period: `daily` / `weekly` / `monthly` |
| `crawler.language` | `""` | Filter by language, e.g. `python` |
| `crawler.spoken_language` | `""` | Filter by spoken language, e.g. `zh` |
| `display.max_items` | `25` | Max repos to display |
| `display.show_language_color` | `true` | Show language emoji |
| `display.show_description` | `true` | Show repo description |

## Project Structure

```
github-trends-pusher/
├── .github/workflows/push.yml   # GitHub Actions workflow
├── config/config.yaml            # Configuration
├── src/
│   ├── __main__.py               # Entry point
│   ├── formatter.py              # Message formatting
│   ├── crawler/                  # Data sources
│   │   ├── base.py               # Abstract interface
│   │   └── github_trending.py    # GitHub Trending scraper
│   └── notification/             # Notification channels
│       ├── base.py               # Abstract interface
│       ├── feishu.py             # Feishu sender
│       ├── wechat.py             # WeChat sender
│       └── dispatcher.py         # Channel dispatcher
├── docs/README-EN.md             # English docs
└── .env.example                  # Environment template
```

## Extending

- **New channel**: Implement `BaseSender`, register in `dispatcher.py`
- **New data source**: Implement `BaseCrawler`, switch in config
- **Docker**: Coming soon

## Reference

Design inspired by [TrendRadar](https://github.com/sansan0/TrendRadar).

## License

MIT
