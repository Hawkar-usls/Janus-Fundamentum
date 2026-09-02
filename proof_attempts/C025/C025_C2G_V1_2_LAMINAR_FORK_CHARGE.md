# C025-C2G v1.2 — Laminar Fork-Charge Repair

**Status:** `V1_1_PAIRWISE_DISJOINT_FORK_RULE_REFUTED__V1_2_LAMINAR_COUNT_THEOREM_PROVED`.

## v1.1 barrier — nested forks cannot receive disjoint context-applicable cubes

Let ancestor fork `A` have an explored first-child context `rho_A`, and let descendant fork `D` lie inside that first-child subtree with first-child context `rho_D` extending `rho_A`.

If root clause `C_A` is falsified by `rho_A`, its falsifying cube contains every full assignment extending `rho_A`. If `C_D` is falsified by `rho_D`, its cube contains every full assignment extending `rho_D`.

Since every completion of `rho_D` also extends `rho_A`, the two charge cubes intersect. Therefore pairwise-disjoint fork charges are impossible for ancestor/descendant forks.

An exact frozen-machine finite witness is the odd-charge `K4` Tseitin CNF: the Policy-0B.1 false-first execution has root fork on edge variable 1 and a nested fork on edge variable 2 inside its false subtree.

## v1.2 repair — laminar cubes

Require the immutable charge-cube family to be laminar. For every two distinct cubes exactly one is allowed:

```text
Q(C) intersect Q(D) = empty,
Q(C) proper_subset Q(D),
Q(D) proper_subset Q(C).
```

For falsifying cubes of canonical root clauses:

```text
disjoint iff some shared variable occurs with opposite signs;
Q(C) subseteq Q(D) iff D subseteq C.
```

Both relations are polynomially checkable from explicit literal sets.

## Width-to-count theorem

For a finite laminar family of distinct nonempty falsifying cubes, each represented by a root clause of width at most `w`:

- every strict nesting chain has length at most `w+1`, because each strict cube containment adds at least one fixed falsifying coordinate;
- inclusion-minimal cubes are pairwise disjoint;
- each minimal cube has size at least `2^(n-w)`, so there are at most `2^w` of them.

Hence total family size is at most

```text
(w+1) * 2^w.
```

If `w<=c log_2 N` for a universal fixed constant `c`, the number of charges is `N^O(1)`.

## Fork-charge sufficient theorem

At every actual binary fork of the explored deterministic execution, after the first child returns UNSAT and before the second child is opened, require one fresh root reason `(C_j,pi_j)` such that:

1. `pi_j` standalone-verifies `F |= C_j`;
2. the first-child root context falsifies `C_j`;
3. `|C_j|<=c log_2 N`;
4. adding `Q(C_j)` preserves laminarity of the immutable charge ledger.

Then binary forks are at most `(w+1)2^w=N^O(1)`. From the previously proved execution-tree combinatorics,

```text
TOTAL_NODES <= (n+1)(B+1),
```

so explored state count is polynomial.

This is a **sufficient theorem only**. It does not prove universal existence, short proof bytes, or deterministic discovery.

## Remaining exact gate

Full decision-context clauses automatically have laminar geometry, but their width can be `Theta(n)`. Therefore the true C2G-v1.2 obligation is:

```text
SHORT_LAMINAR_GENERALIZATION_OF_DEEP_CONFLICT.
```

A future theorem must show that every actual fork admits such a short context-independent reason, that the reason has polynomial proof bytes, and that a deterministic algorithm finds it in globally polynomial total work.

```text
C2G_V1_1_PAIRWISE_DISJOINT_FORK_RULE  = REFUTED
C2G_V1_2_LAMINAR_RELATION             = PROVED
C2G_V1_2_LAMINAR_WIDTH_COUNT          = PROVED
C2G_V1_2_POLY_STATE_BOUND             = PROVED_AS_SUFFICIENT
C2G_V1_2_UNIVERSAL_SHORT_REASON       = OPEN
C2G_V1_2_DETERMINISTIC_DISCOVERY      = OPEN
P_VS_NP                              = OPEN
```

Arbiter: `Hawkar-usls/Demi_Head/docs/TOPA_C025_C2G_V1_2_LAMINAR_FORK_CHARGE.md`.
