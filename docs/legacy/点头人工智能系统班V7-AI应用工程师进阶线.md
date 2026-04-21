# 点头人工智能系统班 V7.0 —— AI 应用工程师实战线·进阶

---

## 定位

AI 应用工程师实战线的进阶课程。从「自己动手构建 AI 应用」升级到「设计环境让 AI Agent 替你构建应用」。掌握 Harness Engineering——2026 年最核心的开发者技能：模型是大宗商品，Harness 才是护城河。

**前置要求：** 完成 AI 应用工程师实战线基础版（具备 RAG/Agent 应用构建经验，能读懂和审查 AI 生成的代码）

**核心交付物：** 一个完整的 Agent Harness 工程——包含约束文档、自定义 Skills、MCP Server、Hooks 安全管道——让 AI Agent 在该 Harness 下自主完成一个真实项目

---

## 设计理念

### 范式转变：从写代码到设计 Agent 工作环境

基础版课程中，学员的角色是**程序员**——调用 LLM API、手写 RAG pipeline、搭建 Agent 工作流。

进阶版课程中，学员的角色是 **Agent 的架构师**——设计约束、封装技能、接入工具、构建安全门控，让 AI Agent 在终端里自主完成开发任务。

```
基础版：人 → 写代码调用 LLM → 构建应用
进阶版：人 → 设计 Harness → Agent 在 CLI 里自主构建应用
```

这不是「不写代码」，而是工作方式的根本转变——从「做执行者」到「做管理者」。正如基础版中 Vibe Coding 培养的「描述需求 → AI 生成 → 审查修改」循环，进阶版将这个循环系统化、工程化。

### 为什么 Harness Engineering 是核心

2026 年的事实：OpenAI、Anthropic、Google、Cursor 四家独立构建编码 Agent，最终收敛到几乎相同的架构——Agent Runtime + 约束文档 + 记忆系统 + 工具集成 + 自动审查。LangChain 只改 Harness 不改模型，benchmark 从 Top 30 跳到 Top 5。

核心认知：**模型能力会持续提升且趋于同质化，但如何约束和引导模型——Harness——才是创造差异化价值的地方。**

### 一个 Harness，逐层搭建

课程围绕同一个 Harness 工程从空目录到完整系统逐层构建：

```
模块 1-2：约束层 + CLI 实战 —— Agent 能理解项目并执行任务
    ↓
模块 3：扩展层 —— Agent 获得领域专属技能
    ↓
模块 4：工具层 —— Agent 能连接外部系统
    ↓
模块 5：安全层 —— Agent 的行为受到确定性门控
    ↓
模块 6：综合项目 —— Agent 在完整 Harness 下自主交付一个真实项目
```

---

## 课程内容

### 模块 1：Context Engineering（4 课时，直播）

从 Prompt Engineering 升级到 Context Engineering——不再只关注「怎么措辞」，而是「怎么组装让 Agent 正确工作的完整上下文」。

| 课时数 | 课题描述 | 课程形式 |
|-------|--------|--------|
| 1课时 | **从 Prompt 到 Context：范式升级** | 直播 |
| | Prompt 只是 Context 的子集；Context 的六大组成（系统指令、对话历史、检索结果、工具输出、结构化约束、动态注入）；Context Window 管理与压缩策略 | |
| 1课时 | **约束文档设计：CLAUDE.md / AGENTS.md** | 直播 |
| | 约束文档的结构与写法；编码规范、架构决策、反模式的文档化；项目级 vs 全局级约束；实战：为一个真实项目编写 CLAUDE.md | |
| 1课时 | **动态上下文工程** | 直播 |
| | Rules 文件设计（.claude/rules/）；条件化上下文注入；项目结构映射；上下文优先级与裁剪策略 | |
| 1课时 | **记忆系统设计** | 直播 |
| | Memory 系统原理（跨会话持久化）；记忆类型设计（用户/反馈/项目/引用）；MEMORY.md 索引管理；何时写入、何时清理、何时信任 | |

**项目作业**——为指定项目编写完整的约束文档体系（CLAUDE.md + Rules + Memory 结构），提交后由讲师评审约束质量

---

### 模块 2：CLI Agent 实战（3 课时，直播+代码审查）

掌握终端原生 AI Agent 的深度使用，从「对话式问答」升级到「自主执行复杂开发任务」。

| 课时数 | 课题描述 | 课程形式 |
|-------|--------|--------|
| 1课时 | **CLI Agent 深度使用** | 直播 |
| | Claude Code / Codex CLI 核心工作流；Agent 模式 vs 对话模式；多文件自主编辑；Worktree 隔离执行；后台 Agent 并行任务 | |
| 1课时 | **任务分解与 Agent 委派** | 直播 |
| | 复杂任务拆解为 Agent 可执行的子任务；Subagent 定义与编排（.claude/agents/）；前台 vs 后台执行策略；Handoff 文档设计 | |
| 1课时 | **Agent 输出评估与迭代** | 直播+代码审查 |
| | Evaluation-Driven Development（EDD）；Agent 输出的系统化评估方法；迭代约束文档改进 Agent 行为；实战：用 Agent 完成一个功能开发并评估 | |

**项目作业**——使用 CLI Agent 在约束文档指导下完成一个完整的功能开发任务，提交 Agent 会话记录 + 评估报告

---

### 模块 3：Skill 开发（4 课时，直播+代码审查）

将领域知识封装为 Agent 可复用的技能——从「每次手动指导 Agent」到「一次封装、反复调用」。

| 课时数 | 课题描述 | 课程形式 |
|-------|--------|--------|
| 1课时 | **Skill 系统架构** | 直播 |
| | Skill vs Slash Command 的演进；SKILL.md 结构与 Frontmatter 控制（allowed-tools、context、agent）；全局 Skill vs 项目 Skill；Skill 自动激活机制 | |
| 1课时 | **Skill 设计与封装实战** | 直播 |
| | 领域知识技能化的方法论；从重复性任务提取 Skill；支持文件（模板、示例、脚本）组织；动态上下文注入（Shell 命令输出） | |
| 1课时 | **Subagent Skill 与编排** | 直播 |
| | context: fork 模式；Skill 内 Subagent 调度；多 Skill 协作工作流；Skill 参数化设计 | |
| 1课时 | **Skill 工程实战与审查** | 直播+代码审查 |
| | 实战：设计并封装 3-5 个业务 Skill；Skill 测试与调试；代码审查：学员演示 Skill 执行效果与设计思路 | |

**项目作业**——设计并交付一套项目专属 Skill 库（3-5 个 Skill），包含 SKILL.md、支持文件、使用文档

---

### 模块 4：MCP Server 开发（4 课时，直播+代码审查）

MCP 是 Agent 连接外部工具的「USB-C」标准协议。学会写 MCP Server = 给 Agent 接入任何外部系统的通用能力。

| 课时数 | 课题描述 | 课程形式 |
|-------|--------|--------|
| 1课时 | **MCP 协议原理** | 直播 |
| | MCP 解决什么问题（N x M → N + M）；Client/Server 架构；Transport 层（stdio/HTTP SSE）；Tool / Resource / Prompt 三种能力类型 | |
| 1课时 | **MCP Server 开发实战** | 直播 |
| | Python MCP SDK；Tool 定义与参数设计；Server 注册与调试；实战：开发一个连接数据库的 MCP Server | |
| 1课时 | **复杂 MCP Server 与生态** | 直播 |
| | Resource 暴露与动态发现；多工具 Server 设计；接入第三方 API；MCP Server 生态（500+ 公开 Server）的使用与选型 | |
| 1课时 | **MCP 集成与审查** | 直播+代码审查 |
| | 将自定义 MCP Server 接入 Agent Harness；工具发现与懒加载；实战演示 + 代码审查 | |

**项目作业**——开发并交付一个自定义 MCP Server（至少 3 个工具），接入 Agent Harness 并演示 Agent 通过 MCP 调用外部系统

---

### 模块 5：Hooks 与安全管道（2 课时，直播）

给 Agent 的行为加上确定性门控——Agent 可以自主工作，但每一步都有安全检查。

| 课时数 | 课题描述 | 课程形式 |
|-------|--------|--------|
| 1课时 | **Hook 系统设计** | 直播 |
| | Hook 生命周期（PreToolUse / PostToolUse / Notification 等）；Hook 脚本编写；settings.json 配置；审批 vs 拦截 vs 修改三种模式 | |
| 1课时 | **安全管道与自动审查** | 直播 |
| | 危险命令检测；文件写入拦截与校验；自动 Lint / Format Hook；CI/CD 中的 Agent 审查管道；Doom Loop 检测与迭代上限 | |

**项目作业**——为 Harness 工程设计并实现一套 Hook 安全管道（至少覆盖：危险命令拦截、代码格式检查、敏感文件保护）

---

### 模块 6：Harness 综合项目（3 课时，直播+代码审查）

将前五个模块的所有组件整合为一个完整的 Agent Harness，让 Agent 在该 Harness 下自主完成一个真实项目。

| 课时数 | 课题描述 | 课程形式 |
|-------|--------|--------|
| 1课时 | **Harness 架构整合** | 直播 |
| | 约束文档 + Skills + MCP Server + Hooks 的协同设计；Harness 目录结构规范；组件间依赖管理 | |
| 1课时 | **Agent 自主交付实战** | 直播 |
| | 定义一个真实项目需求；让 Agent 在 Harness 下自主完成（从代码生成到测试到部署）；讲师现场演示 + 学员同步实操 | |
| 1课时 | **项目展示与 Harness 互评** | 直播+代码审查 |
| | 学员展示各自的 Harness 工程；Agent 自主交付的项目成果演示；互评 Harness 设计质量 | |

**最终交付物**——完整的 Agent Harness 工程 GitHub 仓库，包含：
- 约束文档体系（CLAUDE.md / AGENTS.md / Rules）
- 自定义 Skill 库（3-5 个）
- 自定义 MCP Server（至少 3 个工具）
- Hook 安全管道
- Agent 自主完成的项目代码 + 文档
- Harness 架构说明文档

---

## 课程总览

| 模块 | 课时 | 核心能力 | 交付物 |
|------|------|---------|--------|
| Context Engineering | 4 | 约束文档设计、动态上下文工程、记忆系统 | 项目约束文档体系 |
| CLI Agent 实战 | 3 | CLI Agent 深度使用、任务委派、输出评估 | Agent 会话记录 + 评估报告 |
| Skill 开发 | 4 | 领域知识技能化、Subagent 编排、Skill 工程化 | 项目 Skill 库 |
| MCP Server 开发 | 4 | MCP 协议、Server 开发、工具生态接入 | 自定义 MCP Server |
| Hooks 与安全管道 | 2 | 生命周期 Hook、安全门控、自动审查 | Hook 安全管道 |
| Harness 综合项目 | 3 | 架构整合、Agent 自主交付、Harness 评估 | 完整 Harness 工程 |
| **合计** | **20** | | |

---

## JD 关键词覆盖对照

| JD 高频关键词 | 课程对应模块 | 掌握程度 |
|-------------|------------|---------|
| Agent 架构 / 智能体 | 模块 1-6 全程 | 从使用者升级为 Agent 系统架构师 |
| Prompt Engineering / Context Engineering | 模块 1 核心 | 掌握上下文工程完整方法论 |
| MCP / 工具集成 | 模块 4 核心 | 能自主开发 MCP Server 接入任意外部系统 |
| LLM 应用开发 | 模块 2-6 贯穿 | 通过 Agent 自主完成，而非手写 |
| RAG / 检索增强 | 模块 1、3 | 作为 Skill / MCP 工具接入 Agent |
| CI/CD / DevOps | 模块 5 | Agent 审查管道、自动化安全检查 |
| Python | 模块 3-5 | MCP Server / Hook 脚本开发 |

---

## 配套服务

- 全套课程资料与 Harness 工程模板
- 班群答疑（技术问题实时响应）
- 代码审查（模块 2、3、4、6 各一次，讲师评审 Harness 设计质量）
- 1V1 项目指导（Harness 架构设计、Skill 设计、MCP Server 选型）
- 班主任督学
