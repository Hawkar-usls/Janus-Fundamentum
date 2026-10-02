# R5 E9 — partial-sign projected cost bisubmodularity falsifier

Date: 2026-10-01

Status:
`JANUS_EXACT_PG15_BISUBMODULARITY_FALSIFIER__PARTIAL_SIGN_ROOF_DUALITY_SHORTCUT_CLOSED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_SIGN_CROSSING_PROJECTED_ORTHANT_COST_SUBMODULARITY_FALSIFIER_2026-10-01_v1.0.md`
- `research/R5_E9_INTEGER_LATTICE_L1_GRAVER_AUGMENTATION_GATE_2026-09-29_v1.0.md`

Checker:
- `experiments/r5_e9_sign_crossing_partial_sign_bisubmodular_falsifier.py`

## 1. Scope

The binary full-orthant projected cost is already known not to be submodular on frozen PG15 SAT.  The natural next relaxation leaves some signs unspecified and asks whether the exact projected value becomes bisubmodular on the signed-set domain.

This note falsifies that precise shortcut.  It does not rule out all discrete-convex or flow methods and does not provide a universal SAT algorithm.

## 2. Frozen integer lattice

Use the frozen PG15 incidence matrix `A` and Boolean Exact-One witness

```text
X = 1_{ {0,4,6,8,13} }.
```

The parent checker certifies

```text
rank_Q(A)=11,
ker_Z(A)=span_Z{N1,N2,N3,N4},
```

with

```text
N1 = (-1,-1, 2,-1,-1,-1,-1, 1, 1, 1,0,1,0,0,0)
N2 = (-1, 0, 1,-1,-1, 0, 0, 0, 0, 1,0,0,1,0,0)
N3 = ( 0,-1, 1,-1, 0,-1, 0, 0, 1, 0,0,0,0,1,0)
N4 = ( 0, 0, 0, 1, 0, 0,-1, 0,-1,-1,1,0,0,0,1).
```

The `4 x 4` kernel minor on coordinate columns `(0,1,3,7)` has determinant `-1`; hence this row lattice is primitive and is the full integer kernel.

Every integer feasible point is uniquely

```math
z=X+c_1N_1+c_2N_2+c_3N_3+c_4N_4,
\qquad c\in\mathbb Z^4,
```

and satisfies `Az=1`.

Put

```math
D(z):=\sum_i \operatorname{dist}(z_i,\{0,1\}).
```

For the corresponding odd point `y=2z-1`,

```math
\|y\|_1=15+2D(z).
```

Thus minimizing `D` is exactly the odd-coset L1 problem up to a positive affine rescaling.

## 3. Partial-sign value

Represent a partial sign vector by a disjoint signed pair `(P,N)`:

```text
i in P  => z_i >= 1  (equivalently y_i>0),
i in N  => z_i <= 0  (equivalently y_i<0),
i outside P union N => sign free.
```

Define

```math
\Psi(P,N)=\min\{D(z):Az=1,\ z\in\mathbb Z^{15},\ z_P\ge1,\ z_N\le0\}.
```

For signed pairs the standard bisubmodular operations are

```math
(P_1,N_1)\sqcap(P_2,N_2)
=(P_1\cap P_2,\ N_1\cap N_2),
```

and

```math
(P_1,N_1)\sqcup(P_2,N_2)
=\bigl((P_1\cup P_2)\setminus(N_1\cup N_2),
       (N_1\cup N_2)\setminus(P_1\cup P_2)\bigr).
```

Bisubmodularity would require

```math
\Psi(p)+\Psi(q)\ge\Psi(p\sqcap q)+\Psi(p\sqcup q)
```

for all signed pairs `p,q`.

## 4. Two-coordinate exact violation

Use zero-based coordinate labels and take

```text
p = ({7},  empty),
q = ({13}, empty).
```

There is no sign conflict, so

```text
p sqcap q = (empty,empty),
p sqcup q = ({7,13},empty).
```

The exact four values are

```math
\boxed{
\Psi(\varnothing,\varnothing)=0,
\quad
\Psi(\{7\},\varnothing)=0,
\quad
\Psi(\{13\},\varnothing)=0,
\quad
\Psi(\{7,13\},\varnothing)=4.
}
```

Explicit minimizers for the zero-valued terms are

```text
c=(1,0,-1,0):
z=(0,0,1,0,0,0,0,1,1,1,0,1,0,0,0),

c=(0,1,0,1):
z=(0,0,1,0,0,0,0,0,0,0,1,0,1,1,1).
```

The first has `z_7=1`; the second has `z_13=1`; both are Boolean and therefore have `D=0`.  The unconstrained value is also zero.

For the joint constraint, the coefficient vector

```text
c=(1,0,0,1)
```

gives

```text
z=(0,-1,2,0,0,-1,-1,1,1,0,1,1,0,1,1)
```

with

```text
z_7=1,
z_13=1,
D(z)=4.
```

Hence `Psi({7,13},empty)<=4`.

## 5. Exact lower bound for the joint constraint

Suppose a better jointly constrained point existed with `D(z)<=3`.
Then every coordinate obeys

```text
-3 <= z_i <= 4.
```

On the unimodular coordinate set `(0,1,3,7)`, write `q=z-X` and use the exact integer inverse of the frozen kernel minor.  Interval propagation gives the complete coefficient box

```text
c1 in [-3,4],
c2 in [-7,7],
c3 in [-8,6],
c4 in [-14,14].
```

It contains exactly

```text
8*15*15*29 = 52,200
```

integer coefficient tuples.

The checker exhausts all of them.  None simultaneously satisfies

```text
z_7>=1,
z_13>=1,
D(z)<=3.
```

Because the coefficient box is derived from every possible coordinate of every hypothetical point with `D<=3`, this is exhaustive, not sampled.

Therefore

```math
\boxed{\Psi(\{7,13\},\varnothing)=4.}
```

## 6. Bisubmodular inequality fails

Consequently

```math
\Psi(p)+\Psi(q)=0+0=0
<0+4
=\Psi(p\sqcap q)+\Psi(p\sqcup q).
```

Thus

```math
\boxed{\Psi\text{ is not bisubmodular, already on frozen PG15 SAT}.}
```

The violation occurs in a single signed orthant square: each one-coordinate requirement is individually compatible with a Boolean Exact-One model, but imposing both creates a strictly positive lattice-distance defect.

## 7. Algorithmic consequence

The route

```text
leave signs partially unspecified
-> project magnitudes exactly
-> obtain a {- ,0,+} value function
-> invoke generic bisubmodular / roof-duality minimization
```

is closed for this exact projected objective.

This strengthens the earlier binary-submodularity negative result.  Allowing an undecided sign state does not restore the required discrete-convex inequality.

It does **not** exclude richer non-bisubmodular global augmentations, symbolic Graver-like moves, threshold-changing blossom/Lehman inequalities, or another representation with a separately proved polynomial separation oracle.

## 8. New live gate

Return to the current global frontier:

```text
R5_E9_GLOBAL_SIGN_CROSSING_SOURCE_TRADE_GATE_V2
```

The next admissible candidate must cross NAE orthants globally and cannot rely on ordinary submodularity, bisubmodularity, support-minimal rational circuits, or explicit Graver enumeration.

Priority target:

```text
construct a polynomially separable threshold-changing global inequality / augmentation
for the exact NAE-transversal plus copy-flow normal form,
and hostile-test it on both the unique-model SAT lift tower and the prime UNSAT tower.
```

## 9. Firewall

```text
PG15 partial-sign value Psi          = EXACTLY DEFINED
full integer-kernel parametrization  = CERTIFIED
joint sign minimum                   = 4 EXACT
bisubmodular inequality              = STRICTLY VIOLATED
partial-sign/roof-duality shortcut   = CLOSED IN THIS FORM

GLOBAL SIGN-CROSSING AUGMENTATION     = OPEN
UNIVERSAL POLYNOMIAL SAT SOLVER       = NOT PROVED
E8_D1                                = EMPTY
P_VS_NP                              = OPEN
```
