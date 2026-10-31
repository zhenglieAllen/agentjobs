# 着陆页部署指南 —— 解锁 H1.2 引流

> **这份文档解决什么问题**：`tasks.md` 任务 14 [A1.1] 的代码已完成，但 M1（着陆页订阅数）
> 的数据**只能由一个公网可访问的着陆页产生**。在它上线前，任务 2 [H1.2] 无法开始，
> 验证窗口（2026-10-25 ~ 11-22）的第 1 周已空转过去。
>
> **当前状态（2026-10-31）**：代码已推送至 GitHub（`main`），部署链路与本指南齐备，
> **但线上仍未部署**——这是验证期唯一的硬阻塞项。部署目标：Railway Hobby 档
> （免费档无持久盘，订阅数据会随容器重启静默清零）。
>
> **技术选型依据**：`.spec-workflow/specs/agentjobs/tech-decision.md` 第 8 节——
> 验证期着陆页保持 Python 标准库实现，**不重写为 FastAPI**（重写是纯风险零收益：
> M1 数据完全依赖这个服务，重写期间不可用就是一天的数据损失）。

---

## ⚠️ 先读这条：持久化是硬需求

着陆页用 SQLite 存 `subscribers` 表。**部署目标必须提供持久磁盘**，
否则容器每次重启/重新部署都会清空订阅数据，M1 指标随之失效——
而且你不会立刻发现，因为服务看起来一切正常。

| 平台 | 档位 | 持久盘 | 月费 | 结论 |
|---|---|---|---|---|
| **Railway** | Hobby | ✅ 1 GB volume | ~$5（含 $5 usage credit） | **推荐** |
| Render | Starter | ✅ 1 GB disk | $7 | 备选 |
| Render | Free | ❌ 无 | $0 | ❌ 不可用——订阅数据会丢 |
| Fly.io | — | ✅ volume | 按量 | 可用，但配置更繁琐 |

`railway.json` / `render.yaml` 已配好卷挂载到 `/data`，`DB_PATH=/data/landing.db`。

---

## 前置条件

- [ ] Railway 账号（[railway.app](https://railway.app)，GitHub 登录即可）
- [ ] 仓库已推送到 GitHub（部署从 Git 仓库拉取）
- [ ] 本地 `python3 -m unittest discover -s landing/tests` 全绿

---

## 部署步骤（Railway，推荐）

### 1. 新建项目

1. Railway Dashboard → **New Project** → **Deploy from GitHub Repo** → 选 `agentjobs` 仓库
2. Railway 会检测到 `railway.json`，自动使用 Dockerfile 构建

### 2. 挂载持久卷（**不要跳过**）

1. 项目 → 选中 service → **Volumes** → **New Volume**
2. Mount Path 填 `/data`
3. Volume 会自动挂载并触发一次重新部署

### 3. 设置环境变量

选中 service → **Variables** → **+ New Variable**：

| 变量名 | 值 | 说明 |
|---|---|---|
| `AGENTJOBS_ADMIN_TOKEN` | 点 **Generate** 生成 | 管理端令牌。访问 `/api/subscribers/export` 和 `/api/stats` 必需 |
| `AGENTJOBS_SECURE_COOKIES` | `1` | 走 HTTPS，cookie 加 `Secure` 属性 |
| `HOST` | `0.0.0.0` | 监听所有网卡（Dockerfile 已设，此处确认即可） |
| `PORT` | **不要设** | Railway 自动注入 |

> **令牌别丢**：`AGENTJOBS_ADMIN_TOKEN` 存在 Railway 的 secret 里，页面看不到明文。
> 若忘记了，删除该变量重新生成即可——但导出接口的旧令牌会立刻失效。

### 4. 生成域名并部署

1. service → **Settings** → **Networking** → **Generate Domain**
2. 得到形如 `agentjobs-landing.up.railway.app` 的 HTTPS 地址
3. Railway 会自动构建部署。看 **Deployments** 日志确认成功

### 5. 验证

```bash
# 把 <URL> 换成上一步的域名，把 <TOKEN> 换成 AGENTJOBS_ADMIN_TOKEN

# 健康检查（无需令牌）
curl -s https://<URL>/healthz
# 期望：{"ok": true}

# 着陆页（确认返回 HTML 且设置了变体 cookie）
curl -sI https://<URL>/ | grep -iE "set-cookie|content-security-policy|strict-transport"

# M1 实时计数（按变体分列）
curl -s -H 'X-Admin-Token: <TOKEN>' https://<URL>/api/stats
# 期望：{"active": ["A","B","C"], "variants": {...}, "m1_total_subscribers": 0, ...}

# 导出 CSV（表头须与 validation/schemas/templates/subscribers.csv 逐字一致）
curl -s -H 'X-Admin-Token: <TOKEN>' https://<URL>/api/subscribers/export | head -1
# 期望：email,source_channel,ab_variant,subscribed_at,confirmed_at,unsubscribed_at
```

**逐条验收清单**：

- [ ] `/healthz` 返回 `{"ok": true}`
- [ ] 访问 `/` 后浏览器收到 `aj_var` cookie，且带 `Secure` 与 `HttpOnly`
- [ ] 响应头含 `Strict-Transport-Security` 与 `Content-Security-Policy`
- [ ] `/privacy` 可访问，页面说明了 `aj_var` cookie 的用途
- [ ] 浏览器**强制刷新**两次，页面标题/主标题**不变**（粘性归因生效）
- [ ] `/api/stats` 无令牌返回 401，有令牌返回按 A/B/C 分列的计数
- [ ] 导出的 CSV 表头与 `validation/schemas/templates/subscribers.csv` 逐字相同

### 6. 真实订阅冒烟测试

用**你自己**的邮箱走一遍表单，填一个 `source_channel`。然后：

```bash
curl -s -H 'X-Admin-Token: <TOKEN>' https://<URL>/api/stats | python3 -m json.tool
```

确认 `m1_total_subscribers` 变成 1，且变体计数 +1。
测完**删掉这一行**（否则 M1 会被自己的订阅污染，浪费掉一个样本）：

```bash
# 本地删除（需先 rsync/scp 出数据库文件），或在 Railway 控制台执行
# 见下方「本地取回数据库」
```

> 更省事的做法：**先别测**。直接上线开始推广，冒烟测试用真实流量完成。
> 若一定要测，用一个明显的测试邮箱，测完删。

---

## 备选部署：Render

1. Render Dashboard → **New** → **Blueprint** → 指向本仓库（会读 `render.yaml`）
2. Blueprint 里 `plan: starter` 是必需的——免费档没有持久盘
3. 部署后按上面第 5 步同样验证

---

## 环境变量总表

| 变量 | 默认 | 生产取值 | 作用 |
|---|---|---|---|
| `AGENTJOBS_ADMIN_TOKEN` | 随机生成 | **必须显式设置** | `/api/*` 鉴权令牌 |
| `AGENTJOBS_SECURE_COOKIES` | `0` | `1` | cookie 加 `Secure` + 下发 HSTS 头 |
| `HOST` | `127.0.0.1` | `0.0.0.0` | 监听地址 |
| `PORT` | `8000` | 平台注入 | 监听端口 |
| `DB_PATH` | `landing/landing.db` | `/data/landing.db` | SQLite 路径（须在持久卷上） |

---

## 每周数据回灌（M1 的正确用法）

`validation-metrics.md`「数据归属与存储」要求：订阅数据的**权威存储是本服务的
`subscribers` 表**，第三方 ESP 只是投递通道，**每周导出回灌**。

每周执行一次：

```bash
# 1. 从线上导出（带 BOM，compute_metrics.py 以 utf-8-sig 读取会自动剥离）
curl -s -H 'X-Admin-Token: <TOKEN>' \
  https://<URL>/api/subscribers/export \
  -o validation/data/subscribers.csv

# 2. 跑指标脚本，确认 M1 数值合理
python3 validation/compute_metrics.py --data-dir validation/data
```

> `validation/data/` 已在 `.gitignore` 中——订阅者邮箱是 PII，不入版本控制。

若接入了 ESP（Mailchimp 等），每周还要把 ESP 的退订名单回灌：
在 `subscribers` 表上执行 `UPDATE subscribers SET unsubscribed_at = ... WHERE email IN (...)`。

---

## 本地取回数据库（备份 / 清理测试数据）

线上 SQLite 文件在持久卷上，取回本地：

```bash
# Railway：先用 railway CLI 或在控制台执行
railway run cat /data/landing.db > landing/landing.db.bak
# 或在 service 的 shell 里执行
```

本地打开检查：

```bash
sqlite3 landing/landing.db.bak "SELECT id, email, source_channel, ab_variant FROM subscribers;"
sqlite3 landing/landing.db.bak "SELECT ab_variant, COUNT(*) FROM page_views GROUP BY ab_variant;"
```

---

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 部署后访问 502 / 服务反复重启 | 端口不匹配 | Railway/Render 注入 `PORT`，`server.py` 已读取；确认没有在 `railway.json` 里覆盖 `startCommand` 的端口参数 |
| 重启后订阅数据清空 | 卷没挂上 | 检查卷 Mount Path 必须是 `/data`，且 `DB_PATH=/data/landing.db` |
| cookie 没有 `Secure` | 环境变量没设 | 设 `AGENTJOBS_SECURE_COOKIES=1` 并重新部署 |
| 导出接口 401 | 令牌不对 | 重新生成 `AGENTJOBS_ADMIN_TOKEN` |
| 频繁 `database is locked` | 卷不支持 WAL，或多副本 | 已用 WAL + busy_timeout 兜底；确认 `numReplicas: 1` |
| 变体每次刷新都变 | cookie 被拦截 | 检查 `SameSite=Lax` 与 `Secure` 是否被浏览器/代理改写 |
| 页面显示但表单一提交就失败 | CSP 拦截 | 确认 CSP 的 `connect-src 'self'` 存在 |

---

## 上线之后：把 H1.2 交回给创始人

服务上线、拿到 URL 后，`tasks.md` 任务 2 [H1.2] 的执行条件就满足了。
**该任务属人工轨**——投放渠道、发帖、盯数据都是创始人的活，agent 不得代勾。

落地页这边已经准备好承接的：

- 变体归因：3 个变体的分流、粘性 cookie、按变体计数都就绪
- 渠道归因：表单里的「你从哪里了解到我们」下拉框，产出的就是 `subscribers.source_channel`
- 实时看板：`/api/stats` 直接看 M1 与各变体转化
- 样本不足预警：`under_sampled` 与 `degrade_suggestion` 字段会在某变体访问数 < 100 时提示降级

**推广清单见 `landing/PROMO.md`**（渠道、话术、每日动作）。
