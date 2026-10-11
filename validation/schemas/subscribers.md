# subscribers.csv —— 着陆页邮件订阅

**权威来源**：任务 14 [A1.1] 着陆页实现的 `subscribers` 表（见 `design.md` 第 151 行）

**供计算指标**：M1（着陆页邮件订阅）

**产出任务**：任务 14 [A1.1]（A 轨 `[代码]`）

## 表头

```
email,source_channel,ab_variant,subscribed_at,confirmed_at,unsubscribed_at
```

模板文件：[templates/subscribers.csv](templates/subscribers.csv)

## 字段定义

| 字段 | 类型 | 必填 | 取值 | 说明 |
|---|---|---|---|---|
| `email` | text | ✅ | — | 订阅邮箱 |
| `source_channel` | text | ✅ | 自由文本 | 推广渠道，须与投放记录逐条对应（H1.2 负责逐条记录） |
| `ab_variant` | enum | ✅ | `A` \| `B` \| `C` | 落地页价值主张变体，见 `risk-analysis.md` 实验 1 |
| `subscribed_at` | date | ✅ | ISO 8601 | 订阅时间。M1 首周/次周累计按此字段切窗 |
| `confirmed_at` | date | ❌ | ISO 8601 | 双重确认时间，空表示未确认 |
| `unsubscribed_at` | date | ❌ | ISO 8601 | 退订时间，空表示未退订 |

## 约束

- `ab_variant` 只接受 `A`/`B`/`C`，其他值会触发脚本报错。实验 1 降级为 A/B 两变体时，留空或填 `A`/`B` 均可，**不得填 `C` 以外的自定义值**。
- 时间须为 ISO 8601（如 `2026-10-07T14:30:00+08:00` 或 `2026-10-07`）。
- ESP（Mailchimp 等）**不得作为唯一副本**，每周须导出回灌本表，见 `validation-metrics.md`「数据归属与存储」。

## M1 口径

- **M1 首周** = `subscribed_at` 落在验证窗口第 1–7 天的记录数
- **M1 次周累计** = `subscribed_at` 落在验证窗口第 1–14 天的记录数

窗口起点默认取最早的 `subscribed_at` 日期，可用 `--window-start YYYY-MM-DD` 显式指定。