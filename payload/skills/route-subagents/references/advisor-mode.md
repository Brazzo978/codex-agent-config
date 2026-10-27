# Advisor after a real stall

The primary normally reasons, acts, and verifies on its own. It may request a brief independent view when focused work is failing to converge: a bug survives plausible fixes, observed behavior contradicts the current explanation, or a difficult GUI/design problem remains unresolved after concrete attempts. It should pass the attempts and evidence to the advisor so the advisor can break the impasse.

Do not consult for every thought, ordinary uncertainty, initial plan, model-agnostic task, GUI mention, or completed phase. An explicit user request for a second opinion is also sufficient, without waiting for failure.

## Select the advisor

- A normal stalled technical or design question -> Sol Medium; Low can suffice for a narrow modest blocker.
- Raise Sol to High/XHigh only when the scoped blocker needs more reasoning.
- An exceptionally difficult blocker across design, interaction, systems, or disciplines where Astra's specialized fit matters -> Astra Low.
- Increase Astra to Medium only if Low lacks the necessary depth.
- Astra High/XHigh/Max and every Ultra remain explicit-only.

The advisor can differ from the executor's family; the current executor retains its task. A Luna or Terra task does not become a full Astra task because it needs one piece of advice. Astra Low's aggregate benchmark score is lower than Sol Medium's; its use reflects a justified specialized fit and independent perspective.

## Evidence and one scoped question

Send what is not working, what has already been tried, the relevant observations/errors/screenshots, the constraints, and one precise question. Ask for a short recommendation, strongest reason, main risk/tradeoff, and the next useful check.

The resolver enforces an observed-stall input for automatic advice:

```text
python <skill-dir>/scripts/select_profile.py --mode advisor --stalled-on "The layout still clips at 200% zoom after trying both sizing approaches; screenshots show the same failure" --consult-reason "Which constraint is causing this and what should I check next?"
```

Use `--advisor-fit heavy` only for a genuinely exceptional specialized blocker. In that lane, `--difficulty deep` selects Astra Medium when Low is insufficient. If the user directly asks for advice, `--advisor-requested` permits consultation without a prior stall; it must not be set merely because the model is uncertain.

The resolver selects a profile and returns a consultation contract; it does not start agents. The primary supplies the question and performs the permitted spawn.

## Keep the consultation brief

Normally ask for at most 250 words or 3-5 bullets, unless the user asks for more. The advisor does not implement, edit files, or delegate. Read-only inspection is allowed only when needed and within the assigned scope.

Start with one consultation about the blocker. A follow-up needs a material new fact or an unresolved contradiction; no routine panel, recursive consultation, or advice at every step. The primary assesses the answer against evidence, decides what to try, and verifies whether it works.
