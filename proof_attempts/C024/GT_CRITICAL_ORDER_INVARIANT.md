# C024 — Critical-Order Witness Candidate for GT Local-Resolution Robustness

**Status:** root form survived / raw residual cardinality form falsified / stronger labelled witness required.

## Target

C023 left one precise transfer problem:

```text
historical graph-tautology lower bound for basic Formula Caching
+ Policy-0A one-pass local Resolution
---------------------------------------------------------------
? lower bound for JANUS-FC_local
```

A polynomial local inference budget cannot be assumed harmless: one derived
clause may eliminate exponentially many future states. C024 therefore constructs
candidate witness measures and tries to destroy them before attempting an
asymptotic induction.

## Critical total orders

Every permutation of the `n` graph-tautology vertices defines a total-order
assignment that satisfies all transitivity clauses and violates exactly the
non-minimality clause of its minimum vertex. Thus there are `n!` critical orders,
partitioned into `n` classes of `(n-1)!` orders.

## Root result — survived

For each accepted root resolvent `C`, define

```text
damage_n(C) = number of critical orders falsifying C.
```

Exhaustive audits through `n=8` show:

- no accepted root resolvent destroys almost all critical orders;
- for `n=5..8`, maximum single-clause damage is `(n-1)!/2`, only `1/(2n)`
  of the complete witness space;
- the complete root pass damages only orders whose minimum is vertex `0`;
- at `GT_8`, `36,120` of `40,320` critical orders survive the complete pass;
- all other minimum classes remain intact.

Therefore raw critical-order counting is not falsified at the root.

## Residual result — falsified

The second audit reconstructs the full assignment entering every unique
Policy-0A state from branch decisions and recorded unit propagation. Its raw
state witness is:

```text
all critical orders consistent with the entry assignment.
```

The complete local pass is then applied to this set. Results:

```text
GT_4: 2 of 3 witness-bearing states lose every compatible order
GT_5: 2 of 3
GT_6: 5 of 6
GT_7: 5 of 6
```

Maximum damage is `100%` at internal states. Hence the naive residual invariant

```text
witness mass = number of entry-assignment-compatible critical orders
```

is **falsified**. Root symmetry concealed the failure; after decisions and units,
the local pass can eliminate the entire remaining raw witness set.

This does not falsify the historical Formula-Caching lower bound. It shows that
its invariant cannot be reconstructed as assignment-compatible permutation
cardinality alone.

## Required successor — proof-labelled critical orders

A viable witness must retain more than an assignment. Candidate labels include:

- the unique original minimum axiom designated as the allowed violation;
- a provenance obligation identifying which learned clauses the witness is
  permitted to falsify and why;
- a residual restriction map linking root clauses to simplified clauses;
- a charge for each local Resolution event that changes the allowed-violation
  label;
- cache compatibility conditions ensuring identical residual keys carry
  composable labels across different contexts.

The next candidate is therefore a set of pairs

```text
(total order, proof/provenance label)
```

rather than total orders alone.

## Next falsification gates

1. Construct the smallest label language closed under one recorded local
   Resolution event.
2. Test whether one pass still destroys every labelled witness at the internal
   counterexample states.
3. Reject any label whose update invokes unrestricted implication or proof
   search.
4. Require exact-cache reuse to preserve or polynomially transform labels.
5. Normalize every eventual lower bound to actual CNF encoding length.

## Artifacts

```text
experiments/direct/janus_tear_gt_critical_order_damage.py
experiments/direct/janus_tear_gt_residual_critical_damage.py
.github/workflows/validate-c024-gt-witness.yml
```

## Claim boundary

C024 has falsified one naive witness reconstruction, not the historical theorem
and not H140. No graph-tautology lower bound has yet been transferred to
Policy-0A. Nothing here resolves P versus NP or lower-bounds unrestricted clause
learning.
