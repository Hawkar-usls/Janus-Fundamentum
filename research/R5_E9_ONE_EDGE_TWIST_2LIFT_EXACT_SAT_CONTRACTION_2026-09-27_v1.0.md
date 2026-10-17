# R5 E9 — One-Edge-Twist 2-Lift Exact SAT Contraction

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_REPRESENTATION_CONTRACTION_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_one_edge_twist_exact_sat_contraction.py`

Parents:
- `R5_E9_ONE_EDGE_TWIST_2LIFT_DISSOCIATED_NULLITY_AMPLIFIER_2026-09-27_v1.0.md`
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_TRADE_FREE_UNIQUE_MODEL_DISSOCIATED_NULLITY_GATE_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS AN EXACT CONTRACTION DONOR FOR A RECOGNIZABLE 2-LIFT SUBCLASS.
IT DOES NOT SOLVE OET-IRREDUCIBLE CUBIC-LINEAR EXACT-ONE.
IT DOES NOT SUPPLY A UNIVERSAL SAT ALGORITHM.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. One-edge-twist lift

Let `A in {0,1}^{n x n}` be a square cubic incidence matrix: every row and every column has sum three. Choose an incidence `(i,j)` with `A_ij=1` and put

\[
E=e_i e_j^T,\qquad P=A-E.
\]

The one-edge-twist 2-lift is

\[
\widehat A=\begin{pmatrix}P&E\\E&P\end{pmatrix}.
\]

A Boolean lift assignment is written `(u,v)`, with `u,v in {0,1}^n`.

## 2. Exact model-space theorem

### Theorem OEC-1

\[
\boxed{
\operatorname{Mod}(\widehat A)
=
\{(u,v): Au=\mathbf1,\ Av=\mathbf1,\ u_j=v_j\}.
}
\]

Consequently

\[
\boxed{\widehat A\text{ is Exact-One SAT}\iff A\text{ is Exact-One SAT}.}
\]

No signed-trade-free, uniqueness, linearity, girth, rank, or nullity assumption is required.

### Proof

Suppose `(u,v)` is a lifted Exact-One model. Then

\[
Pu+Ev=\mathbf1,\qquad Eu+Pv=\mathbf1.
\]

Subtract the equations and put `h=u-v`. We obtain

\[
(P-E)h=0.
\]

Since `P-E=A-2E`,

\[
Ah=2Eh=2h_j e_i.
\]

Every column of `A` has sum three, hence

\[
\mathbf1^T A=3\mathbf1^T.
\]

Left-multiplying the last equation by `1^T` gives

\[
3\sum_{\ell=1}^n h_\ell=2h_j.
\]

Because `u,v` are Boolean, `h_j in {-1,0,1}`. The left side is divisible by three while the right side belongs to `{-2,0,2}`. Therefore

\[
h_j=0,
\]

so `u_j=v_j`.

Now

\[
Pu+Ev
=Au-Eu+Ev
=Au+e_i(v_j-u_j)
=Au.
\]

Thus `Au=1`. Symmetrically `Av=1`.

Conversely, if `Au=Av=1` and `u_j=v_j`, then

\[
Pu+Ev=Au+e_i(v_j-u_j)=1
\]

and similarly `Eu+Pv=1`. Hence `(u,v)` is a lifted model. QED.

## 3. Exact contraction and reconstruction

Theorem OEC-1 gives an explicit equisatisfiable dimension-halving contraction:

```text
CONTRACT(Ahat) = A.
```

Given any lifted witness `(u,v)`, project to `u` (or `v`) to obtain a base witness. Given any base witness `x`, lift it diagonally as `(x,x)`.

Therefore witness construction and reconstruction are linear in the vector size once the quotient is recognized.

The model-space theorem is stronger than mere equisatisfiability: a non-diagonal lift model is exactly an ordered pair of base models that agree at the twisted coordinate `j`.

## 4. Polynomial recognition from the Tanner graph

Assume the input is a connected cubic bipartite Tanner graph `H` and ask whether it is a one-edge-twist lift of a smaller connected cubic bipartite graph.

For a genuine one-edge-twist lift, the two crossed copies of the twisted incidence form a 2-edge cut. Removing them leaves two copies of the base Tanner graph with the twisted incidence deleted.

A connected cubic bipartite graph has no bridge. If a bridge cut leaves a component whose bridge endpoint is on the left shore, internal degree counting gives

\[
3|L_C|-1=3|R_C|,
\]

impossible modulo three; the right-shore case is symmetric. Thus deleting the twisted base incidence leaves the base connected, so the two components after the lifted 2-edge cut are connected.

A deterministic recognition algorithm is therefore:

1. enumerate every unordered pair of edges of `H`;
2. delete the pair and test whether exactly two connected components remain;
3. require that each component contains exactly one left-shore and one right-shore cut endpoint;
4. test whether the two components are color-preserving isomorphic with the marked left endpoint mapped to the marked left endpoint and the marked right endpoint mapped to the marked right endpoint;
5. if so, take one component and restore the missing edge between its two marked endpoints to reconstruct `A`;
6. verify directly that rebuilding the one-edge-twist lift yields an isomorphic copy of `H`.

The graph degree is at most three. Bounded-valence graph isomorphism is polynomial-time by Luks (1982); vertex colors/marks are handled by the standard colored reduction. There are only `O(|E(H)|^2)` edge pairs. Hence this recognition/contraction procedure is deterministic polynomial time.

The theorem does not claim a new graph-isomorphism result; Luks is a source-bound donor.

## 5. Recursive contraction

If an instance is produced by `t` successive recognizable one-edge-twist lifts, every successful contraction halves the variable count. Therefore

```text
number of successful contractions <= floor(log2 n).
```

At each level the recognition scan, bounded-degree isomorphism tests, quotient construction, and witness map are polynomial. The geometric series of instance sizes remains polynomial in the original input size.

Thus any iterated one-edge-twist tower is polynomially reducible to its OET-irreducible root.

## 6. Consequence for the nullity-amplifier family

The parent theorem remains valid:

- one-edge twisting preserves signed-trade-freeness in its stated setting;
- rational nullity obeys `k' >= 2k-1`;
- the explicit seed generates an infinite connected cubic-linear SAT unique-model trade-free family with `nu_Q=Omega(n)`.

However that family is not a hard survivor against representation-changing contraction. Its construction history is visible through the exact OET quotient and contracts back to the 18-variable seed in logarithmically many exact steps.

Therefore the previous family still falsifies

```text
TRADE_FREE => O(log n) RATIONAL NULLITY,
```

but it no longer witnesses hardness of the stronger gate

```text
TRADE_FREE HIGH-NULLITY OET-IRREDUCIBLE CONTRACTION.
```

This distinction is mandatory.

## 7. Prior-art / anti-loop boundary

Source-bound ingredients:

- graph 2-lifts and signed-lift block formalism;
- connectivity/balance language for signed lifts;
- polynomial-time isomorphism testing for bounded-valence graphs.

Representative sources:

- Y. Bilu and N. Linial, *Lifts, Discrepancy and Nearly Optimal Spectral Gap*, Combinatorica 26 (2006), 495–519, DOI `10.1007/s00493-006-0029-7`.
- E. M. Luks, *Isomorphism of Graphs of Bounded Valence Can Be Tested in Polynomial Time*, Journal of Computer and System Sciences 25(1) (1982), 42–65, DOI `10.1016/0022-0000(82)90009-5`.
- F. Martin, *Frustration and isoperimetric inequalities for signed graphs*, Discrete Applied Mathematics 217 (2017), 276–285, DOI `10.1016/j.dam.2016.09.015`.

The checked literature did not supply the exact Boolean Exact-One model-space identity in OEC-1 or this exact contraction composition. No novelty or priority claim is made.

## 8. New live frontier

Freeze the trade-free branch as

```text
R5_E9_OET_IRREDUCIBLE_TRADE_FREE_HIGH_NULLITY_CONTRACTION_GATE_V1
```

Input:

```text
connected cubic-linear Exact-One incidence A,
signed-trade-free,
nu_Q(A)=omega(log n),
no recognized one-edge-twist quotient.
```

Target: deterministic polynomial construction of one of

1. another exact dimension-dropping quotient;
2. an exact negative-kernel augmentation / absence certificate;
3. a decomposition into already proved polynomial carriers;
4. a terminal SAT/UNSAT certificate with polynomial discovery and reconstruction.

The parallel trade-rich gate remains:

```text
R5_E9_SIGNED_TRADE_POLY_DISCOVERY_OR_MIXED_CARRIER_CLOSURE_GATE_V1.
```

A universal SAT route must eventually cover both branches and compose back through the polynomial source reduction.

## 9. Ceiling

```text
ONE_EDGE_TWIST MODEL SPACE
= EXACTLY CHARACTERIZED

ONE_EDGE_TWIST EQSAT CONTRACTION
= PROVED AS THEOREM CANDIDATE

WITNESS PROJECTION / LIFT
= LINEAR TIME AFTER RECOGNITION

OET RECOGNITION
= POLYNOMIAL VIA 2-EDGE-CUT ENUMERATION + BOUNDED-DEGREE COLORED GI

ITERATED OET TOWER
= POLYNOMIALLY CONTRACTIBLE TO ROOT

OET NULLITY AMPLIFIER AS HARD SURVIVOR
= CLOSED

OET-IRREDUCIBLE TRADE-FREE HIGH-NULLITY CORE
= OPEN

TRADE-RICH MIXED-CARRIER GLOBAL CLOSURE
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
