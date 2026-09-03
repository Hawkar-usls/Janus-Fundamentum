# JANUS TRUMP R44AV — Dual cubic edge-cover lift

Consider exact Monotone 3-Sat-(2,2). Every variable occurs in exactly two positive clauses and exactly two negative clauses, while every clause contains exactly three distinct variables.

Construct two graphs on a common edge-label set `E=variables(F)`:

- `G+`: vertices are positive clauses; variable `x` is the edge joining its two positive clause occurrences.
- `G-`: vertices are negative clauses; the same variable `x` is the edge joining its two negative clause occurrences.

Every clause vertex has degree three, so both layers are cubic multigraphs.

For `T subseteq E`, interpret `x=true` iff `x in T`. Then

`F is SAT iff T edge-covers G+ and E\T edge-covers G-`.

This is an exact semantics-preserving structural lift, not a relaxation.

## Paired complementary-clause terminal

If every positive clause `{x,y,z}` occurs together with the negative complement `{not x,not y,not z}`, the conjunction of the pair is exactly `NAE(x,y,z)`. Döcker's Monotone 3-Sat-(2,2) work isolates this special case and proves that all such k=2 instances are satisfiable, using the variable-graph coloring route.

Thus the predicate `U(F)=0`, where `U` counts clauses missing their complement, is a polynomially recognizable exact SAT terminal condition on the fixed (2,2) class.

No descent theorem for `U` is claimed. Adding the missing complementary clause would strengthen the formula and is not an exact transition unless separately justified.

Seals:

- `DUAL_CUBIC_EDGE_COVER_LIFT = EXACT`.
- `U(F)=0 => SAT` on the fixed paired (2,2) class.
- `POLY_TERMINAL_CLASS != UNIVERSAL_DESCENT`.
- `UNPAIRED_COUNT != PROGRESS_RANK_WITHOUT_A_SAFE_TRANSITION`.
- `P_VS_NP=OPEN`.
