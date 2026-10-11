# social_posts.csv —— 社媒内容互动记录

**权威来源**：创始人手工记录（Reddit / X / GitHub / Discord 等渠道的推广内容）

**供计算指标**：M2（社交媒体互动率）

**产出任务**：创始人手工记录，无对应 A 轨自动化任务

## 表头

```
platform,post_url,published_at,impressions,likes,comments,shares
```

模板文件：[templates/social_posts.csv](templates/social_posts.csv)

## 字段定义

| 字段 | 类型 | 必填 | 取值 | 说明 |
|---|---|---|---|---|
| `platform` | text | ✅ | 自由文本 | `reddit` / `x` / `github` / `discord` 等 |
| `post_url` | text | ✅ | URL | 帖子链接，用于核对与去重 |
| `published_at` | date | ✅ | ISO 8601 | 发布时间 |
| `impressions` | int | ✅ | ≥ 0 | 曝光/浏览量 |
| `likes` | int | ✅ | ≥ 0 | 点赞数 |
| `comments` | int | ✅ | ≥ 0 | 评论数 |
| `shares` | int | ✅ | ≥ 0 | 分享/转发数 |

## 指标口径

```
单条互动率 = (likes + comments + shares) / impressions
M2 = 各条互动率的算术平均
```

阈值不变：通过值 ≥ 3%，理想值 ≥ 8%，失败值 < 1%。

## 约束

- **`impressions = 0` 的帖子必须跳过**，并在输出中提示跳过条数。
  **不得按 0 计入均值**——否则会系统性低估互动率，把曝光未起量的内容
  误判为「零互动」。
- 四个计数字段均须为非负整数，负数会报错退出。
- 一条帖子一行。重复记录同一 `post_url` 会重复计入，应先去重。
- 记录范围应与 H1.2 的推广渠道一致，`platform` / `post_url` 须能对应到投放记录。

## 补记（2026-10-11）

本 schema 是 A1.2 实现后的补齐项。`validation-metrics.md`「数据归属与存储」原本就要求
社媒数据「按内容条目记录发布时间与互动数」，但该「手工记录表」从未被定义结构，
导致 M2 长期无数据源。现按该要求补齐为结构化 CSV。