# C024-A / Issue #211 — Resolution-Sink Counterfamily

**Status:** strong formal refutation candidate for `UNIVERSAL_POLYNOMIAL_RESIDUAL_COUNT`; pending independent replay before issue closure.

**Claim ceiling:** this attacks the exact registered deterministic Policy-0A only. It does not prove `P != NP`.

## Source theorem

For theorem-matched directed `GT_n`, Beame–Impagliazzo–Pitassi–Segerlind, *Formula Caching in DPLL*, Definition 4.24 / Theorem 4.28, prove that every `FCWS` refutation requires at least `2^(n-2)` nodes; their proof identifies `2^(n-2)` distinct residual formulas at novelty level `n-2`.

The prior direct transfer to `JANUS-FC_local` was blocked by Policy-0A's extra one-layer local Resolution pass. The construction below forces that pass to spend its entire frozen attempt budget on an independent tautological sink, so it never reaches the GT core.

## Construction

For `n >= 3`, let `GT_n` be the directed source encoding and set

```text
V = n(n-1)
B = 256 n^2
p = 64 n^2.
```

For every GT variable `x`, add `B` fresh private booster clauses

```text
(x OR b[x,r]), r=1..B.
```

Give a fresh sink pivot `d` the smallest variable id. Add fresh `a,u_1..u_p,v_1..v_p` and

```text
(d OR a OR u_r),       r=1..p
(~d OR ~a OR v_s),     s=1..p.
```

Every resolution pair on pivot `d` produces a tautology containing both `a` and `~a`, so the attempts are charged and no clause is added.

## Lemma 1 — the sink permanently starves core Resolution

The theorem-matched GT core has `L_GT = 3n(n-1)^2 <= 3n^3` literal occurrences. Boosters add at most `512n^4`, and the sink adds `384n^2`. Hence the root has

```text
L0 <= 512n^4 + 3n^3 + 384n^2,
4L0 < 4096n^4 = p^2.
```

The exact Policy-0A local rule uses `attempt_budget=max(64,4L)` and visits pivots in increasing variable-id order. Pivot `d` has `p` positive and `p` negative parents. Since its `p^2` pairs exceed the entire root attempt budget, and every one is tautological, the pass terminates inside `d` with zero additions and before any later pivot.

Because zero clauses are added and all recursive restrictions/unit propagations only delete clauses/literals, every later state has `L <= L0`. The sink variables are never assigned (Lemma 2), so the same argument repeats at every state. Therefore the local Resolution layer never touches a GT-core pivot. □

## Lemma 2 — branching remains in the GT core

Every unassigned GT variable retains all `B=256n^2` booster occurrences. The two largest sink frequencies are

```text
freq(d)=freq(a)=2p=128n^2,
```

and all private leaves have frequency one after exhaustive unit propagation. Therefore any nonterminal state with a remaining core variable has a core maximum frequency strictly above every padding variable.

The deterministic most-frequent-variable rule must branch on a GT variable. Since the same `B` is added to each unassigned core variable, its relative core ordering/tie-breaking is unchanged. When a core variable is set true, its boosters disappear; when set false, its booster leaves become private true units and do not force any other core variable. □

## Lemma 3 — projection to exact Formula Caching

Let `P(K)` delete every clause containing a padding variable from a pre-resolution augmented key `K`.

The sink is core-disjoint; booster leaves occur only in their own `(x OR b)` clause and cannot force `x`; and by Lemma 1 no Resolution inference reaches the core. Thus under cumulative core restriction `rho`,

```text
P(K) = unitprop(GT_n | rho).
```

Exact equality of augmented keys implies equality after projection, so augmented caching cannot identify two different projected core residuals.

The augmented execution therefore projects to a valid exact Formula-Caching refutation of `GT_n`; exact FC is no stronger than `FCWS`. By Theorem 4.28, the projection contains at least `2^(n-2)` distinct residual formulas. Hence

```text
S(H_n) >= 2^(n-2)
```

for the padded family `H_n`. □

## Lemma 4 — input length is polynomial in n

There are `O(n^4)` variables, clauses and literal occurrences. With deterministic integer literal encoding the maximum id costs `O(log n)` bits, so

```text
N_n = O(n^4 log n).
```

Thus `2^(n-2)` is superpolynomial in `N_n`. □

## Conditional conclusion pending replay

If the implementation-parity probe confirms the exact registered ordering/budget mechanics, then Issue #211 is refuted:

```text
UNIVERSAL_POLYNOMIAL_RESIDUAL_COUNT_FOR_POLICY0A = FALSE.
```

The conditional bridge theorem remains mathematically valid, but its first premise is false for the current Policy-0A. This kills this algorithmic route to `P=NP`; it says nothing about `P!=NP` or other algorithms.

## Required replay before closure

1. exact parity with registered `limited_resolution`, unit propagation and branch selection;
2. frozen small-n check: sink exhausts attempt budget, zero additions;
3. frozen small-n check: selected branches remain core variables;
4. core-projection check after both branch values;
5. independent review of source `GT_n` Definition 4.24 and Theorem 4.28;
6. independent `n -> N` parameter audit.

Executable mirror is maintained in TOPA and should also be mirrored into this branch before final promotion.
