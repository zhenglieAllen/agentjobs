# survey —— 开发者求职需求调查问卷

任务 **16 [A1.3]** 的产出（`[文档]` 子轨）。

**投放由任务 3 [H1.3] 执行**（H 轨，创始人）——本目录只负责题项设计。

## 快速开始

```bash
python3 survey/check_instrument.py       # 校验题项与 schema / 判定阶梯是否一致
python3 survey/check_instrument.py --json
python3 -m unittest discover -s survey/tests
```

## 文件

| 文件 | 用途 |
|---|---|
| `survey-instrument.md` | **人类可读版**，投放者照此录入问卷工具 |
| `questions.json` | **机器可读版**，校验器的输入 |
| `check_instrument.py` | 校验器 |
| `tests/test_instrument.py` | 17 项测试，全部是「故意破坏 → 必须报错」 |

两份内容必须同步；`test_questions_json_and_markdown_stay_in_sync` 会在 Markdown
漏掉题号时报错。

## 问卷规模

14 题，预计 3–5 分钟，zh-CN 单语言，全题选项随机化。

## 四项硬性题项

这三道题写错会导致对应指标**静默失效**，因此受校验器守护：

| 题 | 指标 | 绑定关系 |
|---|---|---|
| **Q8** | M4 强需求表达比例 | 选项措辞与判定阶梯绑定，**不得改动/增删**。M4 = 选「非常需要」的比例 |
| **Q9** | M11 差异化需求 | 多选不限项。**M11 的唯一数据源**，漏做即永久无数据源 |
| **Q10** | M12 价值认同度 | 5 分量表。M12 = 「同意」+「非常同意」的比例 |
| 埋点 | M3 问卷完成率 | 需「打开问卷即计数」+「交卷计数」两处埋点 |

另有 Q7 为 M5 的问卷侧旁证（M5 主数据源仍是访谈的 `interviews.csv`）。

## 校验器抓什么

```
$ python3 survey/check_instrument.py
问卷：AgentJobs 开发者求职需求调查
题量：14 题，预计 3-5 分钟
指标题：M4, M11, M12
M3 开始埋点：已配置
选项随机化：已开启

✓ 题项与 validation 的 schema、判定阶梯一致
```

改动 `questions.json` 后若破坏约束，会指名道姓地报出来：

| 破坏方式 | 报错 |
|---|---|
| 删掉 Q9 | `M11 的题项 Q9 已丢失` / `differentiation_needs：无题项产出` |
| Q9 改成单选 | `M11：题型必须是多选（single 无法产出列表）` |
| Q9 加了选项上限 | `M11：必须不限项（unlimited_choices=true）` |
| M4 分子改成「比较需要」 | `M4：分子选项的值应为 very_needed` |
| Q8 加一个新选项 | `m4_answer：出现 schema 未定义的取值 ['depends']（load_csv 会报错）` |
| 删掉 M3 开始埋点 | `M3：必须配置「打开问卷即计数」…M3 不可计算` |
| 关闭选项随机化 | `未开启选项随机化` |

## 与 validation 的契约

导出列名必须与 `validation/schemas/survey_responses.csv` 一致：

| 导出列 | 供计算 |
|---|---|
| `respondent_id` | 去重 |
| `submitted_at` | M3 分子（空 = 未提交） |
| `source_channel` | 渠道归因 |
| `m4_answer` | M4 |
| `m12_answer` | M12 |
| `differentiation_needs` | M11（`;` 分隔，不含「其他」自由文本） |
| `survey_started` | M3 分母 |

校验器直接读取 `compute_metrics.SCHEMAS` 作为真值来源——schema 改了，校验器跟着变。

## 投放前必读（交给任务 3 [H1.3]）

1. **确认问卷工具支持「打开即计数」。** Google Forms 默认在提交时才产生一行响应，
   直接用它投放会导致 `survey_started` 全部为 0 或缺失，**M3 完全无法计算**。
2. **选项随机化全部开启** —— 抑制顺序偏差。
3. **单邮箱限一次**，并配好反垃圾规则（见 `survey-instrument.md` 末节）。
4. **渠道参数带入 `source_channel`** —— 用 UTM 或隐藏字段，否则渠道归因失效。
5. **不要加题。** 题量越多完成率越低，M3 越难达标；当前 14 题已接近上限。

## 数据质量提示

`compute_metrics.py` 会在以下情况显式告警：已开始但未提交、却带有指标答案的记录。
这类半填数据会稀释 M4/M11/M12 的分母。若看到该告警，检查问卷工具的导出设置——
它应只在提交后才导出答案。