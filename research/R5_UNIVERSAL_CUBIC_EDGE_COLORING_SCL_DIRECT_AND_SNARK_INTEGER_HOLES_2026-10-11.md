# R5 — Gadget-Free Cubic Edge-Colouring SCL Bridge and Infinite Signed-Integer Semigroup-Hole Family

Date: 2026-10-11.
Repo: Hawkar-usls/Janus-Fundamentum, PR #515, branch
research/parity-isolation-trade-checkpoint-20261009.

**User goal unchanged:** Construct a deterministic ALL-INPUT
n^O(1)-bit-time SolveLinearCubicXSAT(A), returning verified SAT
witness or rigorous UNSAT on EVERY square-cubic-linear Positive
Exact-One matrix, with complete soundness, completeness and
worst-case polynomial runtime proof.

**Verdict:** A new exact, gadget-FREE bijection from 3-edge colouring
of SIMPLE CUBIC GRAPHS to a legal SCL instance is established.
An all-input rational-nullity theorem and a signed-integer
semigroup-hole theorem for every uncolourable cubic graph with a
perfect matching are established. A Petersen graph UNSAT45
fixture with an INDEPENDENT perfect-matching obstruction is
implemented. No polynomial universal solver or full hard
bounded-depth Frege family is proved; P_VS_NP OPEN.

## I. Exact gadget-free construction

Let G=(V,E) be ANY finite simple cubic graph, with
  N=|V| even, M=|E|=3N/2.
Introduce one Boolean variable x_(e,c) for each
  (e,c) in E x {0,1,2},
and the following exact-one checks:

   (E_e)    x_(e,0)+x_(e,1)+x_(e,2)=1
            for every edge e;

   (C_vc)   sum_{e incident to v} x_(e,c)=1
            for every vertex v and colour c.

Each check has EXACTLY THREE entries because deg_G(v)=3.
Each variable x_(e,c) occurs in exactly THREE checks:
E_e, C_(u,c), C_(v,c) for e={u,v}.
There are 3M variables and M+3N checks, and since
3N=2M,

   M+3N=3M.

Thus the incidence is SQUARE with every row/column
weight three, i.e. cubic in both directions.

Linearity/C4-freeness is exact:
  * two edge checks share zero variables;
  * edge check E_e and vertex-colour C_(v,c) share
    precisely x_(e,c) when e meets v, zero otherwise;
  * distinct vertex-colour checks with different
    colours share zero variables;
  * distinct vertex-colour checks with the same
    colour share x_(e,c) if and only if e joins
    their vertices, at most one because G is simple.

Therefore every two rows share at most ONE variable.
NO occurrence splitting, padding or E118 gadget is needed.

## II. SAT equivalence is a TRUE BIJECTION

Every Boolean assignment satisfying edge checks
selects one colour for every edge e.
Every vertex-colour check requires precisely one
incident edge for each colour, which is equivalent
to a proper 3-edge-colouring of the cubic graph.
Conversely any proper 3-edge-colouring produces
a unique satisfying assignment x.

Therefore:

    Graph G proper 3-edge-colourable
       IFF SCL_A(G) has an Exact-One Boolean witness.

Moreover the witness maps are deterministic, inverse,
linear-size, and checkable in O(M) bit operations
on the sparse representation. This is a direct
proof-complexity **identity of the usual CNF axioms**
of graph 3-edge-colouring and the generated Exact-One
CNF, not merely an existential SAT-preserving gadget.
To prove a bounded-depth Frege LOWER bound still
requires independently established hardness of an
appropriate graph edge-colouring family; source
NP-completeness by itself does NOT establish proof-size
lower bounds.

Ian Holyer, "The NP-Completeness of Edge-Coloring",
SIAM Journal on Computing 10(4):718-720, 1981,
DOI: https://doi.org/10.1137/0210055,
establishes NP-completeness on cubic graphs. Hence
SCL NP-completeness follows from THIS independent direct
linear reduction, in addition to predecessor E118.

## III. New all-input rational-rank lower bound

For each graph vertex v, the following row identity
holds over ordinary integers, not merely modulo 2/3:

   sum_{c=0}^{2} row(C_(v,c))
    - sum_{e incident v} row(E_e) = 0.

Indeed for any column x_(e,c), the contribution is
+1-1=0 when v is an endpoint of e and 0 otherwise.
For different v these N left-nullspace relations are
LINEARLY INDEPENDENT: the coefficient of the unique
vertex-colour row C_(v,0) is +1 only in relation v.

Therefore

   rank_Q(A_G) <= 3M - N;
   nullity_Q(A_G) >= N.

For Petersen: N=10, M=15, matrix size n=45 and
rational nullity >=10. Thus the easy rational
invertibility obstruction E129 CANNOT decide the
whole graph-edge-colouring SCL subfamily: these
matrices are uniformly far from invertible.

The checker constructs and directly verifies all
N independent integer left-kernel relations.

## IV. New integer-lattice saturation holes for snarks

Suppose G is cubic and has ANY perfect matching M.
Define an integer vector z on all 3M edge-colour
coordinates by

    z_(e,0)=z_(e,1)= 1,  z_(e,2)=-1
       when e in M;

    z_(e,0)=z_(e,1)= 0,  z_(e,2)= 1
       when e not in M.

For every edge e, its three integers sum to 1.
At any vertex v exactly one incident edge belongs
to M, so for colours 0,1 exactly one of its
incident z_(e,c) is 1, and for colour 2 the sum is
(-1)+1+1=1.

Thus

    A_G z = 1

with z INTEGRAL, although some entries z=-1.
It follows that the modular linear system
A_G x=1 mod q is solvable for EVERY positive
modulus q (indeed, the SAME z modulo q works).
The uniform nonnegative rational vector x=1/3
also solves A_G x=1 for EVERY cubic graph.
Therefore every UNCOLOURABLE cubic G with a
perfect matching yields a genuine semigroup hole

    b=1 in (Z A_G intersect Q_>=0 A_G) BUT
    b not in S(A_G)=A_G Z_>=0^(3M).

Because every nonnegative integral solution to
positive EO3 would automatically be Boolean,
the missing semigroup membership is exactly
the graph's 3-edge uncolourability.

In particular EVERY bridgeless SNARK has a
perfect matching by Petersen's matching theorem
(Julius Petersen, 1891; see
https://mathworld.wolfram.com/PetersensTheorem.html).
Hence all such snarks produce legitimate SCL
UNSAT instances on which ALL linear-congruence
consistency filters, even checking every modulus,
return compatible. This gives a STRUCTURAL
infinite FAMILY of integer semigroup holes
(using the known infinite families of snarks).

**This does NOT prove graph edge-colouring hard
for the polynomial-time oriented semigroup algorithm
or for bounded-depth Frege proof systems.** It
only refutes all-input decision by integer/rational/
finite-ring LINEAR consistency.

## V. Exact independent finite fixtures

Executable:
  python experiments/r5_universal_cubic_edgecolor_direct_scl_bridge.py

It independently constructs cubic graphs, validates
the exact incidence structural promise and checks
3-edge-colourability using an independent exponential
graph backtracker, then asks the production hybrid
ExactSupport and verifies SAT witnesses.

Expected and previously validated in focused CI:
  K4 graph N=4 E=6 -> target n=18 SAT
  K3,3 graph N=6 E=9 -> target n=27 SAT
  cube graph N=8 E=12 -> target n=36 SAT
  Petersen graph N=10 E=15 -> target n=45 UNSAT

For Petersen, enumerate all six perfect matchings
and prove that the residual 2-regular complement
is NEVER bipartite, hence cannot be covered
by two alternating edge-colours. This gives
a graph-side exhaustive UNSAT certificate
INDEPENDENT of ExactSupport.

The checker also:
 - verifies all N independent rational-left-kernel
   vectors directly against the source matrix;
 - explicitly constructs and verifies the signed
   integer z with A z=1 for Petersen;
 - confirms polynomial mod9 linear consistency
   despite Boolean UNSAT on Petersen.

These finite tests are exact controls, not worst-case
asymptotic size proofs.

## VI. Parallel modular no-go for isolated parity gadgets

The separate checker
experiments/r5_universal_xor3_mod3_incidence_boundary_no_go.py
proves an all-input necessary constraint on any
SEPARATED positive EO3 gadget with 3 Boolean ports
and all internal variables of occurrence degree3.

Sum all gadget EO rows:
  m = d1*p+d2*q+d3*r+3*sum_internal z.

Modulo3 the port tuple must lie on one
fixed affine linear congruence
  d1*p+d2*q+d3*r == m (mod3).

For the gadget projection to contain ALL four
even-parity or ALL four odd-parity triples,
this forces d1=d2=d3=0 mod3.
Thus ports of local degree 1 or 2 cannot implement
even OR odd ternary XOR3 in such an isolated
regular-EO3 construction. This blocks an
incorrect naive Tseitin-to-SCL proof transfer,
not coupled or re-encoded global gadgets.

For an exact positive control, rows
(a,b,p),(a,b,q),(a,b,r) with ports degree1
and internal a,b degree3 enforce exactly equality
p=q=r; models 000 twice and 111 once.
This is a non-linear gadget so not by itself
a legal standalone SCL source. The exact
3-port equality control is consistent with
the modular count.

## VI-A. Explicit infinite Isaacs flower snark J_k SCL family

The signed-integer hole theorem is not confined to a finite
Petersen graph. The reproducible program

    experiments/r5_universal_isaacs_flower_snark_scl_hole_family.py

constructs for every k>=5 the standard flower graph:
- 4k vertices A_i,B_i,C_i,D_i, i in Z/kZ;
- 3k claw edges A_i B_i, A_i C_i, A_i D_i;
- k-cycle B_0 B_1 ... B_(k-1) B_0;
- 2k-cycle C_0 C_1 ... C_(k-1) D_0 D_1 ...
  D_(k-1) C_0.

These have exactly 6k edges and all vertices degree3.
For ODD k>=5 they are the flower SNARKS J_k of
Rufus Isaacs (1975), a published infinite family of
bridgeless cubic graphs with chromatic index FOUR:

    R. Isaacs, Infinite Families of Nontrivial Trivalent
    Graphs Which Are Not Tait Colorable,
    American Mathematical Monthly, 1975.
    https://mathworld.wolfram.com/FlowerSnark.html

Their exact legal square+cubic+linear JANUS incidence
matrices have n=3*(6k)=18k rows and 18k columns.

An explicit O(k)-constructible perfect matching is
M={A_i B_i : all i} together with edges pairing
consecutive positions 0-1,2-3,... of the
2k-cycle. This directly proves the existence of an
integer signed solution to A_G z=1, with exactly
2k coordinates z=-1. It also yields
rational nullity at least 4k.

Thus the infinite set J_k for odd k>=5 provides
independently sourced ALL-UNSAT legal SCL matrices
which cannot be excluded by any family of integer
linear solvability or mod-q linear consistency
filters. This does NOT prove high Frege complexity
or an exponential lower bound on any particular
DAG solver.

Focused CI run #38153209789 = SUCCESS:

    J5: graph=20 vertices, 30 edges; target SCL n= 90;
        Z-solution verified, nullity>=20,
        original DAG explored 200 states -> UNKNOWN.

    J7: graph=28 vertices, 42 edges; target SCL n=126;
        Z-solution verified, nullity>=28,
        original DAG explored 200 states -> UNKNOWN.

    J9: graph=36 vertices, 54 edges; target SCL n=162;
        Z-solution verified, nullity>=36,
        original DAG explored 200 states -> UNKNOWN.

For J5, independent explicit graph-edge-colour search also
returned UNSAT. For J7/J9 the full uncolourability
assertion uses Isaacs' published all-odd-k theorem,
not a truncated search result.

Each 200-state exhaustion is a RESOURCE GUARD: no
SAT/UNSAT conclusion is inferred from it, and the
numbers are finite OBSERVATIONS, not a
superpolynomial asymptotic lower bound.

## VII. Next decisive missing theorem

To establish a genuine worst-case polynomial
SolveLinearCubicXSAT one must still provide an
explicit all-input exact decision/witness evaluator
in n^C BIT time. This direct graph reduction
confirms that doing so would in particular solve
3-edge-colouring of ALL cubic graphs in polynomial
time, a known NP-complete problem.

To establish a SUPERPOLYNOMIAL lower bound for the
frozen JANUS AND/OR residual refutation system,
one now has a candidate interface with NONE of
the hidden E118 gadget choices: produce a hard
family of cubic graph edge-colouring contradictions
and prove a bounded-depth Frege lower bound on
their edge-colouring CNF. Our predecessor AND/OR
to bounded-depth Frege simulation would transfer
it immediately to the exact SCL incidence matrices.

No such hard 3-edge-colouring lower bound was
verified in the targeted literature sweep.
Do not infer it from NP-completeness, snarkness,
Petersen's six matchings, or integer semigroup holes.

## Gate ledger

GADGET_FREE_CUBIC_EDGE3COLOR_TO_SCL = PROVED_ALL_INPUTS.
SCL_PRESERVES_EDGE_COLORING_WITNESS_BIJECTION = PROVED.
SCL_GRAPH_EDGE_COLOR_NP_COMPLETENESS = HOLYER_LITERATURE.
SCL_GRAPH_LEFT_NULLITY_GE_NVERTICES = PROVED_ALL_INPUTS.
SCL_BRIDGELESS_SNARK_INTEGER_SEMIGROUP_HOLES = PROVED.
ISAACS_ODD_FLOWER_SNARK_JK_SCL_N18K_SEMIGROUP_HOLES = PROVED_USING_LITERATURE.
ISAACS_J5_J7_J9_200_STATE_GUARD_UNKNOWN = VERIFIED_FINITE.
PETERSEN_UNSAT45_W_PERFECT_MATCHING_CERT = VERIFIED_FINITE.
SEPARATED_XOR3_DEG1_OR_DEG2_MOD3_NO_GO = PROVED.
LEGAL_SCL_SUPERPOLYNOMIAL_BDFREGE_PROOF_LOWER_BOUND = OPEN.
FROZEN_ANDOR_SUPERPOLYNOMIAL_PROOF_LOWER_BOUND = OPEN.
ALL_INPUT_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
