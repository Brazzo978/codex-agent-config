# Model and effort catalog

Runtime exposure and account/workspace availability override this catalog. Start a new Codex task after changing custom-agent files.

## Thirty-second decision tree

1. **Did the user name a profile?** Use it exactly or stop if unavailable.
2. **Is the task tiny, local, and latency-sensitive?** Use `spark_medium`.
3. **Is the output format and success condition explicit and repeatable?** Use Luna.
4. **Is this everyday repository work requiring tools, implementation, exploration, or debugging?** Use Terra.
5. **Does success depend on ambiguity resolution, architecture, difficult judgment, polish, or critical independent review?** Use Sol.
6. Use the profile intelligence ladder to choose the cheapest fitting profile in the required capability band. Increase effort only for concrete complexity, risk, or verification needs.

When uncertain between Terra and Sol: use **Terra to execute a settled plan** and **Sol to decide or challenge the plan**.

## Two layers of tiering

1. **Workload fit from the official model roles:** Sol for complex/open-ended judgment, Terra for everyday reasoning and tool use, Luna for clear/repeatable work, and Spark for near-instant microtasks.
2. **Observed general intelligence by concrete profile:** use the dated Artificial Analysis ladder below after workload fit.

At the same effort, the observed intelligence order is `Sol > Terra > Luna`. Across different efforts the profiles interleave: a higher-effort Luna or Terra can score above a lower-effort profile from the family above. This changes the empirical intelligence tier, not the model's workload strengths. Spark is absent from the index; expected family speed and cost efficiency still generally run `Spark > Luna > Terra > Sol`.

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

Use two distinct cost layers:

1. **ChatGPT/Codex allowance cost:** official family credit rates estimate how quickly a route consumes the user's main allowance.
2. **Artificial Analysis API benchmark cost:** the observed total API cost of running the same evaluation suite estimates the relative end-to-end expense of each concrete effort profile.

The API benchmark cost is a routing proxy, not a conversion from dollars to ChatGPT credits. It is still useful because it includes the profile's actual input, cache, reasoning, and output mix over one common workload.

Official ChatGPT credit-rate snapshot checked on **2026-08-11**:

| Family | Input / cached input / output credits per 1M tokens | Relative same-token cost index |
|---|---:|---:|
| GPT-5.6 Sol | 125 / 12.5 / 750 | **25× Luna** |
| GPT-5.6 Terra | 50 / 5 / 300 | **10× Luna** |
| GPT-5.6 Luna | 5 / 0.5 / 30 | **1×** |
| GPT-5.3 Codex Spark | Research preview, separate usage limit | Not comparable |

Use these ratios as the main-allowance weight, not a guaranteed per-message bill. Actual usage also depends on context, reasoning tokens, output, tools, cache, agent count, and retries. OpenAI does not publish a fixed Low/Medium/High/XHigh/Max/Ultra multiplier, so never invent one. Refresh the official pricing page before relying on exact numbers at a later date.

### Artificial Analysis profile intelligence and API cost

Snapshot supplied by the user and checked on **2026-08-11** from Artificial Analysis Intelligence Index v4.1.1. The cost is the USD total to run all evaluations in the index, including non-cached input, cache read/write, reasoning, and output. Treat equal intelligence scores as one tier.

| Rank | Profile | Intelligence Index | AA full-suite API cost |
|---:|---|---:|---:|
| 1 | `sol_max` | 61 | $2,823 |
| 2 | `sol_xhigh` | 59 | $1,525 |
| 3 | `sol_high` | 57 | $955 |
| 3 | `terra_max` | 57 | $1,390 |
| 4 | `sol_medium` | 56 | $580 |
| 5 | `terra_xhigh` | 53 | $590 |
| 6 | `luna_max` | 52 | $172 |
| 7 | `sol_low` | 51 | $344 |
| 8 | `terra_high` | 50 | $395 |
| 8 | `luna_xhigh` | 50 | $95 |
| 9 | `luna_high` | 47 | $55 |
| 9 | `terra_medium` | 47 | $192 |
| 10 | `terra_low` | 41 | $130 |
| 11 | `luna_medium` | 39 | $21 |
| 12 | `luna_low` | 34 | $14 |

Artificial Analysis also reports non-reasoning variants at $10 for Luna, $99 for Terra, and $240 for Sol. They are not installed custom-agent profiles, so do not route to them.

Use the ladder as the empirical intelligence order after workload fit:

- Equal scores are intelligence ties; prefer the cheaper/faster suitable profile unless risk or verification confidence justifies otherwise.
- `terra_max` ties `sol_high` at 57, `luna_xhigh` ties `terra_high` at 50, and `luna_high` ties `terra_medium` at 47.
- `luna_max` at 52 ranks above `sol_low` at 51, but Luna still fits clear, bounded work rather than open-ended Sol work.
- Spark is not scored. Keep it as the near-instant lane for tiny self-contained tasks and exploit its separate usage limit.
- Ultra is not a single benchmarked profile. It remains a parallel-orchestration choice and always passes through the confirmation gate.
- Max remains quota-heavy despite its benchmark rank. Never select Max automatically without explicit request or confirmation.

Soft capability bands for routing are `34-41` straightforward, `47-50` non-trivial, `51-53` hard, `56-57` complex/high-value, and `59-61` exceptional. These are heuristics, not service-level guarantees.

The index combines agentic work, coding, scientific reasoning, and general knowledge. It is a useful broad prior, not a guarantee for a specific repository, language, toolchain, language of conversation, or long-context workload.

Approximate expected usage as:

```text
AA profile cost proxy × task-size factor × number of agents × retries
```

Use the official family credit rate separately to estimate pressure on the user's main ChatGPT/Codex allowance. Do not add the two numbers or claim a dollar-to-credit conversion.

### Fitness rule

Do not maximize raw `Intelligence Index / API cost`. That ratio strongly favors the smallest profiles even when they are below the capability needed for the task. Use constrained optimization instead:

```text
eligible(profile, task) =
  family_task_fit(profile, task) >= required_fit
  AND intelligence(profile) >= required_intelligence(task)

winner(task) = eligible profile with the lowest AA full-suite API cost
```

Apply it lexicographically:

1. Prefer natural family fit (`5`) over merely workable fit (`4`) when a natural-fit profile reaches the intelligence floor.
2. Set the minimum Intelligence Index from task complexity, ambiguity, risk, and verification burden.
3. Within that fit tier, choose the cheapest profile meeting the floor.
4. Use lower latency, smaller context, and fewer expected retries as tie-breakers.
5. Apply the Max/Ultra confirmation gate after selection.

This is a **fit-conditioned cost frontier**. A global Pareto frontier would incorrectly remove many Terra profiles because Luna is cheaper at several scores and Sol can be stronger at nearby costs. Terra remains the correct lane when repository execution, tools, and debugging are the dominant workload.

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

1. Apply the task-fit matrix and exclude families scoring below `4` for the task's dominant shape.
2. For a tiny self-contained task where Spark scores `5`, prefer `spark_medium` before spending the main GPT-5.6 allowance.
3. Prefer candidates from a family scoring `5`; use a fit-`4` family only when no natural-fit profile reaches the required capability or runtime availability blocks it.
4. Estimate the minimum soft capability band from complexity, ambiguity, risk, and verification burden.
5. Retain concrete profiles that meet the capability band in the dated intelligence ladder.
6. Choose the retained profile with the lowest AA full-suite API cost, adjusted qualitatively for task size, context, agent count, and likely retries.
7. Use the official family credit index to check main-allowance pressure, and preserve Spark as a separate-budget lane rather than assigning it a fabricated comparable cost.
8. For equal intelligence, prefer lower cost and latency when workload fit is equal.
9. Require confirmation for Max or Ultra even when that candidate wins.
10. Escalate only after evidence shows that the cheaper suitable candidate was insufficient.

For an implicit choice, if Spark is unavailable or its separate limit is exhausted, fall back to the next suitable GPT-5.6 candidate and disclose the route change. For an explicitly requested `spark_medium`, stop instead of substituting.

This means `luna_max` can be the higher-intelligence candidate than `terra_high` or `sol_low` for a Luna-shaped task, but it is not their general workload substitute. For multi-file implementation, broad tool coordination, or open debugging, use Terra; for architecture and difficult open-ended judgment, use Sol. OpenAI publishes no fixed effort multiplier for ChatGPT allowance usage, so the Max confirmation gate still applies.

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

- Choose workload fit before the profile tier. Higher effort can move a lower family above a lower-effort higher family in the intelligence ladder, but it never repairs a workload mismatch.
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
