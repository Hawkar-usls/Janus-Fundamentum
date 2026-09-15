# C025-E2R-L1E — NW-neighborhood-local ER3 extension-count lower bound

**Status:** `RESTRICTED_EXISTENTIAL_SUPERPOLY_EXTENSION_COUNT_PROVED_FROM_SOURCE_THEOREM`; deterministic explicit family remains `OPEN`.

This is a restriction-only provider theorem. It is not a lower bound for unrestricted ER3/ER/Extended Frege.

## Source lower-bound regime

Use Sokolov's heavy-width Resolution lower bound for the full functional Nisan-Wigderson encoding with

```text
m=n^(2-delta)
Delta=log^(2-delta) n
```

and balanced base functions. Choose parity as every base function; parity on `Delta` inputs is `(1/2,Delta-1)`-balanced, so it satisfies the required balance asymptotically.

For suitable graphs (existing with high probability in the source distribution) and any `b` outside the generator image, every Resolution refutation of the full functional encoding has size

```text
L_n = exp(n^Omega(delta)).
```

## Direct root CNF

For each output constraint `PARITY(Vars_i)=b_i`, include all `2^(Delta-1)` width-`Delta` clauses forbidding local assignments of the wrong parity.

The direct input length is

```text
N_n = O(m * 2^Delta * Delta * log n),
```

so

```text
log N_n = O(log^(2-delta) n).
```

Hence `L_n` is superpolynomial in the actual encoded input length `N_n`.

## Frozen proof restriction

Every B2 extension `e <-> (a AND b)` must satisfy

```text
support(a) union support(b) subseteq Vars_i
```

for one fixed NW neighborhood `Vars_i`. Every extension therefore computes a local Boolean function.

## Transfer into the full functional encoding

Associate each root variable with its projection function and each B2 extension variable with the recursively computed local Boolean function `g_e`. Map literals by

```text
x_j -> y_(projection x_j)
e   -> y_(g_e).
```

The map may identify variables that compute the same function. Ordinary Resolution is polynomially closed under literal substitutions, so this causes at most polynomial proof overhead after standard deletion of tautological images.

Every direct root clause is a semantic consequence of one local parity constraint and is therefore an axiom of the full functional encoding. Every legal B2 definitional clause is a Boolean identity among functions contained in one neighborhood and is also a semantic consequence clause in the full functional encoding.

Thus any NW-local B2 refutation of the direct parity CNF yields a Resolution refutation of the full functional encoding with polynomial overhead. The source theorem gives a superpolynomial-in-`N_n` lower bound on the B2 proof size.

## ER3 extension-count consequence

If the proof is additionally ER3 and uses `K` extension variables, the already-proved width-3 clause-universe/dedup lemma gives some refutation with the same definitions and size

```text
O(N_n + K + (n+K)^3)
```

up to standard encoding factors.

If `K<=N_n^c` for any fixed `c`, this bound is polynomial in `N_n`, contradicting the transferred heavy-width lower bound for all sufficiently large family members.

Therefore, for every fixed `c`, all sufficiently large family members require

```text
K > N_n^c
```

in every NW-neighborhood-local ER3 refutation.

## Exact boundary

```text
NW_LOCAL_ER3_SUPERPOLY_K                  = PROVED_FROM_SOURCE_THEOREM
DETERMINISTIC_EXPLICIT_GRAPH_FAMILY       = OPEN
FULL_ER3_SUPERPOLY_K                      = NOT_PROVED
GLOBAL_ISSUE_217                          = OPEN
NEXT_ESCAPE_RESOURCE                      = CROSS_NEIGHBORHOOD_MIXING
P_VS_NP                                   = OPEN
```
