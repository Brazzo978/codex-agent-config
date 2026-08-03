# Dynamic subagent routing

Use the `route-subagents` skill for every subagent routing decision, whether delegation is requested explicitly or becomes materially useful during the task.

When delegation would materially improve speed, quality, context isolation, or independent verification, select the narrowest sufficient custom-agent profile from the installed `<model>_<effort>` matrix.

- Prefer `spark_medium` for near-instant, very small coding answers, tiny edits, narrow lookups, and mechanically specified tasks with little required context.
- Prefer `luna_low` or `luna_medium` for small, repetitive, high-volume, or mechanically specified work.
- Prefer `terra_low` or `terra_medium` for fast exploration, routine implementation, and supporting work.
- Prefer `terra_high`, `terra_xhigh`, or `terra_max` for progressively harder implementation, debugging, review, and evidence-heavy analysis where speed still matters.
- Prefer `sol_medium` or `sol_high` for ambiguous multi-step work, architecture, planning, and consequential review.
- Reserve `sol_xhigh`, `sol_max`, and `sol_ultra` for genuinely difficult reasoning, high-risk decisions, or final independent verification.
- Use `luna_high`, `luna_xhigh`, `luna_max`, `luna_ultra`, `terra_ultra`, or any other uncommon combination only when the runtime explicitly exposes and supports it and the task benefits from that exact tradeoff.

Do not silently substitute another model, effort, or agent type when an explicitly selected profile is unavailable. Report the unavailable route and choose a fallback only when the user authorizes it. Keep each delegated task bounded, preserve concurrent edits, verify returned claims in the primary session, and summarize the evidence rather than raw subagent output.
