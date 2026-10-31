# R5 E9 — Kernel-Tope Raw-Radius 2-Lift Amplifier

Date: 2026-09-28

Status: `JANUS_DERIVED_CONNECTED_SAT_RAW_AUGMENTATION_RADIUS_AMPLIFIER__GEOMETRIC_RADIUS_NOT_AMPLIFIED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_KERNEL_TOPE_GREEDY_LOCAL_MINIMUM_BARRIER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_kernel_tope_raw_radius_2lift_amplifier.py`

Scientific ceiling:

```text
CONNECTED SAT SOURCES EXIST FOR WHICH THE PG15 RAW SIGN-HAMMING TRAP
AMPLIFIES TO LINEAR DISTANCE FROM EVERY LOWER-p KERNEL TOPE.

THIS KILLS FIXED / SUBLINEAR RAW-COORDINATE AUGMENTATION RADII.

IT DOES NOT KILL BOUNDED GEOMETRIC CHAMBER-GRAPH AUGMENTATION:
THE PROJECTIVE ARRANGEMENT ITSELF IS REPEATED WITH MULTIPLICITY, SO ITS
GEOMETRIC DISTANCE REMAINS THE PG15 VALUE 4.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Base trap

For `PG15_SAT_R11`, the repaired parent note proves an exact full-support kernel chamber

```text
t0 = --+---+-++--++-
```

with

```text
p(t0)=6,
n0=15,
SAT boundary p=5,
minimum raw Hamming distance from t0 to any p=5 chamber = 5,
minimum geometric chamber-graph distance = 4.
```

The four exact SAT boundary supports are also frozen in the parent checker.

The present note asks whether the raw multi-coordinate distance can remain bounded at larger `n`.

## 2. Signed 2-lift of a square incidence matrix

Let `A` be an `n x n` 0/1 matrix and choose a sign `sigma_e in {+1,-1}` for every nonzero entry. Let

```text
S_ij = sigma_(i,j) A_ij
```

be the signed matrix. Split the support into positive and negative parts

```text
P = (A+S)/2,
E = (A-S)/2,
```

so `P,E` are disjoint 0/1 matrices and `A=P+E`, `S=P-E`.

The corresponding bipartite 2-lift incidence matrix is

```text
H = [ P  E ]
    [ E  P ].
```

For vectors `u,v`,

```text
H (u,u)   = (Au,Au),
H (v,-v)  = (Sv,-Sv).
```

Therefore

```text
ker_Q(H)
=
{(u,u):u in ker_Q(A)}
  direct-sum
{(v,-v):v in ker_Q(S)}.
```

This is the rectangular/incidence analogue of the standard old/new decomposition for graph 2-lifts.

Hence if `S` is nonsingular,

```text
ker_Q(H) = {(u,u):u in ker_Q(A)}.
```

Every full-support kernel sign vector of `H` is then exactly two copies of a kernel sign vector of `A`.

## 3. A nonsingular signing always exists on the cubic source

The bipartite support graph of a cubic square source is 3-regular, hence it has a perfect matching by Hall's theorem.

Attach an independent sign variable `z_e` to every support edge. The determinant of the signed matrix is the multilinear polynomial

```text
D(z)=det(S(z))
    = sum over perfect matchings M of
      sgn(M) product_(e in M) z_e.
```

Distinct perfect matchings give distinct monomials. Because at least one perfect matching exists, `D` is not the zero multilinear polynomial.

The square-free monomials `product_(e in F) z_e` are the characters of the Boolean cube `{+1,-1}^E` and are linearly independent as functions on that cube. Consequently a nonzero multilinear polynomial cannot vanish on every signing.

Therefore:

### Theorem R2LA-1

Every square 0/1 support with a perfect matching admits an edge signing `S` with

```text
det(S) != 0.
```

In particular every cubic square Exact-One source admits a full-rank signed matrix.

No claim of novelty is made for this elementary determinant-signing observation.

## 4. Connectedness of the lift

Assume the bipartite support graph of `A` is connected and `A` is singular. Choose a signing with `S` nonsingular.

If that signing were switching-equivalent to the all-positive signing, then

```text
S = D_r A D_c
```

for diagonal `+/-1` row and column switching matrices, which would preserve rank. That is impossible because `A` is singular and `S` is nonsingular.

Thus the signing is unbalanced. For a connected signed graph, the associated 2-lift is connected iff the signing is unbalanced. Hence this full-rank signing yields a connected 2-lift.

So the amplifier does not rely on disconnected direct sums.

## 5. SAT survives the lift

If `x in {0,1}^n` satisfies

```text
A x = 1,
```

then the duplicated assignment satisfies

```text
H (x,x)
= (Px+Ex, Ex+Px)
= (Ax,Ax)
= (1,1).
```

Therefore every SAT source remains SAT after every such 2-lift.

## 6. Recursive connected family

Start from

```text
A_0 = PG15_SAT_R11.
```

Inductively, given connected cubic SAT `A_t` with nonzero rational kernel:

1. choose a full-rank signing `S_t` using Theorem R2LA-1;
2. form the connected 2-lift `A_(t+1)`;
3. since `S_t` is full rank,

```text
ker_Q(A_(t+1)) = {(u,u):u in ker_Q(A_t)}.
```

Thus

```text
n_t = 15 * 2^t,
nullity_Q(A_t)=4
```

for every `t`, and every kernel sign vector is exactly `2^t` repeated copies of a base PG15 sign vector.

The duplicated SAT witness proves every `A_t` is SAT.

## 7. Raw Hamming amplification theorem

Let `T_t` be the `2^t`-fold repetition of the base trap `t0`.

Then

```text
p(T_t)=6*2^t.
```

Every lower-`p` tope of `A_t` is the repeated lift of a lower-`p` base tope, because the entire rational kernel is symmetric. On the base, the source depth floor is 5 and the only possible lower value from 6 is the SAT boundary `p=5`.

The parent checker proves every base boundary tope is raw Hamming distance exactly 5 from `t0`. Repeating every sign `2^t` times multiplies every raw Hamming distance by `2^t`.

Therefore:

### Theorem R2LA-2

For the connected SAT family above,

```text
minimum raw Hamming distance
from T_t to any lower-p kernel tope
=
5 * 2^t
=
n_t / 3.
```

Hence no universal augmentation rule whose admissible move changes at most

```text
r(n)=o(n)
```

raw kernel-sign coordinates can guarantee a direct `p`-decreasing move from every nonboundary chamber.

In particular every fixed raw-coordinate radius is falsified.

This is stronger than the single-instance PG15 radius-5 observation.

## 8. Critical geometric caveat

The same construction **does not** amplify geometric arrangement distance.

If `B_t` is a kernel-basis matrix for `A_t`, then one may take `B_t` to be `2^t` repeated copies of `B_0`. Repeated proportional rows do not create new geometric hyperplanes; they only increase multiplicity.

Therefore the projective hyperplane arrangement of every `A_t` is geometrically identical to the base PG15 arrangement. In particular

```text
minimum geometric chamber-graph distance
from T_t to a boundary chamber
=
4
```

for every `t`.

So the admissible conclusion is precisely:

```text
RAW COORDINATE / HAMMING BOUNDED-RADIUS DESCENT = FALSIFIED,
BOUNDED GEOMETRIC CHAMBER-RADIUS DESCENT = STILL OPEN.
```

Any future claim must state the metric explicitly.

## 9. Explicit first lifts

The checker gives concrete exact controls.

At level zero, flipping the four source entries

```text
(1,1), (2,10), (6,3), (8,4)
```

in 1-based `(row,column)` indexing gives a signed `15 x 15` matrix with

```text
det(S_0) = -32.
```

The resulting connected 30-variable lift has

```text
rank_Q(A_1)=26,
nullity_Q(A_1)=4.
```

A second explicit full-rank signing on `A_1`, using 0-based checker indices

```text
(23,24), (15,0), (27,23), (5,6),
```

has

```text
det(S_1)=64.
```

Its connected 60-variable lift has

```text
rank_Q(A_2)=56,
nullity_Q(A_2)=4.
```

The checker verifies the duplicated kernel basis at both levels and raw boundary distances `10` and `20` respectively.

## 10. Prior-art audit

Bilu and Linial's 2-lift formalism supplies the standard decomposition of a lift into old/symmetric and signed/new/antisymmetric sectors; see:

- Y. Bilu and N. Linial, *Lifts, discrepancy and nearly optimal spectral gap*, Combinatorica 26 (2006), 495–519, DOI `10.1007/s00493-006-0029-7`.

JANUS is not claiming the 2-lift decomposition as new. The source-specific content here is its binding to the exact rational-kernel depth trap and the resulting metric-specific augmentation barrier.

## 11. New live gate

Freeze

```text
R5_E9_PROJECTIVE_KERNEL_GEOMETRIC_AUGMENTATION_GATE_V1
```

Input:
- connected cubic Exact-One source;
- exact rational-kernel arrangement;
- source depth floor `p>=n/3`;
- SAT iff the boundary `p=n/3` is attained;
- raw-coordinate local/radius shortcuts already excluded.

A PASS must provide one of:

1. a deterministic polynomial method finding a lower-`p` chamber within a provably polynomially searchable **geometric** neighborhood whenever one exists;
2. a global projective pivot/augmenting structure with a strict polynomial progress measure;
3. a closure/decomposition theorem that removes non-global projective local minima;
4. the full universal polynomial algorithm contract.

Forbidden:
- measuring radius only by raw repeated coordinates;
- counting proportional kernel rows as independent geometric hyperplanes;
- claiming the 2-lift family disproves bounded geometric radius;
- enumerating all chambers in unbounded nullity.

## 12. Ceiling

```text
CONNECTED SAT 2-LIFT FAMILY
= PROVED EXISTENT

n_t
= 15*2^t

nullity_Q(A_t)
= 4

RAW TRAP p
= 6*2^t

SAT BOUNDARY p
= 5*2^t

MIN RAW HAMMING DISTANCE TO LOWER-p
= 5*2^t = n_t/3

FIXED / SUBLINEAR RAW-COORDINATE AUGMENTATION RADIUS
= FALSIFIED

MIN GEOMETRIC CHAMBER DISTANCE TO BOUNDARY
= 4 FOR THIS FAMILY

BOUNDED GEOMETRIC AUGMENTATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```