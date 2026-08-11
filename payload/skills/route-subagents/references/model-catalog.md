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

## Canonical family hierarchy

- **Capability and depth ceiling:** `Sol > Terra > Luna > Spark`.
- **Expected speed and cost efficiency:** `Spark > Luna > Terra > Sol`.

This is the primary ordering. Choose the lowest family whose capability ceiling and workload fit are sufficient. Reasoning effort changes depth inside a family; it does not promote Luna into Terra, Terra into Sol, or Spark into Luna. Cross-effort benchmark scores can overlap, but they do not reverse the family hierarchy.

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
| **GPT-5.6 Sol** | Complex, open-ended, high-value work requiring judgment, detail, or polish | Architecture, difficult tradeoffs, deep research, cross-system reasoning, critical review, polished deliverables | Mechanical high-volume work where Spark, Luna, or Terra can meet the same acceptance criteria faster |
| **GPT-5.6 Terra** | Pragmatic everyday work with strong tool use and a mostly settled objective | Repository mapping, implementation, tests, debugging, review, log analysis, evidence gathering | The main challenge is deciding architecture, resolving deep ambiguity, or producing maximum polish |
| **GPT-5.6 Luna** | Clear, repeatable, high-volume work whose desired output is already known | Extraction, classification, formatting, structured summaries, batch transformations, tightly specified edits | Architecture, open-ended investigation, large-context synthesis, high-risk judgment |
| **GPT-5.3 Codex Spark** | Near-instant, text-only coding iteration with very little context | One-line commands, syntax lookup, tiny obvious fixes, short code explanations | Multi-file work, ambiguity, deep debugging, broad research, consequential decisions |

Spark is a separate, faster and less-capable research-preview model with its own availability and usage limits. Do not treat it as “fast mode” for another model.

## Cost-performance routing

Official ChatGPT credit-rate snapshot checked on **2026-08-11**:

| Family | Input / cached input / output credits per 1M tokens | Relative same-token cost index |
|---|---:|---:|
| GPT-5.6 Sol | 125 / 12.5 / 750 | **25× Luna** |
| GPT-5.6 Terra | 50 / 5 / 300 | **10× Luna** |
| GPT-5.6 Luna | 5 / 0.5 / 30 | **1×** |
| GPT-5.3 Codex Spark | Research preview, separate usage limit | Not comparable |

Use these ratios as a routing weight, not a guaranteed per-message bill. Actual usage also depends on context, reasoning tokens, output, tools, cache, agent count, and retries. OpenAI does not publish a fixed Low/Medium/High/XHigh/Max/Ultra multiplier, so never invent one. Refresh the official pricing page before relying on exact numbers at a later date.

### Artificial Analysis empirical prior

Snapshot checked on **2026-08-11** from the comparison supplied by the user and the Artificial Analysis OpenAI model table. Cost is the weighted average API cost per Artificial Analysis Intelligence Index v4.1.1 task, not Codex subscription usage. Values are rounded and can change as the benchmark is rerun.

| Profile | Intelligence Index | Cost per task (USD) |
|---|---:|---:|
| `sol_low` | 49 | $0.24 |
| `sol_medium` | 54 | $0.39 |
| `sol_high` | 56 | $0.55 |
| `sol_xhigh` | 58 | $0.83 |
| `sol_max` | 59 | $1.23 |
| `terra_low` | 40 | $0.09 |
| `terra_medium` | 46 | $0.12 |
| `terra_high` | 49 | $0.22 |
| `terra_xhigh` | 52 | $0.31 |
| `terra_max` | 55 | $0.51 |
| `luna_low` | 34 | $0.01 |
| `luna_medium` | 38 | $0.01 |
| `luna_high` | 47 | $0.02 |
| `luna_xhigh` | 49 | $0.03 |
| `luna_max` | 51 | $0.05 |

Use this table as a **secondary empirical signal**, not a raw `index / dollars` ratio and not a replacement for the official family hierarchy:

- First establish the minimum family tier and apply the task-fit gate. A benchmark winner below the required family is false economy.
- When two profiles are already sufficient and have comparable fit, prefer the cheaper profile that meets the required capability; do not pay merely to maximize the score.
- The snapshot contains cross-effort overlaps and places some Luna or Sol points ahead of Terra on generic intelligence per dollar. This describes benchmark efficiency, not canonical family capability. Never infer `Luna > Terra` or down-tier a Terra-shaped task from it.
- `luna_high` and `luna_xhigh` are especially attractive for work that is already clear, repeatable, and bounded. `luna_max` scores above `terra_high` in this general benchmark, but that does not make it a Terra substitute; select it only when the task was Luna-shaped from the start and is indivisible, deterministic, and narrow.
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

| Task shape | Sol | Terra | Luna | Spark |
|---|---:|---:|---:|---:|
| Tiny local answer, lookup, or obvious micro-fix | 3 | 3 | 4 | 5 |
| Deterministic extraction, transformation, or batch | 3 | 4 | 5 | 2 |
| Routine repository implementation and tool use | 4 | 5 | 2 | 1 |
| Complex debugging or verification-heavy execution | 5 | 5 | 2 | 1 |
| Architecture, unresolved tradeoffs, or high-stakes judgment | 5 | 3 | 1 | 0 |
| Maximum polish or critical independent review | 5 | 4 | 2 | 1 |

### Selection algorithm

1. Establish the minimum capability tier using `Sol > Terra > Luna > Spark`, then exclude any family below that tier or scoring below `4` for the task's dominant shape.
2. If the required tier is Spark, Spark scores `5`, is available, and the task is self-contained, prefer `spark_medium` before spending the main GPT-5.6 allowance.
3. For each remaining sufficient family, estimate the lowest sufficient effort.
4. Use the dated Artificial Analysis snapshot only as a secondary empirical prior. Eliminate a profile only when the alternative has the same or higher family capability and comparable task fit.
5. Prefer the remaining candidate with the lowest expected usage, using benchmark cost, the official family cost index, and qualitative effort burden. Never down-tier solely for price.
6. Break close ties with latency, then verification confidence.
7. Require confirmation for Max or Ultra even when that candidate wins.
8. Escalate only after evidence shows that the cheaper suitable candidate was insufficient.

For an implicit choice, if Spark is unavailable or its separate limit is exhausted, fall back to the next suitable GPT-5.6 candidate and disclose the route change. For an explicitly requested `spark_medium`, stop instead of substituting.

This means `luna_max` is not a general alternative to `terra_high`. It may be considered only when the task is Luna-shaped from the start: one exceptionally difficult, indivisible, deterministic, narrow transformation, after `luna_xhigh` is judged insufficient and the Max confirmation gate is passed. Do not claim that it is quantitatively cheaper in ChatGPT allowance terms: OpenAI publishes family rates, but no fixed effort multiplier. For multi-file implementation, broad tool coordination, or open debugging, preserve the higher family requirement and use Terra. Similarly, Terra may execute a settled architecture, while Sol remains the higher-capability choice when deciding or challenging that architecture is the task.

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

- Choose the **family before effort** and preserve `Sol > Terra > Luna > Spark`. Higher effort does not repair a family mismatch or promote a lower family.
- Luna High remains a narrow-task model; it does not become Terra or Sol by reasoning longer.
- Sol Low still favors judgment and polish; it is not the fastest mechanical worker.
- If a Luna task grows into multi-file tool coordination or open debugging, switch to Terra.
- If a Terra task becomes an architecture or high-stakes judgment problem, switch to Sol.
- If the family is still correct but the first lane misses edge cases, escalate effort one level with a fresh agent.
- For independent final verification, use a fresh Sol profile and request read-only behavior when isolation matters.
- Never conceal an unavailable explicit route or silently fall back.

## Installed profiles

- Sol: `sol_low`, `sol_medium`, `sol_high`, `sol_xhigh`, `sol_max`, `sol_ultra`.
- Terra: `terra_low`, `terra_medium`, `terra_high`, `terra_xhigh`, `terra_max`, `terra_ultra`.
- Luna: `luna_low`, `luna_medium`, `luna_high`, `luna_xhigh`, `luna_max`, `luna_ultra`.
- Spark: `spark_medium`.

## Official basis

- [Codex models](https://learn.chatgpt.com/docs/models)
- [Codex pricing and usage limits](https://learn.chatgpt.com/docs/pricing)
- [Speed and Codex-Spark](https://learn.chatgpt.com/docs/agent-configuration/speed)
- [Subagents and custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## External empirical basis

- [Artificial Analysis: GPT-5.6 Sol, Terra, and Luna intelligence versus cost](https://artificialanalysis.ai/articles/gpt-5-6-intelligence-vs-cost-across-sol-terra-luna)
- [Artificial Analysis OpenAI model table](https://artificialanalysis.ai/providers/openai/)
- [Artificial Analysis Intelligence Index methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
