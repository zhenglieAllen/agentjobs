# 问卷投放方案 —— H1.3

> **H 轨任务，创始人执行。** agent 不得代为投放或代为勾选 `tasks.md` 任务 3。
> 题项本身已完成（任务 16 [A1.3]），见 `survey/survey-instrument.md` 与 `survey/questions.json`。
> 本文件只讲**怎么投放、怎么保证数据可聚合、怎么不白做**。

**目标**：S3 ≥ 100 份有效回复（理想 200）。

---

## ⚠️ 投放前必做的一件事：确认 M3 能被计算

**这是唯一一件不做就会让整批数据白跑的事。**

M3（问卷完成率）的口径是：

```
M3 = submitted_at 非空的行数 ÷ survey_started == true 的行数
```

也就是说，数据里必须**同时有**「开始但没交卷」和「已交卷」两类记录。

### 为什么这件事会踩坑

> **Google Forms 默认只在提交后产生响应行。** 直接用它投放，
> `survey_started` 会恒为 0，M3 **完全不可计算**——
> 脚本会报「无数据源」，而这看起来像是「没人填问卷」，其实是工具选错了。

### 投放前的 5 分钟检查

在问卷工具里发一条**测试问卷**给自己，然后：

1. 打开问卷但**不提交**，直接关掉页面
2. 到导出数据里看：**这一行在不在？**
   - **在，且某列能区分「未提交」** → ✅ 直接用，把那列映射到 `survey_started=true` + `submitted_at` 留空
   - **不在** → ⚠️ 换工具，或启用「部分作答 / partial responses / 保存进度」功能

### 各工具的对应做法

| 工具 | 开始埋点 | 说明 |
|---|---|---|
| **问卷星** | ✅ 统计里有「答题开始」计数 | 中文用户多、题型全、支持选项乱序。**推荐**（目标用户大量在中文社群） |
| **金数据** | ✅ 有开始/提交计数 | 同上，备选 |
| **Qualtrics** | ✅ Partial Responses | 需在设置里开启并开启记录 |
| **Typeform** | ✅ Partial Responses | 需开启；中文题型支持较弱 |
| **Google Forms** | ❌ 无 | **不要用**，除非另有埋点方案 |
| **自建表单页** | ✅ 可完全控制 | 成本高，验证期不划算 |

> **选问卷工具时优先看三件事**：① 有没有开始/提交双计数；② 能否导出未提交行；
> ③ **选项能否随机化**（`questions.json` 的 `randomize_all_options: true` 是抑制顺序偏差的要求）。
> 中文用户还会额外在意：**手机端体验**（开发者群体大量用手机填）。

### 如果最终确实拿不到开始埋点

**正确做法**：把 M3 标为「不可计算（工具限制）」，在第 5 周打分时显式说明，
**不要**用别的数字替代（例如用「打开问卷页面的 UV ÷ 提交数」凑一个数）——
那会让 M3 变成一个口径不清的伪指标，比没有更糟。

M3 未达标与 M3 不可计算在判定阶梯里是不同的东西：前者是信号，后者是工具缺陷。

---

## 投放渠道

问卷的 `source_channel` 字段（自由文本）与着陆页的 `subscribers.source_channel`
**是两套独立的归因**，不要混填。建议问卷侧用这套取值：

| 取值 | 渠道 | 预计有效回复 |
|---|---|---|
| `github` | GitHub Discussions / issue 评论区 | 15–25 |
| `huggingface` | Hugging Face 社区讨论区 | 10–20 |
| `reddit` | Reddit r/LocalLLaMA / r/AI_Agents | 10–20 |
| `x` | X / Twitter | 10–20 |
| `discord` | Discord 中文 AI 服务器 | 15–25 |
| `wechat` | 微信 / 中文 AI 社群 | 20–30 |
| `zhihu` | 知乎 / V2EX / 掘金 | 10–20 |
| `other` | 其他 | — |

**目标合计 ≥ 100 → 触达量需约 400–600 人次**（按 20–25% 打开并提交估算）。

### 渠道优先级（按性价比排）

1. **中文社群（Discord / 微信）** —— 开发者密度最高，AI 社群里的开发者愿意聊技术
2. **GitHub** —— 触达精准，但需要**逐个私聊**（在 issue 下公开贴链接会被当成 spam）
3. **Hugging Face / Reddit** —— 英文渠道，AI Agent 密度最高，但语言门槛筛掉一部分人
4. **知乎 / V2EX** —— 泛 AI 开发者，Agent 纯度较低，但量能补

### UTM 标记

每个渠道用**独立链接**，把渠道带进 `source_channel`：

```
https://<问卷链接>?utm_source=github&utm_medium=survey&utm_campaign=2026-10
```

`utm_source` 的值就是 `source_channel` 的取值。问卷工具不支持 UTM 时，
在链接后手工带一个 `?ch=github`，导出后按此列回填。

---

## 投放文案

> 三个渠道各一版。**每版都强调「3–5 分钟」「不做推销」「结果不公开」**——
> 这三点显著提高开发者社区的回应率，尤其是 Reddit 和 GitHub。

### GitHub Discussions / issue 回复

> 调研招募（不是招聘）：我在做一份关于 **AI Agent 开发者求职**的问卷，3–5 分钟。
> 目的只有一个——搞清楚大家找工作时真正卡在哪，所以我能决定这个方向还值不值得做。
> 没有对错，不推销任何东西，结果只做汇总统计，不会公开到个人。
> 问卷链接：`<带 utm 的链接>`

### Reddit（r/LocalLLaMA / r/AI_Agents）

> **Survey request — 3–5 min, no promo.** I'm researching how AI agent developers
> actually find jobs (or don't), and whether a dedicated job board is worth building.
> No selling, no recruiting, no lead-gen — the findings are aggregated and anonymous.
> If you've applied to agent-ish roles recently, I'd value your take even if you
> never use such platforms.
> Link: `<带 utm 的链接>`

> ⚠️ **Reddit 的社区规则很严**：不要重复发同一链接、不要标题党、不要在多个 subreddit
> 复制粘贴同一段话（Reddit 会判定为 spam 并封号）。每发一个 sub，用自己的话改写开头。

### 中文社群（Discord / 微信群 / 群公告）

> **【调研招募｜3-5 分钟】AI Agent 开发者的求职现状**
>
> 大家好，我在做一个关于「AI Agent 开发者找工作」的调研。
> 起因很简单：我发现很多人在找纯 Agent 岗位时被通用平台折腾，
> 想搞清楚这是不是普遍问题、值不值得专门做一个平台。
>
> - 3–5 分钟，14 道题，没有对错
> - 不推销、不招聘、不做产品推荐
> - 结果只做汇总统计，不会公开到个人
>
> 问卷：`<带 utm 的链接>`
>
> 如果你最近正好在投 Agent 相关岗位，你的经历对这个问题特别有价值，谢谢 🙏

---

## ⚠️ 一个新出现的测量风险：Q9 的选项可能已经过时

> **这一节是 2026-10-25 补记**，起因是任务 18 [A3.1] 的竞品检索结论。

问卷 Q9 问的是「**你希望求职平台提供哪些现有平台没有的功能？**」，
选项包含「Agent 技能标签筛选」「Agent 岗位专区」等。

但现在已确认：`agenticcareers.co`（2,962 岗位 / 890 家公司）与
`agenticengineeringjobs.com`（200 岗位）**已经提供**了技能标签筛选与 Agent 岗位专区。

**后果**：受访者如果用过这些竞品，可能会认为「技能标签筛选」不算「现有平台没有的功能」
而**不勾**——M11 会被系统性压低。**这不是受访者没需求，是参照系变了。**

**处理方式（不要改问卷）**：

1. **保持 Q9 措辞不动。**它测的是「受访者心中的现有平台」，改了就废了——
   改了之后的历史投放数据不可比，且 `survey/check_instrument.py` 会对措辞变更报错。
2. **在解读 M11 时必须结合竞品证据。**若 M11 落在未达标区间（< 70%），
   **不能直接判失败**，须先看：
   - 受访者中实际用过垂直竞品的比例是多少
   - 他们是否因为竞品已有该功能而不勾
3. **在问卷的收尾/访谈里追加一句**（不改题目，作为补充信息）：
   「你用过 agenticcareers.co 这类站点吗？它们有没有解决你的问题？」
   这条**不参与任何指标计算**，但会写入转写/备注，供任务 8 [H4.1] 解读 M11 时用。
4. **把这个张力记进任务 8 [H4.1] 的输入**——它是「产品定义更新」的重要输入：
   差异化点必须相对垂直竞品重新定义，不能再相对通用平台定义。

---

## 反垃圾（`survey_responses.md`「反垃圾」）

- **单邮箱限一次** —— 问卷工具本身开启该限制
- **异常作答人工抽查** —— 判废规则：
  - 完成时长 < 40 秒
  - 自相矛盾的组合（如 Q8 选「非常需要」但 Q7 勾「上述都不是我的问题」）
  - Q9 全选 + Q12 选「完全免费即可」这类无信息量组合
- **已剔除的作答不写入 `survey_responses.csv`** —— 写进去会污染 M3/M4/M11/M12 的分母与分子
- **`respondent_id` 用邮箱哈希**（便于去重，且不落明文邮箱）

> 剔除的作答**单独存一份**，不要删——万一判定阶梯的某项因剔除而掉档，
> 你需要能回溯「剔了哪些、为什么」。

---

## 每日节奏（两周内拿到 S3 ≥ 100）

| 天 | 动作 | 目标 |
|---|---|---|
| D1 | 5 个渠道各投一轮 + 3 个转介绍（访谈对象） | 15–20 份 |
| D2 | 检查 M3 埋点是否生效（见上）+ 追加 2 个渠道 | 累计 30 |
| D3–D7 | 每日 2 个渠道 + 跟进 D1 的转发 | 累计 80 |
| D8–D10 | 补投表现最好的 2 个渠道 | 累计 100+ |

**早期警报**（`validation-metrics.md`）：**问卷首日回收 < 20 份（S3 进度落后）
→ 检查问卷分发渠道，而不是调整问卷内容。**

> ⚠️ 不要因为回收慢就去改问卷题目。改题会让数据不可比，且
> `survey/check_instrument.py` 会因措辞/选项变更直接报错——这是刻意的护栏。

---

## 导出与回灌

投放结束后：

```bash
# 1. 从问卷工具导出 CSV
# 2. 按 survey_responses.csv 的表头映射列，填进 validation/data/survey_responses.csv
#    表头：respondent_id,submitted_at,source_channel,m4_answer,m12_answer,differentiation_needs,survey_started

# 3. 校验 + 跑指标
python3 validation/compute_metrics.py --data-dir validation/data
```

**映射规则**：

| CSV 列 | 来源 |
|---|---|
| `respondent_id` | 邮箱哈希，或工具的响应 ID |
| `submitted_at` | 提交时间（ISO 8601）；**未提交的留空** |
| `source_channel` | utm_source，或按投放记录回填 |
| `m4_answer` | Q8 的选项 value（`very_needed` / `somewhat_needed` / `not_needed` / `not_at_all`） |
| `m12_answer` | Q10 的选项 value（`strongly_agree` / `agree` / `neutral` / `disagree` / `strongly_disagree`） |
| `differentiation_needs` | Q9 的勾选项，**`;` 分隔**；「其他」自由文本不计入计数但保留 |
| `survey_started` | 全部行 `true`（只有开始的行才在表里） |

> `validation/data/` 已在 `.gitignore` 中——邮箱是 PII，不入版本控制。

**校验**：脚本会明确报出缺列、非法枚举值、非法日期格式。
**读不出数据 ≠ 没数据**——先排掉格式错误。
