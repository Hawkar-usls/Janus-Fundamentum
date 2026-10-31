# R5 E9 — Paley(11) Cyclic-Triangle Post-RKPR Linear Control

Date: 2026-09-29

Status:
`JANUS_EXACT_CONTROL__LINEAR_CUBIC_CONNECTED_POST_RKPR_NULLITY_10_UNSAT`

## 1. Construction

Let `T_11` be the Paley tournament on `Z_11`. Write

```text
R = {1,3,4,5,9}
```

for the nonzero quadratic residues modulo 11 and orient

```text
u -> v  iff  v-u in R.
```

There is one directed tournament arc for every unordered pair of vertices, hence

```text
N = C(11,2) = 55
```

arc variables.

For every directed cyclic triangle

```text
u -> v -> w -> u
```

create one Exact-One source row containing its three directed arcs. Let `A` be the resulting cyclic-triangle / arc incidence matrix.

## 2. Exact source parameters

The Paley tournament is doubly regular. Here `11=4*2+3`, so every directed arc lies in exactly

```text
t+1 = 3
```

directed 3-cycles. For this order the statement can also be verified directly: the arc `0->1` has cyclic third vertices `{2,6,10}`, and affine Paley automorphisms are transitive on arcs.

Therefore the total number of cyclic triangles is

```text
55*3/3 = 55.
```

Thus `A` is `55 x 55` and every row and every column has sum 3.

Two distinct graph triangles share at most one tournament arc, and two distinct arcs lie together in at most one graph triangle. Hence `A` is a linear cubic source. Its Levi graph is connected.

## 3. Root-difference kernel

For every tournament arc `e=(u->v)` define the row vector

```text
h_e = e_v - e_u in Q^11.
```

Let `H` be the `55 x 11` matrix with rows `h_e`.

Every cyclic source row telescopes:

```text
h_(u->v) + h_(v->w) + h_(w->u) = 0.
```

Hence

```text
A H = 0.
```

Because the underlying unoriented graph is `K_11`, the oriented incidence matrix `H` has rank 10. Therefore

```text
nullity_Q(A) >= 10.
```

Exact rational elimination gives

```text
rank_Q(A)    = 45
nullity_Q(A) = 10.
```

Consequently

```text
ker_Q(A) = col_Q(H).
```

This equality is the key structural identity of the control.

## 4. RKPR is inert

Each coordinate functional on the kernel is represented, through `ker(A)=col(H)`, by one root direction

```text
e_v-e_u.
```

No such row is zero.

Two distinct tournament arcs cannot have proportional root directions over `Q`: proportional vectors of type `e_v-e_u` have the same unordered endpoint pair, while a tournament contains exactly one orientation of each unordered pair.

Therefore the full rational kernel has

```text
zero kernel rows                = 0
proportional kernel-row pairs   = 0.
```

So the existing Rational Kernel Projective Ratio Pinning Quotient has nothing to merge, pin, or reject:

```text
RKPR(A) = A
```

up to trivial relabeling.

This is a genuine connected linear post-RKPR singular control with rational nullity 10.

## 5. Exact UNSAT certificate from vertex potentials

Since every source row has size 3,

```text
A * (1/3)*1 = 1.
```

Suppose a Boolean Exact-One witness `x in {0,1}^55` existed. Then

```text
y = x - (1/3)*1 in ker_Q(A) = col_Q(H).
```

So there is `alpha in Q^11` such that for every arc `u->v`,

```text
y_(u->v) = alpha_v-alpha_u.
```

Set `beta=3 alpha`. Since `x_(u->v)` is either 0 or 1,

```text
beta_v-beta_u in {-1,2}
```

for every directed tournament arc `u->v`.

Because exactly one of `u->v` and `v->u` exists for every distinct pair, this implies

```text
beta_u != beta_v
```

for every `u!=v`.

Fix one vertex `r`. For any other vertex `w`, depending on the orientation of the pair `{r,w}`,

```text
beta_w-beta_r in {-2,-1,1,2}.
```

But the other ten vertices require ten pairwise distinct offsets while only four values are available. Pigeonhole contradiction.

Therefore

```text
A is Exact-One UNSAT.
```

This is a polynomial-size global UNSAT certificate derived from the exact kernel geometry; it does not enumerate `2^10` kernel states.

## 6. Noncommuting consequence

A connected cubic bipartite Levi graph has a perfect matching, hence this source admits the normalized form

```text
A = I + P + Q
```

after relabeling.

The companion theorem `CONNECTED_COMMUTING_TWO_PERM_NULLITY_COLLAPSE` proves that connected `PQ=QP` carriers have rational nullity only 0 or 2. Since this source has nullity 10, every such normalized representation of the Paley(11) control is necessarily in the genuinely noncommuting branch.

Thus this one object simultaneously has

```text
linear cubic source
connected Levi carrier
post-RKPR projective simplicity
noncommuting two-permutation normalization
rational nullity 10
Exact-One UNSAT.
```

## 7. Why this matters

Previous large-nullity controls in this branch failed at least one of the two hard premises:

```text
post-RKPR hostility
linear cubic source.
```

Paley(11) passes both at once.

It therefore closes any proposed theorem of the form

```text
linear + connected + post-RKPR => nullity bounded by a tiny universal constant < 10.
```

It does **not** by itself refute an asymptotic `O(log n)` nullity conjecture: one finite instance cannot do that.

The construction suggests a stronger family program. In a doubly regular tournament of order `v=4t+3`, every arc belongs to `t+1` cyclic triangles. If one can select a 3-regular spanning subhypergraph of those cyclic triangles for infinitely many `v`, the same root-difference argument gives a square linear cubic source with

```text
n = v(v-1)/2
nullity_Q(A) >= v-1 = Theta(sqrt(n))
```

and automatic RKPR projective simplicity. Such an infinite family would rigorously kill `post-RKPR nullity = O(log n)`.

That 3-factor existence is a new gate and is **not proved here**.

## 8. Literature binding

The standard homogeneous/doubly-regular tournament identity says that a tournament of order `4t+3` has exactly `t+1` directed 3-cycles through every arc. The Paley tournament is the canonical finite-field example. The JANUS contribution in this note is the interaction of the cyclic-triangle incidence source with the rational Exact-One kernel, RKPR, and the vertex-potential UNSAT certificate.

No novelty claim beyond that scoped internal synthesis is needed for the theorem.

## 9. New live gate

```text
R5_E9_DOUBLY_REGULAR_TOURNAMENT_CYCLIC_TRIANGLE_3_FACTOR_FAMILY_GATE_V1
```

Question:

```text
For an infinite family of doubly regular / Paley tournaments,
can we select cyclic triangles so every tournament arc occurs exactly 3 times?
```

A YES with a uniform polynomial construction would materialize an infinite connected linear post-RKPR family with `Omega(sqrt(n))` rational nullity.

## 10. Ceiling

```text
PALEY11 LINEAR 55_3 SOURCE = PROVED
rank_Q=45 / nullity_Q=10 = EXACT
RKPR PROJECTIVE SIMPLICITY = PROVED
EXACT-ONE UNSAT = PROVED
NONCOMMUTING NORMALIZED BRANCH = PROVED
INFINITE 3-FACTOR FAMILY = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
