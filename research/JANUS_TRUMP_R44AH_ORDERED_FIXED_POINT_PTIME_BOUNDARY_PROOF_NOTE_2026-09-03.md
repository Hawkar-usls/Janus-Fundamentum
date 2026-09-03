# JANUS TRUMP R44AH — Ordered fixed-point = PTIME boundary

## Theorem basis

The Immerman–Vardi theorem states that, over finite structures equipped with a linear order, fixed-point logic captures deterministic polynomial time.

Thus for the standard ordered relational/string encoding of 3-CNF:

`3SAT definable in ordered FP <=> 3SAT in P`.

Because 3SAT is NP-complete:

`3SAT definable in ordered FP <=> P = NP`.

## Why this matters for TRUMP

R44AG only blocks the unordered symmetry-respecting FPC model. Using the input's presented order is a legitimate escape and does not require canonization. But ordered fixed-point logic is already expressive enough to capture **all** polynomial-time algorithms. Therefore moving from unordered FPC to ordered FP does not create a weaker theorem target: exact arbitrary-3SAT decision in that model is simply another formulation of the final `P=NP` question.

So no future R-step may claim progress merely by saying that a proposed transition is expressible in, simulated by, or encoded into ordered fixed-point logic. The mathematical work must be in a **specific transition law plus a proved polynomial invariant**, not in the expressiveness of the host formalism.

Firewalls:

- `INPUT_ORDER != CANONICAL_ORDER`
- `ORDERED_FP = PTIME` (capture theorem scope)
- `HOST_MODEL_CAN_EXPRESS_ALL_PTIME != HOST_MODEL_SOLVES_3SAT`
- `3SAT_IN_ORDERED_FP <=> P_EQUALS_NP`
- `P_VS_NP=OPEN`
