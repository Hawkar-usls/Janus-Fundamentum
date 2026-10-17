# R5 E9 — Factorization-Optimized Z3 Phase / K3,3-Cover Source Audit

Date: 2026-09-25

Authority:
`SOURCE_BOUND_REUSE__CANONICALIZATION_OF_FACTORIZATION_SEARCH__NO_FREE_POLY_PREPROCESSOR`

## G0 — Exact object

Start from a connected cubic bipartite clause-variable incidence graph

```
B=(C disjoint-union V,E).
```

Every cubic bipartite graph has a 1-factorization

```
E = M_0 disjoint-union M_+ disjoint-union M_-.
```

Choosing `M_0` as the identity matching gives the exact normalized cubic
operator

```
A=I+P+Q.
```

For a fixed factorization, the existing E9 phase test asks for

```
phi(P(i)) = phi(i)+1 mod 3,
phi(Q(i)) = phi(i)-1 mod 3.
```

The candidate stronger preprocessor considered here is:

```
DOES THERE EXIST
SOME 1-FACTORIZATION
FOR WHICH THE Z3 PHASE TEST PASSES?
```

## G1 — Internal anti-duplication

The repository already contains:

- the cubic 3-uniform / 3-regular exact-cover hard core;
- the exact `A=I+P+Q` normal form;
- the fixed-factorization commuting and Z3-phase polynomial islands;
- the PA-0001 perfect-kernel audit.

No artifact was found that source-binds optimization over all 1-factorizations.

## G2 — Canonical external object

The factorization-optimized phase question is exactly

```
K_{3,3}-COVER
```

for the cubic bipartite incidence graph, i.e. existence of a locally bijective
homomorphism / covering projection

```
B -> K_{3,3}.
```

### Exact equivalence

Suppose first that a 1-factorization
`M_0,M_+,M_-` and a phase `phi:V->Z_3` exist.

For each clause `c`, let `v_0(c)` be its `M_0` neighbor and define

```
psi(c)=phi(v_0(c)).
```

The `M_+` and `M_-` phase equations imply that the three variable
neighbors of `c` have colors

```
psi(c), psi(c)+1, psi(c)-1.
```

Conversely, because each `M_delta` is a perfect matching, at a fixed
variable `v` the three incident clauses have `psi` colors

```
phi(v), phi(v)-1, phi(v)+1.
```

Thus mapping

```
c |-> left vertex psi(c) of K_{3,3},
v |-> right vertex phi(v) of K_{3,3}
```

is locally bijective.

Conversely, given a covering `B->K_{3,3}`, label the two target parts by
`Z_3`.  Partition every input edge by the color difference

```
delta = phi(v)-psi(c) in {0,+1,-1}.
```

Local bijectivity says that at every clause and every variable there is exactly
one incident edge of each delta.  Therefore the three delta classes are perfect
matchings `M_0,M_+,M_-`.  After normalizing `M_0`, the induced `P,Q`
satisfy the E9 Z3 phase equations.

Hence

```
EXISTS FACTORIZATION WITH PHASE
iff
B COVERS K_{3,3}.
```

## G3 — Public-source audit

Kratochvil--Proskurowski--Telle established the graph-covering complexity
framework for regular targets.

Chalopin--Paulusma explicitly record the relevant classification:

```
K_{k,l}-COVER is NP-complete for k,l >= 3,
```

while the cases with `min(k,l)<=2` are polynomial.

Therefore

```
K_{3,3}-COVER
=
NP-COMPLETE.
```

This source result closes the candidate use of factorization optimization as a
known polynomial preprocessor.

The 2025--2026 graph-covering literature continues to describe fixed-target
covering / locally bijective homomorphism as a live complexity area, but the
specific `K_{3,3}` case is already covered by the older classification.

## G4 — Collision matrix

```
fixed factorization + phase test
=
JANUS POLYNOMIAL ISLAND

choose an arbitrary factorization and test phase
=
K3,3-COVER

K3,3-COVER
=
SOURCE-BOUND NP-COMPLETE

"search all factorizations until phase appears"
=
NOT A FREE POLYNOMIAL PREPROCESSOR
```

This does not say a polynomial algorithm is impossible.  A polynomial solver
for this NP-complete subproblem would itself constitute P=NP-level progress.

It only blocks treating the extra freedom of choosing the factorization as
already-available tractability.

## Audit decision

```
FACTORIZATION_OPTIMIZED_Z3_PHASE
=
EXACT COLLISION WITH K3,3-COVER

KNOWN COMPLEXITY
=
NP-COMPLETE

NEW JANUS MATH ON THIS AS A "CHEAP PREPROCESSOR"
=
STOP

ACTIVE UNIVERSAL-SOLVER FRONTIER
=
R5_E9_NONABELIAN_PHASE_INCONSISTENT_PERFECT_KERNEL_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
