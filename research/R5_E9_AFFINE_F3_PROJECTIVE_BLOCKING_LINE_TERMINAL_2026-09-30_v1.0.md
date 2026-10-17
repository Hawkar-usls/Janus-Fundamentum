# R5 E9 — Affine F3 Projective Blocking-Set Duality and Line Terminal

Date: 2026-09-30

Status:
`JANUS_EXACT_PROJECTIVE_DUAL_NORMAL_FORM__POLY_LINE_UNSAT_TERMINAL__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS NOTE GIVES A NEW POLYNOMIAL UNSAT CERTIFICATE AND AN EXACT
PROJECTIVE DUAL FORM OF THE AFFINE F3 GATE.

IT DOES NOT PROVE THAT EVERY UNSAT BLOCKING SET CONTAINS A LINE.
PG15 SAT SURVIVES THE LINE TEST, AS IT SHOULD.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Affine F3 source gate

Assume the affine system

\[
Ar=\mathbf1\quad(\mathbb F_3)
\]

is consistent and write all solutions as

\[
r=r^{(0)}+B\alpha,
\qquad \alpha\in\mathbb F_3^d,
\]

where the columns of `B` form a basis of `ker_F3(A)`.
For coordinate `i`, write `b_i` for row `i` of `B`.

The parent theorem gives

\[
A\text{ Exact-One SAT}
\iff
\exists\alpha\in\mathbb F_3^d
\quad
r_i^{(0)}+b_i\alpha\ne0\quad\forall i.
\]

Thus coordinate `i` forbids the affine hyperplane

\[
H_i=\{\alpha:b_i\alpha+r_i^{(0)}=0\}.
\]

If `b_i=0` and `r_i^(0)=0`, that coordinate is identically zero on the affine solution space, so the source is immediately UNSAT.  If `b_i=0` and `r_i^(0) != 0`, the corresponding forbidden hyperplane is empty and can be discarded.  Below assume all retained `b_i` are nonzero.

## 2. Homogeneous dual points

Homogenize affine parameter points as

\[
X_\alpha=(\alpha,1)\in PG(d,3).
\]

Associate to coordinate `i` the projective dual point

\[
p_i=[b_i:r_i^{(0)}]\in PG(d,3).
\]

Then

\[
p_i\cdot X_\alpha=0
\iff
b_i\alpha+r_i^{(0)}=0
\iff
\alpha\in H_i.
\]

Let

\[
p_\infty=[0:\cdots:0:1].
\]

Every affine parameter point `alpha` corresponds to the projective hyperplane

\[
\Pi_\alpha=\{p:p\cdot X_\alpha=0\}.
\]

Since

\[
p_\infty\cdot X_\alpha=1,
\]

`Pi_alpha` never contains `p_infty`.

Conversely every projective hyperplane not containing `p_infty` has a unique normal vector whose last homogeneous coordinate is one and therefore is `Pi_alpha` for a unique `alpha`.

## 3. Exact projective blocking-set duality

Define

\[
S=\{p_i\},
\qquad
\mathcal B=S\cup\{p_\infty\}\subseteq PG(d,3).
\]

### Theorem PBL-1

\[
\boxed{
A\text{ Exact-One UNSAT}
\iff
\mathcal B\text{ meets every projective hyperplane of }PG(d,3).
}
\]

In other words, `A` is UNSAT iff `B` is a projective blocking set with respect to hyperplanes.

### Proof

The affine source is UNSAT iff every `alpha` lies in at least one forbidden coordinate hyperplane `H_i`.  By the duality above, this is equivalent to saying that every projective hyperplane `Pi_alpha` avoiding `p_infty` meets `S`.

Every projective hyperplane containing `p_infty` automatically meets `B` at `p_infty`. Therefore all projective hyperplanes meet `B` iff all affine-parameter hyperplanes `Pi_alpha` avoiding `p_infty` meet `S`. QED.

Equivalently,

\[
A\text{ SAT}
\iff
\exists\text{ a projective hyperplane disjoint from }\mathcal B.
\]

This is exactly the full-support ternary-code condition in projective dual language.

## 4. Complete projective line gives immediate UNSAT

Every projective line in `PG(d,3)` intersects every projective hyperplane: by the dimension formula, a projective `1`-flat and a projective `(d-1)`-flat cannot be disjoint inside `PG(d,3)`.

Therefore:

### Theorem PBL-2 — line terminal

If `B` contains all four points of any projective line `PG(1,3)`, then

\[
\boxed{A\text{ is Exact-One UNSAT}.}
\]

The certificate is just four projective points together with a rank-two span check.

There are two geometrically distinct visible cases.

### Case A: the line contains `p_infty`

The other three points correspond to three affine hyperplanes with one common normal direction and all three offsets.  They are one complete parallel class and already partition the entire affine parameter space.

This is the obvious three-parallel-hyperplane UNSAT certificate.

### Case B: the line avoids `p_infty`

All four points come from source coordinates.  The four associated affine hyperplanes form one projective pencil through a common codimension-two affine flat in the dual quotient.  They still cover all affine parameter points even though no three need be parallel.

This closes the false shortcut

```text
NO COMPLETE PARALLEL CLASS
=> hyperplane cover needs Omega(d) members.
```

Already four hyperplanes can cover `F3^d` through such a pencil.

## 5. Polynomial detection

Normalize every nonzero homogeneous vector `(b_i,r0_i)` to a canonical projective representative by scaling its first nonzero coordinate to one.  Add the canonical `p_infty`.

Deduplicate equal points.  For every pair of distinct projective points `u,v`, their projective line is

\[
L(u,v)=\{[u],[v],[u+v],[u+2v]\},
\]

with projective normalization applied to each vector.

Check whether all four normalized points belong to `B`.

With hash lookup this costs at most polynomial time; even the naive implementation is `O(N^3 d)` bit/field operations, and the four-point certificate verifies in polynomial time.

If a full line is found, return UNSAT. If none is found, return

```text
NOT_IN_PROJECTIVE_LINE_TERMINAL
```

and make no SAT conclusion.

## 6. Frozen controls

### Singular UNSAT n=15

The frozen singular UNSAT source has

```text
rank_F3(A)=14,
d=1.
```

Its affine parameter projectivization contains the three finite points

```text
[1:0], [1:1], [1:2]
```

and after adjoining

```text
p_infty=[0:1]
```

one obtains the whole projective line `PG(1,3)`.

Thus PBL-2 certifies UNSAT immediately.

### PG15 SAT

The frozen PG15 SAT source has

```text
rank_F3(A)=11,
d=4.
```

Its 15 coordinate hyperplanes collapse to 11 distinct projective points after homogeneous normalization.  Adding `p_infty`, exact finite enumeration finds **no** complete projective line.

This is required: PG15 has four Exact-One witnesses and must not be rejected by the line terminal.

## 7. Finite-geometry prior-art boundary

The projective blocking-set language is classical finite geometry.  In particular, lines are the smallest obvious hyperplane-blocking sets, and Jamison/Brouwer--Schrijver type results characterize related affine blocking/almost-cover extremal problems.

Those results do **not** imply that every blocking set relevant here contains a line.  Line-free/nontrivial blocking sets exist in finite geometry, so PBL-2 is a polynomial terminal, not a universal algorithm.

The JANUS-specific contribution is the exact coordinate-preserving bridge

```text
linear-cubic Exact-One
-> affine nowhere-zero F3
-> homogeneous projective blocking set with distinguished p_infty,
```

plus the source-level witness/certificate interpretation.

## 8. New residual

After applying the line terminal, the affine-F3 hard residue can be frozen as

```text
PROJECTIVE BLOCKING-SET RESIDUAL:
  B subset PG(d,3),
  p_infty in B,
  B contains no complete projective line,
  decide whether B blocks every projective hyperplane.
```

A future universal PASS must either:

1. find a projective hyperplane disjoint from `B` and decode the Exact-One witness; or
2. construct a polynomial blocking certificate for a line-free blocking set; or
3. contract/decompose the source with a strict polynomial progress measure.

It may not assume that line-free implies nonblocking.

## 9. Ceiling

```text
AFFINE-F3 UNSAT
iff PROJECTIVE HYPERPLANE BLOCKING SET
= PROVED

COMPLETE PG(1,3) INSIDE B
=> UNSAT
= PROVED / POLYNOMIAL CERTIFICATE

THREE PARALLEL HYPERPLANES
= SPECIAL p_infty-LINE CASE

FOUR-HYPERPLANE PENCIL
= LINE-AVOIDING-p_infty CASE

FROZEN SINGULAR UNSAT
= CAUGHT BY LINE TERMINAL

PG15 SAT
= SURVIVES LINE TERMINAL

LINE-FREE BLOCKING RESIDUAL
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
