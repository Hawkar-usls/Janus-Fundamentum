# C020 proof attempt — Policy-0A simulation lemma

## Status

`BLOCKED / NAIVE FORM UNSUPPORTED / FORMULA-CACHING BARRIER`

## Original target

The attempted statement was:

> Let `F` be an UNSAT CNF on `N` variables. If the Policy-0A root affine
> shortcut does not fire and the policy terminates with total charged work `W`,
> then there is a `Res(⊕)` refutation of `F` with size `O(W)` and depth `O(N)`.

This statement was intended to connect Policy-0A to the MAJ3 width-to-depth
lifting theorem.

## Decisive attack

Policy-0A does not merely build a DPLL tree. It caches exact unsatisfiable
residual formulas and reuses their answers under later recursive calls.

Beame, Impagliazzo, Pitassi, and Segerlind formalized this operation in
*Formula Caching in DPLL*, ACM TOCT 1(3), 2010, DOI
`10.1145/1714450.1714452`.

Their basic `FC` system checks whether the current residual formula is already
known UNSAT. They show that formula caching is naturally represented by a
formula-level calculus `CC`, and explicitly reject the naive intuition that
memoized DPLL is simply ordinary DAG Resolution. Some strengthened natural
caching systems are even exponentially more powerful than Resolution. The paper
leaves open whether the basic `FC`, `FCW`, or `FCWS` systems are p-simulated by
Resolution.

Policy-0A contains the basic exact-formula cache operation and adds local learned
resolvents. Therefore the desired `O(W)` simulation into Resolution or
`Res(⊕)` cannot be assumed from memoization alone.

Read `docs/C020_FORMULA_CACHING_BARRIER.md`.

## Finite work accounting

The new accounting audit distinguishes unique residuals from incoming cache
contexts:

```text
triangular masked K4:
  unique residual states: 3842
  recursive calls:        7077
  memo hits:              2111
  branch edges:           7076

MAJ3-lifted K4:
  unique residual states: 2427
  recursive calls:        4117
  memo hits:               888
  branch edges:           4116
```

Thus even before proof reconstruction, unique cache entries undercount the
execution graph.

```bash
python experiments/direct/janus_tear_policy0a_work_accounting.py
```

## Why charging all calls is still insufficient

Suppose `W` includes every recursive call, branch edge, memo hit, generated
resolvent, and unit event. A short formula-caching derivation may still fail to
translate to a comparably short Resolution proof because its inference lines are
whole residual formulas rather than clauses.

The missing issue is therefore structural, not only numerical:

```text
formula-level cache inference
!= established clause-level Resolution inference
```

A proof that counts all cache edges still needs a valid simulation theorem.

## Remaining syntactic problems

Even after the caching barrier is solved, a proof-emitting implementation must
record:

1. stable clause IDs;
2. parent IDs and pivots for every resolvent;
3. unit reasons and restriction events;
4. branch-combination steps;
5. exact cache formula IDs and incoming cache-check edges;
6. proof depth for every derived object;
7. an independently checkable terminal empty object.

## Clean restricted successor

Define `Policy-0T` by deleting the residual cache from Policy-0A and charging
every recursive occurrence. Its proof object is a tree of restrictions augmented
with explicit Resolution additions.

For Policy-0T, a DPLL-to-Resolution translation with size linear in full tree work
and depth `O(N)` is a plausible and standard-style target. If certified, the
MAJ3 lifting theorem would yield an exponential lower bound for Policy-0T on
lifted expander-Tseitin formulas.

That result would not automatically extend to Policy-0A.

## New targets

### T1 — Policy-0T simulation

Prove and verify:

```text
Policy-0T work W
  -> Resolution proof size O(W), depth O(N).
```

### T2 — Policy-0A caching classification

Express every Policy-0A step in an explicit `FC`/`CC`-style calculus, including
local Resolution additions, and identify the weakest known proof system that
p-simulates it.

### T3 — direct caching lower bound

Prove a lower bound for the exact Policy-0A caching calculus, or establish a
lifting theorem for it. Resolution lower bounds cannot be imported before this
step.

## Current conclusion

The original Policy-0A-to-`Res(⊕)` simulation lemma is not proved and its naive
justification has been destroyed. The MAJ3 bridge survives only for a no-cache
restricted successor or after a new theorem controlling formula caching.
