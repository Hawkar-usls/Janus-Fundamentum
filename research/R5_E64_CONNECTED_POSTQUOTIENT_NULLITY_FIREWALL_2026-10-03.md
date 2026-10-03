# R5 E64 — Connected Post-Quotient Nullity Firewall

Date: 2026-10-03

Status:
`CONNECTED_POSTQUOTIENT_NULLITY_CAN_BE_NONTRIVIAL__SINGULARITY_HIGH_GIRTH_AND_SYMMETRY_DO_NOT_FORCE_TWO_LEVEL_KERNEL__P_VS_NP_OPEN`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT MOVES THE E61 NULLITY TEST PAST THE E63 RAW-GADGET FIREWALL AND APPLIES IT
DIRECTLY TO GENUINE CONNECTED SQUARE-CUBIC-LINEAR QUOTIENTS.

THE MAIN NEW CONTROLS ARE:

  TUTTE-COXETER / GQ(2,2): q=15, d=5, SAT;
  TUTTE 12-CAGE / GH(2,2): q=63, d=14, UNSAT.

BOTH ARE CONNECTED CUBIC BIPARTITE LEVI GRAPHS OF GIRTH >= 6, SO THEIR
BIADJACENCY MATRICES ARE TRUE LINEAR SQUARE-CUBIC EXACT-ONE CARRIERS.

THE SECOND CONTROL SHOWS THAT EVEN A HIGH-GIRTH, HIGHLY SYMMETRIC, CONNECTED
SINGULAR QUOTIENT CAN HAVE A LARGE REAL/RATIONAL KERNEL WHILE CONTAINING NO
REQUIRED {-1,2}-VALUED KERNEL VECTOR.

THIS REFUTES A TINY/AUTOMATIC CONNECTED-QUOTIENT NULLITY HOPE.  IT DOES NOT
PROVE AN ASYMPTOTIC LOWER BOUND d=Omega(q), AND IT DOES NOT RULE OUT A MORE
SUBTLE POST-QUOTIENT PARAMETER.

P_VS_NP = OPEN.
```

## 1. Why E64 is post-quotient

R5 E63 proved that on the frozen E12 reduction family the raw target parameters

```text
raw real nullity,
raw strong-odd-cycle packing,
raw balanced-edge modulator size
```

can all be linear because each bounded gadget contributes local structure.
Complete Boolean elimination removes that local debt and returns the source
RXC3 quotient.

Therefore E64 deliberately avoids the E12 target.  Its matrices are direct
incidence matrices of connected symmetric `v_3` configurations.  There is no
17-column gadget layer to eliminate first.

## 2. Universal two-level kernel identity

Let `R` be any square cubic 0/1 incidence matrix, so

```math
R 1 = 3 1.
```

For `x in {0,1}^q`, define

```math
y = 3x-1.
```

Then

```math
R y = 3 R x - R1.
```

Hence

```math
R x = 1
```

if and only if

```math
R y = 0,
```

with every coordinate of `y` in `{-1,2}`.

Therefore

```text
Exact-One SAT
    iff
ker_Q(R) contains a {-1,2}-valued vector.
```

This is the E61 exact kernel formulation, now tested on direct quotients.

## 3. Levi-nullity identity

For a square incidence matrix `R`, its bipartite Levi adjacency matrix is

```math
L = [[0,R],[R^T,0]].
```

A vector `(u,v)` is in `ker(L)` exactly when

```math
R v = 0,
R^T u = 0.
```

Because `R` is square,

```math
nullity(R)=nullity(R^T).
```

Therefore

```math
boxed:
nullity(L)=2 nullity(R).
```

This gives an independent spectral cross-check whenever the Levi spectrum is
known.

## 4. SAT control: Tutte-Coxeter / GQ(2,2)

Use the classical 15-by-15 incidence construction:

```text
points = 15 edges of K6,
blocks = 15 perfect matchings (1-factors) of K6,
incidence = edge belongs to perfect matching.
```

Every edge of `K6` belongs to exactly three perfect matchings and every perfect
matching contains exactly three edges.  Two perfect matchings share at most one
edge.  Thus the resulting matrix is square, cubic and linear.

The companion checker verifies exactly:

```text
q              = 15
girth(Levi)    = 8
rank_Q(R)      = 10
nullity_Q(R)   = 5
two-level y    = 6
SAT            = true
```

The six two-level kernel vectors are the six Exact-One covers, equivalently the
six 1-factorizations of `K6` in this labeling.

The known Tutte-Coxeter adjacency spectrum has zero eigenvalue multiplicity 10,
which independently agrees with

```text
nullity(Levi)=2*5=10.
```

## 5. UNSAT control: Tutte 12-cage / GH(2,2)

The companion checker reconstructs the Tutte 12-cage from the standard LCF
notation

```text
[17,27,-13,-59,-35,35,-11,13,-53,53,-27,21,57,11,-21,-57,59,-17]^7.
```

It then independently verifies:

```text
vertices        = 126
degree          = 3
connected       = true
bipartition     = 63 + 63
girth           = 12
```

and extracts the 63-by-63 biadjacency matrix `R`.

For that matrix the exact rational elimination gives

```text
rank_Q(R)      = 49
nullity_Q(R)   = 14.
```

The published graph spectrum contains zero with multiplicity 28, independently
matching

```text
nullity(Levi)=2*14=28.
```

The checker then uses the E61 free-coordinate parameterization.  There are
exactly

```text
2^14 = 16384
```

possible assignments of `{-1,2}` to the 14 free kernel coordinates.  Every
pivot coordinate is then forced rationally.

Exhausting all 16384 assignments yields

```text
two-level kernel vectors = 0.
```

Therefore this direct quotient is UNSAT:

```math
boxed:
R x = 1, x in {0,1}^63
has no solution.
```

This is substantially stronger than the old E57 warning `singular != SAT`:
here the nullity is 14, the carrier is connected, and the Levi graph has girth
12 and strong global symmetry.

## 6. What this kills

The following shortcuts are now forbidden without additional hypotheses:

```text
connected square-cubic-linear => nullity <= 1 or 2;

high girth => singular kernel is nearly one-dimensional;

high symmetry + singularity => a two-level kernel vector exists;

post-quotient singularity alone is close enough to SAT;

small random-search nullities are evidence for a universal tiny bound.
```

The random small controls that often show `d=0,1,2` were not representative of
all connected configurations.

## 7. What survives

E61 remains an exact FPT algorithm:

```text
runtime = 2^d * poly(q),
d = nullity_Q(R).
```

E64 does not invalidate it.  It shows that `d` is already 14 on a highly
structured connected quotient of size 63, so a universal polynomial theorem
cannot simply assert a tiny constant bound on connected carriers.

The strongest surviving direction is therefore not raw nullity and not mere
connectedness/girth.  A new parameter must distinguish the geometry of the
kernel from its dimension.

Candidate objects include:

```text
1. two-level defect:
   minimum number of coordinates outside {-1,2} over nonzero kernel vectors;

2. kernel sign-pattern complexity:
   number/rank of distinct coordinate sign or ratio classes forced by RREF;

3. star-complement / forced-coordinate dimension:
   how many free coordinates remain after propagating the two-level alphabet;

4. conflict-graph regular-set obstruction:
   distance from a -3 eigenspace to a (0,3)-regular equitable partition;

5. exact boundary-relation width after every bounded exact module has already
   been eliminated.
```

Any proposed invariant must be tested on both E64 controls and on the frozen E12
quotient family.

## 8. External anti-loop anchors

The Tutte-Coxeter graph is the connected cubic bipartite Levi graph on 30
vertices associated with the 15 edges and 15 perfect matchings of `K6`; its
known spectrum contains zero with multiplicity 10.

Useful external spectral cross-check:

```text
https://dalspaceb.library.dal.ca/server/api/core/bitstreams/6d9fb36e-45a2-4a21-96cd-afe880fc795f/content
```

The Tutte 12-cage is the 126-vertex cubic bipartite graph associated with the
generalized hexagon `GH(2,2)`.  MathWorld records both the LCF notation used by
the checker and the spectrum with zero multiplicity 28:

```text
https://mathworld.wolfram.com/Tutte12-Cage.html
```

House of Graphs independently identifies the same graph as graph 1397 and
publishes its adjacency representation:

```text
https://houseofgraphs.org/graphs/1397
```

These sources are external cross-checks only.  The replay checker reconstructs
and verifies the graph properties and exact rational ranks itself.

## 9. E64 exact replay

Companion checker:

```text
experiments/r5_e64_connected_postquotient_nullity_firewall.py
```

Required output:

```text
TUTTE_COXETER_GQ22: q=15 girth=8 rank=10 nullity=5 two_level=6 sat=True
TUTTE_12_CAGE_GH22: q=63 girth=12 rank=49 nullity=14 two_level=0 sat=False
R5 E64 connected post-quotient nullity firewall: PASS
```

## 10. Frontier after E64

The new frontier is narrower:

```text
raw gadget dimension                    -> forbidden by E63
raw balanced odd-cycle parameter        -> forbidden by E63
connectedness alone                     -> insufficient
high girth alone                        -> insufficient
singularity alone                       -> insufficient
small post-quotient nullity conjecture  -> false in tiny-constant form
```

What remains is the discrete intersection problem

```math
ker_Q(R) intersect {-1,2}^q != empty,
```

but now with a sharper requirement: exploit structure of the **position of the
kernel subspace relative to the two-level cube**, not only its dimension.

That is the next E65 target.
