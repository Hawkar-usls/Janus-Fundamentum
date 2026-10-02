# R5 E9 — Cycle-Syndrome Homology Gauge and Projected-Delta-Matroid Boundary

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_HOMOLOGY_IDENTITY__DIRECT_PROJECTED_DELTA_MATROID_03_ROUTE_CLOSED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_MATCHING_NORMALIZED_CYCLE_2FACTOR_EXACTONE_2026-09-27_v1.0.md`
- `governance/audits/2026-09-28_rank3_03_general_factor_boundary.md`

Checker:
- `experiments/r5_e9_cycle_syndrome_homology_delta_matroid_boundary.py`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT ISOLATES THE TOPOLOGICAL PART OF THE CYCLE-SYNDROME COUPLING EXACTLY
AND CLOSES ONLY A DIRECT PROJECTED-LINEAR-DELTA-MATROID REALIZATION OF
THE LOCAL {0,3} HARD ATOM.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Matching-normalized carrier

Use the proved normalization

```text
A = I + P + Q
```

over `F2`, where `P,Q` are permutation matrices and the row support of `I,P,Q`
is pairwise disjoint.  Write `p(i),q(i)` for the two non-identity columns in row
`i`.

The graph `C_M` on the common row/column index set has one edge

```text
e_i={p(i),q(i)}
```

for every row `i`.  On the linear-cubic source this is a simple 2-factor, hence a
disjoint union of cycles.

The exact source condition is

```text
A x = 1 over F2
AND
supp(x) is independent in C_M.
```

## 2. Component-homology identity

Let `C` be one connected component of `C_M`, and let `chi_C` be its 0/1 vertex
indicator, viewed in the common row/column coordinate system.

### Theorem CSH-1

Over `F2`,

\[
\boxed{(P+Q)\chi_C=0}
\]

and therefore

\[
\boxed{A\chi_C=\chi_C}.
\]

### Proof

For a row `i`, the two coordinates read by `P` and `Q` are exactly `p(i)` and
`q(i)`, the endpoints of the single 2-factor edge `e_i`.

Because `C` is a connected component, either both endpoints of `e_i` belong to
`C` or neither does.  Hence

```text
chi_C[p(i)] = chi_C[q(i)]
```

for every row `i`, so their sum over `F2` is zero.  This is precisely
`(P+Q)chi_C=0`.  Adding the identity contribution gives `Achi_C=chi_C`. QED.

## 3. Exact edge-label homology after converting cycle independence to matching

For each cycle component, take an isomorphic cycle `H_C` whose matching edges
are indexed by the original vertices `j in C`.  Give matching edge `j` the
syndrome label

```text
a_j := A e_j in F2^n,
```

the `j`-th column of `A`.

An independent set in `C_M` is exactly a matching in the disjoint union of the
`H_C` under this edge-index relabelling.  The parity equation is therefore the
exact group-labelled matching condition

\[
\bigoplus_{j\in M} a_j = \mathbf 1.
\]

For one cycle component, the XOR of all edge labels is

\[
\bigoplus_{j\in C}a_j
=A\chi_C
=\chi_C.
\]

Thus the unique cycle-homology defect of the edge labelling is not an unknown
large vector: it is exactly the component indicator.

### Corollary CSH-2 — marker rank is exact

If the 2-factor has components `C_1,...,C_c`, then the homology defects are

```text
chi_C1,...,chi_Cc.
```

Their supports are pairwise disjoint and nonempty.  Hence they are linearly
independent over `F2` and

\[
\boxed{
\operatorname{rank}_{F2}\{\chi_{C_1},...,\chi_{C_c}\}=c.
}
\]

Therefore the attempted shortcut

```text
cycle gauge -> automatically O(log n) independent homology markers
```

is false in general.  The gauge removes no cross-cycle endpoint-syndrome
information by itself.

## 4. Coboundary-plus-one-marker normal form on each cycle

For completeness, any group edge labelling on a cycle admits the standard
spanning-tree gauge.

Choose one distinguished edge `e*_C`.  Assign vertex potentials `g_v` along the
cycle so that for every non-distinguished edge `uv`,

```text
a_uv = g_u + g_v.
```

The remaining distinguished edge has residual

```text
a_e* + g_u + g_v
= XOR_{e in C} a_e
= chi_C.
```

Hence for a matching `M` the complete syndrome can be written exactly as

\[
\boxed{
\bigoplus_{v\in\partial M} g_v
\oplus
\bigoplus_C [e_C^*\in M]\,\chi_C
=\mathbf1.
}
\]

Since the cycle indicators partition the index set,

\[
\mathbf1=\bigoplus_C\chi_C.
\]

This is a genuine exact representation change, but not yet a solver: the first
term is the surviving global endpoint-syndrome coupling.

## 5. Direct projected-delta-matroid route is blocked by the hard atom

The surviving rank-three General-Factor atom has local feasible family

\[
\mathcal F_{03}=\{\varnothing,\{1,2,3\}\}.
\]

### Lemma CSH-3

`F_03` is not a delta-matroid.

### Proof

Take

```text
X=empty,
Y={1,2,3},
e=1 in X triangle Y.
```

The symmetric-exchange axiom requires some

```text
f in {1,2,3}
```

such that `X triangle {e,f}` is feasible.  If `f=e`, the result has one element;
if `f` is different from `e`, the result has two elements.  Neither belongs to
`F_03`.  Hence symmetric exchange fails. QED.

Projection of a delta-matroid is again a delta-matroid.  Consequently
`F_03` cannot itself be represented as a projected linear delta-matroid.

This closes only the **direct** proposal

```text
replace every {0,3} atom by a projected-linear-delta-matroid constraint
and invoke polynomial linear-DM intersection/parity.
```

It does not rule out a genuinely global construction in which matching and
auxiliary structure jointly realize the source semantics.

## 6. Prior-art boundary

Source-bound ingredients:

- projected linear delta-matroids and matching with projected-linear-DM
  constraints: N. Kakimura and M. Takamatsu, *Matching Problems with
  Delta-Matroid Constraints*, SIAM J. Discrete Math. 28(2), 942–961 (2014),
  DOI `10.1137/110860070`;
- modern algorithms/closure operations for linear and projected linear
  delta-matroids: T. Koana and M. Wahlström, *Faster Algorithms on Linear
  Delta-Matroids*, STACS 2025, DOI `10.4230/LIPIcs.STACS.2025.62`.

The component identity `A chi_C=chi_C` is derived here from the frozen
`A=I+P+Q` JANUS normalization.  No novelty or priority claim is made beyond
this source audit.

## 7. Sharpened live obligation

The cycle-syndrome route is now split cleanly into

```text
LOCAL CYCLE MATCHING
= POLYNOMIAL

CYCLE HOMOLOGY DEFECT
= EXACTLY chi_C
= EXPLICIT / EASY

DIRECT PROJECTED-LINEAR-DM ENCODING OF {0,3}
= IMPOSSIBLE BY SYMMETRIC EXCHANGE

SURVIVING HARD OBJECT
= GLOBAL ENDPOINT-SYNDROME COUPLING
```

Freeze the source-specific gate

```text
R5_E9_CYCLE_ENDPOINT_SYNDROME_GLOBAL_QUOTIENT_GATE_V1
```

A PASS must provide a deterministic polynomial construction deciding

```text
matching M in disjoint cycles
such that XOR_{e in M} a_e = 1
```

for the source-generated labels `a_e=Ae`, or an exact representation-changing
contraction of that object, with polynomial witness reconstruction.

It may not enumerate the `2^rank(A)` group algebra, hide an exponential boundary
truth table, or pack the vector syndrome into a binary-encoded exponentially
large exact integer weight and call a pseudo-polynomial weighted-matching
routine polynomial.

## 8. Ceiling

```text
A chi_C = chi_C FOR EVERY C_M COMPONENT
= PROVED

CYCLE EDGE-LABEL HOMOLOGY DEFECT
= chi_C
= PROVED

HOMOLOGY MARKER RANK
= NUMBER OF CYCLE COMPONENTS
= PROVED

DIRECT {0,3} PROJECTED-LINEAR-DELTA-MATROID REALIZATION
= CLOSED

GLOBAL ENDPOINT-SYNDROME QUOTIENT
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
