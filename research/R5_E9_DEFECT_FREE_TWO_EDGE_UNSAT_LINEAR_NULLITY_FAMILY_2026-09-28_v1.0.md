# R5 E9 — Defect-Free Two-Edge Lifts: UNSAT 3-Cut-Prime Family with Linear Rational Nullity

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_N_HOSTILE_FAMILY__LARGE_NULLITY_IMPLIES_SAT_FALSIFIED__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS FALSIFIES THE SHORTCUT
  3-CUT-IRREDUCIBLE + UNBALANCED + LARGE RATIONAL NULLITY => SAT.

IT DOES NOT PROVIDE A UNIVERSAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_SINGULAR_UNSAT_3CUT_IRREDUCIBLE_ODD_CYCLE_CONTROL_2026-09-28_v1.0.md`
- `research/R5_E9_ONE_EDGE_TWIST_2LIFT_EXACT_SAT_CONTRACTION_2026-09-27_v1.0.md`
- `research/R5_E9_TWO_EDGE_TWIST_3CUT_IRREDUCIBLE_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_defect_free_two_edge_unsat_linear_nullity.py`

## 1. Seed

Use the frozen connected linear-cubic `15_3` UNSAT control with rows

```text
(0,5,12) (1,7,9) (2,9,14) (3,10,11) (3,4,13)
(1,5,10) (6,7,14) (2,3,7) (1,4,8) (0,6,9)
(2,10,12) (5,11,13) (6,8,12) (0,8,13) (4,11,14).
```

Its incidence matrix `A_0` satisfies

```text
rank_Q(A_0)=14,
nu_Q(A_0)=1,
Exact-One(A_0)=UNSAT,
connected / linear / cubic,
no nontrivial edge cut of size <=3,
unbalanced.
```

The UNSAT proof and small-cut census are frozen in the parent hostile-control artifact.

## 2. Two-edge lift

Let `A` be any square cubic incidence matrix. Choose two nonadjacent incidences

```text
(i,j), (p,q),
```

and put

```text
E = e_i e_j^T + e_p e_q^T,
P = A-E.
```

The two-edge 2-lift is

\[
\widehat A=
\begin{pmatrix}
P&E\\
E&P
\end{pmatrix}.
\]

For a Boolean lifted assignment `(u,v)`, put `h=u-v`.

Subtracting the two lifted Exact-One equations gives

\[
(A-2E)h=0,
\]
so

\[
Ah=2h_j e_i+2h_q e_p.
\]

Because every column of `A` sums to three,

\[
3\sum_r h_r=2(h_j+h_q).
\]

Since `h_j,h_q in {-1,0,1}`, the right side belongs to `{-4,-2,0,2,4}`. The only multiple of three is zero. Hence

\[
\boxed{h_q=-h_j.}
\]

Thus every possible non-diagonal defect has the form

\[
Ah=2t(e_i-e_p),\qquad t\in\{-1,+1\}.
\]

## 3. Left-kernel separation kills the defect

### Theorem DFT-1 — exact defect-free contraction

Assume there exists

\[
y\in\ker_{\mathbb Q}(A^T)
\]
with

\[
y_i\ne y_p.
\]

Then

\[
\boxed{
\operatorname{Mod}(\widehat A)=
\{(u,v): Au=Av=\mathbf1,\ u_j=v_j,\ u_q=v_q\}.
}
\]

In particular

\[
\boxed{\widehat A\text{ SAT}\iff A\text{ SAT}.}
\]

### Proof

If `t != 0`, left-multiply

\[
Ah=2t(e_i-e_p)
\]
by `y^T`. The left side vanishes, whereas the right side is

\[
2t(y_i-y_p)\ne0,
\]
a contradiction. Therefore `t=0`, hence `h_j=h_q=0` and `E h=0`.

Now the first lift equation is

\[
Pu+Ev=Au+E(v-u)=Au-Eh=Au=\mathbf1,
\]
and symmetrically `Av=1`.

Conversely, any two base models agreeing at `j` and `q` satisfy the lifted equations directly. QED.

This is stronger than equisatisfiability and gives linear-time witness projection/reconstruction after the quotient is known.

## 4. A defect-free nonadjacent pair always exists when left nullity is nonzero

### Lemma DFT-2

Let `A` be square cubic and linear with

\[
\ker(A^T)\ne\{0\}.
\]

Then there are two rows `i != p`, a vector `y in ker(A^T)`, and nonadjacent incidences `(i,j),(p,q)` such that

\[
y_i\ne y_p.
\]

### Proof

If every left-kernel vector had all row coordinates equal, every `y in ker(A^T)` would be a scalar multiple of the all-ones vector. But

\[
A^T\mathbf1=3\mathbf1,
\]
so no nonzero constant vector belongs to the left kernel. Therefore some `y` distinguishes two rows `i,p`.

Each row has three incidences. Since the carrier is linear, two distinct rows share at most one column, so one can choose an incidence in row `i` and one in row `p` with distinct column endpoints. The two incidence edges are then nonadjacent. QED.

The pair is polynomially discoverable by exact Gaussian elimination followed by a row/edge scan.

## 5. Structural preservation

For a cubic 3-cut-irreducible Levi graph, any two nonadjacent crossed incidences have frustration index exactly two. The parent two-edge-twist theorem proves that a 2-lift with frustration index at least two remains 3-cut-irreducible.

Therefore every DFT step preserves

```text
connected,
cubic,
no nontrivial edge cut of size <=3.
```

A graph cover preserves bipartiteness and cannot create a new 4-cycle below the base girth, hence linearity is preserved as well.

If the base is UNSAT, DFT-1 makes the lift UNSAT. The parent balanced set-partitioning theorem says every balanced source matrix is SAT with a polynomial witness, so every member of this UNSAT family is automatically unbalanced.

## 6. Nullity recurrence

The symmetric/antisymmetric change of coordinates block-diagonalizes the lift over `Q`:

\[
\widehat A\sim A\oplus(A-2E).
\]

Let

\[
k=\nu_{\mathbb Q}(A).
\]

Since `rank(E)<=2`,

\[
\nu_{\mathbb Q}(A-2E)\ge k-2.
\]

Hence

\[
\boxed{k'\ge2k-2.}
\]

For `k>=3`, every defect-free pair supplied by DFT-2 therefore gives at least one signed null mode and strictly amplifies the residual nullity according to this recurrence.

## 7. Two exact bootstrap steps

The seed has `k_0=1`, so two finite bootstrap choices are frozen explicitly.

### Bootstrap 1

Choose

```text
(1,7), (8,4).
```

They are nonadjacent incidences of `A_0`. A primitive left-kernel vector is

```text
(8,-4,5,11,-1,-16,14,-10,20,-1,5,8,-13,-7,-19),
```

whose values at rows `1` and `8` are `-4` and `20`, so DFT-1 applies.

Exact elimination gives

```text
nu_Q(A_0-2E_0)=1,
nu_Q(A_1)=2,
n_1=30.
```

Thus `A_1` is still UNSAT and 3-cut-irreducible.

### Bootstrap 2

In `A_1`, choose

```text
(0,0), (2,14).
```

A left-kernel basis may be chosen so that the row signatures at `0` and `2` are

```text
row 0 : (4,12),
row 2 : (-7,11),
```

hence they are separated by the left kernel and DFT-1 applies again.

Exact elimination gives

```text
nu_Q(A_1-2E_1)=1,
nu_Q(A_2)=3,
n_2=60.
```

## 8. Infinite recursion

For every stage `t>=2`, compute a nonzero left-kernel basis and choose a defect-free nonadjacent pair by DFT-2. Form the corresponding two-edge lift.

All structural and UNSAT properties are preserved, while

\[
k_{t+1}\ge2k_t-2.
\]

Since `k_2=3`, let `h_t=k_t-2`. Then

\[
h_{t+1}\ge2h_t,\qquad h_2=1.
\]

Therefore for every `t>=2`,

\[
\boxed{k_t\ge2+2^{t-2}.}
\]

The variable count is

\[
n_t=15\cdot2^t,
\]
so

\[
\boxed{
\nu_{\mathbb Q}(A_t)
\ge
2+\frac{n_t}{60}.
}
\]

Thus the family has linear rational nullity.

## 9. Main consequence

There is an explicit recursively constructible infinite family satisfying simultaneously

```text
connected,
linear,
cubic / square,
UNSAT,
unbalanced,
no nontrivial edge cut of size <=3,
nu_Q(A) >= 2+n/60.
```

Hence both residual shortcuts are false:

```text
3-cut-irreducible + unbalanced + large nullity => SAT
```

and

```text
3-cut-irreducible + unbalanced => O(log n) nullity.
```

The existing low-nullity and overlap-excess FPT routers remain exact polynomial islands, but rational nullity alone cannot be the universal complexity currency even after separator and balanced preprocessing.

## 10. Updated universal obligation

The live hard core must now tolerate both explicit residual lineages:

```text
SAT  + 3-cut-prime + unbalanced + Theta(n) nullity
UNSAT + 3-cut-prime + unbalanced + Theta(n) nullity.
```

Therefore any universal polynomial solver needs a semantic/global currency that distinguishes these lineages without enumerating their kernels.

The next attack is the actual-row-basis semantic core: exploit the exact basis equation equivalence `Bx=1 iff Ax=1`, factor private variables for free, and seek a polynomial global algorithm on the shared-variable overlap core. Local nullity/singularity and fixed-cut summary states are forbidden as universal shortcuts.

## 11. Ceiling

```text
TWO-EDGE DEFECT CHARACTERIZATION
= PROVED

LEFT-KERNEL SEPARATION => EXACT EQSAT CONTRACTION
= PROVED

DEFECT-FREE NONADJACENT PAIR EXISTS WHEN LEFT NULLITY>0
= PROVED / POLYNOMIALLY DISCOVERABLE

BOOTSTRAP n=15 -> 30 -> 60
nullity 1 -> 2 -> 3
= EXACT

RECURSIVE NULLITY
k' >= 2k-2
= PROVED

INFINITE UNSAT PRIME RESIDUAL FAMILY
nu_Q >= 2+n/60
= PROVED

LARGE-NULLITY-IMPLIES-SAT ROUTE
= FALSIFIED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```