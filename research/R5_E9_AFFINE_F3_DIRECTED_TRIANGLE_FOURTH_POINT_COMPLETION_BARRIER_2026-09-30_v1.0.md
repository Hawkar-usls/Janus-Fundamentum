# R5 E9 — Affine F3 Directed-Triangle Fourth-Point Completion Barrier

Date: 2026-09-30

Status:
`JANUS_EXACT_PROJECTIVE_COMPLETION_BARRIER__ARBITRARY_SIZE__NO_D1_PROMOTION`

## 1. Purpose

The AF3 normal form turns a cubic Exact-One source into an affine hyperplane-avoidance problem over `F3`.  For every source row `{e1,e2,e3}`, the three coordinate-normal functionals satisfy

```text
lambda_e1 + lambda_e2 + lambda_e3 = 0
```

on the ternary source kernel, so after projective simplification they occupy three of the four points of a projective line `PG(1,3)`.

A tempting representation shortcut is that the missing fourth points might repeatedly coincide, producing a small completion set that can be contracted into a frame / gain-graph / Dowling-style quotient.

This note proves that this shortcut fails maximally on an arbitrary-size directed-triangle source class containing the Paley full-orbit families: every distinct source triangle has its own external fourth point.

This is a structural barrier only.  It does **not** rule out frame/lift representations by a different global mechanism, and it does not prove `P != NP`.

## 2. Tournament-triangle source setting

Let `T` be a tournament on a vertex set `V`, with `|V|>3`.  Let the Exact-One variables be the directed arcs of `T` (one oriented arc for every unordered vertex pair).  Let the source rows be a set `F` of distinct directed 3-cycles of `T`.

Let

```text
A in F3^{F x E(T)}
```

be the row-by-arc incidence matrix.  Every row has three ones.

Put

```text
K = ker_F3(A).
```

For every arc `e`, let

```text
lambda_e : K -> F3
```

be coordinate evaluation on `e`.

The theorem applies in particular to the square linear-cubic Paley tournament sources already materialized in this repository.

## 3. A universal gradient-plus-constant subspace of K

For a potential `p:V->F3`, define the directed gradient

```text
grad(p)_{u->v} = p(v)-p(u).
```

Every source row is a directed cycle, so the three gradient values telescope to zero.  Therefore

```text
im(grad) subseteq K.
```

Also the all-one arc vector belongs to `K`, because every source row contains three arcs and `3=0` in `F3`:

```text
1_E in K.
```

For `|V|>3`, `1_E` is not a gradient.  Indeed, if `p(v)-p(u)=1` on every directed tournament arc, then every two distinct tournament vertices have different `p`-values.  This would inject more than three vertices into `F3`, impossible.

Hence

```text
W = im(grad) direct_sum span{1_E}
```

is a subspace of `K`.

Represent `W` by a potential modulo additive constants together with one scalar `c`:

```text
y_{u->v} = p(v)-p(u)+c.
```

The coordinate functional restricted to `W` is therefore

```text
lambda_{u->v}|_W : (p,c) -> p(v)-p(u)+c.
```

## 4. Source triples are nondegenerate projective lines

Take a source triangle

```text
C = (u->v, v->w, w->u).
```

For every `y in K`, its row equation gives

```text
lambda_uv(y)+lambda_vw(y)+lambda_wu(y)=0.
```

Thus the three coordinate points lie on one projective line.

They are nonzero and pairwise nonparallel.  It is enough to restrict them to `W`.  Every restricted coordinate has `c` coefficient `1`; projective proportionality therefore forces proportionality scalar `1`, and then equality of the gradient incidence forms.  In a tournament that identifies the same directed arc.

So every source row gives exactly three distinct points of a `PG(1,3)` line.

## 5. Exact fourth point

The fourth projective point on the line through `lambda_uv` and `lambda_vw` can be represented by

```text
kappa_C = lambda_uv - lambda_vw.
```

Restrict to `W`:

```text
kappa_C(p,c)
 = [p(v)-p(u)+c] - [p(w)-p(v)+c]
 = 2p(v)-p(u)-p(w).
```

Over `F3`, `-1=2`, so projectively this is

```text
kappa_C|_W  ~  p(u)+p(v)+p(w).
```

The `c` coefficient is exactly zero.

### Theorem DT4P-1 — completion point is external

For every source triangle `C`, its fourth projective point `kappa_C` is not projectively equal to any coordinate point `lambda_e`.

Proof: after restriction to `W`, every coordinate point has nonzero `c` coefficient while `kappa_C` has zero `c` coefficient.  Projective equality would preserve zero versus nonzero.  QED.

### Theorem DT4P-2 — distinct triangles have distinct completion points

Let `C` and `C'` be two distinct source triangles.  A tournament has a unique orientation on each 3-vertex set, so distinct directed triangles have distinct underlying vertex triples.

On the potential quotient, the completion restrictions are projectively represented by the 0/1 incidence vectors of those vertex triples:

```text
chi_{V(C)}, chi_{V(C')} in F3^V,
```

and each has coordinate sum `3=0`, so it is a well-defined functional modulo constant potentials.

If they were projectively equal, the scalar is `1` or `2`.  Scalar `1` forces equal supports; scalar `2` changes every nonzero coefficient from `1` to `2` and cannot equal another 0/1 triple-incidence vector.  Hence the supports, and therefore the triangles, would coincide.  Contradiction.

Thus

```text
C != C'  =>  kappa_C != kappa_C' projectively.
```

## 6. Arbitrary-size consequence

For every tournament-triangle source in the setting above,

```text
number of source rows = |F|
number of distinct fourth completion points = |F|
completion points already among coordinate normals = 0.
```

Therefore the naive completion-compression currency has **linear defect**:

```text
one new external projective point per source row.
```

In particular, completing the source lines does not by itself produce a smaller representation.

The Paley full-orbit constructions give arbitrarily large square linear-cubic examples of this phenomenon.

## 7. Exact Paley(19) control

The companion checker reuses the frozen Paley(19) `171 x 171` source.

Exact `F3` elimination gives a 19-dimensional kernel.  Its 171 coordinate normals are projectively distinct.  For all 171 source rows the checker verifies:

```text
three source normals are distinct and collinear,
171 fourth points are pairwise projectively distinct,
0 fourth points coincide with coordinate normals,
completion multiplicity = 1 for every source row.
```

This is a finite regression only; DT4P-1/2 are symbolic arbitrary-size theorems.

## 8. What this closes and what remains open

Closed shortcut:

```text
DIRECTED-TRIANGLE SOURCE LINES
  -> fourth projective points heavily repeat
  -> small completion quotient
```

is false in the strongest possible way on this class.

Not closed:

```text
all such augmented ternary matroids are non-frame              NOT PROVED
all gain/lift representations require completion reuse         FALSE / NOT ASSUMED
some larger extension has a polynomial representation          OPEN
source-specific global decomposition beyond local completion   OPEN
```

A useful next direction is therefore to treat the completed points as **new structured objects**, rather than hoping they merge away.  On the universal subspace `W`, each completion is a vertex-triple functional `p(u)+p(v)+p(w)`, suggesting an incidence-level extension rather than a scalar defect bound.

## 9. Ceiling

```text
SOURCE 3-CIRCUIT PROJECTIVE LINE
= PROVED

FOURTH POINT FORMULA ON W
= p(u)+p(v)+p(w)

FOURTH POINT EXTERNAL TO ALL ARC COORDINATES
= PROVED

DISTINCT SOURCE TRIANGLES -> DISTINCT FOURTH POINTS
= PROVED

PALEY19
= 171 ROWS / 171 DISTINCT EXTERNAL COMPLETIONS

LOW-CARDINALITY LINE-COMPLETION QUOTIENT
= FALSIFIED ON ARBITRARY-SIZE DIRECTED-TRIANGLE FAMILY

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```