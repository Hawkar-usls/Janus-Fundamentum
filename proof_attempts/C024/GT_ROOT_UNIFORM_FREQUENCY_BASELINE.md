# C024 — Uniform GT root frequency baseline

Status: **PROVED_ARBITRARY_N**  
Scope: the canonical one-variable-per-unordered-pair encoding of `GT_n` used by exact Policy-0A.

## 1. Encoding

For each unordered pair `{a,b}` with `a<b`, one Boolean variable represents the two directed order literals:

```text
lt(a,b) = x_{a,b}
lt(b,a) = -x_{a,b}.
```

The root CNF contains:

1. one non-minimality clause `N_v` for every vertex `v`;
2. the canonicalized cyclic-transitivity clauses generated from every ordered triple of distinct vertices.

Canonicalization leaves exactly

```text
n + 2 * C(n,3)
```

clauses.

## 2. Non-minimality contribution

Fix pair variable `x_{a,b}`.

The literal `lt(b,a)=-x_{a,b}` occurs in `N_a`, and `lt(a,b)=x_{a,b}` occurs in `N_b`. No other non-minimality clause mentions the pair `{a,b}`.

Therefore

```text
nonminimality_frequency(x_{a,b}) = 2.
```

## 3. Transitivity contribution

Fix a third vertex `c` distinct from `a,b`. The unordered triple `{a,b,c}` contributes exactly two canonical cyclic-orientation clauses. Each of those two width-three clauses contains one orientation literal of every unordered pair in the triple, including `{a,b}`.

Thus `x_{a,b}` occurs twice for each choice of `c`. There are `n-2` such vertices, so

```text
transitivity_frequency(x_{a,b}) = 2(n-2).
```

## 4. Uniform baseline theorem

Adding the two independent root sources gives

```text
root_frequency(x_{a,b})
    = 2 + 2(n-2)
    = 2(n-1).
```

This value is independent of `{a,b}`.

### Theorem

For every `n>=3`, every comparison variable in the canonical root `GT_n` CNF has exactly `2(n-1)` literal occurrences.

```text
GT_ROOT_UNIFORM_FREQUENCY_BASELINE = PROVED
```

The total count cross-checks globally:

```text
C(n,2) * 2(n-1)
    = n(n-1)^2,
```

which equals

```text
n(n-1) + 3 * 2*C(n,3),
```

the literal count from the non-minimality and transitivity clause families.

## 5. Consequence for the selector theorem

At the root there are no initial unit assignments. Let `F` be the fresh clauses added by the deterministic frozen Resolution pass. For every variable `v`,

```text
post_frequency(v)
    = 2(n-1) + fresh_surplus(v),
```

provided the root post-unit stage is empty, as independently verified on the finite root frontier.

Therefore every selected-versus-unsafe frequency comparison cancels the entire original GT CNF:

```text
post_frequency(s) > post_frequency(u)
iff
fresh_surplus(s) > fresh_surplus(u).
```

The remaining root theorem is purely about the exact frozen-pass output schedule and does not require comparing the symmetric root axioms again.

## 6. Remaining policy-specific lemma

### Frozen Unsafe-Surplus Separation

For every root immediate-local unshielded occurrence and every unsafe head-internal comparison `u`, prove that the exact frozen Resolution pass gives some safe-template maximum `s` strictly greater fresh surplus:

```text
fresh_surplus(s) > fresh_surplus(u).
```

This lemma must respect the implemented pivot order, parent order, attempt budget, addition budget, width limit, and duplicate suppression. It may not assume full saturation.

## Claim boundary

The uniform root baseline `2(n-1)` is proved for arbitrary `n`. Frozen unsafe-surplus separation, selected safe-template reachability, Non-Root Wing Reachability, T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
