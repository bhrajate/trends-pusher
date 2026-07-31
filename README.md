# GitHub Trends Pusher

> 定时抓取 [GitHub Trending](https://github.com/trending) 热门项目，推送到飞书、微信（Server酱）等 IM 渠道。

## 功能

- 📊 抓取 GitHub Trending 页面，解析每日/每周/每月热门仓库
- 📮 推送到**飞书群机器人**、**微信个人号**（通过 Server酱）
- ⏰ 通过 GitHub Actions 定时运行，默认北京时间每天 9:00
- 🎨 语言颜色 emoji 标识，项目描述、Star 数一目了然
- 🔌 可扩展架构：新增通知渠道或数据源只需实现相应接口

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

### 3. （可选）调整推送频率

编辑 `.github/workflows/push.yml`，修改 `cron` 表达式：

```yaml
on:
  schedule:
    - cron: "0 1 * * *"   # UTC 01:00 = 北京时间 09:00
```

### 4. 手动触发测试

在 GitHub Actions 页面选择 `Push GitHub Trending` → `Run workflow`，立即执行一次。

## 本地运行

```bash
# 安装依赖
uv sync

# 运行（需通过代理访问 GitHub）
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897

# 配置环境变量
export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
export WECHAT_SENDKEY=SCTxxxxx

uv run python -m src
```

## 配置说明

编辑 `config/config.yaml` 或通过环境变量覆盖：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `crawler.since` | `daily` | 榜单类型：`daily` / `weekly` / `monthly` |
| `crawler.language` | `""` | 编程语言过滤，如 `python` |
| `crawler.spoken_language` | `""` | 自然语言过滤，如 `zh` |
| `display.max_items` | `25` | 最大展示项目数 |
| `display.show_language_color` | `true` | 是否显示语言 emoji |
| `display.show_description` | `true` | 是否显示项目描述 |

## 项目结构

```
github-trends-pusher/
├── .github/workflows/push.yml   # GitHub Actions 工作流
├── config/config.yaml            # 配置文件
├── src/
│   ├── __main__.py               # 入口
│   ├── formatter.py              # 消息格式化
│   ├── crawler/                  # 数据源
│   │   ├── base.py               # 抽象接口
│   │   └── github_trending.py    # GitHub Trending 抓取
│   └── notification/             # 通知渠道
│       ├── base.py               # 抽象接口
│       ├── feishu.py             # 飞书
│       ├── wechat.py             # 微信
│       └── dispatcher.py         # 分发器
├── docs/README-EN.md             # English docs
└── .env.example                  # 环境变量模板
```

## 扩展

- **新通知渠道**：实现 `BaseSender`，在 `dispatcher.py` 中注册
- **新数据源**：实现 `BaseCrawler`，在 config 中切换
- **Docker 部署**：后续支持

## 参考

本项目设计参考了 [TrendRadar](https://github.com/sansan0/TrendRadar)。

## License

MIT
