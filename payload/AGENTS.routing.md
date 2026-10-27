# Dynamic subagent routing

Use `route-subagents` for explicit agent/model/effort requests or useful delegation. Automatic choices use GPT-6 Luna, GPT-6.1 Terra, and GPT-6.1 Sol. Astra Low/Medium are available for justified exceptional workflows or brief advice.

Pricing preference supplied by the user on 2026-10-27: Luna is free; Terra has half Sol's tariff for the same usage. Choose Luna for clear bounded work, Terra for normal repository execution and moderate investigation, and Sol when the capability requirement exceeds Terra or its measured task cost is lower at equal suitability. More tokens can offset a lower tariff.

Use the skill's workload/difficulty baseline as the minimum Intelligence Index. Exclude unavailable, incompatible, under-floor, and gated profiles; keep the highest fit tier. Prefer free Luna whenever it qualifies; for paid profiles choose the lowest supplied benchmark task cost. Terra and Sol can have equal task fit. The benchmark USD values are comparison proxies, not Codex credits. Data: user-supplied Artificial Analysis v4.3.2 charts dated 2026-10-27.

Defaults: Luna Max for demanding bounded work, lower efforts for positively simpler tasks; Terra High for normal execution, Medium for routine work and XHigh for subtle work. At floor 48 prefer Sol Medium ($0.21 benchmark/task) over Terra Max ($0.40). Sol High/XHigh cover floors 50/51; Sol Max requires a demonstrated indivisible extreme need. Astra starts at Low for exceptionally difficult specialized workflows and rises to Medium only when needed; Astra High/XHigh/Max and all Ultra profiles require an explicit request. Ultra has no inferred benchmark score/cost and does not itself authorize extra agents. Length and repetition do not raise effort.

Honor explicit exposed profiles exactly; an explicit model restricts optimization to that family. If unavailable, stop without substitution. Preserve scope and keep verification and synthesis with the primary agent. Read the skill catalog or run its select_profile.py resolver for cross-family choices and availability filtering.

Advisor mode is discretionary and triggered by a real stall: after focused attempts, something still fails, behavior remains unexplained, or a difficult GUI/design solution does not converge. The executor normally reasons and works independently; do not consult at every thought, uncertainty, planning step, GUI mention, or phase. Ask Sol (usually Medium) or Astra Low/Medium for one brief independent opinion on the blocker, including what failed, attempts, evidence, constraints, and a precise question. The advisor does not implement, edit files, or spawn agents. The primary retains execution, judgment, and verification. The resolver requires --stalled-on and --consult-reason for automatic advice; only a direct user request permits --advisor-requested without a prior stall. Start with one consultation; follow up only for material new facts or unresolved contradiction.

The local OpenCode/Qwen worker is explicit opt-in only: use or consult it only when the current user request names local Qwen, local OpenCode, or the local worker. Generic delegation, free usage, and quota pressure do not authorize it.

For each spawn set `task_name=<scope>_<model>_<effort>`, model codes `l/t/s/a`, effort codes `l/m/h/xh/mx/u`; lowercase and underscores only.
