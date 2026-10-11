# interviews.csv —— 开发者深度访谈结构化摘要

**权威来源**：任务 1 [H1.1]（创始人执行，H 轨）

**供计算指标**：S1（开发者访谈数）、M4（强需求表达，访谈口径交叉校验）、M5（痛点认同度）

**产出任务**：任务 1 [H1.1] —— 创始人。agent **不得**代为标记本文件的数据完成状态。

## 表头

```
respondent_id,skill_tags,job_search_status,pain_points,needs,strong_need,interview_date,channel
```

模板文件：[templates/interviews.csv](templates/interviews.csv)

## 字段定义

| 字段 | 类型 | 必填 | 取值 | 说明 |
|---|---|---|---|---|
| `respondent_id` | text | ✅ | — | 受访者匿名标识（如 `dev-001`），不记录真实姓名 |
| `skill_tags` | list | ✅ | `;` 分隔 | 如 `LangChain;AutoGen;Python` |
| `job_search_status` | text | ✅ | 自由文本 | 如 `actively_looking` / `passive` / `employed` |
| `pain_points` | list | ✅ | `;` 分隔 | 认同的核心痛点。**M5 数 ≥3 个者计入分子** |
| `needs` | list | ✅ | `;` 分隔 | 表达的功能需求 |
| `strong_need` | bool | ✅ | `true`/`false` | 是否表达强需求。M4 访谈口径的分子 |
| `interview_date` | date | ✅ | ISO 8601 | 访谈日期 |
| `channel` | text | ✅ | 自由文本 | 触达渠道（GitHub / Reddit / 中文社群等） |

## 约束

- 多值字段一律用 **英文分号 `;`** 分隔（不要用中文分号，脚本不识别）。
- `strong_need` 接受 `true/false`、`1/0`、`yes/no`、`是/否`，其余值报错。
- 一份访谈一行。转写文本路径不入表，另行归档。
- 半结构化提纲须确保回答可归类到 M4 / M5，否则该行无法聚合。

## 指标口径

- **S1** = 行数（通过值 ≥ 10）
- **M5 痛点认同度** = `pain_points` 项数 ≥ 3 的行数 ÷ 总行数
- **M4 访谈口径** = `strong_need == true` 的行数 ÷ 总行数

> **M4 双口径提示**：判定阶梯中 M4 只有一条，定义口径为问卷「非常需要」比例（见
> `survey_responses.md`）。本表提供的是**访谈交叉校验口径**。问卷有有效作答时，脚本以问卷为准，
> 访谈口径仅在输出中作为参考列出。