# R5 E9 — AF3 PCQ-Fixed Line-Free 2-Lift UNSAT Infinite Family

Date: 2026-09-30

Status:
`JANUS_EXACT_INFINITE_CONNECTED_LINEAR_CUBIC_UNSAT_FAMILY__PCQ_FIXED_LINE_FREE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_CLASS_FIXED_POINT_QUOTIENT_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PROJECTIVE_BLOCKING_LINE_TERMINAL_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_LINE_FREE_PROPER_BLOCKING_SOURCE_COUNTERCONTROL_2026-09-30_v1.0.md`
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`

Scientific ceiling:

```text
THIS NOTE FALSIFIES THE HOPE THAT THE CURRENT AF3 PREPROCESSING STACK
  PCQ FIXED POINT + PROJECTIVE-LINE TERMINAL
LEAVES ONLY A BOUNDED / FINITE EXCEPTION CLASS.

IT DOES NOT PROVE P!=NP.
IT DOES NOT RULE OUT A STRONGER POLYNOMIAL CONTRACTION OF THE FAMILY.
THE LIFT HISTORY ITSELF MAY BE RECOGNIZABLE BY OTHER REPRESENTATION ROUTES.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Base source A*

Use the connected square linear-cubic `n=15` source from the proper-blocking countercontrol, with rows

```text
(0,1,2)
(0,9,10)
(0,11,12)
(1,8,10)
(1,11,13)
(2,3,6)
(2,4,5)
(3,8,12)
(3,9,13)
(4,7,8)
(4,9,14)
(5,7,13)
(5,12,14)
(6,7,14)
(6,10,11).
```

The parent theorem/checker proves exactly:

```text
A* is connected / square / linear / cubic,
A* is Exact-One UNSAT,
rank_F3(A*)=11,
d_0 = nullity_F3(A*) = 4,
AF3-PCQ performs no pin and finds no complete three-offset class,
the homogenized AF3 blocking set contains no complete PG(1,3) line.
```

Choose the two nonincident incidences

```text
F_0={(0,0),(1,9)}.
```

An integer left-kernel vector is

```text
y_0=(0,-1,1,1,-1,0,0,-1,1,0,0,0,0,0,0),
```

and direct multiplication gives

```text
A*^T y_0=0,
y_0[0]=0 != -1=y_0[1].
```

The checker also verifies that deleting the two Levi edges `F_0` leaves the base Levi graph connected.

## 2. Recursive two-edge twist

Suppose `A_t` has size `n_t` and distinguished nonincident incidences

```text
F_t={(i_1,j_1),(i_2,j_2)}.
```

Let `E_t` mark exactly those incidences and put

```text
P_t=A_t-E_t.
```

Define

\[
A_{t+1}=\begin{pmatrix}
P_t&E_t\\
E_t&P_t
\end{pmatrix}.
\]

Define the next distinguished pair to be the two upper-right crossed copies:

```text
F_{t+1}={
  (i_1,j_1+n_t),
  (i_2,j_2+n_t)
}.
```

Thus

\[
n_t=15\cdot2^t.
\]

Every stage is an explicit polynomially constructible 2-cover.

## 3. Exact UNSAT preservation

Let `(u,v)` be a Boolean Exact-One model of `A_{t+1}` and put `h=u-v`.
Subtracting the two lifted block equations gives

\[
A_t h
=2\bigl(h_{j_1}e_{i_1}+h_{j_2}e_{i_2}\bigr).
\]

Since every column of `A_t` has sum three,

\[
3\sum_j h_j=2(h_{j_1}+h_{j_2}).
\]

Because each `h_j` lies in `{-1,0,1}`, the right side lies in
`{-4,-2,0,2,4}`.  The only multiple of three in this set is zero, hence

\[
h_{j_1}+h_{j_2}=0.
\]

Suppose `y_t in ker(A_t^T)` separates the distinguished rows:

\[
y_t[i_1]\ne y_t[i_2].
\]

Left-multiplication by `y_t^T` yields

\[
0=2(y_t[i_1]-y_t[i_2])h_{j_1},
\]

so `h_{j_1}=h_{j_2}=0`.  Therefore the lifted equations reduce to

```text
A_t u=1,
A_t v=1.
```

Conversely every base model lifts diagonally. Thus

\[
\boxed{A_{t+1}\text{ SAT}\iff A_t\text{ SAT}.}
\]

The separator recurses because

\[
y_{t+1}=(y_t,y_t)\in\ker(A_{t+1}^T)
\]

and its values on the two upper-sheet distinguished rows remain unequal.
Since `A_0=A*` is UNSAT, every `A_t` is UNSAT.

## 4. Connected square linear-cubic structure

A graph 2-cover preserves all vertex degrees, so every `A_t` remains square cubic.

Linearity of the source is equivalent to absence of a Levi `C4`. A graph cover cannot create a closed `C4` whose projection is not already a closed walk of length four in the base; directly, two lifted copies of distinct source rows can share at most the one column shared by their base rows, while the two copies of the same base row share no column. Hence linearity is inherited.

For connectedness use the stronger induction invariant

```text
G_t - F_t is connected,
```

where `G_t` is the Levi graph and `F_t` denotes the two distinguished incidence edges.
The base case is checked exactly.

In the lift, the untwisted edges contain two copies of `G_t-F_t`.  Deleting the two upper-right distinguished crossed edges leaves the lower-left crossed copy of each twisted edge.  At least one such crossed edge joins the two connected sheet copies. Therefore

```text
G_{t+1}-F_{t+1} is connected,
```

and in particular `G_{t+1}` is connected.

Thus every member is connected, square, linear and cubic.

## 5. Exact F3 sum/difference decomposition

Work over `F3`, where `2` is invertible. Put

\[
S_t=A_t-2E_t.
\]

Writing a lifted affine solution as `(u,v)` and using

\[
s=(u+v)/2,\qquad d=(u-v)/2,
\]

the two block equations are exactly equivalent to

\[
A_t s=\mathbf1,
\qquad
S_t d=0.
\]

Hence the lifted affine solution space is the direct product

\[
\boxed{
\{A_{t+1}r=1\}\cong
\{A_t s=1\}\times\ker_{F3}(S_t).
}
\]

For homogeneous kernels this gives

\[
\ker A_{t+1}\cong\ker A_t\oplus\ker S_t.
\]

Let

\[
d_t=\nu_{F3}(A_t).
\]

Define

\[
W_t^0=\{z\in\ker A_t:z_{j_1}=z_{j_2}=0\}.
\]

Two coordinate equations lower dimension by at most two, so

\[
\dim W_t^0\ge d_t-2.
\]

For `z in W_t^0`, `E_tz=0`, therefore

\[
S_tz=(A_t-2E_t)z=0.
\]

Thus

\[
\nu_{F3}(S_t)\ge d_t-2
\]

and

\[
\boxed{d_{t+1}\ge2d_t-2.}
\]

Since `d_0=4`, induction gives

\[
\boxed{
d_t\ge2+2^{t+1}
=2+\frac{2}{15}n_t
=\Omega(n_t).
}
\]

So the AF3 residual dimension is not merely unbounded; it grows linearly along the family.

## 6. Projective lift map

Let a base affine parameterization be

\[
s=r^{(0)}+B\alpha,
\]

and let `C beta` parameterize `ker S_t`.  The lifted coordinates are

\[
u_j=r_j^{(0)}+b_j\alpha+c_j\beta,
\qquad
v_j=r_j^{(0)}+b_j\alpha-c_j\beta.
\]

The corresponding homogenized projective source points can therefore be written

\[
\widehat p_j^+=(b_j,c_j,r_j^{(0)}),
\qquad
\widehat p_j^-=(b_j,-c_j,r_j^{(0)}),
\]

plus the distinguished point

\[
\widehat p_\infty=(0,0,1).
\]

There is a linear projection deleting the new `c` block:

\[
\pi:(b,c,r)\mapsto(b,r).
\]

It satisfies

\[
\pi(\widehat p_j^+)=
\pi(\widehat p_j^-)=p_j,
\qquad
\pi(\widehat p_\infty)=p_\infty.
\]

Every lifted blocking-set point has nonzero image under `pi`.

## 7. PCQ fixed point is inherited

At an AF3-PCQ fixed point, a two-offset projective-normal class is projectively the statement that

```text
p_infty and two distinct source points are collinear.
```

Suppose such a triple existed in the lifted blocking set and let `L` be their projective line.
The restriction of `pi` to the two-dimensional vector space underlying `L` cannot have rank one: then the projective images of `p_infty` and the source points would coincide, impossible because the base source normal is nonzero whereas `p_infty` has zero normal block.
Therefore the restriction has rank two and induces a projective isomorphism from `L` onto a base projective line.
The images give `p_infty` and two distinct base source points collinear, contradicting the base PCQ fixed-point invariant.

A lifted coordinate cannot acquire zero affine normal because its projected normal contains the nonzero base normal.
Hence neither a two-offset pin class nor a complete three-offset class can be created by the lift.

Therefore:

\[
\boxed{
\text{AF3-PCQ fixed point is preserved by the recursive lift.}
}
\]

## 8. Projective line-freeness is inherited

Suppose the lifted blocking set contained all four points of a projective line `L=PG(1,3)`.
Restrict `pi` to the two-dimensional vector space underlying `L`.

If its rank is two, it is projectively bijective on `L`, so the four lifted blocking points map to all four points of a complete projective line in the base blocking set, contradiction.

If its rank is one, the restriction has a one-dimensional vector kernel.  That kernel is one projective point of `L`.  Since the whole line is assumed contained in the lifted blocking set, that kernel point would be a lifted blocking-set point with zero image under `pi`.  But no lifted source point and not `p_infty` has zero image. Contradiction.

Rank zero is impossible because `p_infty` has nonzero image.

Thus

\[
\boxed{
\text{projective-line-free is preserved by the recursive lift.}
}
\]

Since the base proper-blocking source is PCQ-fixed and line-free, every `A_t` survives both current AF3 terminals.

## 9. Infinite proper-blocking residual family

Combining the previous sections, for every `t>=0`:

```text
n_t = 15*2^t,
connected = true,
square cubic = true,
linear = true,
Exact-One = UNSAT,
AF3 affine dimension d_t >= 2 + (2/15)n_t,
AF3-PCQ pins = none,
AF3 complete parallel cover = none,
AF3 projective-line terminal = no line.
```

Because each member is UNSAT, its homogenized source set plus `p_infty` is a projective blocking set.  Because no complete projective line is present, it lies in the proper/line-free blocking residual.

### Theorem AFL2-1

There is therefore an explicit infinite connected square linear-cubic Exact-One UNSAT family of unbounded size and linear AF3 affine dimension that survives both the parallel-class fixed-point quotient and the projective-line UNSAT terminal.

This falsifies the proposed shortcut

```text
AF3-PCQ fixed
+ no projective line
=> only bounded-size exceptional UNSAT cores.
```

## 10. Finite exact regression

The companion checker builds levels `t=0..4` and verifies exact arithmetic over `F3`:

```text
t=0: n=15,  d=4,  PCQ pins=0, line=false
t=1: n=30,  d=6,  PCQ pins=0, line=false
t=2: n=60,  d=10, PCQ pins=0, line=false
t=3: n=120, d=18, PCQ pins=0, line=false
t=4: n=240, d=34, PCQ pins=0, line=false
```

It also verifies at every tested level:

```text
row/column degree 3,
linearity,
Levi connectedness,
G_t-F_t connectedness,
left-kernel separator inheritance,
and the recurrence lower bound.
```

The displayed equalities for `d_t` are finite regression facts only.  The arbitrary-size theorem uses only the proved lower bound `d_{t+1}>=2d_t-2`.

## 11. Scope firewall

This family is a barrier to the **current AF3 preprocessing stack**, not a hardness theorem.
In particular, do not infer:

```text
proper blocking residual is NP-hard from this family alone;
2-lift history is unrecognizable;
no stronger exact contraction exists;
P != NP.
```

The family was deliberately built by a visible representation operation.  A future universal solver is allowed to recognize and contract such lifts; if it does so in polynomial total cost, this family becomes a positive control for that stronger route.

## 12. New live finite-field gate

The finite-field route must now handle an arbitrary-size residual of the form

```text
connected square linear-cubic source,
Ar=1 consistent over F3,
PCQ fixed point,
one forbidden offset per projective normal,
blocking set line-free,
source triples give rooted four-circuit relations,
affine dimension may be Theta(n).
```

Freeze the next gate as

```text
R5_E9_AFFINE_F3_PROPER_BLOCKING_GLOBAL_CONTRACTION_GATE_V2
```

Required PASS: construct in deterministic polynomial time either

1. a projective hyperplane disjoint from the blocking set and decode a Boolean Exact-One witness; or
2. a polynomially discoverable blocking certificate / exact contraction with strict progress and witness reconstruction; or
3. a source-specific decomposition into already proved polynomial terminals.

A claimed PASS must replay both the finite `A*` source and the present infinite 2-lift family.

## 13. Ceiling

```text
A* BASE UNSAT / PCQ-FIXED / LINE-FREE = PROVED BY PARENT
TWO-EDGE SAT CONTRACTION UNDER LEFT-KERNEL SEPARATION = PROVED
RECURSIVE UNSAT PRESERVATION = PROVED
CONNECTED / LINEAR / CUBIC = PROVED
F3 DIMENSION RECURRENCE d' >= 2d-2 = PROVED
PCQ FIXED-POINT PRESERVATION UNDER THE LIFT = PROVED
PROJECTIVE LINE-FREE PRESERVATION UNDER THE LIFT = PROVED

INFINITE AF3 PROPER-BLOCKING RESIDUAL FAMILY = PROVED
AFFINE DIMENSION = OMEGA(n)

CURRENT PCQ + LINE TERMINALS AS UNIVERSAL AF3 SOLVER = CLOSED
STRONGER PROPER-BLOCKING GLOBAL CONTRACTION = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```