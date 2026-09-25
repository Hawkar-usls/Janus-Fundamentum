# R5 E10A — Mersenne Family-Wide S8 Binding

Date: 2026-09-25

Authority:
`JANUS_DERIVED_FAMILY_WIDE_S8_EXISTENCE_BINDING_INSIDE_PA0014_SCOPE`

Authorizing audit:
`PA-0014-CUBIC-LINEAGE-LIFT-RANK-GROWTH-AND-CONSTRUCTION-SOURCE-AUDIT`

Continuation:
`NM-0020-THREE-DEFECT-TORUS-PROPAGATION`

Authorized scope:
`R5_E10A_MERSENNE_TORUS_LIVE_LEAF_EXTRACTION_GATE_V1`

Checker:
`experiments/r5_e10a_mersenne_family_s8_binding.py`

## 1. Result

For every
```
L = 2^k - 1,  k >= 3,
```
let
```
M_L = M([I + P_x + P_y | 1]).
```

Using the all-Mersenne inputs already sealed by PA-0014 and NM-0020, together
with two standard source-bound structure theorems, this artifact proves

```
M_L has an S8 minor
for every k >= 3.
```

This is a family-wide existence theorem. It does not claim one fixed list of
contraction/deletion coordinates valid for every L. The finite L=7 explicit
coordinate witness from NM-0019 remains an independent positive control.

## 2. Source-bound structure theorems

### S8-free binary 3-connected classification

Erickson (Australasian Journal of Combinatorics 52 (2012), Section 4, fact
(4)), citing Choe-Wagner and Seymour, records:

```
binary + 3-connected + no S8 minor
=>
regular or F7 or F7* or AG(3,2).
```

The same structural route is used in Choe and Wagner, *Rayleigh Matroids*,
Combinatorics, Probability and Computing 15 (2006), Theorem 3.8 and its
supporting decomposition facts.

### Internally 4-connected regular classification

Mayhew, Whittle and van Zwam,
*An Obstacle to a Decomposition Theorem for Near-Regular Matroids*,
SIAM J. Discrete Math. 25(1) (2011), 271-279, DOI 10.1137/090759616,
Theorem 2.2, state:

```
internally 4-connected + regular
=>
graphic or cographic or R10.
```

This is a direct consequence of Seymour's regular-matroid decomposition
theorem.

## 3. JANUS family inputs

PA-0014 and NM-0020 give, for every Mersenne L above,

```
|E(M_L)| = L^2 + 1,
r(M_L)   = L^2 - L + 1,
r(M_L*)  = L,

M_L binary,
M_L 3-connected,
M_L has no exact 3-separation,
g*(M_L) = 4,
M_L* simple.
```

Since a 3-connected matroid with no exact 3-separation has no 3-separation
with both sides of size at least three, `M_L` is internally 4-connected.

## 4. M_L is not graphic

Assume `M_L=M(G)`. Since `M_L` is connected, discard isolated vertices
and take G connected. Then

```
|V(G)| = r(M_L)+1 = L^2-L+2,
|E(G)| = L^2+1.
```

Now

```
3|V(G)| - 2|E(G)|
=
L^2 - 3L + 4
>
0
```

for every `L>=7`. Hence the average degree is strictly below three, so
some non-isolated vertex has degree at most two. Its incident cut contains a
nonempty bond of size at most two. Therefore the graphic matroid has a
cocircuit of size at most two.

But

```
g*(M_L)=4.
```

Contradiction. Thus `M_L` is not graphic.

## 5. M_L is not cographic

Assume `M_L` is cographic. Then `M_L*` is graphic.

NM-0020's dual representation has distinct nonzero columns, so `M_L*` is
simple. It is also connected because `M_L` is 3-connected. A simple
connected graph representing `M_L*` therefore has

```
|V| = r(M_L*)+1 = L+1
```

and at most

```
C(L+1,2)=L(L+1)/2
```

edges.

But `M_L*` has the same ground-set size as `M_L`:

```
|E(M_L*)| = L^2+1,
```

and

```
L^2+1 - L(L+1)/2
=
(L^2-L+2)/2
>
0.
```

Contradiction. Thus `M_L` is not cographic.

## 6. Nonregularity

Suppose `M_L` were regular.

It is internally 4-connected, so the Mayhew-Whittle-van Zwam/Seymour theorem
forces

```
M_L graphic, cographic, or R10.
```

The first two cases were just excluded. The third is impossible because
```
|E(M_L)| >= 50 > 10 = |E(R10)|.
```

Therefore

```
M_L is nonregular.
```

## 7. Family-wide S8 conclusion

Suppose `M_L` had no `S8` minor. The source-bound S8-free classification
then gives

```
M_L regular
or
M_L ~= F7
or
M_L ~= F7*
or
M_L ~= AG(3,2).
```

The three exceptional matroids have 7, 7 and 8 elements, whereas
`|E(M_L)|>=50`. They are impossible. Regularity was excluded in Section 6.

Hence

```
boxed(M_L has an S8 minor for every L=2^k-1, k>=3).
```

No finite-size extrapolation is used.

## 8. Relation to NM-0019

For `L=7`, NM-0019 gave an explicit minor witness in the dual:

```
contract = (0,1,2)
keep     = (18,19,9,3,16,6,13,4).
```

NM-0021 is stronger in scope but different in certificate type:

```
NM-0019:
explicit coordinate witness at L=7.

NM-0021:
uniform theorem-level existence binding for every Mersenne L.
```

The latter is sufficient for the domain predicate `S8_MINOR_PRESENT`.
If a downstream component requires explicit contraction/deletion coordinates
for arbitrary L, that is a separate witness-extraction task and must not be
silently conflated with the existence theorem proved here.

## 9. Gate verdict

Freeze:

```
NM-0021
MERSENNE FAMILY-WIDE S8 BINDING
=
PASS

S8_MINOR_PRESENT
=
PROVED FOR EVERY L=2^k-1, k>=3

CERTIFICATE TYPE
=
SOURCE-BOUND STRUCTURAL EXISTENCE THEOREM
+ JANUS FAMILY INVARIANTS

UNIFORM EXPLICIT MINOR COORDINATES
=
NOT CLAIMED / NOT REQUIRED FOR THIS BINDING

MERSENNE TERMINALITY
=
PROVED BY NM-0020

MERSENNE q_graph
=
Omega(|E|) [PA-0014]

GLOBAL SOLVER PROMOTION
=
HOLD PENDING THE REMAINING END-TO-END ROUTE OBLIGATIONS

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
