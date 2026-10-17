# R5 E9 — Cubic-Linear Exact-One as Hoffman-Coclique Equality

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_SPECTRAL_EQUIVALENCE_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Scientific firewall:

```text
THIS IS AN EXACT STRUCTURAL/SPECTRAL EQUIVALENCE.
IT DOES NOT SUPPLY A POLYNOMIAL HOFFMAN-COCLIQUE FINDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_PERFECT_KERNEL_CONFLICT_GRAPH_SOURCE_AUDIT_2026-09-25_v1.0.md`
- `R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `R5_E9_ONE_EDGE_TWIST_2LIFT_EXACT_SAT_CONTRACTION_2026-09-27_v1.0.md`

Checker:
`experiments/r5_e9_cubic_linear_hoffman_coclique_equivalence.py`

## 1. Setup

Let

\[
A\in\{0,1\}^{n\times n}
\]

be the incidence matrix of a **linear cubic 3-uniform** hypergraph:

- every row has exactly three ones;
- every column has exactly three ones;
- two distinct columns meet in at most one row.

Define the conflict graph `G=G(A)` on the columns of `A`: two vertices are
adjacent exactly when the corresponding columns meet in a row.

Linearity makes `G` simple.  Each column lies in three rows and each such row
contributes two distinct neighbours, so `G` is 6-regular.  Every source row
induces a triangle, and linearity implies that every edge of `G` belongs to
exactly one source-row triangle.

## 2. Gram identity

The diagonal entries of `A^T A` are three.  An off-diagonal entry is the number
of source rows shared by two columns, hence is zero or one and is exactly the
corresponding adjacency entry of `G`.

Therefore

\[
\boxed{A^T A=3I+G.}
\]

Consequences:

1. `3I+G` is positive semidefinite;
2. every eigenvalue of `G` is at least `-3`;
3. the `-3` eigenspace is exactly `ker_R(A)`;
4. its multiplicity equals `nu_Q(A)` because `A` is rational.

Thus

\[
\boxed{\lambda_{\min}(G)\ge -3}
\]

and equality holds exactly when `A` is singular.

## 3. Exact-One is a two-valued `-3` eigenvector

For a Boolean vector `x`, put

\[
w=3x-\mathbf1.
\]

Then `w_i` belongs to `{-1,2}`.

If `Ax=1`, then

\[
A(3x-1)=0,
\]

so by the Gram identity

\[
Gw=-3w.
\]

Conversely, suppose

\[
w\in\{-1,2\}^n,
\qquad Gw=-3w,
\]

and put `x=(w+1)/3`.  Then `x` is Boolean and

\[
(3I+G)x=3\mathbf1.
\]

Equivalently,

\[
Gx=3(\mathbf1-x).
\]

If `x_v=1`, the right side at `v` is zero, hence `v` has no selected
neighbour.  Therefore the selected set is independent.

If `x_v=0`, then `v` has exactly three selected neighbours.  Its six neighbours
are partitioned into three pairs, one pair from each source-row triangle
containing `v`.  Since the selected set is independent, at most one endpoint
of each pair can be selected.  A total of three selected neighbours therefore
forces exactly one selected endpoint in every pair.  Hence every source-row
triangle contains exactly one selected vertex.

Thus every source row contains exactly one `1` in `x`, i.e. `Ax=1`.

### Theorem HCE-1

For a linear cubic square incidence matrix,

\[
\boxed{
Ax=\mathbf1,\ x\in\{0,1\}^n
\iff
w=3x-\mathbf1\in\{-1,2\}^n,\ Gw=-3w.
}
\]

This is the same source problem expressed as a two-level vector in the bottom
eigenspace of the conflict graph.

## 4. Hoffman equality

The prior conflict-graph bridge gives

\[
Ax=\mathbf1
\iff
\alpha(G)=n/3.
\]

The spectral identity now sharpens the meaning of this equality.

For a `d`-regular graph with least eigenvalue `tau<0`, Hoffman's ratio bound is

\[
\alpha(G)\le \frac{n(-\tau)}{d-\tau}.
\]

Here `d=6` and `tau>=-3`.  Therefore

\[
\alpha(G)\le n/3,
\]

with the target `n/3` possible only when `tau=-3`.

When `tau=-3`, equality in the ratio bound holds exactly when every vertex
outside the coclique has three neighbours inside it.  Therefore an Exact-One
witness is precisely a Hoffman coclique meeting the ratio bound.

### Theorem HCE-2

For the present carrier the following are equivalent:

1. `A` has an Exact-One Boolean witness;
2. `G(A)` has an independent set of size `n/3`;
3. `G(A)` has a Hoffman coclique attaining the ratio bound;
4. `G(A)` has an equitable two-cell partition with quotient matrix

```text
Q = [[0,6],
     [3,3]];
```

5. the `-3` eigenspace contains a vector in `{-1,2}^n`.

The cell sizes in item 4 are forced: double-counting cross edges gives
`6|S|=3|V\S|`, hence `|S|=n/3`.

## 5. Immediate polynomial terminal: nonsingular incidence

Because every Exact-One witness produces the nonzero kernel word

\[
3x-\mathbf1,
\]

we obtain the exact rejection rule

```text
rank_Q(A)=n
=>
lambda_min(G)>-3
=>
UNSAT.
```

This is polynomial-time Gaussian elimination / spectral linear algebra and
needs no branching.

This terminal is not claimed as new relative to the existing rational-nullity
router; the new content is the exact identification of the remaining search
with Hoffman-bound equality.

## 6. Relation to the nullity router

Let

\[
k=\nu_Q(A)=\dim E_{-3}(G).
\]

The existing rational-kernel router is polynomial when `k=O(log n)` by exact
`2^k poly(n,L)` enumeration.  In the present language this is precisely the
small-multiplicity case of finding a two-valued point in the bottom eigenspace.

The hard residual is therefore not arbitrary maximum independent set.  It is:

```text
6-regular conflict graph
+ edge partition into source-row triangles
+ lambda_min = -3
+ large multiplicity of -3
+ decide whether the Hoffman ratio bound is attained.
```

The one-edge-twist contraction theorem already removes a concrete infinite
high-nullity family from this residual by a polynomially recognizable exact
quotient.

## 7. External anti-loop

Source-bound facts used here:

- Hoffman's ratio bound and its equality condition; see W. H. Haemers,
  *Hoffman's ratio bound*, Linear Algebra and its Applications 617 (2021),
  215–219, DOI `10.1016/j.laa.2021.02.010`.
- The language of `(k,tau)`-regular sets / equitable two-partitions and spectral
  methods; see D. M. Cardoso, V. V. Lozin, C. J. Luz, M. F. Pacheco,
  *Efficient domination through eigenvalues*, Discrete Applied Mathematics 214
  (2016), 54–62, DOI `10.1016/j.dam.2016.06.014`.

The latter paper gives a polynomial easy case for `(0,tau)`-regular-set search
when `-tau` is not an eigenvalue.  That condition does not close the JANUS
residual: our target is `(0,3)` and a witness can exist only in the branch where
`-3` **is** an eigenvalue.

No located source was found that gives a polynomial algorithm for the exact
special class above (triangle-decomposed 6-regular conflict graphs generated by
linear cubic incidence, quotient `[[0,6],[3,3]]`).  This absence is not a
novelty or hardness claim; it only prevents importing an unverified donor.

## 8. New scoped gate

Freeze

```text
R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1
```

Input:

```text
A: connected linear cubic square incidence matrix,
G=G(A),
nu_Q(A)=omega(log n),
no recognized one-edge-twist quotient,
lambda_min(G)=-3.
```

PASS requires a deterministic polynomial construction of one of:

1. a Hoffman coclique `S` of size `n/3` and therefore an Exact-One witness;
2. a polynomial certificate that no such coclique exists;
3. an exact dimension-dropping quotient/decomposition preserving Hoffman
   equality and witness reconstruction;
4. a source-proved polynomial terminal carrier.

Forbidden pseudo-progress:

- generic maximum-independent-set oracle;
- enumeration of the `-3` eigenspace when its multiplicity is superlogarithmic;
- treating the spectral necessary condition `lambda_min=-3` as sufficient;
- claiming that an arbitrary `-3` eigenvector can be rounded to `{-1,2}`;
- reusing the OET tower as an irreducible hard family after its exact contraction
  has been proved.

## 9. Ceiling

```text
A^T A = 3I + G
= PROVED

lambda_min(G) >= -3
= PROVED

E_{-3}(G) = ker_R(A)
= PROVED

EXACT-ONE
iff {-1,2}-VALUED -3 EIGENVECTOR
iff HOFFMAN COCLIQUE OF SIZE n/3
iff EQUITABLE QUOTIENT [[0,6],[3,3]]
= PROVED

FULL-RANK A
=> UNSAT
= PROVED

LOW -3 MULTIPLICITY O(log n)
= EXISTING POLYNOMIAL FPT TERMINAL

RECOGNIZABLE OET HIGH-NULLITY TOWERS
= EXISTING POLYNOMIAL EXACT CONTRACTION

OET-IRREDUCIBLE HIGH-MULTIPLICITY HOFFMAN-COCLIQUE SEARCH
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
