# C025-E2R-L1F — Crossing-extension elimination tradeoff

**Status:** `ONE_GATE_ELIMINATION_PROVED`; provider replay pending.

For a frozen B2 definition `e <-> (a AND b)`, eliminate a topologically last crossing extension by replacing a proof clause as follows:

```text
A OR e   -> {A OR a, A OR b}
A OR ~e  -> {A OR ~a OR ~b}
```

with tautology/duplicate deletion.

Every old clause yields at most two clauses. The three defining clauses of `e` become tautologies. A Resolution inference on a pivot different from `e` maps to at most two matching Resolution inferences after expansion; a Resolution inference on pivot `e` is simulated by

```text
A OR a
A OR b
B OR ~a OR ~b
------------ resolve a
A OR B OR ~b
------------ resolve b
A OR B.
```

Thus one crossing extension can be eliminated with proof-line blow-up at most factor two. Crossing variables can be eliminated in reverse introduction order. A local extension cannot depend on a crossing ancestor because transitive support is monotone by union along dependency edges.

Therefore a B2/ER3 proof of size `S` with `t` crossing extension variables yields a local-only Resolution proof of size at most

```text
S_local <= S * 2^t.
```

After mapping duplicate local functions by literal substitution, the remaining root/local axioms are contained in the NW functional encoding. If the functional encoding has Resolution lower bound `L`, then

```text
S * 2^t >= L,
t >= log2(L/S).
```

Using the formal source heavy-width theorem plus its random-expander existence lemma in a `Delta=C log n`, `m=n^(2-delta)` regime, parity remains balanced, the direct truth-table CNF has polynomial encoded size `N=n^O(1)`, and one obtains an existential family with `L=exp(n^Omega(delta)/polylog n)` after fixing constants. Consequently every polynomial-size B2/ER3 proof requires `t >= N^alpha` crossing extensions for some fixed `alpha>0`.

This is a **polynomial**, not superpolynomial, crossing-count lower bound. It does not close Issue #217.

Hard boundaries:

```text
POLYNOMIAL_CROSSING_LOWER_BOUND != SUPERPOLYNOMIAL_EXTENSION_LOWER_BOUND
CROSSING_ELIMINATION_TRADEOFF != FULL_ER3_LOWER_BOUND
P_VS_NP = OPEN
```
