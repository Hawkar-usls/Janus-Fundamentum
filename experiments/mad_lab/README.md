# JANUS MAD-LAB

Status: **EXPERIMENTAL / NOT THEOREM**  
Seal: **IANUS VIAS SERVAT.**

This directory is a deliberately isolated sandbox for speculative, adversarial,
reverse-order, numerological, physical-metaphor, unusual-search, and otherwise
high-risk research ideas that must not contaminate the proof-carrying theorem
path.

## One-way membrane

The MAD-LAB may read frozen theorem-side artifacts as test instruments, but the
theorem runtime must never import MAD-LAB code. Nothing in this directory may
be cited as a theorem merely because it passes a finite experiment or CI run.

Promotion requires a separate proof artifact outside this directory, exact
soundness/completeness scope, polynomial accounting where relevant, independent
replay, claim-ceiling audit, and an explicit human-reviewed promotion commit.
There is no automatic promotion.

## M2R pre-action jump gate

`m2r_jump_counter.py` is the MAD-LAB pre-action counter.

Before a supplied abstract action is taken, M2R computes its frozen theorem-side
raw upper bound and compares it with the current cap `N^2`:

- `LAND` — bound is at or below the cap; the action may be tested.
- `VETO` — bound is above the cap; the primary action is not taken.
- `JUMP` — after a veto, another *already supplied* cap-safe action for the same
  state is selected by a deterministic canonical order.
- `OPEN` — no supplied action is certified cap-safe; the obstruction is kept.

M2R has **veto power, not truth power**. It never invents a pivot/action, never
hides a failed state, and never upgrades an experimental route into a theorem.
A jump is **action-level**, not an instruction to skip a failed `N`. Therefore a
MAD-LAB jump cannot advance the finite theorem frontier.

The counter also records `jump_debt = max(0, raw_bound - N^2)`, cumulative debt,
maximum debt, number of landings, vetoes, jumps, and OPEN outcomes. This lets us
look for repeated obstruction geometry without contaminating theorem runtime.

## Reverse-prime probe lane

The first calibration schedule is a descending prime sequence beginning at
`N=937`: `937, 929, 919, 911, 907, ...`.

Every future action executed by this lane is expected to pass through the M2R
pre-action gate first. The prime schedule itself is only a schedule; it does not
fabricate action candidates.

These probes are stress tests only. A PASS at `N=937` does **not** prove any
intermediate N, unbounded totality, universal GPEI, SAT in P, or P=NP. Their
purpose is to reveal repeated normalized obstruction geometry that may suggest
a future general lemma.

## Labels

Every result produced here must carry:

- `lane = JANUS_MAD_LAB`
- `status = EXPERIMENTAL_NOT_THEOREM`
- `P_VS_NP = OPEN`
- `theorem_runtime_heuristics = FORBIDDEN`
- `automatic_promotion = false`

Failure is data. Weird ideas are welcome here; theorem claims are not.
