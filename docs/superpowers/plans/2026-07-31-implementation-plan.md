# Implementation Plan — GitHub Trends Pusher

**Based on spec:** `docs/superpowers/specs/2026-07-31-github-trends-pusher-design.md`
**Date:** 2026-07-31

---

## Dependency Graph

```
pyproject.toml / .gitignore
    │
    ├─► crawler/base.py (Repo + BaseCrawler)
    │       │
    │       └─► crawler/github_trending.py
    │
    ├─► formatter.py (uses Repo type)
    │
    ├─► notification/base.py (BaseSender)
    │       │
    │       ├─► notification/wechat.py
    │       └─► notification/feishu.py
    │               │
    │               └─► notification/dispatcher.py
    │
    ├─► config/config.yaml + .env.example
    │
    └─► src/__main__.py (orchestrates all above)
            │
            └─► .github/workflows/push.yml
                      │
                      └─► README.md + docs/README-EN.md
```

## Vertical Slices

Each phase delivers one complete, verifiable path through the system.

### Phase 1: Project Scaffolding

Files: `pyproject.toml`, `.gitignore`, `src/__init__.py`, `src/crawler/__init__.py`, `src/notification/__init__.py`

Verify: `uv sync` succeeds.

### Phase 2: Crawler Core (data model → HTML parse → format)

Files: `crawler/base.py`, `crawler/github_trending.py`, `formatter.py`

End-to-end: run crawler → get `list[Repo]` → formatter produces markdown string.

Verify: local script prints formatted trending output.

### Phase 3: Notification Infrastructure

Files: `notification/base.py`, `notification/wechat.py`, `notification/feishu.py`, `notification/dispatcher.py`

Verify: with a test config (real webhook/sendkey), each sender delivers a test message.

### Phase 4: Integration & Config

Files: `src/__main__.py`, `config/config.yaml`, `.env.example`

End-to-end: `uv run python -m src` crawls trending, formats, dispatches to enabled channels.

Verify: one real push to a configured channel.

### Phase 5: GitHub Actions Deployment

Files: `.github/workflows/push.yml`

Verify: `workflow_dispatch` manual trigger succeeds in the repo.

### Phase 6: Documentation

Files: `README.md`, `docs/README-EN.md`

Verify: GitHub renders README correctly, English docs linked and readable.

---

## Checkpoints

| Checkpoint | After Phase | What to confirm |
|------------|-------------|-----------------|
| CP1 | Phase 2 | Crawler returns valid repos, formatter output looks correct |
| CP2 | Phase 4 | Local end-to-end run works (at least one real channel) |
| CP3 | Phase 5 | GitHub Actions scheduled/manual run succeeds |

## Verification Strategy

Each phase includes a concrete verification step — no "looks right" assertions:

- **Phase 1:** `uv sync --frozen` exits 0, `uv run python -c "import src"` exits 0
- **Phase 2:** Run crawler script, check output contains repo names with stars
- **Phase 3:** Send test message to WeChat/Feishu, confirm receipt
- **Phase 4:** Full local `uv run python -m src` push to real channel
- **Phase 5:** Trigger workflow_dispatch in GitHub, check Actions log + receipt
- **Phase 6:** Open repo page, verify README renders, English link works
