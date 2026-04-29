# Ops — automation

本目录是 agent-hunt 的本地自动化（launchd），让数据生产 + 部署在你不操作时自动跑。

## 文件清单

| 文件 | 作用 |
|---|---|
| `weekly_refresh.sh` | 跑全流程：collect 增量 → backfill → export → commit/push → wrangler deploy |
| `launchd/com.llm-x-factorer.agent-hunt.weekly.plist` | 每周日 02:00 触发 weekly_refresh.sh |
| `launchd/com.llm-x-factorer.agent-hunt.celery.plist` | Celery worker + beat 持续运行（月度快照 / 未来定时任务） |

## 安装（一次性）

```bash
# 1. 拷贝 plist 到 LaunchAgents 目录
cp ops/launchd/com.llm-x-factorer.agent-hunt.weekly.plist ~/Library/LaunchAgents/
cp ops/launchd/com.llm-x-factorer.agent-hunt.celery.plist ~/Library/LaunchAgents/

# 2. 注册到 launchd
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.weekly.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.celery.plist

# 3. 验证已加载
launchctl list | grep agent-hunt
# 应该看到两条
```

## 验证 / 调试

```bash
# 立即手动 trigger weekly（测试用，不等周日）
launchctl kickstart -k gui/$(id -u)/com.llm-x-factorer.agent-hunt.weekly

# 看 weekly 实时日志
tail -f ~/Library/Logs/agent-hunt/weekly-*.log

# 看 celery 实时日志
tail -f ~/Library/Logs/agent-hunt/launchd-celery-stderr.log

# 看 launchd 自身的 stderr
tail -f ~/Library/Logs/agent-hunt/launchd-weekly-stderr.log
```

## 卸载

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.weekly.plist
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.celery.plist

rm ~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.weekly.plist
rm ~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.celery.plist
```

## 注意事项

- **mac 必须在通电状态**才能 trigger（笔记本合盖也会触发，但需要电源）。
- **docker compose 必须能拉起**（db + redis）—— weekly_refresh.sh 会 `docker compose up -d`，但如果 Docker Desktop 没开自动启动，请到 Docker Desktop 设置勾选 "Start Docker Desktop when you log in"。
- **wrangler 需要登录**——首次手动跑 `npx wrangler login`，token 会存到 `~/.wrangler/`，后续 launchd 跑也能用。
- **git push 需要 SSH 或缓存的 HTTPS 凭证**——若用 HTTPS 确保 macOS Keychain 里有 GitHub 凭证。
- **OpenRouter 余额耗尽不致命**——`generate_insights.py` / `generate_report.py` 失败时整个 weekly 仍继续跑（这些脚本默认未在 weekly 列表里，由 Claude 手写）。
- **如果电脑周日凌晨没开**：launchd plist 里 `StartCalendarIntervalAcceptsMissedRuns=false`，错过就跳过。下周日继续。如果想要补跑，把这个改成 `true`。

## 架构图

```
launchd（macOS）
   ├── 每周日 02:00 触发 weekly_refresh.sh
   │      └── docker compose up -d (db + redis)
   │      └── 后端 collect 增量
   │      └── 后端 export 衍生 JSON
   │      └── git commit + push
   │      └── npm run build + wrangler deploy
   │
   └── 持续运行 Celery worker + beat
          └── 每月 1 号 03:00 UTC 跑月度快照
          └── 跑完更新 snapshots 表 + frontend/public/data/trends/*.json
```
