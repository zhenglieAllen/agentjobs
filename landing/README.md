# landing —— AgentJobs 着陆页

任务 **14 [A1.1]** 的产出。这是 `risk-analysis.md` **实验 1**（价值主张 A/B 测试）的执行载体，
也是 M1 着陆页订阅数的唯一数据源。

> **H1.2 [创始人] 的执行入口**：本服务上线后即可开始推广。推广渠道必须逐条记录——
> 订阅表单里的「你从哪里了解到我们」下拉框产出的就是 `subscribers.source_channel`。

## 快速开始

```bash
# 启动（零依赖，仅需 Python 3.9+）
python3 landing/server.py

# 启动时会打印管理令牌（访问管理端接口必需）
# 着陆页:      http://127.0.0.1:8000/
# 隐私说明:    http://127.0.0.1:8000/privacy

# 测试
python3 -m unittest discover -s landing/tests
```

常用参数：

```bash
python3 landing/server.py --port 9000        # 换端口
python3 landing/server.py --active A,B       # 降级为两变体（样本不足时）
python3 landing/server.py --db /path/db.sqlite
AGENTJOBS_ADMIN_TOKEN=固定令牌 python3 landing/server.py   # 固定管理令牌
```

## 技术选型说明

**Python 3 标准库**（`http.server` + `sqlite3`），无第三方依赖、无需 `npm install`。

任务 14 明确「落地页可用任意栈实现」且**不受任务 17 [A1.4] 技术选型阻塞**。选择标准库的理由：

- **零安装**：验证期只有 30 天、solo founder，不应为一次性落地页引入构建链
- **自带 SQLite**：按变体归因需要自建存储，`sqlite3` 是标准库自带的
- **与 `validation/` 同栈**：两个子系统都是 Python 3，导出→聚合的链路无需跨语言胶水

> 若任务 17 [A1.4] 最终选定 Node.js/FastAPI 栈，本目录需按新栈重写。
> 届时 `subscribers.csv` 的**列名契约不变**，`validation/` 无需改动。

## 目录结构

```
landing/
├── server.py           # HTTP 服务：路由、服务端分流、API
├── db.py               # subscribers 表 + 访问计数 + CSV 导出
├── variants.json       # 三个变体的文案与分流配置（文案出自 risk-analysis.md 实验 1）
├── static/
│   ├── index.html      # 落地页模板（占位符由服务端替换）
│   ├── privacy.html    # 隐私声明（说明 A/B 归因 cookie）
│   ├── styles.css
│   └── app.js          # 仅负责表单提交，不参与分流逻辑
└── tests/test_landing.py
```

## 需求对照

| A1.1 Requirements | 实现位置 |
|---|---|
| 3 个变体 1:1:1 随机分流 | `server.Config.pick()` — `secrets.choice` 在活跃变体中随机 |
| 文案见 risk-analysis.md 实验 1 | `variants.json` — A 功能向 / B 痛点向 / C 供需向 |
| 分流须服务端或构建期决定 | 服务端渲染进 HTML（`server.render`），不依赖客户端 JS |
| 避免 SEO 与缓存导致变体错乱 | 响应头 `Vary: Cookie` + `Cache-Control: private, no-cache` |
| 样本不足时降级为 A/B | `--active A,B` 或改 `variants.json` 的 `active`；`/api/stats` 会提示 |
| **必须自建 subscribers 表** | `db.py` 的 `SCHEMA`，对齐 `design.md` 第 151 行 |
| POST /api/subscribers | `server.Handler._subscribe` |
| GET /api/subscribers/export | `server.Handler._serve_export`（需令牌） |
| 表单采集 source_channel 与 ab_variant | `static/index.html` 的两个字段 + POST body |
| 隐私声明说明 A/B 归因 cookie | `static/privacy.html` |
| M1 实时计数（按变体分列） | `GET /api/stats` → `variants.*.subscribers` |

## 为什么必须自建表

若采用纯静态页 + 第三方 ESP（Mailchimp 等），**无法按变体归因**，
`risk-analysis.md` 实验 1 的结论不可用，`validation-metrics.md`「数据归属与存储」
也已规定 ESP 不得作为唯一副本、须每周导出回灌本表。

## 接口

### `POST /api/subscribers`

```json
{ "email": "a@x.com", "source_channel": "reddit", "ab_variant": "A", "company": "" }
```

| 情况 | 状态码 |
|---|---|
| 新订阅 | `201 {"ok":true,"created":true}` |
| 邮箱已订阅（**不报错、不重复计数**） | `200 {"ok":true,"created":false}` |
| 参数非法（邮箱格式 / channel 为空 / 变体非 A/B/C） | `400 {"error":"..."}` |
| 触发频率限制（每 IP 每小时 10 次） | `429` |
| 命中蜜罐 | `200 {"ok":true}` —— 静默接受但不落库，不给机器人反馈 |

### `GET /api/subscribers/export`（需令牌）

返回 CSV，表头与 `validation/schemas/templates/subscribers.csv` **逐字一致**：

```
email,source_channel,ab_variant,subscribed_at,confirmed_at,unsubscribed_at
```

带 UTF-8 BOM（Excel 兼容）。`compute_metrics.py` 以 `utf-8-sig` 读取，会正确剥离 BOM——
该路径由 `test_downloaded_csv_with_bom_still_loads` 单独覆盖。

### `GET /api/stats`（需令牌）

M1 实时计数，按变体分列，含降级建议：

```json
{
  "active": ["A", "B", "C"],
  "variants": { "A": { "angle": "功能向", "visits": 2, "subscribers": 1 } },
  "m1_total_subscribers": 3,
  "min_visits_before_degrade": 100,
  "under_sampled": ["A", "B", "C"],
  "degrade_suggestion": "变体 A, B, C 访问数不足 100，建议用 --active 降级分流"
}
```

令牌传法二选一：`curl -H 'X-Admin-Token: <token>' ...` 或 `?token=<token>`。

## A/B 实验的正确性

两个容易做错、这里已处理的点：

1. **粘性归因**：变体写入 `aj_var` cookie（`HttpOnly`，90 天）。同一访客多次访问
   必须命中同一变体，否则一个人的访问会散落到多个变体，M1 的按变体归因不可信。
   测试 `test_cookie_is_sticky` 与 `test_degraded_variant_cookie_is_reassigned` 守住。
2. **重复订阅不计数**：同一邮箱重复提交返回成功但不新增行——M1 统计的是唯一
   订阅人数，重复提交不应抬高计数。

## 尚未实现（有意为之）

- **无邮件投递**：验证期只收订阅不发送。投递接入 ESP 后须按
  `validation-metrics.md`「数据归属与存储」每周导出回灌。
- **无 `confirmed_at` 双重确认**：字段已建，当前恒为空。
- **无用户系统**：任务 14 明确禁止引入。
- **无 HTTPS / 生产部署**：`http.server` 面向验证期单机部署。公网暴露前需置于
  反向代理之后。