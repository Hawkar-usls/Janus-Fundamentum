# R50G12 — three-wide-resolvent poison against alternate-pivot affine rescue

R50G11 achieved complete R49H blockage on the width-4 XOR-cycle core: every pivot had chi_star > 4. It nevertheless failed to block R47J because eliminating any one core variable normalized to an AFFINE_XOR_SAT terminal.

R50G12 keeps the same core and changes only the dangerous pivot geometry.

Let x=1 and use two positive and two negative parents:

- P1 = `(1,-101,-102,-103)`
- P2 = `(1,104,-105,-106)`
- N1 = `(-1,-107,-108)`
- N2 = `(-1,-104,-105)`

The four cross pairs have the following exact shape:

- P1 x N1 -> C11 = `(-101,-102,-103,-107,-108)`
- P1 x N2 -> C12 = `(-101,-102,-103,-104,-105)`
- P2 x N1 -> C21 = `(104,-105,-106,-107,-108)`
- P2 x N2 -> tautology because `104` and `-104` coexist.

Thus four pivot-parent clauses are removed and exactly three unique non-tautological width-5 resolvents are inserted. Clause count strictly decreases 4 -> 3, so if no earlier R33 rule exists and x is the first BVE pivot, the frozen BVE progress condition is satisfied regardless of the larger literal count.

Crucially,

`vars(C11) intersect vars(C12) intersect vars(C21) = empty`.

Hence no single core variable belongs to every wide resolvent. The intended obstruction is exact: after an alternate DP on any one core variable, at least one of the three x-resolvent templates is independent of that eliminated variable. R50G12 does not assume this suffices after full normalization; it executes every R47J pivot and independently replays it.

If all R49H tokens remain unauthorized and every R47J pivot ends nonterminal with final width > 4, the local existential existing-door theorem is refuted by a concrete SAT W4 OPEN state. Reachability from the W3 input domain is deliberately a separate gate.
