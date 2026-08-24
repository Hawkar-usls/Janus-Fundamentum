# C025-E2R-L1 — Support-local ER3 restricted frontier

**Status:** `OPEN_RESTRICTED_FRONTIER`.

This is a deliberately restricted testbed after the naive class-count invariant was refuted.

## Definition

For root literal `x`, set `support(x)={x}`. For each frozen B2 definition

```text
e_i <-> (a_i AND b_i)
```

set

```text
support(e_i)=support(a_i) union support(b_i).
```

A proof is `kappa-local` if every extension variable satisfies

```text
|support(e_i)| <= kappa.
```

The initial regime is `kappa=O(log N)`.

## Exact restricted target

Find an explicit polynomial-size UNSAT CNF family `F_N` such that every `ER3[kappa-local]` refutation either

1. uses superpolynomially many extension variables, or
2. does not exist inside the restriction.

Either outcome is only a lower bound for this restricted proof system. It does not transfer to unrestricted ER3.

## Why this restriction

Recursive B2 extensions form a Boolean circuit DAG, so flat semantic/case counting is unstable. Transitive root support measures locality of the auxiliary computation itself and is stable under exact dependency tracking.

Neighboring literature contains lower-bound techniques for local extension variables (e.g. heavy width for Resolution functional encodings and locality/arity bounds for Polynomial Calculus with extensions), but object identity with this ER3 restriction is not established. The first task is theorem-transfer auditing, not citation by analogy.

## Gates

```text
L1-A support calculator / verifier                    NEXT
L1-B restriction stability under partial assignments OPEN
L1-C exact relation to NW functional encodings       OPEN
L1-D heavy-width transfer or transfer refutation      OPEN
L1-E explicit restricted counterfamily                OPEN
```

## Hard boundary

```text
ER3[kappa-local] LOWER BOUND != FULL ER3 LOWER BOUND
```
