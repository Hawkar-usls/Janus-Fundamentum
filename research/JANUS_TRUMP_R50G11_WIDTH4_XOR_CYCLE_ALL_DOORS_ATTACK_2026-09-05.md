# JANUS TRUMP R50G11 — width-4 XOR-cycle attack on the existential existing-door theorem

## Frontier after R50G10

R50G10 proves that reachable same-pivot safety is false: an explicit W3 root reaches, by one authorized U_mu R33 microstep, a W4 immediate-BVE state whose same-pivot R47J successor is a nonterminal W5 certified fixpoint. That state is nevertheless rescued by sixteen R49H pivots.

Therefore the only relevant immediate-BVE theorem is existential over **all** existing certified doors:

`IMMEDIATE_BVE_ESCAPE(F) => exists v R49H(F,v) OR exists v R47J_SAFE(F,v)`.

R50G11 attacks this theorem locally before attempting a reachable-domain proof.

## Why replace the width-3 prism by a width-4 XOR cycle?

For a W3 clause, a pivot parent residual has size at most 2, so any cross-polarity residual union has size at most 4. Thus sparse W3 XOR structure naturally creates many R49H pivots.

To block that automatic rescue, use complete width-4 parity bundles. A pivot parent residual then has size 3. If the same variable occurs in two different parity bundles that overlap in the pivot plus one additional variable, a non-tautological cross-bundle pair can have residual union size

`3 + 3 - 1 = 5`,

which lies outside the R49H width-4 sufficient condition.

The frozen core is the four-equation even-parity cycle

- E1 = {101,102,103,104}
- E2 = {103,104,105,106}
- E3 = {105,106,107,108}
- E4 = {107,108,101,102}

with every RHS equal to zero. Each variable occurs in exactly two complete width-4 parity bundles, and neighboring bundles overlap in a pair of variables. The all-false assignment is an explicit model.

## Dangerous immediate-BVE pivot

Add fresh pivot x=1 with parents

P = `(1,-101,-103,-105)`

N = `(-1,-107,-108)`.

Their exact x-resolvent is

C = `(-101,-103,-105,-107,-108)`.

If the source is pre-BVE-clean, x is the first frozen BVE pivot by variable order. Exact DP removes P,N and inserts C, creating W5.

## Exact classification

R50G11 does not assume the construction works. Execution must first verify the source preconditions. If they hold, it computes:

1. every R49H operational token, including chi_star and authorization;
2. every R47J fallback candidate, with independent replay;
3. the frozen refined U_mu step.

If no R49H and no R47J_SAFE pivot exists while the state is SAT, the all-W4/local existential existing-door theorem is refuted by an explicit OPEN obstruction. Reachability of that W4 state is a separate theorem and is not claimed in R50G11.

If any existing door succeeds, the candidate is classified as rescued and the local theorem remains open.

No heuristic, score, learned selector, probabilistic choice, or new semantic inference rule is introduced.
