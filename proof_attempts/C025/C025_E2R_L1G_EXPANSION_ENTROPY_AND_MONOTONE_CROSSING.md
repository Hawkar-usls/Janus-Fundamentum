# C025-E2R-L1G — Expansion entropy and crossing-monotone escape

**Status:** `PROVED_IN_RESTRICTED_SCOPE__PROVIDER_PASS`.

Generic polynomial elimination of crossing extensions is refuted by parity: frozen B2 computes `n`-bit parity with `3(n-1)` AND-extension gates while the exact root-only CNF of the positive parity literal contains `2^(n-1)` width-`n` clauses. Exponential decompression is therefore a real capability of extension circuits.

Freeze a narrower subsystem. A crossing skeleton is **crossing-monotone** if every crossing extension variable used as operand of another crossing extension occurs positively. Negated root/NW-local literals remain allowed.

Then every crossing macro flattens to a conjunction of signed local literals

```text
e = l1 AND ... AND lr.
```

so

```text
CNFEXP(e)  = {{l1},...,{lr}}
CNFEXP(~e) = {{~l1 OR ... OR ~lr}}.
```

An ER3 line contains at most three literals. Therefore its local expansion contains at most the product of the distinct leaf counts of its positive crossing macros, hence polynomially many clauses in explicit proof volume. This product is an upper bound: overlapping leaf sets can collapse choices after canonicalization.

For a crossing pivot, from `A OR e` and `B OR ~e`, resolve the expanded clause `B OR ~l1 OR ... OR ~lr` successively against `A OR l1`, ..., `A OR lr` to derive `A OR B`. Componentwise expansion handles other contexts with polynomial overhead.

Thus a crossing-monotone ER3/B2 refutation of explicit size `S` converts to a local-only Resolution refutation of size `poly(S)`. Combining with the established NW-parity local-functional heavy-width lower bound yields, in the frozen existential hard-family scope,

```text
POLY_SIZE_CROSSING_MONOTONE_ER3_REFUTATION = IMPOSSIBLE.
```

Hence every polynomial-size unrestricted escape, if one exists, must contain at least one **negative dependency edge between crossing macros**. This does not lower-bound how many such edges are required.

## Preserved failed replay

First provider run:

```text
run = 32747919279
job = 97497745879
conclusion = FAILURE
```

The fixture incorrectly required exactly `2*3*4=24` distinct clauses from three overlapping macros. Canonicalization gives 11. The proof only needs the upper bound `|EXP(C)| <= product leaves`, so the fixture was repaired without changing the theorem.

## Authoritative repaired replay

```text
run        = 32748097836
job        = 97498313316
conclusion = SUCCESS
```

New gates include parity exponential expansion, crossing-monotone admission, flattening, overlap canonicalization, ER3 macro-clause polynomial upper bound, flattened pivot simulation and rejection of a negative crossing dependency.

Next front: quantify the **number/depth/placement of polarity-inverting crossing edges** together with NW-specific correlation/locality. Expansion entropy alone is insufficient because parity has exponential expansion with a linear B2 circuit.

Hard boundaries:

```text
GENERIC_POLY_ELIMINATION = REFUTED_BY_PARITY
CROSSING_MONOTONE != UNRESTRICTED_CROSSING
ONE_NEGATIVE_CROSSING_EDGE_NEEDED != MANY_NEGATIVE_EDGES_NEEDED
HIGH_EXPANSION_ENTROPY != LARGE_EXTENSION_CIRCUIT
ISSUE_217 = OPEN
P_VS_NP = OPEN
```
