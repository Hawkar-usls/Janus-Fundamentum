# R5 E9 — Levi General-Factor / Dual Matching / Two-Permutation Normal Form

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_NORMAL_FORM_THEOREM__NO_D1_PROMOTION`

Scientific firewall:

```text
THIS NOTE PROVES EXACT EQUIVALENT REPRESENTATIONS OF THE FROZEN CUBIC-LINEAR EXACT-ONE CARRIER.
IT DOES NOT PROVIDE A POLYNOMIAL DECIDER FOR THE HARD RESIDUAL.
GENERIC BIPARTITE GENERAL FACTOR WITH DEGREE SETS {1}/{0,3} IS NP-HARD.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parent:
- `R5_E9_CUBIC_LINEAR_HOFFMAN_COCLIQUE_EQUIVALENCE_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_levi_two_perm_normal_form.py`

## 1. Frozen carrier

Let

\[
A\in\{0,1\}^{n\times n}
\]

be the incidence matrix of a connected linear cubic 3-uniform incidence structure:

- every row has exactly three ones;
- every column has exactly three ones;
- two distinct columns occur together in at most one row.

The source decision problem is

\[
\operatorname{EX1}(A):\quad
\exists x\in\{0,1\}^n\; Ax=\mathbf 1.
\]

No semantic relaxation is made below.

## 2. Levi graph exact General-Factor form

Let `L(A)` be the bipartite Levi graph with left side `R` consisting of the rows of `A`, right side `C` consisting of the columns, and edge `(r,c)` iff `A[r,c]=1`.

Because `A` is cubic on both sides, `L(A)` is a 3-regular bipartite graph. Linearity is equivalent to absence of 4-cycles, hence the Levi graph has girth at least 6.

Assign degree sets

```text
K(r) = {1}     for r in R,
K(c) = {0,3}   for c in C.
```

### Theorem LGF-1

\[
\boxed{
Ax=\mathbf 1,\ x\in\{0,1\}^n
\iff
L(A)\text{ has a General Factor }F\text{ with degrees }{1}/{0,3}.
}
\]

### Proof

If `x` is an Exact-One witness, put into `F` every Levi edge incident with a selected column:

\[
F=\{(r,c):A_{rc}=1,\ x_c=1\}.
\]

Each row sees exactly one selected column because `Ax=1`, hence `deg_F(r)=1`. A column has either `x_c=0`, giving degree zero, or `x_c=1`, in which case all three of its Levi edges are included, giving degree three.

Conversely, suppose `F` satisfies the prescribed degree sets. Since every right vertex has ambient degree three, `deg_F(c)=3` means that all incidences of `c` are in `F`. Define

\[
x_c=1\iff \deg_F(c)=3.
\]

Every left vertex has factor degree exactly one, so exactly one column on every source row has `x_c=1`. Thus `Ax=1`.

The maps in both directions are deterministic and mutually inverse.

## 3. Exact dual-perfect-matching form

Dualize the incidence structure: the `n` original rows become dual vertices, and every original column `c` becomes the 3-set

\[
E_c=\{r:A_{rc}=1\}.
\]

Because every column has three incidences, the dual hypergraph is 3-uniform. Because every original row contains three columns, it is also 3-regular. Original linearity implies dual linearity as well: two dual hyperedges `E_c,E_d` meet in at most one row.

### Theorem DPM-1

\[
\boxed{
\operatorname{EX1}(A)
\iff
\{E_c:x_c=1\}\text{ is a perfect matching (parallel class) of the dual hypergraph.}
}
\]

Indeed, `Ax=1` says exactly that every dual vertex (source row) lies in exactly one selected dual hyperedge.

This representation is exact but is not an algorithmic promotion by itself.

## 4. Three perfect matchings in the Levi graph

A 3-regular bipartite graph has a perfect matching by Hall's theorem. For completeness, if `S` is a subset of one color class, the `3|S|` incident edges enter `N(S)`, whose vertices have degree at most three; therefore `3|S| <= 3|N(S)|`, so `|N(S)| >= |S|`.

Remove one perfect matching `M0`. The remaining graph is 2-regular and bipartite, hence a disjoint union of even cycles. Alternating the edges on each cycle splits the remainder into two further perfect matchings `M1,M2`.

Therefore this decomposition is constructible in polynomial time using standard bipartite matching plus linear-time cycle splitting.

Let `P0,P1,P2` be the corresponding disjoint-support permutation matrices. Then

\[
A=P_0+P_1+P_2.
\]

Left multiplication by `P0^T` gives

\[
A'=P_0^T A=I+P+Q,
\quad
P=P_0^T P_1,
\quad
Q=P_0^T P_2,
\]

where `P,Q` are permutation matrices.

Since `P0^T 1=1`,

\[
Ax=1\iff A'x=1.
\]

Since `P0^T` is invertible,

\[
\ker_{\mathbb Q}(A')=\ker_{\mathbb Q}(A),
\qquad
\nu_{\mathbb Q}(A')=\nu_{\mathbb Q}(A).
\]

### Theorem TPNF-1 — two-permutation normal form

Every frozen cubic square carrier has a deterministic polynomial-time exact representation

\[
\boxed{A' = I+P+Q}
\]

with `P,Q` permutation matrices of disjoint row support with `I`, preserving:

1. the Boolean Exact-One witness set;
2. rational rank and nullity;
3. satisfiable/unsatisfiable status;
4. the size of the instance.

For the linear carrier, if `p,q` are the permutations represented by `P,Q`, then the triples

\[
T_i=\{i,p(i),q(i)\}
\]

have three distinct entries and every unordered pair of symbols occurs in at most one `T_i`.

## 5. Connectedness becomes transitivity

In the normalized Levi graph, left vertex `i` is adjacent to right vertices

\[
i,\ p(i),\ q(i).
\]

Starting at right vertex `i`, traversing the identity edge to left `i` and then a `P` or `Q` edge reaches right `p(i)` or `q(i)`. Reverse traversals realize `p^{-1}` and `q^{-1}`.

Therefore the connected components of the Levi graph are exactly the orbits of the permutation group generated by `p` and `q`.

### Theorem TPNF-2

\[
\boxed{
L(A)\text{ connected}
\iff
\langle p,q\rangle\text{ acts transitively on }[n].
}
\]

This exposes a new exact algebraic language for the residual without claiming that transitivity, primitivity, or a block system solves it.

## 6. Kernel equation in the new representation

For any rational vector `z`,

\[
Az=0
\iff
(I+P+Q)z=0.
\]

Writing permutation action rowwise,

\[
\boxed{z_i+z_{p(i)}+z_{q(i)}=0\quad\forall i.}
\]

The Exact-One witness is the special two-valued kernel vector

\[
w=3x-1\in\{-1,2\}^n.
\]

Thus the current hard residual can equivalently be written as:

```text
transitive two-permutation system <p,q>
+ linear triple condition on {i,p(i),q(i)}
+ dim_Q ker(I+P+Q) = omega(log n)
+ no recognized OET quotient
+ decide whether ker(I+P+Q) meets {-1,2}^n.
```

This is the same residual, not a relaxation.

## 7. External anti-loop

The General-Factor representation must not be mistaken for a known polynomial donor.

Gutin, Kim, Soleimanfallah, Szeider and Yeo, *Parameterized Complexity Results for General Factors in Bipartite Graphs with an Application to Constraint Programming*, Algorithmica 64(1), 112–125 (2012), DOI `10.1007/s00453-011-9548-8`, record the NP-hardness of bipartite General Factor even when one bipartition has singleton degree lists. The standard hard special case with degree sets `{1}` and `{0,3}` is also described in the General-Factor literature. Preprint: `https://arxiv.org/abs/1106.3527`.

Li and Toulouse, *Some NP-Completeness Results on Partial Steiner Triple Systems and Parallel Classes*, Ars Combinatoria 80 (2006), 45–51, prove NP-completeness for existence of a parallel class in general partial Steiner triple systems. Their theorem is useful as a hardness warning, but this note does **not** import it as hardness of the stricter regular JANUS carrier.

Therefore:

```text
GENERAL {1}/{0,3} FACTOR = HARDNESS WARNING, NOT SOLVER.
GENERAL PARTIAL-STS PARALLEL CLASS = HARDNESS WARNING, NOT EXACT REGULAR-CARRIER HARDNESS CLAIM.
TWO-PERMUTATION NORMAL FORM = EXACT REPRESENTATION, NOT POLYNOMIAL DECIDER.
```

## 8. New research split inside the existing gate

Keep the authoritative gate unchanged:

```text
R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1
```

but expose an additional exact attack surface:

```text
A' = I + P + Q
GAMMA = <p,q> transitive
nullity_Q(A') = omega(log n)
linear triple system
OET quotient absent
```

The next admissible theorem must prove at least one of:

1. high nullity forces a polynomially recognizable exact quotient/decomposition in this two-permutation representation;
2. a broader block-system/imprimitivity contraction preserves Exact-One and reconstructs witnesses in polynomial time;
3. the primitive residual has a polynomial solver or polynomial UNSAT certificate;
4. a counterfamily falsifies one of those structural hopes, allowing that branch to be frozen as forbidden.

No implication `high nullity => imprimitive` is assumed.
No implication `OET-irreducible => primitive` is assumed.

## 9. Ceiling

```text
LEVI GENERAL-FACTOR {1}/{0,3} EQUIVALENCE
= PROVED

DUAL PERFECT-MATCHING / PARALLEL-CLASS EQUIVALENCE
= PROVED

CUBIC LEVI THREE-MATCHING DECOMPOSITION
= PROVED / POLYNOMIALLY CONSTRUCTIBLE

A -> I+P+Q EXACT NORMALIZATION
= PROVED

CONNECTED LEVI <=> <p,q> TRANSITIVE
= PROVED

RATIONAL NULLITY PRESERVED
= PROVED

HIGH NULLITY => NONTRIVIAL BLOCK SYSTEM
= NOT PROVED / FORBIDDEN TO ASSUME

OET-IRREDUCIBLE => PRIMITIVE
= NOT PROVED / FORBIDDEN TO ASSUME

POLYNOMIAL SOLVER FOR THE RESIDUAL
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
