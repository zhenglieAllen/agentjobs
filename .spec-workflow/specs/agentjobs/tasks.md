# AgentJobs 任务分解 - 30 天市场验证

> **时间线对齐**：本文件阶段 1-5 对应第 1-4 周验证期 + 第 5 周决策 Gate，与 `mvp-boundaries.md`「时间边界」、`validation-metrics.md` Week 1-4 一致。**平台开发不在本文件内**，其任务分解在验证通过后另行编写。

## ⚠️ 执行轨道说明（必读）

任务分两类，**执行方式与工具完全不同**：

| 轨道 | 标记 | 任务性质 | 可否由 coding agent 执行 |
|---|---|---|---|
| **人工轨** | 🔴 | 真实世界人类互动：发消息、约访谈、做访谈、发问卷、联系企业 | ❌ **不可** |
| **agent 轨** | 🟢 | 代码/文档/页面产出：着陆页实现、问卷题项设计、竞品资料收集、文档更新 | ✅ 可 |

**`log-implementation` 工具仅适用于 agent 轨**。该工具要求填写 `apiEndpoints` / `components` / `functions` / `classes` / `integrations` 五个 artifact 字段，对人工轨任务（如"发 10 封邮件约访谈"）全部为空——强行调用只会产出空日志与虚假完成标记。

**人工轨任务的完成标准**：由创始人手动勾选，并附证据链接（录音转写、问卷导出、邮件记录）。**禁止 agent 自动勾选人工轨任务。**

**任务详情中未提供 Prompt 块的任务**（阶段 3.3、阶段 4.2-4.4、阶段 5 全部）属人工轨或待补充，需人工执行或补写 Prompt 后再自动化。

## 任务清单

### 阶段 1: 产品验证准备（第 1 周）
- [x] 创建产品定义文档（requirements.md）
- [x] 创建设计文档（design.md）
- [x] 制定任务分解文档（本文件）
- [x] 确定验证指标和方法（validation-metrics.md）
- [x] 风险台账与缓解策略（risk-analysis.md）
- [x] MVP 边界定义（mvp-boundaries.md）
- [ ] **确定技术选型** 🟢 — design.md 技术选型仍为"或"式候选，将阻塞开发期启动

### 阶段 2: 市场验证（第 1-2 周）
- [ ] 识别并联系 10 名 AI Agent 开发者进行访谈 🔴
- [ ] 识别并联系 5 家招聘 AI Agent 开发者的公司进行访谈 🔴
- [ ] 创建着陆页收集兴趣表达 🟢（含 3 变体 A/B）
- [ ] 在相关社区发布调查问卷 🟢（设计题项）
- [ ] **问卷投放与回收** 🔴 — 依赖陌生人填写，agent 只能产出问卷本体
- [ ] **企业职位 seeding 谈判** 🔴 — 要求 M8 承诺企业提供具体职位内容

### 阶段 3: 竞品分析（第 3 周）
- [ ] 分析现有求职平台对 AI/ML 岗位的支持情况 🔴（需实际使用平台）
- [ ] 评估技术岗位专用求职平台的适用性 🔴
- [ ] 调研是否有专门针对 AI Agent 的求职服务 🟢（公开资料检索）
- [ ] 总结竞品优缺点及差异化机会 🔴（需综合判断 D1）
- [ ] **输出结构化对比表** 🟢 — D1 统计依赖结构化数据，见 `validation-metrics.md`「数据归属与存储」

### 阶段 4: 需求细化（第 4 周）
- [ ] 基于访谈结果更新产品定义 🔴（需人工综合）
- [ ] 确定 MVP 最小功能集 🔴
- [ ] 制定用户故事(User Stories) 🟢
- [ ] 估算开发时间和资源 🟢

### 阶段 5: 决策 Gate（第 5 周）
- [ ] 汇总全部验证数据，对照判定阶梯逐项打分 🔴
- [ ] 评估技术和法律可行性 🟢
- [ ] 分析运营成本和盈利模式 🔴
- [ ] 制定风险缓解策略 🔴
- [ ] **做出项目方向决策** 🔴 — 通过 / 未达标 / 失败

> 旧版阶段 5 为"可行性评估"，但真正的 Go/No-Go 判定在 `validation-metrics.md`。现明确阶段 5 即决策 Gate，判定规则不独立定义。

## 任务详情

### 任务 2.1: 识别并联系 10 名 AI Agent 开发者进行访谈 🔴 人工轨

**执行方式**：创始人手动执行。agent 不可代为发消息或约访谈。

**交付物**：
- 10 份访谈转写文本
- 10 行结构化摘要（字段：技能标签 / 求职状态 / 痛点 / 需求 / 是否强需求）——供 M4、M5 直接聚合，见 `validation-metrics.md`「数据归属与存储」

**Success**：S1 ≥ 10（理想 15），M4 ≥ 60%（理想 80%），M5 ≥ 70%

**禁止**：调用 `log-implementation`（五个 artifact 字段对本任务全为空）

---

### 任务 2.2: 识别并联系 5 家招聘 AI Agent 开发者的公司进行访谈 🔴 人工轨

**执行方式**：创始人手动执行。

**交付物**：
- 5 份访谈转写文本
- 5 行结构化摘要（字段：Agent 项目 / 招聘挑战 / 技能要求 / 预算 / 是否承诺发布 / 招聘难度评分）——供 M6–M9 聚合

**Success**：S2 ≥ 5（理想 8），M6 ≥ 40%（理想 70%），M8 ≥ 20%（理想 40%），M9 ≥ 60%

**禁止**：调用 `log-implementation`

---

### 任务 2.3: 创建着陆页收集兴趣表达 🟢 agent 轨

_Prompt:
Implement the task for spec agentjobs, first run spec-workflow-guide to get the workflow guide then implement the task:

Role: 产品验证专家，专注于MVP着陆页设计和部署
Task: 创建一个简单的着陆页，介绍AgentJobs的概念，并收集访问者的邮箱作为兴趣指标
Restrictions: 不要创建复杂的功能，只专注于价值主张和邮箱收集；避免复杂的开发
_Leverage: 使用静态站点生成器(如VitePress)、托管服务(Vercel/Netlify)、邮箱服务(Mailchimp/Firebase)
_Requirements:
  - 部署可访问的着陆页，包含清晰的价值主张和邮箱收集表单
  - **必须实现 3 个价值主张变体（A/B/C）的随机分流**，变体定义见 risk-analysis.md 实验 1
  - **订阅数据写入自建 subscribers 表**（API: POST /api/subscribers），不得仅存第三方 ESP
  - 订阅表单需记录 source_channel 与 ab_variant 两个字段
  - 隐私声明需说明 A/B 归因的 cookie 使用
Success: 着陆页上线；变体归因可验证；首周订阅 ≥ 50（M1 通过值，理想 100）
After completing this task, record implementation details with log-implementation tool, then mark this task as complete in tasks.md
_

> **补充说明**：旧版此任务仅要求"部署着陆页 + 收集邮箱"，但 (a) 无 A/B 变体，而 `mvp-boundaries.md` 把 A/B 列为验证期功能；(b) 未指定数据存储，导致 M1 无法按变体归因。现已在 Requirements 中补齐。若采用纯静态页 + 第三方 ESP，则 A/B 实验无法执行——必须先有 `subscribers` 表。

---

### 任务 2.4: 设计并投放调查问卷 🟢 问卷设计 / 🔴 投放

_Prompt:
Implement the task for spec agentjobs, first run spec-workflow-guide to get the workflow guide then implement the task:

Role: 产品验证专家，专注于大规模用户调研
Task: 设计一份关于AI Agent开发者求职需求的调查问卷，含可导出结构化结果的字段设计
Restrictions: 问卷长度控制在5分钟内完成；避免引导性问题，保持客观
_Leverage: 利用Google Forms、SurveyMonkey等免费工具
_Requirements:
  - 设计涵盖技能分布、求职行为、平台偏好、痛点识别的问卷
  - **必须包含 M4 题项**：以单选呈现"你需要一个专门面向 AI Agent 开发者的求职平台吗"，选项为 非常需要/比较需要/不太需要/完全不需要。M4 = 选"非常需要"的比例
  - **必须包含 M12 题项**：对 AgentJobs 价值主张的认同度
  - **必须包含 M3 计量**：问卷开始与提交的埋点或计数，用于计算完成率
  - 导出字段须含 submitted_at 与来源渠道，供去重与渠道归因
  - 设置反垃圾机制（见 validation-metrics.md 数据质量保证）
Success: 问卷上线；题项可聚合出 M3/M4/M12；S3 ≥ 100（理想 200）
After completing this task, record implementation details with log-implementation tool, then mark this task as complete in tasks.md
_

> **轨道拆分**：agent 可完成问卷**设计**（本 Prompt）；**投放与回收**为人工轨——依赖社区发帖、熟人转发等真实渠道，且回收量 S3 ≥ 100 不由 agent 控制。
>
> **指标缺口修复**：旧版任务与 `risk-analysis.md` 实验 3 假设"70% 受访者评分 7 分以上（10 分制）"，但问卷中无此题项，该假设不可测量。现改用 M4 并明确要求加入题项。

---

### 任务 2.5: 企业职位 seeding 谈判 🔴 人工轨（新增）

**背景**：`risk-analysis.md` 风险 4（双边市场冷启动）指出，平台若以空职位集上线则第一印象即失败。M8 的口头承诺不构成供给。

**执行方式**：在任务 2.2 的企业访谈中同步谈判，要求承诺企业提供**具体可发布的职位内容**（职位名、描述、必需技能）。

**交付物**：≥ 1 家企业的具体职位内容草稿

**Success**：`requirements.md` 验证期验收标准第 8 项达成（seeding 就绪）

**禁止**：调用 `log-implementation`

---

### 任务 3.1: 分析现有求职平台对 AI/ML 岗位的支持情况 🔴 人工轨

**执行方式**：需真实注册并使用各平台搜索 Agent 相关职位，记录体验与限制。agent 无法代替。

**交付物**：3-5 个平台的结构化对比行（字段：平台 / Agent 职位搜索结果数 / 是否支持技能标签筛选 / 体验问题），供 M10、M11 聚合

**Success**：完成 3-5 个平台分析，明确现有平台在 Agent 技能标签支持上的不足

**禁止**：调用 `log-implementation`

---

### 任务 3.2: 评估技术岗位专用求职平台的适用性 🔴 人工轨

**执行方式**：同 3.1，需实际使用。

**交付物**：≥ 5 个技术求职平台的结构化对比行

**Success**：完成对比报告，明确 AgentJobs 差异化定位

**禁止**：调用 `log-implementation`

---

### 任务 3.4: 输出结构化竞品对比表 🟢 agent 轨（新增）

**执行方式**：agent 将 3.1/3.2 的人工记录整理为结构化表。

_Requirements:
  - 每平台一行，字段固定：平台名 / 覆盖岗位类型 / Agent 职位可得性 / 技能标签支持 / 差异化能力 / 证据链接
  - 从该表可归纳出 D1（差异化功能点候选）
Success: 结构化表可导出；D1 可据此统计
_

---

### 任务 4.1: 基于访谈结果更新产品定义 🔴 人工轨

**执行方式**：需人工综合访谈与问卷数据并做产品判断。agent 可起草，但结论须由创始人确认。

**交付物**：更新后的 requirements.md（用户定义、功能范围、验收标准）

**Success**：形成经真实用户反馈校准的产品定义

**禁止**：agent 自动勾选完成——需创始人确认后手动勾选

---

### 未提供 Prompt 的任务（需人工执行或补写 Prompt）

以下任务在旧版中无 Prompt 块，无法自动化：

| 任务 | 轨道 | 说明 |
|---|---|---|
| 2.4 问卷投放 | 🔴 | agent 只能产出问卷本体 |
| 阶段 3.3 调研是否有专门针对 AI Agent 的求职服务 | 🟢 | 可补写 Prompt 做公开资料检索 |
| 阶段 4.2 确定 MVP 最小功能集 | 🔴 | 需人工裁剪决策 |
| 阶段 4.3 制定用户故事 | 🟢 | 可补写 Prompt |
| 阶段 4.4 估算开发时间和资源 | 🟢 | 可补写 Prompt |
| 阶段 5.1 汇总数据打分 | 🔴 | 需人工判读 |
| 阶段 5.3 分析运营成本和盈利模式 | 🔴 | 需人工判断 |
| 阶段 5.4 制定风险缓解策略 | 🔴 | 需人工判断 |
| 阶段 5.5 做出方向决策 | 🔴 | **创始人专属，不可委托** |
