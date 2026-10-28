# Dynamic subagent routing

Use `route-subagents` for explicit agent/model/effort requests or useful delegation. Automatic choices use GPT-6 Luna, GPT-6.1 Terra, and GPT-6.1 Sol. Astra Low/Medium are available for justified exceptional workflows or brief advice.

Luna is very inexpensive, not free. Use the user's nominal same-usage tariff preference Luna:Terra:Sol = 0.1:1:2 after task fit and required capability. When Terra and Sol both meet the task requirement with equal suitability, choose Terra for its half tariff. Token volume and cache mix can affect totals, so do not describe this as a measured task bill.

Intelligence is the user-supplied Artificial Analysis v5.0 index dated 2026-10-28. Available task costs belong to v4.3.2 dated 2026-10-27; retain their separate provenance and use them only as an enabled historical secondary comparison within equal tariffs. They must not override the user's Terra-before-Sol preference. These USD values are not measured v5.0 costs or Codex credits.

Keep the workload/difficulty baseline's v5.0 score as a floor. Exclude unavailable, incompatible, under-floor, and gated profiles; retain the highest fit tier, then compare nominal tariffs, secondary same-tariff task costs, and sufficient effort. Current examples: Luna Max=28 for demanding bounded work; Terra High=42 normally, XHigh=45 for subtle execution, Max=51 for complex execution. Terra Max can cover floors 46/50 when its fit equals Sol's; Sol XHigh=52 is used above Terra's capability or when suitable Terra is unavailable. Sol Max=55 requires a demonstrated indivisible extreme need.

Astra starts at Low (43) for justified exceptionally difficult specialized workflows, rising to Medium (51) only when needed. Astra High/XHigh/Max and all Ultra profiles require an explicit request. Ultra has no inferred benchmark score/cost and does not itself authorize extra agents. Length and repetition do not raise effort.

Honor explicit exposed profiles exactly; an explicit model restricts optimization to that family. If unavailable, stop without substitution. Preserve scope and keep verification and synthesis with the primary agent. Read the skill catalog or run its select_profile.py resolver for cross-family choices and availability filtering.

Advisor mode is discretionary and triggered by a real stall: after focused attempts, something still fails, behavior remains unexplained, or a difficult GUI/design solution does not converge. The executor normally reasons and works independently; do not consult at every thought, uncertainty, planning step, GUI mention, or phase. Ask Sol (usually Medium) or Astra Low/Medium for one brief independent opinion on the blocker, including what failed, attempts, evidence, constraints, and a precise question. The advisor does not implement, edit files, or spawn agents. The primary retains execution, judgment, and verification. The resolver requires --stalled-on and --consult-reason for automatic advice; only a direct user request permits --advisor-requested without a prior stall. Start with one consultation; follow up only for material new facts or unresolved contradiction.

The local OpenCode/Qwen worker is explicit opt-in only: use or consult it only when the current user request names local Qwen, local OpenCode, or the local worker. Generic delegation, free usage, and quota pressure do not authorize it.

For each spawn set `task_name=<scope>_<model>_<effort>`, model codes `l/t/s/a`, effort codes `l/m/h/xh/mx/u`; lowercase and underscores only.
