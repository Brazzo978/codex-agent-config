# Dynamic subagent routing

Use `route-subagents` for explicit agent/model/effort requests or material delegation benefit.

Implicit route: first match the skill's plain-language examples; otherwise choose family by dominant need and use the static route table. For scored implicit profiles, the example/table profile sets the minimum Intelligence Index. Always cost-optimize without degrading suitability: exclude incompatible, under-floor, or gated profiles, retain the highest workload-fit tier, then choose its lowest published task cost; intelligence breaks cost ties. If the best-fit baseline cost is unpublished, preserve it instead of estimating. Spark, Ultra, and explicitly named profiles bypass numeric optimization and remain exact. Difficulty depends on cognition/risk, not length or repetitive volume. No external refresh, raw `I/C`, or API-USD/ChatGPT-credit equivalence.

Defaults: Spark=microtask only when all required context is tiny and local; reject multi-file, long-document, broad-history, tool-heavy, or cross-source context. Luna=`max` unless positively simple; Terra=`high`, `max` if complex; Sol=`medium`, up to `xhigh` normally. Astra starts at `low`, approximately Sol Max capability, only for the hardest end-to-end work where Sol is insufficient or Astra's fit matters. Astra `medium` is the only implicit escalation. Astra `high`/`xhigh`/`max`/`ultra` require an explicit user request. Sol Max requires explicit request or confirmed exceptional indivisible need. Ultra=max reasoning+delegation: Luna allowed for independent homogeneous lanes; Terra limited to 2-3 disjoint lanes with material speedup; Sol/Astra explicit-request-only.

Explicit exposed profile wins. Unavailable explicit profile => stop; no substitution. Bound scope; avoid overlapping ownership/redundant retries; primary verifies and synthesizes.

The local OpenCode/Qwen worker is explicit opt-in only. Use or consult it only when the user's current request explicitly asks for local Qwen, local OpenCode, or the local worker by name. A general request for a subagent, a simple task, free/unlimited usage, native quota pressure, or apparent task fit is not authorization. Otherwise route only among native Codex profiles. Its default agent mode may use OpenCode tools and modify the supplied workspace; give it only user-authorized scope and always verify its work.

For every spawn set `task_name=<scope>_<model>_<effort>` using model codes `sp/l/t/s/a` and effort codes `l/m/h/xh/mx/u`; lowercase and underscores only. Example: `audit_cross_system_a_xh`.
