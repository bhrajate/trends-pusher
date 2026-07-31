# Task List — GitHub Trends Pusher

---

## Phase 1: Project Scaffolding

### T1.1 Initialize project structure

- **Files:** `pyproject.toml`, `.gitignore`, `src/__init__.py`, `src/crawler/__init__.py`, `src/notification/__init__.py`
- **What:** Create project skeleton with `uv` configuration using Aliyun PyPI mirror.
- **Acceptance:** `uv sync` succeeds, `uv run python -c "import src"` exits 0.
- **Dependencies:** none

---

## Phase 2: Crawler Core

### T2.1 Implement `crawler/base.py`

- **What:** Define `Repo` dataclass (owner, name, description, language, language_color, stars, stars_today, url) and `BaseCrawler` abstract class (crawl method + name property).
- **Acceptance:** Can instantiate `Repo`, `BaseCrawler` subclasses enforce `crawl` and `name`.
- **Dependencies:** T1.1

### T2.2 Implement `crawler/github_trending.py`

- **What:** `GitHubTrendingCrawler` extends `BaseCrawler`. Requests `https://github.com/trending` with query params (since, language, spoken_language). Uses BeautifulSoup to parse `.Box-row` elements. Extracts owner/name, description, language, stars, stars_today, url, language_color.
- **Acceptance:** Run crawl → returns `list[Repo]` with populated fields. Verify a few repos have expected data.
- **Dependencies:** T2.1

### T2.3 Implement `formatter.py`

- **What:** Takes `list[Repo]` + channel name + display config. Renders Markdown with: header (date + since type), per-repo block (number, language color emoji, owner/name, description, stars, stars_today, link), footer (count + attribution). Language → emoji mapping. Respects `max_items`. Channel-specific formatting hooks.
- **Acceptance:** Given mock `list[Repo]`, output matches spec preview format.
- **Dependencies:** T2.1 (needs Repo type)

---

## Phase 3: Notification Infrastructure

### T3.1 Implement `notification/base.py`

- **What:** `BaseSender` ABC with `send(content: str) -> bool`, `validate_config(config: dict) -> bool`, `channel_name` property.
- **Acceptance:** Subclass instantiation enforces all abstract methods.
- **Dependencies:** T1.1

### T3.2 Implement `notification/wechat.py`

- **What:** `WeChatSender` extends `BaseSender`. Reads `sendkey` from config. POSTs to `https://sctapi.ftqq.com/{sendkey}.send` with `title` and `desp` (Markdown content).
- **Acceptance:** With valid SendKey, test message arrives in WeChat.
- **Dependencies:** T3.1

### T3.3 Implement `notification/feishu.py`

- **What:** `FeishuSender` extends `BaseSender`. Reads `webhook_url` + optional `secret`. Implements HMAC-SHA256 signing if secret provided. Sends interactive card or text Markdown. Splits messages > 30KB.
- **Acceptance:** With valid webhook, test message arrives in Feishu group.
- **Dependencies:** T3.1

### T3.4 Implement `notification/dispatcher.py`

- **What:** `NotificationDispatcher` iterates notification config, instantiates senders for `enabled: true` channels, calls `send()` for each. Logs success/failure counts.
- **Acceptance:** With one enabled channel, dispatcher calls correct sender. With all disabled, dispatcher reports no channels.
- **Dependencies:** T3.2, T3.3

---

## Phase 4: Integration

### T4.1 Create `config/config.yaml`

- **What:** Default config with crawler section (since/language/spoken_language), display section (max_items, show_language_color, show_description), notification section (feishu + wechat, all disabled).
- **Acceptance:** YAML parses without errors, all expected keys present.
- **Dependencies:** none

### T4.2 Create `.env.example`

- **What:** All env var overrides with comments: `FEISHU_*`, `WECHAT_*`, `CRAWLER_*`, `DISPLAY_*`.
- **Acceptance:** File matches spec section 5.2.
- **Dependencies:** T4.1

### T4.3 Implement `src/__main__.py`

- **What:** Entry point. Loads config (YAML → env override). Instantiates `GitHubTrendingCrawler` with crawler config. Calls `crawl()`. Formats message via `formatter.py`. Passes to `NotificationDispatcher.dispatch()`. Logs each step.
- **Acceptance:** `uv run python -m src` completes full pipeline with at least one real channel.
- **Dependencies:** T2.2, T2.3, T3.4, T4.1

---

## Phase 5: GitHub Actions

### T5.1 Create `.github/workflows/push.yml`

- **What:** Workflow with `schedule` (cron: `0 1 * * *`, UTC 01:00 = Beijing 09:00) + `workflow_dispatch`. Sets up Python 3.12 + uv, runs `uv sync --frozen --no-dev`, then `uv run python -m src`. Injects Secrets as env vars: `FEISHU_WEBHOOK_URL`, `FEISHU_SECRET`, `WECHAT_SENDKEY`.
- **Acceptance:** `workflow_dispatch` succeeds in GitHub Actions log.
- **Dependencies:** T4.3

---

## Phase 6: Documentation

### T6.1 Write `README.md` (Chinese)

- **What:** Project intro, features, quick start, configuration guide, GitHub Actions setup, FAQ.
- **Acceptance:** Renders correctly on GitHub.
- **Dependencies:** T5.1

### T6.2 Write `docs/README-EN.md` (English)

- **What:** English version of README with same structure.
- **Acceptance:** Renders correctly. Linked from root README.
- **Dependencies:** T6.1
