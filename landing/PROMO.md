# 推广手册 —— H1.2 着陆页引流

> **H 轨任务，创始人执行。** agent 不得代为投放，也不得代为勾选 `tasks.md` 任务 2。
> 着陆页代码已就绪（任务 14 [A1.1]），部署步骤见 `landing/DEPLOY.md`。
> **本手册的唯一目的**：让 `subscribers.source_channel` 填得准，让 M1 算得出。

**目标**（`validation-metrics.md` 判定阶梯）：
- **M1 首周 ≥ 50**（理想 100）
- **M1 次周累计 ≥ 100**（理想 200）
- **M2 社媒互动率 ≥ 3%**（理想 8%）

---

## ⚠️ 三条不能违反的规则

### 1. 每个渠道用**同一个链接**

**不要**为不同渠道做不同的落地页或不同的推广文案。落地页的变体由服务端随机分流，
你看到的 A/B/C 是随机的——**推广文案一旦按渠道定制，变体归因就废了**。

允许变的只有**分发方式**（在哪里发、发给谁）；不允许变的：
落地页 URL、推广文案里的价值主张表述、CTA 措辞。

> 反例：「给 Reddit 贴一段强调『不用再解释 Agent』的文案，给微信群贴一段强调『技能标签筛选』的文案」
> ——这会让渠道和变体两个因素纠缠在一起，M1 的按变体归因失去意义。

### 2. 渠道名必须选对

表单的「你从哪里了解到我们」下拉框**只有 8 个选项**，填的值直接进 `subscribers.source_channel`：

| 下拉框取值 | 什么时候选它 |
|---|---|
| `reddit` | 从 Reddit 的帖子/评论/私信来的 |
| `huggingface` | 从 Hugging Face 社区来的 |
| `github` | 从 GitHub 来的（issue、PR、Discussions、个人主页） |
| `x` | 从 X / Twitter 来的 |
| `discord` | 从 Discord 服务器来的 |
| `wechat` | 从微信群/公众号/中文 AI 社群来的 |
| `friend` | 朋友推荐、熟人转发 |
| `other` | 其他（**尽量别用**——用 `other` 等于放弃渠道归因） |

> **「我从搜索引擎看到的」算什么？** 归到最接近的来源渠道（`github` / `reddit` / `other`）。
> 搜索引擎流量在当前阶段量很小，不必单列。`other` 用得越多，M1 的渠道分析越没用。

### 3. 不要在访谈/问卷里塞着陆页链接

访谈与问卷是**另外两条数据线**。在那两个场景里推链接会：
- 污染 M1 的渠道归因（本来是 `friend` 的量变成 `github`）
- 让访谈对象带着「这是一次推广」的预期回答问题，污染 M4/M12

访谈与问卷里可以**口头提一句「我们做了个东西」**，但**不放链接**。

---

## 推广文案

三个渠道各一版。**三版的价值主张表述必须一致**（规则 1），只改语气和场景。

> 三个变体的实际文案（服务端随机分流，你无法控制访客看到哪个）：
> - **A 功能向**：「The job board for people who build AI Agents」
> - **B 痛点向**：「Stop explaining what an AI Agent is in every interview」
> - **C 供需向**：「Where AI Agent teams hire」
>
> 推广文案**不要**引用具体某个变体的话术，否则等于人为给变体加权，归因失真。
> 用一个**不指向任何变体**的中性开场。

### Reddit（r/LocalLLaMA、r/AI_Agents、r/LangChain）

> **Feedback wanted: are there enough agent-specific jobs?**
>
> I'm validating a job board focused on AI agent developers — before building anything,
> I want to know whether the problem is real. If you've applied for agent-ish roles
> recently: are you actually finding them, or are they buried in generic AI/ML listings?
>
> If so, I'd like your take (it also goes to the "what would actually be useful"
> question). No signup required to reply, and everything gets aggregated anonymously.
>
> Landing page if you want to follow along: `<URL>`

### GitHub（issue / Discussions / 个人 README 提及）

> ⚠️ **不要**在别人的 issue 下贴链接——会被当 spam，直接被无视甚至被封。
> 只在**你自己**的仓库、Discussions、或自己的推文里提。

> 「我在做 AI Agent 开发者求职方向的小项目，先放个着陆页收集需求：
> `<URL>`
> 主要想弄清楚一件事——现在大家找纯 Agent 岗位，实际体验如何。
> 如果你最近投过这类岗位，欢迎在 Discussions 里说说遇到的问题。」

### Discord / 微信群 / 中文 AI 社群

> 「**【调研 + 早期用户招募】AI Agent 开发者的求职现状**」
>
> 大家好，在做一个关于 AI Agent 开发者求职的小项目。
>
> 起因：不少人投 Agent 相关岗位时，职位藏在通用 AI/ML 岗位里，
> 技能标签对不上，面试还要从零解释 Agent 是什么。
>
> 我在验证这个问题到底有多普遍，所以做了个页面收集反馈：
> `<URL>`
>
> - 不是招聘，不卖任何东西
> - 订阅只是说一声「上线时通知我」，每封可一键退订
> - 结果只做汇总统计
>
> 如果你最近正好在投 Agent 岗，你的经历特别有价值 🙏」

### X / Twitter

> 「Agent 开发岗位现在到底好不好找？我在验证一个垂直方向的求职平台，先收集需求再决定做不做。
> 不是招聘，是求职体验调研。`<URL>`」

---

## 投放节奏（两周拿 M1 ≥ 100）

| 天 | 动作 | 触达量 |
|---|---|---|
| D1 | Reddit 3 个 sub + Discord 3 个服务器 + 微信 2 个群 | 300–500 人可见 |
| D2 | GitHub（自己的渠道）+ X 发帖 + 复投 D1 表现最好的 1 个渠道 | 200–300 |
| D3–D5 | 每日 2 个渠道 + 回应评论区提问（**互动率会影响 M2**） | 每日 200+ |
| D6–D7 | 汇总，看首周 M1 | — |
| D8–D14 | 按首周结果加码 2 个渠道 | — |

### 早期警报（`validation-metrics.md`「何时拉响早期警报」）

> **首周订阅 < 20（M1 未达标区间下沿）→ 立即换渠道，48 小时内重测。**

- 换的是**渠道**，不是文案、不是落地页、不是变体
- 48 小时内重测是为了确认「渠道不行」而不是「这个方向不行」
- 换渠道后**照旧选对应的下拉框选项**

### 另一个早期信号

> **前 5 个开发者访谈中 0 人表示强需求 → 暂停当前访谈渠道，改用开发者社群直接触达。**

这条是**访谈**的早期信号，与 M1 的渠道警告是两条独立的线。

---

## 每日 5 分钟的检查

```bash
# M1 实时计数（按变体分列）
curl -s -H 'X-Admin-Token: <TOKEN>' https://<URL>/api/stats | python3 -m json.tool
```

看三件事：

1. **`m1_total_subscribers`** —— 累计订阅数，对照首周 50 的目标
2. **各变体的 `visits` 与 `subscribers`** —— 哪个变体转化更好
3. **`under_sampled` / `degrade_suggestion`** —— 某变体访问数 < 100 时会提示降级分流

### 什么时候降级分流

`variants.json` 的 `min_visits_before_degrade` 是 100：**单变体访问数不足 100 时**，
建议关掉一个变体，只跑两个（分流更集中，统计更快出结论）。

降级操作：编辑 `variants.json` 的 `active` 数组 → 重启服务。
（或启动时加 `--active A,B`）

> ⚠️ **降级会影响 A/B 结论的可比性**——降级前后的数据不是同一实验。
> 若已经跑了 3 个变体，降级意味着放弃「三变体对比」这个结论，只能用剩余两变体的数据。
> **先跑够样本再降级。** 30 天窗口很紧，但为了一个更快的结论放弃实验完整性不划算。

---

## M2（社媒互动率）的数据录入

社媒帖子的曝光与互动数**不自动进系统**，需要手工记进 `social_posts.csv`：

```
platform,post_url,published_at,impressions,likes,comments,shares
```

- **每天**记一次（曝光数会变）
- **只记自己发的、跟 AI Agent 招聘/求职相关的内容**
- `impressions` 是平台显示的曝光数（Reddit 是 views，X 是 impressions）
- `impressions = 0` 的帖子会被脚本跳过并提示——**不要填 0 凑数**，那会系统性低估互动率

每周跑一次指标脚本核对：

```bash
curl -s -H 'X-Admin-Token: <TOKEN>' https://<URL>/api/subscribers/export \
  -o validation/data/subscribers.csv
python3 validation/compute_metrics.py --data-dir validation/data
```

---

## 每周必做（`validation-metrics.md`「数据归属与存储」）

> **第三方 ESP 不得作为唯一副本**。若接入了 Mailchimp 等邮件服务，
> **每周导出回灌** `subscribers` 表（含退订名单回灌：`unsubscribed_at`）。

```bash
# 1. 从线上导出（权威副本）
curl -s -H 'X-Admin-Token: <TOKEN>' \
  https://<URL>/api/subscribers/export \
  -o validation/data/subscribers.csv

# 2. 若有 ESP，把 ESP 的退订名单回灌到线上 subscribers 表的 unsubscribed_at

# 3. 跑指标脚本，确认 M1 / M2 数值合理
python3 validation/compute_metrics.py --data-dir validation/data
```

> `validation/data/` 已在 `.gitignore` 中——订阅者邮箱是 PII，不入版本控制。

---

## 一个绕不开的问题：竞品已经存在

> **2026-10-25 补记。**任务 18 [A3.1] 的检索确认：`agenticcareers.co`（2,962 岗位 / 890 家公司）
> 和 `agenticengineeringjobs.com`（200 岗位）**已经在做同样的事**，
> 且 `agentjobs.com` 这个域名已被一个同名招聘板占用。

**这对推广的直接含义**：

1. **推广文案里不要自称「唯一」或「第一个」**——事实核查会失败，
   在技术社区里被抓到现形的代价远大于收益。
2. **如果访客在评论区问「agenticcareers 不是已经有了吗」**，这是**极有价值的数据**。
   把这类评论**逐条记下来**——它直接关系到 D1（差异化功能点）是否成立。
3. **品牌名与域名冲突**必须在正式推广前解决。推广一旦铺开再改名，
   积累的流量与口碑会全部作废。
   建议：先用 `landing/` 在现域名下做流量与需求验证，
   **等验证有结论后再定名**——这正是「验证期」的意义。

---

## 投放记录表（手工维护，每周更新）

| 日期 | 渠道 | 发布位置 | 链接 | 曝光/触达 | 订阅数 | 备注 |
|---|---|---|---|---|---|---|
| | | | | | | |

> 这张表是 `subscribers.source_channel` 的人工对照表。
> 线上导出有 3 个来源但说不清是哪个帖子带来的，就靠这张表反查。
