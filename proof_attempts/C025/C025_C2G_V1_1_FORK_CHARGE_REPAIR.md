# C025-C2G v1.1 — Binary-Fork Charge Repair

**Status:** `V1_PER_BRANCH_REQUIREMENT_REFUTED__V1_1_FORK_CHARGE_SUFFICIENT_THEOREM_PROVED`.

## v1 counterfamily

For

`F_n=(x_1 OR ... OR x_n)`,

Policy-0B.1 false-first follows one satisfiable unary spine until UP sets the final variable true. Total branching is `O(n)`.

But every non-tautological implicate of `F_n` has width at least `n`: if a candidate clause `D` omits root `x_j`, set `x_j=1` to satisfy `F_n` and assign all literals of `D` false. Hence `F_n` does not imply `D`.

Thus requiring a fresh `O(log N)` global reason at **every** branch is universally false.

## Repair — charge only actual binary forks

In the explored DFS execution tree, a node has:

- outdegree 0 if terminal;
- outdegree 1 if the first explored child returns SAT and the sibling is never opened;
- outdegree 2 if the first child returns UNSAT and the second child is explored.

Let `B` be the number of outdegree-2 nodes. For any rooted tree with outdegree in `{0,1,2}`:

`leaves=B+1`.

With root-to-leaf depth at most `n`:

`TOTAL_NODES <= (n+1)(B+1)`.

Therefore it suffices to charge only binary forks.

At each fork, after the first child has returned UNSAT, require a fresh globally proof-carrying root clause `C_j` such that:

1. the first-child context falsifies `C_j`;
2. `|C_j|<=c log_2 N`;
3. `Q(C_j)` is disjoint from every earlier fork-charge cube;
4. `F |= C_j` is verified standalone.

Pairwise disjoint width-`w` cubes number at most `2^w`; hence `B<=N^c`, so total explored nodes are polynomial.

This is a **sufficient theorem**, not a proof of universal existence/discovery.

```text
C2G_V1_PER_BRANCH_CHARGE               = REFUTED
C2G_V1_1_FORK_TO_TOTAL_NODE_BOUND      = PROVED
C2G_V1_1_SHORT_DISJOINT_FORK_BOUND     = PROVED_AS_SUFFICIENT
C2G_V1_1_UNIVERSAL_FORK_REASON         = OPEN
C2G_V1_1_DETERMINISTIC_DISCOVERY       = OPEN
P_VS_NP                               = OPEN
```

Arbiter: `Hawkar-usls/Demi_Head/docs/TOPA_C025_C2G_V1_1_FORK_CHARGE_REPAIR.md`.
