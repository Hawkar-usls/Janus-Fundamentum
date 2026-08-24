# C025-E2R-L1G — Expansion entropy and crossing-monotone escape

**Status:** `PROVIDER_REPLAY_PENDING`.

Generic polynomial elimination of crossing extensions is refuted by parity: frozen B2 computes `n`-bit parity with `3(n-1)` AND-extension gates while the exact root-only CNF of the positive parity literal contains `2^(n-1)` width-`n` clauses. Exponential decompression is therefore a real capability of extension circuits.

Freeze a narrower subsystem. A crossing skeleton is **crossing-monotone** if every crossing extension variable used as operand of another crossing extension occurs positively. Negated root/NW-local literals remain allowed.

Then every crossing macro flattens to a conjunction of signed local literals:

```text
e = l1 AND ... AND lr.
```

Hence

```text
CNFEXP(e)  = {{l1},...,{lr}}
CNFEXP(~e) = {{~l1 OR ... OR ~lr}}.
```

An ER3 line contains at most three literals, so its complete local expansion has at most a cubic product of explicit macro leaf counts and is polynomial in the explicit proof/certificate volume.

For a Resolution pivot on such a macro, from

```text
A OR e
B OR ~e
```

we obtain `A OR li` for every leaf and `B OR ~l1 OR ... OR ~lr`; resolving successively on all leaves derives `A OR B` in `r` ordinary Resolution steps. Applying this to every polynomially many expansion combination yields a polynomial-size local-only Resolution simulation of any polynomial-size crossing-monotone ER3/B2 refutation.

Combining with the established NW-parity local-functional Resolution lower bound gives the restricted consequence:

```text
POLY_SIZE_CROSSING_MONOTONE_ER3_REFUTATION = IMPOSSIBLE
```

for the existential hard family, provided the finite flattening/expansion/pivot mechanics replay passes.

Therefore a polynomial-size unrestricted escape, if one exists, must contain at least one **negative dependency edge between crossing macros**. This does not lower-bound how many such edges are needed.

Next analytical measure:

```text
Phi(literal) = log2(max(1, |exact local-CNF expansion|)).
```

High `Phi` alone is not a lower-bound measure because parity builds exponential `Phi` with linear extension count. A useful successor must combine polarity-induced expansion with NW-specific correlation/locality.

Hard boundaries:

```text
GENERIC_POLY_ELIMINATION = REFUTED_BY_PARITY
CROSSING_MONOTONE != UNRESTRICTED_CROSSING
ONE_NEGATIVE_CROSSING_EDGE_NEEDED != MANY_NEGATIVE_EDGES_NEEDED
HIGH_EXPANSION_ENTROPY != LARGE_EXTENSION_CIRCUIT
ISSUE_217 = OPEN
P_VS_NP = OPEN
```
