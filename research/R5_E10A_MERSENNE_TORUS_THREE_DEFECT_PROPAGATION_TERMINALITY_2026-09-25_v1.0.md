# R5 E10A — Mersenne Torus Three-Defect Propagation and Terminality

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_MERSENNE_TORUS_TERMINALITY_INSIDE_PA0014_SCOPE__NO_FULL_CLOSURE_SHORTCUT`

Authorizing audit:
`PA-0014-CUBIC-LINEAGE-LIFT-RANK-GROWTH-AND-CONSTRUCTION-SOURCE-AUDIT`

Authorized scope:
`R5_E10A_MERSENNE_TORUS_LIVE_LEAF_EXTRACTION_GATE_V1`

Predecessor:
`NM-0019-TORUS-L7-LIFT-RANK-STRESS`

Checker:
`experiments/r5_e10a_mersenne_torus_three_defect_propagation.py`

## 1. Result

For every Mersenne circumference

```
L = 2^k - 1,  k >= 3,
```

let

```
H_L = I + P_x + P_y
M_L = M([H_L | 1])
```

on the ordinary ground set `G=Z_L^2` plus the distinguished element `f`.

Using the PA-0014 source-bound/derived inputs

```
rank(M_L) = L^2-L+1,
rank(M_L*) = L,
g*(M_L) = 4,
```

and the Rule-60 Mersenne periodicity already source-bound by PA-0014, this
artifact proves

```
M_L is 3-connected
and
M_L has no exact 3-separation
```

for every `k>=3`.

The proof does **not** use the previously tempting shortcut

```
arbitrary exact 3-separation
 -> choose a representative with both sides coclosed.
```

No such simultaneous-coclosure assertion is needed.

The core new statement is the three-defect torus propagation lemma:

> If `S subset Z_L^2`, `|S|<=3`, and every plaquette disjoint from `S`
> is monochromatic under a two-colouring of ordinary coordinates, then one
> colour occurs on at most `|S|+3<=6` ordinary coordinates.

In fact the equality graph outside `S` has one principal component and total
mass at most three outside that component.

## 2. Dual intersection reduction

Let

```
E=A disjoint-union B,   f in A
```

be a putative separation, and work in a binary representation of

```
N = M_L*.
```

Let the dual columns be `z_e`, and put

```
U = span_N(A),
V = span_N(B),
J = U intersect V.
```

Connectivity is self-dual, and for a represented matroid

```
dim(U intersect V)
=
r_N(A)+r_N(B)-r_N(E)
=
lambda(A).
```

Hence if `lambda(A)=t<=2`,

```
dim J = t.
```

PA-0014 gives the dual-column form

```
ordinary e: z_e = (sig(e),1),
f:          z_f = (0,1),
```

with all ordinary columns nonzero and pairwise distinct, and distinct from
`z_f`. In particular `N` is simple.

Every cubic star of `[H_L|1]` is a weight-four cocycle of `M_L`, hence a
cycle of `N`. For every plaquette

```
T_p={p,p+e_x,p+e_y}
```

we therefore have

```
z_f + sum_{e in T_p} z_e = 0.
```

Project to `W/J`. Since `(U/J) intersect (V/J)=0`, the `B` part of the
plaquette relation must vanish in the quotient:

```
sum_{e in T_p intersect B} z_e in J.
```

Define

```
S_J
=
{e ordinary : z_e in J}
union
{e ordinary : z_e+z_f in J}.
```

If a plaquette is mixed:

- one `B` element `e` implies `z_e in J`, so `e in S_J`;
- two `B` elements imply for the sole ordinary `A` element `e` that
  `z_e+z_f in J`, so `e in S_J`.

Thus

```
EVERY MIXED PLAQUETTE INTERSECTS S_J.
```

The two maps into `J\{0}` are injective, and their images are disjoint because
their last bits are respectively `1` and `0`. Therefore

```
|S_J| <= |J\{0}| = 2^t-1.
```

In particular:

```
t=0 -> |S_J|=0,
t=1 -> |S_J|<=1,
t=2 -> |S_J|<=3.
```

So every `S_J`-free plaquette is monochromatic.

## 3. Plaquette graph

Let `Q_L` have one vertex for each plaquette anchor `p in Z_L^2`, with two
anchors adjacent exactly when their plaquettes share an ordinary coordinate.

Then

```
Q_L
=
Cay(
  Z_L^2,
  { +/-e_x, +/-e_y, +/-(e_x-e_y) }
),
```

the six-regular triangular torus.

An ordinary defect `s` deletes exactly the three plaquette nodes

```
D_s = {s, s-e_x, s-e_y}.
```

These three nodes form one elementary triangle in `Q_L`.

For a defect set `S` define

```
R(S)=union_{s in S} D_s.
```

The surviving plaquette nodes are exactly the `S`-free plaquettes.

## 4. Exact local classification

The only asymptotic-looking part is actually finite because `|S|<=3`.

Two defect triangles can belong to the same connected deleted cluster only
when their centers differ by one of exactly 18 offsets. Enumerating connected
center sets up to translation gives exactly

```
1 defect:   1 shape
2 defects:  9 shapes
3 defects: 99 shapes.
```

The checker exhausts all `109` shapes in the infinite triangular lattice and
computes the bounded components of their complements.

Result:

```
1 defect:  1/1 shapes have no bounded hole
2 defects: 9/9 shapes have no bounded hole

3 defects:
  98/99 shapes have no bounded hole
   1/99 shape has exactly one bounded component,
        and that component is one plaquette node.
```

Normalize that unique hole to `p=(0,0)`. The unique defect-center set is

```
{(-1,1),(1,-1),(1,1)}.
```

This is a finite exhaustive certificate, not a sample over torus sizes.

### Why the plane classification applies to every L>=7

Each `D_s` has diameter one in the plaquette lattice. If up to three such
triangles form one connected deleted component, consecutive defect centers
differ by one of the 18 certified touching offsets, each with coordinate
magnitude at most two. Hence the entire connected deleted component has
coordinate span strictly below `L` for every `L>=7`; it lifts to an embedded
local cluster of the infinite triangular lattice.

Different connected deleted components are disjoint local obstacles on the
torus. The complement outside small disjoint disk neighbourhoods of those
local obstacles is connected. Any non-principal component of `Q_L-R(S)` is
therefore a bounded hole of one lifted local deleted component.

Since a bounded hole needs all three defects, at most one such hole exists.

Therefore for every `L>=7` and every `|S|<=3`:

```
Q_L-R(S)
=
one principal component
plus at most one singleton plaquette component.
```

As an independent finite torus replay, the checker exhausts all

```
sum_{j=0}^3 C(49,j) = 19,650
```

defect sets on `L=7` and obtains the same conclusion.

## 5. From plaquette components to ordinary equality components

Every surviving plaquette identifies its three ordinary coordinates. Adjacent
surviving plaquettes share an ordinary coordinate outside `S`; therefore every
plaquette component induces one ordinary equality component.

There is one additional possibility: an ordinary coordinate `v notin S` may
belong to no surviving plaquette. This happens exactly when

```
D_v subset R(S).
```

Normalize `v=0`. The checker exhausts the finite local cover problem:

```
1 defect: impossible
2 defects: impossible
3 defects: exactly 8 cover triples.
```

For each of those eight triples, `v` is the **only** additional ordinary
coordinate with `D_v subset R(S)`.

Moreover none of the eight isolated-coordinate patterns is the unique
singleton-plaquette-hole pattern. Conversely the unique plaquette-hole pattern
creates no additional isolated ordinary coordinate.

Hence the ordinary equality graph on `Z_L^2-S` has:

```
one principal component,
and total secondary mass <=3.
```

It follows immediately that any two-colouring for which all `S`-free
plaquettes are monochromatic has ordinary minority size

```
<= |S|+3 <= 6.
```

This proves the three-defect torus propagation lemma.

The exact `L=7` replay gives the stronger raw histogram over all `19,650`
defect sets:

```
secondary ordinary components:
  none : 19,209
  (1)  :    392
  (3)  :     49
```

and never anything else.

## 6. Circuit-girth lower bound

This part uses only the Rule-60 Mersenne facts already source-bound in PA-0014.

A dependency of `[H_L|1]` has form `(x,t)` with

```
H_L x + t*1 = 0.
```

### t=0

A nonzero kernel trajectory is generated by a nonzero even initial Rule-60
row. Every row remains even. No row can be zero unless the entire trajectory
is zero, because the Mersenne trajectory is periodic and deterministic.

Thus every one of the `L` rows has weight at least two:

```
wt(x) >= 2L.
```

### t=1

Since every row of `H_L` has odd weight three,

```
H_L 1 = 1.
```

So `H_L x=1` iff `x+1 in ker(H_L)`. Every kernel row has even weight and `L`
is odd, hence every row of `x` has odd weight and therefore at least one.

Including `f`,

```
wt(x,1) >= L+1.
```

Therefore

```
girth(M_L) >= L+1 >= 8.
```

No Newman-Moore distance conjecture is used.

## 7. No 1/2/exact-3 separation

Take a putative separation with `f in A` and `lambda(A)=t<=2`.

### t=0

`|S_J|=0`. All ordinary coordinates lie in one equality component, so one
full side has size at most one.

Let that side be `X`. Since `|X|<girth(M_L)`, deleting `X` from `N=M_L*`
does not lower rank: otherwise `X` would contain a cocircuit of `N`, i.e. a
circuit of `M_L`.

Thus

```
0=lambda_N(X)=r_N(X).
```

But `N` is simple, so every nonempty singleton has rank one. Contradiction.

### t=1

`|S_J|<=1`. With at most one defect the plaquette graph has no secondary
component and there is no isolated ordinary coordinate. Hence the ordinary
minority has size at most one, and one full side `X` has size at most two
after possibly adding `f`.

Again `|X|<girth(M_L)`, so

```
1=lambda_N(X)=r_N(X).
```

A simple binary rank-one restriction has at most one element. Thus a
2-separation with both sides of size at least two is impossible.

### t=2

`|S_J|<=3`. Three-defect propagation gives ordinary minority at most six.

Important bookkeeping point: if the minority ordinary colour is the side
containing `f`, then the **full** small side can have size seven, not six.
This does not hurt the proof:

```
|X| <= 7 < girth(M_L).
```

Hence

```
2=lambda_N(X)=r_N(X).
```

A simple binary rank-two restriction has at most three elements. An exact
3-separation requires `|X|>=3`, so equality would force three nonzero points
of `GF(2)^2`, i.e. a triangle of `N=M_L*`.

But

```
girth(N)=g*(M_L)=4,
```

so `N` has no triangle. Contradiction.

Therefore

```
M_L is 3-connected
and has no exact 3-separation
for every L=2^k-1, k>=3.
```

## 8. Consequence for the PA-0014 frontier

PA-0014 already established for this literal cubic-parent family

```
|E(M_L)| = L^2+1,
rank(M_L) = L^2-L+1,
g*(M_L)=4,

q_graph(M_L)
>=
(L^2-2L+3)/2
=
Omega(|E|).
```

This artifact upgrades the missing structural part from a finite `L=7`
stress to an all-Mersenne theorem:

```
MERSENNE TORUS TERMINALITY
=
PROVED FOR ALL k>=3.
```

When combined with the separately established `S8`-minor/source-terminal-lane
certificate for the same family, the PA-0014 exit becomes an unbounded actual
terminal live-leaf family with linear `q_graph`.

This artifact itself does not silently re-prove or assume that separate
family-wide `S8` certificate; the claims are kept modular.

## 9. External anti-duplication check

A targeted source sweep found a useful independent consistency check, not a
replacement for the local certificate above.

Fülep and Sieben (2010), *Polyiamonds and Polyhexes with Minimum
Site-Perimeter and Achievement Games*, Theorem 5.12, prove that the minimum
site-perimeter of a size-`s` polyhex is

```
ceil(sqrt(12s-3)) + 3.
```

Thus any connected planar plaquette animal of size at least four has at least
ten exterior neighbours. This is fully consistent with the JANUS local
classification: nine deleted plaquette nodes cannot isolate a planar
component of size at least four.

The theorem above does not claim novelty for that isoperimetric fact. The new
step is the exact three-defect structure, its dual-separation reduction, and
the all-Mersenne terminality consequence inside the frozen PA-0014 route.

## 10. Gate verdict and firewall

Freeze:

```
NM-0020
THREE-DEFECT TORUS PROPAGATION
=
PASS

MERSENNE M_L 3-CONNECTED
=
PROVED

MERSENNE M_L EXACT 3-SEPARATION
=
NONE

FULL-CLOSURE / SIMULTANEOUS-COCLOSED SHORTCUT
=
NOT USED

MERSENNE q_graph
=
Omega(|E|)  [PA-0014 input]

FAMILY-WIDE S8 BINDING
=
SEPARATE CERTIFICATE / MUST REMAIN EXPLICIT

GLOBAL SOLVER PROMOTION
=
HOLD UNTIL ALL LIVE-LEAF CONDITIONS ARE BOUND

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
