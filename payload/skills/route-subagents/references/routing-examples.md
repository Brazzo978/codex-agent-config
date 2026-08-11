# Routing examples

Use these examples only when the decision tree leaves a real ambiguity. An explicit user-selected profile always wins.

At equal effort the observed intelligence order is `Sol > Terra > Luna`; across different efforts use the dated profile ladder. Keep workload fit as the gate: a higher score does not grant another family's tool-use or ambiguity-handling role.

| Request shape | Suggested route | Why |
|---|---|---|
| Return one shell command or explain a short pasted error | `spark_medium` | Tiny, local, latency-sensitive, little context |
| Extract one fact, check syntax, or propose one obvious localized fix during a larger task | `spark_medium` | Offload a self-contained microtask to the separate Spark allowance without fragmenting the main work |
| Apply the same explicit transformation to many independent records | `luna_low` | Deterministic, repeatable, high-volume |
| Produce structured summaries from supplied documents with a fixed schema | `luna_medium` | Clear output with several checks |
| Perform a narrow task with known edge cases and stronger verification | `luna_high` | Still well specified, but requires careful checking |
| Solve a very hard, indivisible, deterministic transformation where Luna still fits | `luna_xhigh` (50, $95 AA cost); consider `luna_max` (52, $172) only if XHigh is insufficient and with confirmation | Select the cheapest Luna profile that reaches the required intelligence floor; Max remains quota-heavy |
| Map a repository area and return entry points and evidence | `terra_low` or `terra_medium` | Read-heavy exploration and tool use |
| Implement a routine feature from settled requirements | `terra_medium` (47, $192 AA cost) | Everyday execution with a clear objective; it ties the cheaper `luna_high` on intelligence but has stronger repository fit |
| Debug a multi-file regression and add tests | `terra_high` (50, $395) | It ties the cheaper `luna_xhigh` on intelligence but has the correct tool/debugging fit |
| Compare `luna_max` (52, $172) with `terra_high` (50, $395) for a multi-file regression | `terra_high` | Luna is cheaper and scores higher but fails the repository/debugging fit gate; retries would be false economy |
| Implement a security-sensitive change inside a settled design | `terra_xhigh` | Difficult execution and higher risk, but architecture is fixed |
| Choose an architecture or migration strategy with tradeoffs | `sol_high` (57, $955 AA cost) | Ambiguity and consequential judgment dominate; `terra_max` ties the score, costs more at $1,390, and lacks the natural workload fit |
| Analyze a broad cross-system failure with unclear ownership | `sol_xhigh` | Large context, subtle assumptions, deep reasoning |
| Solve one exceptionally hard algorithmic or verification problem | `sol_max` | Single indivisible problem where depth dominates latency |
| Review a high-impact completed change independently | Fresh `sol_high` or `sol_xhigh` | Judgment and context separation matter |
| Investigate three unrelated subsystems in parallel | Suitable family with `ultra`, if exposed | The work decomposes into independent lanes |
| Review an ordinary patch while preserving allowance | `terra_high` | Strong review and verification without paying for Sol Max |
| Process ten independent but identical batches under a tight budget | `luna_medium`, batched or with only a few lanes | High-volume work benefits from Luna; avoid one agent per batch |
| Router believes Max or Ultra may help, but the user did not request it | Ask before spawning | These tiers can consume allowance rapidly and must pass the budget gate |
| “Use `luna_high` for the weather lookup” | `luna_high` | Explicit selection overrides the default, if available |
| Router selects Spark implicitly but Spark is unavailable | Next cheapest suitable GPT-5.6 profile, disclosed | Implicit routing may fall back; explicit Spark requests may not |
| “Use `luna_ultra`” but runtime does not expose it | Stop | Explicit routes cannot be silently substituted |

Large size alone does not imply Sol or Ultra. A large mechanical job can still fit Luna; a large implementation with a settled design can fit Terra; a small but consequential architecture decision may require Sol.
