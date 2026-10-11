# R5 — Cube of a Pfaffian: explicit K3,3 SAT cancellation and exact labelled repair

Date: 2026-10-11.
Target: deterministic all-input polynomial-time `SolveLinearCubicXSAT` with
rigorous SAT/UNSAT and witness; **NOT CONSTRUCTED**.
Parent authority: PR #515 at `f91ed13f23f027277aeda85ec9b8cbbe1b8b3e8f`.
Successor experiment: draft PR #516.

## 1. Strongest direct exact coefficient formulation tested

For ANY simple cubic graph G=(V,E), |V|=n, |E|=m=3n/2,
define the ordinary perfect-matching polynomial

  M_G(x) = sum_{P perfect matching of G} prod_{e in P} x_e.

Every perfect matching has n/2 edges. Thus in M_G(x)^3
any term has m edge variables counting multiplicity, and

  [prod_{e in E} x_e] M_G(x)^3 = # labelled proper 3-edge-colourings(G).

**Proof:** squarefree full-edge monomial requires each edge to be selected
exactly once across the three matching factors. Each factor meets each
vertex exactly once; disjoint ordered matching triples are exactly
proper edge colourings with fixed colours 0/1/2. This identity is a
representation, NOT a polynomial-time coefficient extractor.
General M_G itself has no guaranteed polynomial-size ordinary
arithmetic circuit available on arbitrary graphs via the Pfaffian
with all coefficients positive.

A tempting replacement is an m-edge-variable skew Tutte matrix
K_G(x) of order n, with entry +x_{uv} at (u,v) for u<v and -x_{uv}
at (v,u). Set

  Q_G(x) = Pf(K_G(x))
         = sum_{P perfect matching} eps(P) prod_{e in P} x_e,

where eps(P) is the parity of the number of crossings when matching
edges are drawn as arcs over the ordered vertex line.

Pfaffians are evaluable in polynomial time over ordinary fields.
But the squarefree coefficient of the cube is the **signed** count

  [prod_e x_e] Q_G(x)^3
   = sum_{proper 3-colourings (P0,P1,P2)}
        eps(P0) eps(P1) eps(P2).

It need NOT be nonzero on SAT inputs.

## 2. A decisive false UNSAT on K3,3

For G=K3,3 with ordered vertices {0,1,2}|{3,4,5} and all 9 edges,
there are exactly SIX perfect matchings, corresponding to S3
permutations, and exactly TWELVE labelled proper 3-edge-colourings.

The exact finite enumeration yields

  positive sign terms: 6
  negative sign terms: 6
  signed cube coefficient: 0
  true unsigned coefficient: 12  (SAT).

There are two unordered 1-factorizations of K3,3:
one uses the three even permutations, the other the three odd
permutations. Each has 3!=6 ordered colour assignments. Their signed
products are opposite (up to a global common sign), hence exact
cancellation. This is a constructive nonzero-vs-zero counterexample
to the naive `Pfaffian^3 squarefree coefficient` SAT criterion.

The failure is not rescued by an arbitrary **common** orientation
flip per edge: replacing x_e by sign_e*x_e in all three Pfaffian
factors multiplies every full-squarefree colouring term by the same
prod_{e in E} sign_e. So if the signed coefficient is zero, it
remains zero. Changing the vertex ordering multiplies the entire
Pfaffian by a common +/-1 and its cube by the same sign: zero again.

By disjoint union with K3,3, the false-zero persists on an infinite
family of SAT cubic graph/SCL instances. This is a theorem only
against this SAME-PFAFFIAN sign-extraction method, not against all
determinant/Pfaffian, holographic, tensor or algebraic algorithms.

## 3. The correct symbolic labelled repair (identity only)

For each of three factors c=0,1,2, replace the edge x_e inside that
factor with x_e*y_{e,c}, where the y_{e,c} are 3m INDEPENDENT
commuting indeterminates. Define

 C_G(y) = [prod_e x_e] prod_{c=0}^2 Pf(K_G(x_e*y_{e,c})).

By expanding the three Pfaffians:

 C_G(y)=sum_{proper colourings chi:E->{0,1,2}}
          eps(P0(chi))*eps(P1(chi))*eps(P2(chi))
          prod_{e in E} y_{e,chi(e)}.

Each proper labelled colouring has a DIFFERENT multivariate y
monomial with coefficient +/-1. Thus NO two distinct witnesses
cancel as formal monomials:

  C_G(y) is the ZERO POLYNOMIAL
       IFF G has NO proper 3-edge-colouring
       IFF SCL_A(G) is Boolean UNSAT.

This is a correct *polynomial-size input representation* of a
coefficient-extraction problem using three polynomial-time
evaluable Pfaffian factors. It is not a proven polynomial-time
algorithm to extract/test the coefficient polynomial.

If a worst-case deterministic poly-bit-time procedure could decide
whether this C_G(y) is identically zero on ALL these promised
simple-cubic inputs, then Holyer's 1981 NP-complete 3-edge-colouring
problem would be polynomial-time decidable, so P=NP. Conversely,
because the nonzero relation has a short edge-colouring witness,
the promised coefficient-polynomial NONZERO problem is NP-complete.
This is a direct restatement of the reduction, **not** a proof P=NP.

A finite independent factor-orientation experiment on K3,3 uses
orientation sign masks (114,25,281) on the three factors and yields
signed scalar coefficient -4 rather than 0. But **arbitrary
independent signs need not prevent cancellation on every graph**,
and finding an orientation after knowing the colourings is not
a universal algorithm.

Important complexity trap: plain Pfaffian evaluation is polynomial;
extracting this common full-edge squarefree coefficient from the
PRODUCT of three Pfaffian polynomials is NOT thereby polynomial.
Interpolating a degree-m polynomial in each of m edge variables
using a naive grid takes exponentially many evaluations. Treating
formal y coefficients as an explicitly accessible table silently
requires up to 3^m monomials. No polynomial compression is proved.

## 4. Reproducible controls and proof distinction

Standalone standard-library program reusing frozen local fixtures:

  python experiments/r5_universal_pfaffian_cube_k33_cancellation.py

It independently enumerates labelled proper colourings and matching
triples, verifies on K4, K3,3, cube, five-prism, Petersen, J5 and
the 20-vertex SAT control, and checks K3,3 common-vs-independent
edge-orientation choices.

The checker is finite/exponential and labelled as such; no asymptotic
polynomial runtime is inferred from CI.

## Gate ledger

UNSIGNED_PERFECT_MATCHING_CUBE_TOP_SQUAREFREE_IDENTITY = PROVED_ALL_CUBIC.
SINGLE_PFAFFIAN_CUBE_NONZERO_SAT_TEST = REFUTED_BY_K33_SAT.
K33_PFAFFIAN_CUBE_ZERO_WITH_12_BOOLEAN_WITNESSES = PROVED_FINITE.
COMMON_EDGE_SIGN_REORIENTATION_CANNOT_REPAIR_ZERO = PROVED_ALL_CUBIC.
THREE_INDEPENDENTLY_LABELLED_PFAFFIANS_COEFFICIENT_POLY =
    EXACT_ZERO_IFF_3EDGECOLORABLE_FALSE; CORRECT NONZERO_IFF_SAT.
UNIFORM_POLYNOMIAL_SYMBOLIC_COEFFICIENT_ZERO_TEST = NOT_CONSTRUCTED.
ALL_INPUT_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Reference: Ian Holyer, The NP-Completeness of Edge-Coloring,
SIAM J. Comput. 10(4):718–720 (1981), DOI 10.1137/0210055.
