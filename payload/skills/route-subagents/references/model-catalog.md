# Model and effort catalog

Runtime exposure and account/workspace availability override this catalog. Start a new Codex task after changing custom-agent files.

## Thirty-second decision tree

1. **Did the user name a profile?** Use it exactly or stop if unavailable.
2. **Is the task tiny, local, and latency-sensitive?** Use `spark_medium`.
3. **Is the output format and success condition explicit and repeatable?** Use Luna.
4. **Is this everyday repository work requiring tools, implementation, exploration, or debugging?** Use Terra.
5. **Does success depend on ambiguity resolution, architecture, difficult judgment, polish, or critical independent review?** Use Sol.
6. Choose the lowest effort that covers the task. Increase only for concrete complexity, risk, or verification needs.

When uncertain between Terra and Sol: use **Terra to execute a settled plan** and **Sol to decide or challenge the plan**.

## Usage-budget policy

Treat the user's allowance as finite:

- Every subagent performs its own model and tool work, so parallel workflows consume more than a comparable single-agent run.
- Model, context size, reasoning effort, output, and tools all affect usage. Long context and repeated verification are not free.
- Prefer the smallest suitable family and the lowest sufficient effort. Luna is the economical high-volume lane; Terra is the everyday balance; Sol is reserved for judgment that materially benefits from it.
- Spark has a separate research-preview usage limit. Prefer it for eligible microtasks to preserve the main GPT-5.6 allowance, but remember that the separate quota can also be exhausted.
- Use `medium` as the normal default. Require concrete task signals for `high` or `xhigh`.
- Never auto-spawn `max` or `ultra` without an explicit user request. If either appears necessary, explain why lower tiers are likely inadequate and ask for confirmation.
- For Ultra, spawn only the minimum useful independent lanes—normally two or three—not one agent per trivial item.
- Do not run multiple agents to obtain redundant opinions unless independent verification is part of the user's objective.
- Do not repeat a failed lane unchanged. Narrow the task or correct the prompt before spending another run.

## Choose the model family

| Family | Best fit | Typical examples | Avoid when |
|---|---|---|---|
| **GPT-5.3 Codex Spark** | Near-instant, text-only coding iteration with very little context | One-line commands, syntax lookup, tiny obvious fixes, short code explanations | Multi-file work, ambiguity, deep debugging, broad research, consequential decisions |
| **GPT-5.6 Luna** | Clear, repeatable, high-volume work whose desired output is already known | Extraction, classification, formatting, structured summaries, batch transformations, tightly specified edits | Architecture, open-ended investigation, large-context synthesis, high-risk judgment |
| **GPT-5.6 Terra** | Pragmatic everyday work with strong tool use and a mostly settled objective | Repository mapping, implementation, tests, debugging, review, log analysis, evidence gathering | The main challenge is deciding architecture, resolving deep ambiguity, or producing maximum polish |
| **GPT-5.6 Sol** | Complex, open-ended, high-value work requiring judgment, detail, or polish | Architecture, difficult tradeoffs, deep research, cross-system reasoning, critical review, polished deliverables | Mechanical high-volume work where Spark, Luna, or Terra can meet the same acceptance criteria faster |

Spark is a separate, faster and less-capable research-preview model with its own availability and usage limits. Do not treat it as “fast mode” for another model.

## Cost-performance routing

Official ChatGPT credit-rate snapshot checked on **2026-08-11**:

| Family | Input / cached input / output credits per 1M tokens | Relative same-token cost index |
|---|---:|---:|
| GPT-5.6 Luna | 5 / 0.5 / 30 | **1×** |
| GPT-5.6 Terra | 50 / 5 / 300 | **10× Luna** |
| GPT-5.6 Sol | 125 / 12.5 / 750 | **25× Luna** |
| GPT-5.3 Codex Spark | Research preview, separate usage limit | Not comparable |

Use these ratios as a routing weight, not a guaranteed per-message bill. Actual usage also depends on context, reasoning tokens, output, tools, cache, agent count, and retries. OpenAI does not publish a fixed Low/Medium/High/XHigh/Max/Ultra multiplier, so never invent one. Refresh the official pricing page before relying on exact numbers at a later date.

### Artificial Analysis empirical prior

Snapshot checked on **2026-08-11** from the comparison supplied by the user and the Artificial Analysis OpenAI model table. Cost is the weighted average API cost per Artificial Analysis Intelligence Index v4.1.1 task, not Codex subscription usage. Values are rounded and can change as the benchmark is rerun.

| Profile | Intelligence Index | Cost per task (USD) |
|---|---:|---:|
| `luna_low` | 34 | $0.01 |
| `luna_medium` | 38 | $0.01 |
| `luna_high` | 47 | $0.02 |
| `luna_xhigh` | 49 | $0.03 |
| `luna_max` | 51 | $0.05 |
| `terra_low` | 40 | $0.09 |
| `terra_medium` | 46 | $0.12 |
| `terra_high` | 49 | $0.22 |
| `terra_xhigh` | 52 | $0.31 |
| `terra_max` | 55 | $0.51 |
| `sol_low` | 49 | $0.24 |
| `sol_medium` | 54 | $0.39 |
| `sol_high` | 56 | $0.55 |
| `sol_xhigh` | 58 | $0.83 |
| `sol_max` | 59 | $1.23 |

Use this table with **Pareto dominance**, not a raw `index / dollars` ratio:

- First apply the task-fit gate. A benchmark winner that cannot handle the task shape is false economy.
- When two candidates have comparable fit, prefer the cheaper profile that meets the required capability; do not pay merely to maximize the score.
- In this snapshot Luna and Sol are ahead of Terra at every point on the generic intelligence-versus-cost frontier. Therefore prefer Luna for bounded work and Sol for ambiguous/high-value judgment. Select Terra only when its everyday repository execution, tool use, latency, or debugging fit is itself valuable.
- `luna_high` and `luna_xhigh` are especially attractive bounded-reasoning lanes. `luna_max` empirically beats `terra_high` on this general benchmark, but only choose it for an indivisible, deterministic, narrow task; it is not a substitute for Terra's multi-file/tool fit.
- `sol_medium` is the normal entry point when Sol-level judgment is truly required. Escalate through High and XHigh only as risk or ambiguity grows.
- Spark is not in this comparison and has a separate allowance. Ultra is orchestration rather than a single benchmarked effort. Keep their existing routing rules.
- API dollars are not the user's ChatGPT allowance. The Max/Ultra confirmation gate still applies even when a benchmark point looks inexpensive.

The index combines agentic work, coding, scientific reasoning, and general knowledge. It is a useful broad prior, not a guarantee for a specific repository, language, toolchain, language of conversation, or long-context workload.

Approximate expected usage as:

```text
family token rate × actual tokens at selected effort × number of agents × retries
```

### Task-fit score

This score is a router heuristic derived from the official workload descriptions, not an OpenAI benchmark. `0` means unsuitable, `3` means workable, and `5` means natural fit.

| Task shape | Spark | Luna | Terra | Sol |
|---|---:|---:|---:|---:|
| Tiny local answer, lookup, or obvious micro-fix | 5 | 4 | 3 | 3 |
| Deterministic extraction, transformation, or batch | 2 | 5 | 4 | 3 |
| Routine repository implementation and tool use | 1 | 2 | 5 | 4 |
| Complex debugging or verification-heavy execution | 1 | 2 | 5 | 5 |
| Architecture, unresolved tradeoffs, or high-stakes judgment | 0 | 1 | 3 | 5 |
| Maximum polish or critical independent review | 1 | 2 | 4 | 5 |

### Selection algorithm

1. Exclude any family scoring below `4` for the task's dominant shape.
2. If Spark scores `5`, is available, and the task is self-contained, prefer `spark_medium` before spending the main GPT-5.6 allowance.
3. For each remaining family, estimate the lowest sufficient effort.
4. Use the dated Artificial Analysis snapshot as an empirical prior. Eliminate a candidate that is Pareto-dominated by another candidate with comparable task fit.
5. Prefer the remaining candidate with the lowest expected usage, using benchmark cost, the official family cost index, and qualitative effort burden.
6. Break close ties with latency, then verification confidence.
7. Require confirmation for Max or Ultra even when that candidate wins.
8. Escalate only after evidence shows that the cheaper suitable candidate was insufficient.

For an implicit choice, if Spark is unavailable or its separate limit is exhausted, fall back to the next suitable GPT-5.6 candidate and disclose the route change. For an explicitly requested `spark_medium`, stop instead of substituting.

This means `luna_max` may be a candidate instead of `terra_high` only for one exceptionally difficult, indivisible, deterministic, narrow transformation—and only after `luna_xhigh` is judged insufficient and the Max confirmation gate is passed. Do not claim that it is quantitatively cheaper: OpenAI publishes family rates, but no fixed effort multiplier. It is not suitable for multi-file implementation, broad tool coordination, or open debugging because Luna fails the fit gate there. Similarly, `terra_xhigh` is usually the better-fit value choice than `sol_medium` for difficult execution inside an already settled architecture, while Sol wins when deciding the architecture is the actual task.

## Choose the effort

| Effort | Positive signals | Do not use merely because |
|---|---|---|
| `low` | One or two direct steps, explicit inputs and output, low risk, easy verification | The task should finish quickly |
| `medium` | Default balanced lane; several straightforward steps or checks, limited ambiguity | The model family was difficult to choose |
| `high` | Multiple steps/files/sources, meaningful edge cases, non-trivial debugging or verification | The task is large but mechanical |
| `xhigh` | Subtle logic, broad context, security/compatibility concerns, difficult assumptions, higher consequences | More tokens might feel safer |
| `max` | One exceptionally hard, indivisible problem where reasoning depth matters more than latency or usage | The workload contains independent subtasks; that is an Ultra signal |
| `ultra` | Several genuinely independent subproblems that benefit from parallel agents and later consolidation | The task is simply hard; use Max for a single hard problem |

Model support for `xhigh`, `max`, and `ultra` is runtime-dependent. An unusual family/effort pairing is valid only when the native spawn tool exposes it.

## Pairing and escalation rules

- Choose the **family before effort**. Higher effort does not repair a family mismatch.
- Luna High remains a narrow-task model; it does not become Terra or Sol by reasoning longer.
- Sol Low still favors judgment and polish; it is not the fastest mechanical worker.
- If a Luna task grows into multi-file tool coordination or open debugging, switch to Terra.
- If a Terra task becomes an architecture or high-stakes judgment problem, switch to Sol.
- If the family is still correct but the first lane misses edge cases, escalate effort one level with a fresh agent.
- For independent final verification, use a fresh Sol profile and request read-only behavior when isolation matters.
- Never conceal an unavailable explicit route or silently fall back.

## Installed profiles

- Spark: `spark_medium`.
- Luna: `luna_low`, `luna_medium`, `luna_high`, `luna_xhigh`, `luna_max`, `luna_ultra`.
- Terra: `terra_low`, `terra_medium`, `terra_high`, `terra_xhigh`, `terra_max`, `terra_ultra`.
- Sol: `sol_low`, `sol_medium`, `sol_high`, `sol_xhigh`, `sol_max`, `sol_ultra`.

## Official basis

- [Codex models](https://learn.chatgpt.com/docs/models)
- [Codex pricing and usage limits](https://learn.chatgpt.com/docs/pricing)
- [Speed and Codex-Spark](https://learn.chatgpt.com/docs/agent-configuration/speed)
- [Subagents and custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## External empirical basis

- [Artificial Analysis: GPT-5.6 Sol, Terra, and Luna intelligence versus cost](https://artificialanalysis.ai/articles/gpt-5-6-intelligence-vs-cost-across-sol-terra-luna)
- [Artificial Analysis OpenAI model table](https://artificialanalysis.ai/providers/openai/)
- [Artificial Analysis Intelligence Index methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
