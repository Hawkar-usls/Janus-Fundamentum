# C025-C2 — Branch-Mass Progress Gate

**Status:** `OPEN__GLOBAL_SEARCH_MASS_IS_THE_EXPLICIT_HIDDEN_EXPONENT`.

Policy-0B.1 freezes every non-C2 transition and has polynomial preprocessing per node, but only the trivial branch-tree bound

```text
nodes <= 2^(n+1)-1.
```

For `u` free root variables define raw assignment mass

```text
A(u)=2^u.
```

A binary root branch satisfies exactly

```text
A(child_0)+A(child_1)=A(parent).
```

Thus plain branching conserves assignment mass; it does not collapse the search space.

## Naive polynomial measures fail

```text
unassigned variables: 2(u-1)>u for u>=3;
clause count: unrelated clauses duplicate into both children;
literal volume: unrelated literal volume duplicates into both children;
assignment mass: additive, but starts at 2^n.
```

## Sufficient global theorem

If a future deterministic Policy-0B successor has a nonnegative integer frontier potential `mu` with

```text
mu(root) <= C*N^c
```

for universal fixed constants and every expansion `s -> {t_i}` obeys

```text
sum_i mu(t_i) <= mu(s)-1,
```

then frontier-potential telescoping bounds the number of expanded states by `mu(root)`.

Together with polynomial state representation and polynomial per-state work this would yield polynomial total work.

This is a sufficient lemma, not a claim that the required potential exists.

## Exhaustive-search trap

Enumerating all candidate proof/certificate bit strings up to polynomial bit length is generally exponential in that bit budget even when verification is cheap.

Therefore:

```text
POLY_CERTIFICATE_SIZE != POLY_EXHAUSTIVE_SEARCH
POLY_WORK_PER_STATE != POLY_NUMBER_OF_STATES
```

## Exact C2 target

A discovery module must provide not only deterministic verified objects, but a **global progress/amortization theorem** defeating branch-mass conservation.

```text
C025_C2_USEFUL_POLY_BOUNDED_FRONTIER_POTENTIAL = OPEN
C025_C2_DETERMINISTIC_DISCOVERY                 = OPEN
P_VS_NP                                        = OPEN
```

Arbiter source: `Hawkar-usls/Demi_Head/docs/TOPA_C025_C2_HIDDEN_SEARCH_EXPONENT_AUDIT.md`.
