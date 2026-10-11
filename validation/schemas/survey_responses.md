# survey_responses.csv —— 调查问卷回收

**权威来源**：任务 16 [A1.3] 设计题项，任务 3 [H1.3] 投放回收

**供计算指标**：S3（问卷有效回复数）、M3（问卷完成率）、M4（强需求表达，问卷主口径）、M11（差异化需求）、M12（价值认同度）

**产出任务**：任务 3 [H1.3]（H 轨，创始人投放）+ 任务 16 [A1.3]（A 轨 `[文档]`，题项设计）

## 表头

```
respondent_id,submitted_at,source_channel,m4_answer,m12_answer,differentiation_needs,survey_started
```

模板文件：[templates/survey_responses.csv](templates/survey_responses.csv)

## 字段定义

| 字段 | 类型 | 必填 | 取值 | 说明 |
|---|---|---|---|---|
| `respondent_id` | text | ✅ | — | 受访者标识（建议用邮箱哈希，便于反垃圾去重） |
| `submitted_at` | date | ❌ | ISO 8601 | 提交时间。**空 = 未提交**（只开始未交卷），M3 的分子据此判定 |
| `source_channel` | text | ❌ | 自由文本 | 投放渠道，供渠道归因 |
| `m4_answer` | enum | ❌ | `very_needed` \| `somewhat_needed` \| `not_needed` \| `not_at_all` | **M4 题项** |
| `m12_answer` | enum | ❌ | `strongly_agree` \| `agree` \| `neutral` \| `disagree` \| `strongly_disagree` | **M12 题项**（5 分量表） |
| `differentiation_needs` | list | ❌ | `;` 分隔 | **M11 题项**：勾选的差异化功能诉求。**≥3 项者计入分子** |
| `survey_started` | bool | ✅ | `true`/`false` | 问卷开始即建行并置 `true`。**M3 的分母据此判定** |

## 埋点约定（M3 的前提）

M3 完成率要求**开始**与**提交**两处计数，因此：

- 用户点开问卷 → 立即写入一行，`survey_started = true`，`submitted_at` 留空
- 用户交卷 → 回填 `submitted_at`（以及 `m4_answer` / `m12_answer`）

若问卷工具（如 Google Forms）无法在开始时落行，则只能得到提交数，**M3 无法计算**——
这是任务 16 [A1.3] 必须支持开始埋点的原因。

## 指标口径

- **S3** = 行数（通过值 ≥ 100）
- **M3 问卷完成率** = `submitted_at` 非空行数 ÷ `survey_started == true` 行数（通过值 ≥ 70%）
- **M4** = `m4_answer == "very_needed"` 占比（通过值 ≥ 60%）——**这是 M4 的主口径**
- **M11** = `differentiation_needs` 项数 ≥ 3 行数 ÷ 有效作答行数（通过值 ≥ 70%）
- **M12** = `m12_answer ∈ {agree, strongly_agree}` 占比（通过值 ≥ 70%）

## M11 口径说明（2026-10-11 裁定）

M11 定义为「提出 3 项以上差异化需求的**用户**比例」，统计单元是**用户**。
此前该指标被归给 `competitors.csv`，但那是平台级数据（一行一平台），统计单元不匹配。
现改由本表的 `differentiation_needs` 列承载，来源是任务 16 [A1.3] 的问卷多选题。

- 问卷题目须为**多选、不限项**
- 选「其他」的自由文本**不计入** M11 计数（避免口径漂移），但应保留在导出中供任务 8 [H4.1] 参考
- **本任务是 `differentiation_needs` 的唯一产出方——漏做此题项将导致 M11 永久无数据源**

## 反垃圾

任务 3 [H1.3] 须执行：单邮箱限一次、剔除明显敷衍作答。已剔除的作答**不应写入本表**，
否则会污染分母与分子。