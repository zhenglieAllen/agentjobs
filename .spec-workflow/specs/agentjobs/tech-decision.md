# AgentJobs 技术选型决策 - 平台期开发

> **任务**：`tasks.md` 任务 17 [A1.4] 技术选型定档。
> **定位**：本文件是 `design.md`「技术选型建议」的**收敛结果**，取代该节的「或式」候选项。`design.md` 保留数据模型与 API 契约的设计决策，**技术栈选型以本文档为准**。
> **约束**：所有决策须与 `mvp-boundaries.md`「技术实现边界」一致，且不改变 `design.md` 已定稿的 12 张表结构与 API 路径。

## 决策摘要

| 决策点 | 结论 | 否决方案 |
|---|---|---|
| 后端语言/框架 | **Python 3.12 + FastAPI** | Node.js + Express |
| 后端数据层 | **SQLAlchemy 2.0 (ORM) + Alembic** | 原生 SQL / Tortoise ORM |
| 数据校验 | **Pydantic v2** | 手写校验函数 |
| 前端框架 | **React 19 + Vite + TypeScript** | Vue 3 |
| 样式方案 | **Tailwind CSS v4** | Bootstrap 5 |
| 数据库 | **Supabase Postgres（托管）** | PlanetScale (MySQL) |
| 缓存 | **不使用 Redis** | Upstash Redis |
| 前端部署 | **Vercel** | Netlify |
| 后端部署 | **Railway** | Render |
| 异步任务 | **Railway Worker（同一镜像，不同启动命令）** | 独立队列服务 |
| 验证期着陆页 | **保持 Python 标准库实现，不重写** | 改写为 FastAPI |

---

## 1. 后端：Python 3.12 + FastAPI

### 选择结论

后端采用 Python 3.12 + FastAPI，SQLAlchemy 2.0 作为 ORM，Alembic 管理迁移，Pydantic v2 做请求/响应校验。

### 选择理由

1. **与既有验证期资产同栈，schema 不会 drift。**
   本项目已有两个 Python 子系统：`validation/compute_metrics.py`（882 行指标计算，读 6 份 CSV schema）与 `landing/`（订阅采集）。平台期的 12 张表与这 6 份 CSV 是**同一批验证数据的两种形态**。若后端用 Node，则「CSV schema → 数据库模型」这层映射要跨语言手写两遍，任何字段增删都会在两处漂移。用 Python + Pydantic 可以让 CSV 列名直接成为 Pydantic 字段的**唯一来源**，校验规则也只有一份。

2. **FastAPI 自带 OpenAPI 文档，前端可自动生成类型客户端。**
   `design.md` 定义了 18 个 API 端点。FastAPI 自动产出 `/docs` 与 OpenAPI schema，前端用 `openapi-typescript` 就能生成 TS 类型，替代手写 API 客户端。这是 3 周工期里省下的确定工时。

3. **Pydantic v2 的枚举与字段约束与 `design.md` 的 schema 完全同构。**
   `design.md` 大量使用 enum：`users.type(developer/company)`、`job_postings.location_type(remote/onsite/hybrid)`、`employment_type`、`experience_required`、`agent_type`、`team_size`、`job_required_skills.importance_level(required/preferred)`、`applications.status`、`reviews.rating`。这些 enum 直接对应 Pydantic `Enum` 字段，配合 `design.md`「字段对齐说明」里的补齐记录，可一次性杜绝枚举值拼写不一致——这类错误在 Node + 手写校验下最容易漏。

4. **性能边界充裕。** `mvp-boundaries.md` 负载目标为 1000 用户 / 每天 100 次职位浏览，API 响应 < 1 秒。FastAPI 的单 worker 在该量级下有数量级的余量，无需异步框架的并发复杂度。

### 否决方案与否决理由

**Node.js + Express** —— 否决。

- 需要额外引入 ORM（Prisma 或 TypeORM）与 schema 校验（Zod），工具链不比 Python 少；而 Express 4 本身不带请求校验，校验要另配。
- 与 `validation/` 的跨语言胶水：CSV schema 的枚举/约束要在 Zod 与 Python 侧各写一遍，字段漂移风险实在存在。
- 唯一优势——前后端同语言、共享 TS 类型——在本项目规模（12 张表、18 个端点）下收益有限：FastAPI 的 OpenAPI 代码生成已覆盖跨语言类型的核心诉求。
- **重新考虑的条件**：若后续要在同仓内做实时通知（WebSocket）且团队构成转向 JS，可复议。MVP 阶段不成立。

---

## 2. 数据层：SQLAlchemy 2.0 + Alembic

### 选择结论

SQLAlchemy 2.0 的声明式 ORM（`Mapped[]` / `mapped_column()` 风格），Alembic 作为迁移工具。

### 选择理由

- `design.md` 的 12 张表里有 5 张关联表（`developer_skills`、`job_required_skills`、`applications`、`conversations`、`messages`、`reviews`），全部依赖外键与唯一约束（如 `reviews UNIQUE(application_id, reviewer_user_id)`）。手写 SQL 管理这套关系模型会产生大量样板代码，且约束容易漏。
- Alembic 让表结构变更可版本化、可回滚，`design.md` 的 `subscribers` 表在验证期与平台期之间会有字段调整（有迁移脚本比有 `CREATE TABLE IF NOT EXISTS` 安全）。

### 否决方案与否决理由

- **原生 SQL / 手写 migration**：样板代码量大，关联表维护成本高，否决。
- **Tortoise ORM**：生态与文档量明显少于 SQLAlchemy，3 周工期不值得为「更简洁」赌社区规模，否决。

---

## 3. 前端：React 19 + Vite + TypeScript

### 选择结论

React 19 + Vite + TypeScript，SPA，zh-CN 单语言 UI。

### 选择理由

1. **Vite 而非 CRA**：Create React App 已于 2025 年停止维护，官方推荐迁移到 Vite 或 Next.js。`mvp-boundaries.md` 要求「简单 React/Vue 组件」+「不使用复杂状态管理」，Vite 的零配置开发服务器与构建速度对 solo founder 友好，配置量接近于零。
2. **生态密度**：React + TypeScript + Supabase JS 客户端 + Vercel 部署的组合，在文档、社区与故障排查资源上最厚。3 周工期里遇到问题时能搜到答案，本身就是一种交付速度。
3. **状态管理保持简单**：符合「不使用复杂状态管理」的边界。**决策**：不引入 Redux/Zustand/React Query，用 React 内置 `useState` / `useContext` + 少量自定义 hook。数据获取用 `fetch` 薄封装（~30 行），不引 React Query。
4. **UI 边界**：React Router（路由必需）+ `react-hook-form`（表单复杂度低）。不引入组件库（Ant Design / MUI）——自绘 + Tailwind 已足够，避免组件库的默认样式与 Tailwind 打架。

### 否决方案与否决理由

**Vue 3** —— 否决。

- Vue 3 + Vite + Pinia 是完全可用的等价方案，Vue 的模板语法在表单密集场景下可读性确实更好。
- 否决理由是生态密度：React 在 Supabase 官方示例、Vercel 模板、招聘/社区资源上更厚。对 solo founder 而言，「出问题能搜到答案」比「写起来更顺手」的边际收益更大——后者可通过约束代码风格弥补，前者不能。
- **重新考虑的条件**：无。

### 附带决策：UI 语言

**zh-CN 单语言，不引入 i18n 框架**（与 `requirements.md`「语言支持」及 `mvp-boundaries.md`「用户管理边界」一致）。硬编码中文文案即可，**不引入 `react-i18next` 等任何 i18n 依赖**。职位描述等用户输入内容允许英文，无需特殊处理。

---

## 4. 样式：Tailwind CSS v4

### 选择结论

Tailwind CSS v4。

### 选择理由

- `mvp-boundaries.md` 前端边界要求「CSS 框架」且「不使用复杂状态管理、动画库、图表库」。Tailwind 满足且不越界。
- Tailwind v4 的 CSS-first 配置（`@theme` 令牌）让设计令牌的改动集中在单个 CSS 文件，不需 JS 配置文件。
- 与 `landing/static/styles.css`（手写 147 行）不冲突——验证期着陆页是**纯静态页**，不引入任何构建链，与平台期前端完全解耦。

### 否决方案与否决理由

**Bootstrap 5** —— 否决。

- Bootstrap 的价值在于「快速拼装后台管理界面」，其组件库（表格、模态框、栅格）与本站的职位卡片/技能标签匹配场景不匹配，多数组件最终都要覆盖样式。
- Tailwind 的 utility-first 模式在「同一套设计语言反复复用」的列表页上更省事——而列表页（职位搜索结果）是本站的核心页面。

---

## 5. 数据库：Supabase Postgres（托管）

### 选择结论

使用 **Supabase 托管的 PostgreSQL** 作为主数据库，**仅使用其托管 Postgres，不使用 Supabase Auth**。

### 选择理由

1. **数据模型是标准关系模型。** `design.md` 的 12 张表含大量外键与唯一约束，Postgres 是原生匹配。PlanetScale 是 MySQL，且其产品定位偏向「无外键的 scale-out」，与本项目「12 张表互相引用」的结构不匹配。
2. **免费额度覆盖 MVP 负载。** 1000 用户 / 每天 100 次职位浏览，远低于 Supabase 免费档上限，验证期与开发期零成本。
3. **Postgres 的全文检索（`tsvector`）未来可用于职位搜索**，属于「基础关键词/标签匹配」范围内，不越界到「智能匹配评分系统」。

### 关键决策：**自建认证，不使用 Supabase Auth**

`design.md` 的 `users` 表已定稿包含 `password_hash` 列，且 `users.type` 枚举为 `developer/company`。若改用 Supabase Auth，会出现第二套用户表与 RLS 策略，与 `design.md` 的 schema 冲突。

- **决策**：自建认证——`password_hash` 存 bcrypt 哈希，签发 JWT（HS256），服务端校验。数据库只当存储用。
- **理由**：`mvp-boundaries.md`「基础身份验证」的要求本就是自建可实现的；引入 Supabase Auth 需同时维护 `auth.users` 与 `public.users` 的映射，属于「复杂中间件」倾向，越过前端/后端边界。JWT + bcrypt 是这个规模下的最小充分方案。
- **代价**：需自行实现密码重置与邮箱验证流程。**接受**——`design.md`「安全考虑」已列出「邮箱验证流程」为平台期项，且 `mvp-boundaries.md` 排除「高级安全功能（2FA、审计日志）」，自建范围可控。

### 否决方案与否决理由

**PlanetScale (MySQL)** —— 否决，理由见上第 1 点：外键与多表关联的适配度不如 Postgres，且平台期无 scale-out 需求。

---

## 6. 缓存：**不使用 Redis**

### 选择结论

**不引入 Redis**，`design.md`「技术选型建议」中的 Redis 项予以否决。

### 取舍理由

- **收益**：缓存能省下的是重复的数据库查询。但本项目最热的查询是「技能标签匹配职位列表」与「我的申请列表」，数据量在 MVP 阶段是**百级职位 × 千级用户**，Postgres 加索引后的查询时间是毫秒级，远低于 `mvp-boundaries.md` 的「API 响应 < 1 秒」目标。
- **成本**：Redis 意味着多一个需要部署、监控、备份、故障排查的组件。在 3 周工期、solo founder 的条件下，每多一个外部依赖，交付风险就多一分。
- **替代方案**：
  - 技能标签搜索 → Postgres 的 `job_required_skills` 关联表 + `skills.name` 索引 + `EXISTS` 子查询，不需缓存。
  - 会话/未读数 → `messages.read_at` 索引查询，不需缓存。
  - 频率限制（`landing/` 的每 IP 每小时 10 次）→ 当前是进程内内存计数；平台期若需多实例共享，改为 Postgres 计数表或托管服务的限流中间件，同样不需自建 Redis。
- **重新考虑的条件**：出现下列任一情况时重新评估 —— (a) 单一查询在生产数据量下超过 500ms；(b) 需要跨实例共享的会话/锁；(c) 需要消息队列做异步扇出。**当前 MVP 一条都不成立。**

---

## 7. 部署

### 选择结论

| 层 | 平台 | 理由 |
|---|---|---|
| 前端 | **Vercel** | React/Vite 的部署体验最好（自动构建、预览部署）。Vercel 的 Hobby 档对个人项目免费，足以覆盖验证期与 MVP 流量。 |
| 后端 | **Railway** | 见下 |
| 数据库 | **Supabase Postgres** | 见第 5 节 |

### 为什么后端选 Railway 而不是 Render

- **无冷启动 sleep**：Render 免费 web service 会在无请求时休眠，首次请求有数秒延迟，对「30 秒内找到职位」这类平台期验收标准不友好。
- **自带持久卷与后台 worker**：需要跑「每周从 ESP 导出回灌 `subscribers` 表」的定时任务（`validation-metrics.md`「数据归属与存储」硬性要求），Railway 的 cron 与 worker 是一等公民，Render 需绕行。
- **一个镜像两种启动命令**：FastAPI 镜像同时用作 web service 与 worker（`uvicorn` vs `python -m app.worker`），避免维护两份部署定义。

### 为什么前端选 Vercel 而不是 Netlify

- 两者都够用。Vercel 对 React/TS 的构建配置默认值更准（TS 项目类型检查、`tsconfig` 路径别名），Netlify 需要更多手工配置。
- Vercel 的 preview deployment 便于在开发期把每次改动发成独立 URL 供创始人验收。

### 容器化边界

**单容器，不引入 Docker Compose 编排、不引入 Kubernetes**——符合 `mvp-boundaries.md`「不使用容器编排」。后端镜像按需多实例（web + worker），数据库是托管服务，不进容器。

### 环境与密钥

- 密钥全部走环境变量，不进代码库：JWT 签名密钥、ESP API Key、数据库连接串、邮件服务凭据。
- 部署平台的 secret 管理替代 `.env` 文件入库。

---

## 8. 验证期与平台期是两个栈（关键澄清）

`tasks.md` 要求选型须「覆盖验证期与平台期两个阶段的需求差异」。本项目的实际情况是：**两个阶段的栈本就不同，且这个差异是刻意的**。

| | 验证期（第 1-4 周） | 平台期（开发触发后） |
|---|---|---|
| 交付物 | 着陆页 + 问卷页 | 双角色平台 |
| 后端 | Python 标准库 `http.server` + `sqlite3` | FastAPI + SQLAlchemy + Supabase Postgres |
| 前端 | 无构建链的静态 HTML/CSS/JS | React 19 + Vite + TS + Tailwind |
| 数据库 | SQLite 单文件 | Supabase Postgres |
| 部署 | 单容器 → Railway | Vercel（前端）+ Railway（后端） |
| 工期 | 已完成 | 3 周 |

### 关键决策：**验证期着陆页不重写为 FastAPI**

`landing/README.md` 原文预留了「若任务 17 最终选定 FastAPI 栈，本目录需按新栈重写」。**本决策否决该重写。**

理由：

1. **重写是纯风险、零收益。** `landing/` 已满足 A1.1 的全部需求（3 变体服务端分流、粘性归因 cookie、自建 `subscribers` 表、`POST /api/subscribers`、`GET /api/subscribers/export` 令牌鉴权、M1 实时计数），22 项测试覆盖。重写成 FastAPI 后功能完全相同，却引入「重写期间服务不可用」的窗口——而 M1 数据完全依赖这个服务产生，一天不可用就是一天的数据损失。
2. **`subscribers` 表在两套实现间是同一个逻辑契约。** 验证期 SQLite 与平台期 Postgres 的列名契约由 `validation/schemas/subscribers.md` 与 `validation/schemas/templates/subscribers.csv` 锁定，两端都必须对齐它。平台期迁移时用 Alembic 建表并对齐列名即可，属于**一次性数据迁移**，不是持续维护成本。
3. **FastAPI 重写应与平台期后端合并进行。** 平台期本来就要写 FastAPI 后端，把订阅 API 一次性写进去，比先写一遍标准库再重写一遍更省。

**唯一约束**：`landing/` 的 SQLite schema 与平台期 Alembic 初始迁移必须列名逐字一致。`validation/schemas/subscribers.md` 是该契约的权威定义。

---

## 9. 与 `mvp-boundaries.md` 技术边界的一致性核对

| `mvp-boundaries.md` 边界 | 本决策的符合情况 |
|---|---|
| 后端不使用 GraphQL | ✅ REST + FastAPI 自动 OpenAPI（仅供文档与类型生成，不作为对外协议） |
| 后端不使用微服务架构 | ✅ 单体应用 + 独立 worker 进程（同一镜像） |
| 后端不使用复杂中间件 | ✅ 仅 CORS、认证、限流三项 |
| 前端不使用复杂状态管理 | ✅ `useState` / `useContext`，不引 Redux / Zustand / React Query |
| 前端不使用动画库、图表库 | ✅ 仅 React + Tailwind + React Router + react-hook-form |
| 数据库不使用复杂视图、存储过程、分片、复杂索引策略 | ✅ 纯表 + 常规索引 |
| 部署不使用容器编排 | ✅ 单镜像，托管数据库，不上 Compose/K8s |
| 不引入 i18n 框架 | ✅ zh-CN 硬编码中文文案 |
| 性能边界 1000 用户 / 每天 100 次职位浏览 | ✅ Postgres + 索引即可满足，无 Redis 也能满足 |
| 响应时间 页面 < 3 秒 / API < 1 秒 | ✅ Vercel CDN + Railway 单实例有余量 |

**逐条确认无越界。** 本决策未引入任何被 `mvp-boundaries.md` 排除的技术。

---

## 10. 落地清单

平台期启动时的执行顺序（供 `tasks.md` 任务 21 [A4.2] 开发估算引用）：

1. 建仓：`FastAPI` 项目骨架 + SQLAlchemy 2.0 + Alembic + `pyproject.toml`
2. Alembic 初始迁移：按 `design.md` 的 12 张表建表，**`subscribers` 表列名与 `validation/schemas/subscribers.md` 逐字一致**
3. JWT 认证：注册/登录/鉴权依赖（bcrypt + PyJWT）
4. 双角色档案：开发者 / 企业
5. 职位发布 + 搜索（技能标签 / `agent_type` / `location_type` / `employment_type` / `team_size` / 薪资区间）
6. 技能标签匹配 + `match_coverage` 计算（口径见 `requirements.md`「基本匹配算法的可验证定义」）
7. 申请/投递 + 站内消息（`applications` → `conversations` → `messages`）
8. 前端 React 应用：职位列表 / 职位详情 / 档案 / 申请跟踪 / 职位管理
9. 部署：Vercel + Railway + Supabase，seed 职位（`is_seed=true`，来自 H2.2 的 seeding 内容）
10. 集成测试 + 上线

**风险提示**：第 9 步的 seeding 职位依赖 `tasks.md` 任务 5 [H2.2] 的产出（企业提供的具体可发布职位内容）。该依赖在 `mvp-boundaries.md`「开发期的前置条件」中已列明。

---

## 附：与 `design.md` 的关系

`design.md`「技术选型建议 (最小化)」一节的「待定」说明已由本文件取代。该节保留的数据模型、API 契约、字段对齐说明、隐私要点**均不受本决策影响**——本决策只收敛技术栈，不改 schema 与 API 路径。
