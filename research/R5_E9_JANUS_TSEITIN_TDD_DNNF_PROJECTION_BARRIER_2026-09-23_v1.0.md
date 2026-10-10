# R5 E9 — JANUS Tseitin TDD / DNNF Projection Barrier

Date: 2026-09-23

Authority:
`SOURCE_BOUND_UNCONDITIONAL_REPRESENTATION_LOWER_BOUND__NO_P_NE_NP_ASSUMPTION__NO_D1_PROMOTION`

Parents:

- `R5_B1B1C5B2B2_E8_6I_PREFIX_FACTOR_WIDTH_TDD_CURRENCY_2026-09-23_v0.1.md`
- `R5_E9_APAC_ARBITRARY_PRODUCT_GRAPH_EMBEDDING_AND_FIXED_TREEWIDTH_BARRIER_2026-09-23_v1.0.md`

Scientific ceiling:

```text
D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT_PROVED
```

## 1. Question closed by this artifact

The open donor gate was:

```text
TSEITIN_CNF_EQSAT
  ->
CNF_WITH_POLY_PREFIX_FACTOR_WIDTH_VTREE_ORDER
  ->
POLY_SIZE_TDD_REPRESENTATION.
```

This artifact proves that **no universal polynomial factor-width/TDD theorem can
hold for all JANUS-generated Tseitin CNFs**.

The proof is a representation lower bound. It does not assume P != NP.

## 2. External lower-bound source

Amarilli, Capelli, Monet and Senellart,
*Connecting Knowledge Compilation Classes and Width Parameters*,
arXiv:1811.02944.

Their Corollary 8.5 states:

For every monotone CNF phi of constant arity and constant degree, the smallest
DNNF computing phi has size

```text
2^{Omega(tw(phi))}.
```

Hence any bounded-degree constant-arity family with treewidth Omega(n) has
DNNF size 2^{Omega(n)}.

Such graph families exist, e.g. constant-degree expanders have linear-size
separators / linear treewidth. For a graph G define the monotone graph CNF

```text
Phi_G
=
AND_{xy in E(G)} (x OR y).
```

Then:

- arity = 2;
- variable degree = degree(G), hence constant on a constant-degree family;
- the primal graph of Phi_G is exactly G;
- for an expander family, tw(Phi_G)=Omega(|V(G)|).

Therefore there is an explicit/asymptotic family Phi_n with

```text
minimum_DNNF_size(Phi_n)
=
2^{Omega(n)}.
```

## 3. Exact 3CNF normalization with projection semantics

If a literal-exact three-literal input is required, replace each 2-clause

```text
(x OR y)
```

by

```text
(x OR y OR s)
AND
(x OR y OR NOT s)
```

with fresh private s.

For every fixed assignment to x,y:

```text
exists s [
 (x OR y OR s)
 AND
 (x OR y OR NOT s)
]
iff
(x OR y).
```

Thus the normalization preserves the exact projected Boolean function, not
merely global satisfiability.

The overhead is linear.

## 4. JANUS exact-extension property

Apply the frozen exact JANUS chain to the normalized formula:

```text
signed 3CNF
  ->
three-sheet exact local lift
  ->
sparse F2 affine/rank-one representation
  ->
Boolean XOR/AND checker circuit
  ->
Tseitin CNF Psi.
```

Let X denote the original variables and Y every auxiliary variable introduced
by normalization, sheet lifting, moment/rank-one representation, checker gates
and Tseitin encoding.

The previously proved exact-lift/reconstruction contracts give, assignment by
assignment:

```text
Phi(X)
iff
exists Y Psi(X,Y).
```

This projection identity is the only JANUS-specific premise required below.

## 5. TDD-to-DNNF projection argument

Capelli, Choi, Mengel, Muñoz and Van den Broeck,
*A Canonical Generalization of OBDD*, SAT 2026,
define TDDs as a restriction of structured deterministic DNNF.

Therefore any TDD for Psi is, after forgetting the extra structure, a DNNF of
the same polynomial order of size.

DNNF supports existential forgetting of auxiliary variables without
superpolynomial growth. Equivalently, in a decomposable NNF the forgotten
literal leaves can be replaced by true and simplified; decomposability is
preserved.

This is also the mechanism used explicitly by Oztok and Darwiche,
*On Compiling DNNFs without Determinism*, arXiv:1709.07092:
compile with auxiliary variables and existentially quantify them from the
deterministic structure in linear time to obtain a DNNF of the projected
function.

Hence:

```text
poly-size TDD(Psi(X,Y))
  =>
poly-size DNNF(Psi)
  =>
poly-size DNNF(exists Y Psi)
  =
poly-size DNNF(Phi).
```

## 6. Contradiction with the source lower bound

Choose Phi=Phi_n from the bounded-degree monotone CNF family in Section 2.

Assume every JANUS-generated Tseitin extension Psi_n had a polynomial-size TDD.

By Section 5, existentially forgetting all auxiliaries would yield a
polynomial-size DNNF for Phi_n.

But Amarilli et al. give

```text
minimum_DNNF_size(Phi_n)
=
2^{Omega(n)}.
```

Contradiction.

Therefore:

```text
there exists a JANUS-generated Tseitin family
whose minimum TDD size is exponential.
```

No complexity assumption is used.

## 7. Prefix factor-width consequence

Capelli et al. relate TDD size under a vtree to factor width and prove their
bottom-up compilation bound in terms of the maximum factor width of prefix
conjunctions.

If every JANUS Tseitin CNF admitted a polynomial-time constructible vtree/order
with polynomial prefix factor width, their compilation theorem would construct a
polynomial-size TDD for every member of the family.

Section 6 proves that this is impossible.

Hence:

```text
R5_E8_6I_JANUS_PREFIX_FACTOR_WIDTH_GATE_V1
=
FAIL AS A UNIVERSAL THEOREM.
```

More precisely, there exists a JANUS-generated family such that for every
vtree/order sufficient for the proposed universal compiler, the required
prefix-factor-width polynomial bound fails on some prefix (in particular the
full conjunction cannot have a factor-width certificate yielding polynomial
TDD compilation).

## 8. Scope firewall

Blocked:

- universal polynomial TDD compilation of all JANUS Tseitin instances;
- universal polynomial prefix-factor-width certificate as the missing SAT
  currency;
- replacing the nonlocal rank-one contraction problem by generic TDD
  compilation.

Not blocked:

- TDD compilation on restricted JANUS subfamilies;
- polynomial factor width after a **new exact contraction/quotient** that changes
  the represented function/interface before compilation;
- native heterogeneous boundary representations not required to be DNNF/TDD;
- local use of TDD inside a decomposition where only polynomial-size pieces are
  compiled.

## 9. Updated frontier

```text
STATIC FIXED TREEWIDTH / RANK-WIDTH
=
BLOCKED

UNIVERSAL TDD / PREFIX FACTOR WIDTH
=
BLOCKED BY DNNF PROJECTION LOWER BOUND

INDIVIDUAL PRODUCT-CUT REFINEMENT
=
CLAUSE REACTIVATION / BLOCKED

DIRECT CYCLE-SPACE RELAXATION
=
BLOCKED

APAC + NO FULL + 2-AFFINE
=
PASS POLYNOMIAL ISLAND

PRIMARY SURVIVOR
=
DYNAMIC NONLOCAL EXACT CONTRACTION / QUOTIENT

REQUIRED PROPERTY
=
STRICTLY DECREASING JOINT POTENTIAL
FOR FULL PRODUCTS + HIGH-WIDTH AFFINE/KROM

D1
=
EMPTY

P_VS_NP
=
OPEN
```
