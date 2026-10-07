# AgentJobs 设计文档 - 30 天市场验证

## 架构概述

AgentJobs 是一个专注于 AI Agent 开发者的求职平台，采用极简设计以快速验证市场需求。考虑到这是 30 天 Solo Founder 项目，我们将采用最小化的技术栈和架构。

**阶段说明**：30 天窗口仅覆盖市场验证，本文档描述的平台在验证通过后才启动开发（工期 3 周，见 `mvp-boundaries.md`「时间边界」阶段三）。

## 核心实体设计

> **范围提示**：本文档描述的是**验证通过后待建的平台**。开发触发条件与工期见 `mvp-boundaries.md`「时间边界」阶段三。唯一例外是 `subscribers` 表——它服务于第 1-4 周的验证期，须在验证期即上线。

### 1. User (用户)
- **Developer Profile** (开发者档案)
  - 基本信息：姓名、联系方式、位置
  - 技能标签：AI Agent 相关技术栈 (LangChain, AutoGen, BabyAGI, 等)
  - 经验级别：初级、中级、高级、专家
  - 作品集链接：GitHub, 个人网站, 发布的 Agent 项目
  - 求职意向：期望职位类型、地点偏好、薪酬范围

- **Company Profile** (公司档案)
  - 基本信息：公司名称、简介、行业、规模
  - Agent 专长：正在开发的 Agent 类型、使用的技术栈
  - 联系人信息：HR 或技术负责人信息

### 2. JobPosting (职位发布)
- **JobSpec** (核心)
  - 职位标题、描述
  - 必需技能标签：核心技术栈要求
  - 期望经验：年限 + Agent 项目经验
  - 工作类型：全职/兼职/合同工
  - 工作地点：远程/本地/混合
  - 薪酬范围：薪资区间
  - 公司 Agent 业务介绍：团队规模、项目类型

### 3. Application (申请)
- 开发者与职位的关联
- 申请状态：待处理、已查看、已邀请、已拒绝、已录用

## 功能模块设计

### 1. 用户管理系统
- **注册/登录**：基础身份验证
- **档案管理**：开发者和公司分别维护自己的档案

### 2. 职位管理系统
- **职位发布**：公司创建并管理职位
- **职位搜索**：开发者按技能、位置、薪资等条件搜索
- **智能匹配**：基于技能标签的推荐算法

### 3. 互动系统
- **申请/投递**：开发者申请职位（`applications`）
- **消息通信**：双方沟通渠道（`conversations` + `messages`）
- **双向评价**：申请结束后的双向评分（`reviews`，可裁剪）

### 4. 验证期数据系统
- **订阅采集**：着陆页邮件订阅（`subscribers`），支持 A/B 变体归因
- **结构化归档**：问卷、访谈、竞品数据的存储要求见 `validation-metrics.md`「数据归属与存储」

## 数据库设计 (简化版)

```sql
-- 用户表
users (
  id, type(enum: developer/company), email, password_hash, 
  created_at, updated_at
)

-- 开发者档案表  
developer_profiles (
  id, user_id, name, location, experience_level, 
  portfolio_url, linkedin_url, salary_expectation,
  desired_role_type,        -- 求职意向：期望职位类型
  preferred_location,       -- 求职意向：地点偏好
  is_open_to_work,          -- 是否 actively looking
  created_at, updated_at
)

-- 公司档案表
company_profiles (
  id, user_id, company_name, industry, size, 
  description, website, agent_specialization,
  created_at, updated_at
)

-- 技能标签表
skills (
  id, name, category(Agent_Frameworks, LLM_Models, etc.)
)

-- 开发者技能关联表
developer_skills (
  id, developer_profile_id, skill_id, proficiency_level
)

-- 职位表
job_postings (
  id, company_profile_id, title, description,
  location_type,            -- enum: remote/onsite/hybrid（唯一来源，不再另设 remote_friendly）
  employment_type,          -- enum: full_time/part_time/contract
  experience_required,      -- enum: junior/mid/senior/expert（对应 JobSpec「技术深度」）
  agent_type,               -- enum: multi_agent/workflow_automation/research_assistant/other
  team_size,                -- enum: startup/small_team/large_lab
  salary_min, salary_max, salary_currency,
  is_seed,                  -- 是否为冷启动 seeding 预置职位（见 risk-analysis.md 风险 4）
  status,                   -- enum: draft/active/closed
  created_at, updated_at
)

-- 职位技能要求表
job_required_skills (
  id, job_posting_id, skill_id, importance_level  -- enum: required(2)/preferred(1)，用于 coverage 计算
)

-- 申请表
applications (
  id, developer_profile_id, job_posting_id, status,
  -- enum: pending/viewed/invited/rejected/accepted
  cover_note,              -- 简历投递时的附言（沟通功能之一）
  match_coverage,          -- 投递时快照的技能覆盖率，用于效果分析
  applied_at, updated_at
)

-- 会话表（站内消息 / 沟通）
conversations (
  id, application_id,       -- 绑定申请，天然限定双方
  created_at, updated_at
)

-- 消息表
messages (
  id, conversation_id, sender_user_id,
  body,                     -- 纯文本，MVP 不做附件/富文本
  read_at,                  -- NULL 表示未读
  created_at
)

-- 双向评价表
reviews (
  id, application_id,
  reviewer_user_id,         -- 评价人
  reviewee_type,            -- enum: developer/company
  reviewee_id,
  rating,                   -- 1-5
  comment,
  created_at,
  UNIQUE (application_id, reviewer_user_id)  -- 同一申请每方仅评一次
)

-- 着陆页订阅表（验证期核心资产，权威存储）
subscribers (
  id, email, source_channel, ab_variant,
  -- ab_variant: 落地页 A/B 变体 A/B/C，见 risk-analysis.md 实验 1
  subscribed_at, confirmed_at, unsubscribed_at
)
```

### 字段对齐说明

**JobSpec 映射**：`requirements.md` 的 JobSpec 6+1 个维度与本表列的对应关系见 `requirements.md`「JobSpec 概念定义」表。

**修复记录**：
- 补齐 `agent_type`、`team_size`、`employment_type`——旧版 JobSpec 定义了这三个维度但表中缺失
- 删除 `remote_friendly`——与 `location_type` 语义重叠且矛盾（旧版两列并存：`location_type` 已是 remote/onsite/hybrid 三态，再存一个布尔"是否远程友好"会产生三态与布尔的映射歧义）
- `salary_range` 拆为 `salary_min` / `salary_max` / `salary_currency`——范围查询需要数值字段，字符串区间无法索引

**MVP 范围外但已建模**：`messages`、`reviews` 两表对应 `mvp-boundaries.md` 的「基础通信」与「双向评价」。`reviews` 为第一顺位可裁剪项，裁剪时连同其 API 一并移除。

## API 接口设计 (精简版)

### 认证相关
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### 开发者相关
- GET /api/profile/developer
- PUT /api/profile/developer
- GET /api/jobs/search (带过滤参数)

### 公司相关
- GET /api/profile/company
- PUT /api/profile/company
- POST /api/jobs
- GET /api/jobs/my-jobs

### 职位相关
- GET /api/jobs/:id
- GET /api/jobs (搜索，支持 ?skills=&agent_type=&location_type=&employment_type=&team_size=&salary_min=)
- POST /api/jobs (企业发布)
- PUT /api/jobs/:id (企业编辑)
- POST /api/jobs/:id/apply (开发者投递，body 含 cover_note；响应返回 match_coverage)
- GET /api/applications/my (开发者查看自己的申请)
- GET /api/jobs/:id/applications (企业查看收到的申请)

### 沟通相关（对应 conversations / messages 表）
- GET /api/applications/:id/conversations
- GET /api/conversations/:id/messages
- POST /api/conversations/:id/messages

> 裁剪降级路径：若站内消息被裁剪（`mvp-boundaries.md` 范围裁剪顺序第 2 项），本组接口移除，`applications.cover_note` + 预置沟通模板替代。

### 评价相关（对应 reviews 表，可裁剪）
- POST /api/applications/:id/review
- GET /api/developers/:id/reviews
- GET /api/companies/:id/reviews

### 验证期相关（对应 subscribers 表）
- POST /api/subscribers (着陆页订阅，body 含 email + ab_variant)
- GET /api/subscribers/export (CSV 导出，供 ESP 回灌与指标计算)

> `subscribers` 是验证期（M1 指标）的权威数据源，必须在第 1 周随着陆页一同上线，不可推迟到开发期。

## 前端页面设计（平台期，开发触发后）

### 开发者视角
1. **首页** - 职位推荐/搜索入口
2. **职位搜索页** - 搜索筛选器
3. **个人档案页** - 管理技能和求职意向
4. **申请跟踪页** - 查看申请状态

### 企业视角
1. **职位管理页** - 创建和管理职位
2. **申请管理页** - 查看收到的申请、进入沟通
3. **公司档案页** - 管理公司信息

### 验证期页面（第 1-4 周，仅需 2 个）

1. **着陆页** - 价值主张 + 订阅表单，3 变体 A/B（`risk-analysis.md` 实验 1）
2. **问卷页** - 投放问卷（M3/M4/M12 的题项载体）

> 旧版前端设计只列平台页面，漏掉了验证期真正需要的着陆页与问卷页，导致第 1-4 周无页面设计依据。现补齐。

## 技术选型建议 (最小化)

> **待定**：本节仍为"或"式候选（Node/Express 或 Python/FastAPI、React 或 Vue、Vercel 或 Netlify）。选型未决会阻塞开发期启动，需在**第 4 周判定通过后立即定档**，并在 `tasks.md` 阶段 4 中作为独立任务记录。此为已知缺口，本次一致性修复不强行替决策者选择。

### 后端
- Node.js + Express 或 Python + FastAPI
- PostgreSQL 作为主数据库
- Redis 用于缓存

### 前端
- React 或 Vue.js (单页应用)
- Tailwind CSS 或 Bootstrap 用于样式
- UI 语言 zh-CN 单语言，不引入 i18n 框架（与 `requirements.md` 语言边界一致）

### 部署
- Vercel/Netlify (前端)
- Railway/Render (后端)
- Supabase/PlanetScale (数据库)

## 验证策略

完整验证设计见 `validation-metrics.md`（指标与判定）与 `risk-analysis.md`（实验设计）。本节仅列手段：

1. **着陆页 A/B 测试** - 3 变体价值主张，转化率归因（`risk-analysis.md` 实验 1）
2. **用户访谈** - 半结构化提纲，S1/S2 样本
3. **问卷调查** - M3/M4/M12 题项载体
4. **竞品分析** - 结构化对比表，支撑 D1
5. **MVP 原型** - Figma 交互原型（可选，成本低）

## 安全考虑

### 验证期（第 1-4 周）
- 订阅者邮箱为 PII：加密存储、最小化留存、导出需鉴权
- 问卷与访谈记录含受访者身份信息：存储前脱敏

### 平台期（开发触发后）
- 基础身份验证和授权
- 输入验证和防注入
- 邮箱验证流程
- 敏感信息加密存储
- **消息与评价的滥用防护**：`messages` 与 `reviews` 涉及用户生成内容，需限流与举报入口
- **越权检查**：企业只能访问自己职位的申请与会话；开发者只能访问自己的申请

## 隐私政策要点

- 用户数据使用说明
- Cookie 和追踪政策（含 A/B 实验的 cookie 归因说明）
- 数据保留期限（订阅者数据在验证期结束后需明确保留或删除策略）
- 用户权利（删除、修改数据）
- **验证期专项**：受访者同意条款——访谈录音、问卷数据的采集用途与撤回权利，须在采集前明示