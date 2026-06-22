# Loop Agent 研究笔记

## 研究目标

- 主题：Loop Agent，也就是以循环为核心的 AI agent 架构。
- 日期：2026-06-22。
- 播客目标：约 10 分钟中文专题播报。
- 重点：解释 Loop Agent 是什么、为什么最近被称为 loop engineering、常见实现形态、适用场景、风险，以及如何落到实际工程。

## 结论摘要

Loop Agent 不是单一产品，而是一类架构模式。它把 LLM 从“一次回答”变成“持续工作”的关键机制：

1. **内层工具循环**：模型读上下文，决定是否调用工具，观察工具结果，再继续推理，直到输出最终结果。OpenAI Agents SDK、AI SDK ToolLoopAgent 都属于这一层。
2. **工作流循环**：按固定顺序反复运行多个子 agent，比如 writer -> critic -> revise，直到达到质量门槛或最大迭代次数。Google ADK 的 LoopAgent 是典型例子。
3. **外层验证循环**：agent 完成一次任务后，由验证器判断“真的完成了吗”；不完成就把反馈注入下一轮。Vercel Labs 的 Ralph Loop Agent 是这个方向的典型开源实现。
4. **产品化 Loop agent**：把循环能力嵌入具体平台，比如 Braintrust Loop 用自然语言分析 logs、traces、datasets、prompts 和 scorers。

一句话定义：Loop Agent = LLM + tools + state + evaluator/stop condition，在循环中持续行动。

## 核心来源

### Oracle：agent loop 的通用架构

来源：

- https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems

要点：

- Oracle 将 agent loop 定义为自主 AI 系统的迭代执行周期：组装上下文、调用 LLM 选择动作、执行动作、观察结果，再把观察结果带入下一轮。
- 文章把 agent loop 拆成五步：Perceive、Reason、Plan、Act、Observe。
- 单次聊天回答的限制是不能根据执行结果迭代、不能从失败中恢复、不能处理依赖前序结果的复杂任务。
- 文章也提醒：agent loop 适合步骤数无法预先确定、需要根据中间结果调整、且延迟成本可以接受的任务。固定流程更适合 deterministic pipeline。
- 生产系统的关键约束是成本和可观测性。文章提到 agent 可能比普通 chat 消耗更多 token，多 agent 系统更明显；调试需要 trace 每个 reasoning step、tool call 和 decision。

### OpenAI Agents SDK：运行时 agent loop

来源：

- https://developers.openai.com/api/docs/guides/agents/running-agents

要点：

- OpenAI 文档把一个 SDK run 看成一个 application-level turn。
- Runner 会循环直到真正停止：
  1. 调用当前 agent 的模型。
  2. 检查模型输出。
  3. 如果模型产生 tool calls，就执行工具并继续。
  4. 如果模型 handoff 给另一个 specialist，就切换 agent 并继续。
  5. 如果模型给出 final answer 且没有后续工具工作，就返回结果。
- 文档强调 tools、handoffs、approvals、streaming 都是在这个 loop 上构建，而不是替代它。
- 状态延续策略包括本地 history、session、conversationId、previousResponseId。
- 审批暂停和失败要被明确处理；如果 run 因 human approval 暂停，应从 state 恢复，而不是开一个新 turn。

### Anthropic：有效 agent 的原则

来源：

- https://www.anthropic.com/engineering/building-effective-agents

要点：

- Anthropic 建议先用最简单的架构解决问题，不要为了 agent 而 agent。
- 文章区分 workflow 和 agent：workflow 是预定义代码路径；agent 是 LLM 动态决定流程和工具调用。
- evaluator-optimizer 是一种反馈循环：一个 LLM 生成，另一个 LLM 评价并反馈。
- 对 agent 的定义接近：LLM 基于环境反馈使用工具循环工作。
- 适用场景：开放性问题、步骤数无法硬编码、需要多轮工具使用和错误恢复。
- 风险：自主 agent 成本更高，错误会累积，需要 sandbox、guardrails、透明 planning、良好的 tool design。
- Anthropic 认为 agent-computer interface（ACI）要像 human-computer interface 一样认真设计：工具描述、输入格式、示例、边界、测试都很重要。

### Google ADK LoopAgent：确定性工作流循环

来源：

- https://adk.dev/agents/workflow-agents/loop-agents/

要点：

- Google ADK 的 LoopAgent 是 template workflow agent，会按顺序执行 sub-agents，直到达到最大迭代次数或终止条件。
- LoopAgent 本身不由 AI 模型动态控制，而是确定性执行 sub-agents。
- 必须实现 termination mechanism，常见策略：
  - Max Iterations。
  - 子 agent 发出停止信号，例如“文档质量已经足够好”。
- 示例场景：Writer Agent 生成或修改文档，Critic Agent 评论，LoopAgent 最多循环 5 次，直到 critic 给出 STOP 信号。

### AI SDK ToolLoopAgent：工具调用循环

来源：

- https://ai-sdk.dev/docs/reference/ai-sdk-core/tool-loop-agent

要点：

- ToolLoopAgent 是 AI SDK Core 中的可复用 agent，支持多步生成、流式响应和工具调用。
- 它适合 autonomous multi-step agents：模型可以调用工具、收集工具结果、基于结果继续推理，直到停止条件或需要用户批准。
- 它不同于 `generateText()` 这样的单步调用。

### Vercel Labs Ralph Loop Agent：外层验证循环

来源：

- https://github.com/vercel-labs/ralph-loop-agent

要点：

- Ralph Loop Agent 是 Vercel Labs 的实验性开源项目，定位是 AI SDK 的 continuous autonomy。
- README 中把 Ralph Wiggum Technique 描述为：持续把任务喂给 AI agent，直到工作真正完成。
- 架构上有两层：
  - 内层是 AI SDK Tool Loop：LLM 与 tools 交替工作，直到模型认为完成。
  - 外层是 Ralph Loop：`verifyCompletion` 判断任务是否真的完成；如果没有完成，把反馈注入下一轮。
- 特性包括：迭代完成、AI SDK 兼容、按迭代/Token/成本限制停止、上下文管理、失败反馈注入。
- `verifyCompletion` 返回 `{ complete: true }` 才停止；否则返回 reason，作为下一轮反馈。

### Braintrust Loop：产品化的观察与优化 agent

来源：

- https://www.braintrust.dev/docs/loop

要点：

- Braintrust Loop 是嵌入 Braintrust 产品里的 AI agent。
- 用途包括分析 logs/traces、生成 SQL filters、找相似 traces、优化 prompts、生成 datasets 和 scorers、搜索文档、提交 support tickets。
- 它支持选择模型、auto-accept edits、选择 data sources、slash commands。
- 它的意义不是展示底层循环代码，而是说明 loop agent 很自然地进入 observability/evaluation 平台：因为 agent 的产物和失败模式本身就需要持续分析。

### Business Insider：loop engineering 成为 AI coding 新话题

来源：

- https://www.businessinsider.com/what-are-loops-ai-engineering-tips-2026-6

要点：

- 2026-06 报道称“loop engineering”开始流行。
- 报道提到 Claude Code 创作者 Boris Cherny 和 OpenAI 工程师 Peter Steinberger 都强调从手写 prompt 转向循环式 agent 工作流。
- Addy Osmani 提到有效 loop 涉及 automation、worktrees、skills、plugins/connectors、sub-agents 等要素。
- 同时提醒：多 agent loop 会消耗更多 tokens，要认真设计成本边界。

## 技术拆解

### Loop Agent 的最小模型

```text
goal -> context -> model -> action/tool -> observation -> evaluator -> continue/stop
```

核心组件：

- Goal：任务目标，必须可验证。
- State：上下文、历史、文件系统、数据库、session、trace。
- Tools：搜索、文件、浏览器、数据库、代码执行、业务 API。
- Policy：权限、预算、审批、禁止动作。
- Evaluator：判断任务是否完成，可能是规则、测试、人审、另一个模型。
- Stop condition：最大迭代、最大成本、成功信号、失败信号、需要人工介入。

### 三种常见 loop

1. **ReAct loop**：reason -> act -> observe。适合搜索、工具调用、API 调用。
2. **Evaluator-optimizer loop**：生成器生成，评价器反馈，再优化。适合写作、代码 review、prompt 优化、SQL 生成。
3. **Outer completion loop**：agent 自认为完成后，外部 verifier 验证。不通过就再跑。适合 coding agent、迁移、批量修复、自动化研究。

### 什么时候适合

- 步骤数无法预先确定。
- 中间结果会改变后续策略。
- 有可验证的完成条件。
- 错误可以通过反馈修复。
- 延迟和 token 成本可以接受。
- 可以把危险动作限制在沙箱或审批之后。

### 什么时候不适合

- 固定流程、固定输入输出：用 pipeline。
- 低延迟场景：loop 会带来多轮调用。
- 没有可靠验证信号：agent 会自信地停在错误结果上。
- 高风险写操作：需要 human-in-the-loop 或强权限边界。
- 成本不可控：必须限制迭代数、token、工具调用和预算。

## 给用户项目的启发

你当前的 AI 播客项目本身就可以抽象成一个 Loop Agent：

1. 研究 agent 收集资料。
2. 写作 agent 生成 notes 和 speech。
3. 生成 agent 生成 MP3。
4. 验证器检查音频时长、RSS、metadata、归档、无播报稿泄漏。
5. 如果不达标，例如时长短于 18 分钟，就把原因反馈给写作 agent 扩稿，然后重新生成。
6. 通过后提交和推送。

这不是“让 AI 自己无限跑”，而是给它明确目标、检查点、预算和停止条件。

