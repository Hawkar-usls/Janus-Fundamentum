# R5 E9 — Paley(11) Gradient-Kernel Post-RKPR UNSAT Terminal

Date: 2026-09-29

Status:
`JANUS_EXACT_POST_RKPR_LINEAR_CUBIC_UNSAT_TERMINAL__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_PROJECTIVE_RATIO_PINNING_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_MATCHING_NORMALIZED_CYCLE_2FACTOR_EXACTONE_2026-09-27_v1.0.md`
- `research/R5_E9_CONNECTED_COMMUTING_TWO_PERM_NULLITY_COLLAPSE_2026-09-29_v1.0.md`

Scientific ceiling:

```text
A connected linear cubic source can survive RKPR with rational nullity > constant.
The explicit Paley(11) cyclic-triangle source has n=55 and nullity_Q=10.
Its entire rational kernel is a complete-graph gradient space, which gives a
polynomially checkable UNSAT certificate.

This is a new exact terminal / hostile control, not a universal polynomial solver.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source construction

Let the vertex set be `Z_11`.  Put a tournament arc

```text
u -> v
```

iff

```text
v-u mod 11 in R={1,3,4,5,9},
```

the nonzero quadratic residues modulo 11.  This is the Paley tournament `P(11)`.
There is exactly one oriented arc for each unordered pair, hence

```text
|E| = C(11,2) = 55.
```

Let the Exact-One constraints be the directed cyclic triangles of the tournament.
For every cyclic triangle `Delta`, create one row containing its three directed arcs.
Let `A` be the resulting triangle-by-arc incidence matrix.

Direct enumeration gives exactly 55 cyclic triangles.  Each row has weight 3.  Every
arc lies in exactly 3 cyclic triangles, so every column has weight 3.  Therefore `A`
is a square `55 x 55` cubic Positive 1-in-3 source.

Distinct directed triangles share at most one arc: two shared tournament arcs already
determine all three vertices and therefore the same directed triangle.  Hence the
source is linear.

The Levi graph is connected; the companion checker verifies all 110 Levi vertices are
in one component.

## 2. Gradient subspace lies in the rational kernel

For a rational vertex potential

```text
p: Z_11 -> Q,
```

define the arc signal

```text
y_(u->v) = p_v - p_u.
```

Around every directed cyclic triangle

```text
u -> v -> w -> u
```

the three values telescope:

```text
(p_v-p_u) + (p_w-p_v) + (p_u-p_w) = 0.
```

Therefore every complete-graph gradient belongs to `ker_Q(A)`.

The gradient map on a connected complete graph has dimension

```text
11-1 = 10,
```

because adding a constant to all vertex potentials changes no arc difference, and
this is the only kernel of the gradient map.

Thus

```text
nullity_Q(A) >= 10,
rank_Q(A) <= 45.
```

## 3. Exact rank certificate: a 45 x 45 minor has determinant -3

Use the deterministic ordering implemented by the checker:

1. arcs are lexicographically ordered by `(u,v)` while retaining only Paley arcs;
2. vertex triples `a<b<c` are scanned lexicographically and retained iff the induced
   tournament is cyclic;
3. each row is the indicator of the three oriented arcs of that cycle.

For that ordering, take the 45 columns

```text
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,44,46,47
```

and the 45 rows

```text
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,45,46
```

The exact integer determinant of this submatrix is

```text
-3.
```

Hence `rank_Q(A)>=45`.  Combined with the gradient upper bound,

```text
rank_Q(A)=45,
nullity_Q(A)=10,
ker_Q(A)=im(gradient).
```

No floating-point spectral inference is used.

## 4. RKPR-clean despite nullity 10

Fix one vertex potential as gauge, say `p_0=0`.  A rational kernel basis can then be
taken as the ten coordinate gradients for `p_1,...,p_10`.

The kernel-basis row attached to tournament arc `u->v` is the coordinate functional

```text
p_v-p_u.
```

No such row is zero.  Two distinct rows can be rationally proportional only if the
corresponding complete-graph edge vectors have the same unordered endpoint pair.
But the tournament contains only one orientation of each unordered pair.  Therefore
there are no distinct proportional kernel rows at all.

So this source survives the complete local RKPR test:

```text
zero kernel rows              = 0
proportional distinct rows    = 0
RKPR equality merges          = 0
RKPR ratio pins               = 0
RKPR illegal-ratio terminals  = 0
```

This is an exact counter-control against any proposed theorem of the form

```text
linear + connected + post-RKPR => constant rational nullity.
```

The control has `nullity_Q(A)=10`.

## 5. Exact UNSAT theorem from the gradient kernel

Assume for contradiction that an Exact-One witness exists:

```text
A x = 1,
x in {0,1}^55.
```

Because every source row contains exactly three variables, define

```text
y = 3x - 1.
```

Then

```text
A y = 3 A x - A 1 = 3*1 - 3*1 = 0,
```

and every coordinate of `y` lies in

```text
{-1,2}.
```

By the kernel equality proved above, there exists a rational potential `p` on the 11
tournament vertices such that for every tournament arc

```text
y_(u->v) = p_v-p_u.
```

Hence, for every unordered pair `{u,v}`, the unique tournament orientation implies

```text
|p_v-p_u| in {1,2}.
```

In particular all 11 potentials are distinct.  Order them increasingly:

```text
p_(1) < p_(2) < ... < p_(11).
```

Every consecutive gap is at least 1, while the difference between the minimum and
maximum is also required to belong to `{1,2}` and is therefore at most 2.  Thus there
can be at most three distinct potential values/vertices.  This contradicts 11.

Therefore

```text
Paley(11) cyclic-triangle source is UNSAT.
```

The contradiction is purely rational/integer and requires no SAT search.

## 6. General certificate pattern

The preceding argument does not depend on quadratic residues after the kernel equality
has been certified.  More generally, let a source have variables bijective with the
arcs of a tournament on `m>=4` vertices, let every Exact-One row be a directed triangle,
and suppose exact linear algebra certifies

```text
ker_Q(A) = complete-graph gradient space.
```

Then the same `y=3x-1` argument forces pairwise vertex-potential differences to have
absolute value 1 or 2, impossible for `m>=4`.

Thus a supplied tournament labelling plus an exact rank/minor certificate gives a
polynomially verifiable UNSAT certificate for this entire recognizable certificate
class.

Firewall: polynomial verification of such a certificate is not yet a proof that every
UNSAT source admits one, nor that a certificate can always be constructed in polynomial
time.

## 7. Why this matters to the live post-RKPR gate

Before this control, a tempting hypothesis was that linearity plus exhaustive RKPR might
force rational nullity into a constant or logarithmic regime.  Paley(11) proves that the
constant-nullity version is false even on a connected linear cubic source with no RKPR
projective coincidences.

At the same time, the control is not hostile to every stronger structure theorem: its
10-dimensional kernel has a very rigid graphical-gradient representation and therefore
admits a short UNSAT proof.

The correct next question is consequently not merely

```text
is post-RKPR nullity large?
```

but

```text
when post-RKPR nullity is large, must the kernel admit a polynomially recognizable
structured representation (gradient / cut / low-complexity quotient), or can a truly
unstructured post-RKPR linear family retain Omega(n) nullity?
```

That is the sharpened live gate.

## 8. Prior-art / anti-loop boundary

Doubly regular tournaments and quadratic-residue/Paley tournaments are classical.  A
standard reference for doubly regular tournaments is Reid and Brown, *Doubly regular
tournaments are equivalent to skew Hadamard matrices*, JCTA 12 (1972), 332–338.
Modern descriptions also record that, for a doubly regular tournament of order
`4t+3`, each oriented pair lies in a constant number of directed 3-cycles.

No literature novelty claim is made for Paley tournaments, doubly regular tournaments,
or gradient/telescoping identities.  The JANUS contribution here is the exact binding of
this explicit `P(11)` cyclic-triangle incidence source to the existing R5 E9 rational
kernel/RKPR boundary, including the determinant certificate and Exact-One UNSAT
terminal.

## 9. Checker

Executable exact regression:

`experiments/r5_e9_paley11_gradient_kernel_post_rkpr_unsat_terminal.py`

It verifies:

- 55 tournament arcs and 55 directed cyclic triangles;
- row degree = column degree = 3;
- source linearity;
- Levi connectedness;
- gradient annihilation `A D = 0`;
- exact fixed 45 x 45 minor determinant `-3` via integer Bareiss elimination;
- rank/nullity conclusion `45/10`;
- no zero or proportional distinct gauge-gradient rows;
- the symbolic potential-difference UNSAT terminal premises.

## 10. Ceiling

```text
PALEY11 SOURCE                       = LINEAR + CUBIC + CONNECTED
RATIONAL RANK / NULLITY              = 45 / 10
RATIONAL KERNEL                       = COMPLETE-GRAPH GRADIENT SPACE
POST-RKPR                             = CLEAN
EXACT-ONE STATUS                      = UNSAT
UNSAT CERTIFICATE                     = GRADIENT POTENTIAL RANGE CONTRADICTION
CONSTANT-NULLITY POST-RKPR HYPOTHESIS = FALSIFIED
OMEGA(n) POST-RKPR LINEAR FAMILY      = NOT YET PROVED
UNIVERSAL POLYNOMIAL SOLVER           = NOT PROVED
E8_D1                                 = EMPTY
P_VS_NP                               = OPEN
```
