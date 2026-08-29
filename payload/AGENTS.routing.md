# Dynamic subagent routing

Use `route-subagents` for explicit agent/model/effort requests or material delegation benefit.

Implicit route: first match the skill's plain-language examples; do not calculate fitness when one fits. If none fits, choose family by dominant need, then use the static route table. Use fitness math only for cross-family fallback/audit. Difficulty depends on cognition/risk, not length or repetitive volume. No external refresh, raw `I/C`, or API-USD/ChatGPT-credit equivalence.

Defaults: Spark=microtask only when all required context is tiny and local; reject multi-file, long-document, broad-history, tool-heavy, or cross-source context. Luna=`max` unless positively simple; Terra=`high`, `max` if complex; Sol=`medium`, up to `xhigh` normally. Sol Max requires explicit request or confirmed ultra-complex indivisible need. Ultra=max reasoning+delegation: Luna allowed for independent homogeneous lanes; Terra limited to 2-3 disjoint lanes with material speedup; Sol explicit-request-only.

Explicit exposed profile wins. Unavailable explicit profile => stop; no substitution. Bound scope; avoid overlapping ownership/redundant retries; primary verifies and synthesizes.

The local OpenCode/Qwen worker is explicit opt-in only. Use or consult it only when the user's current request explicitly asks for local Qwen, local OpenCode, or the local worker by name. A general request for a subagent, a simple task, free/unlimited usage, native quota pressure, or apparent task fit is not authorization. Otherwise route only among native Codex profiles. Its default agent mode may use OpenCode tools and modify the supplied workspace; give it only user-authorized scope and always verify its work.

For every spawn set `task_name=<scope>_<model>_<effort>` using model codes `sp/l/t/s` and effort codes `l/m/h/xh/mx/u`; lowercase and underscores only. Example: `scansione_rete_l_xh`.
