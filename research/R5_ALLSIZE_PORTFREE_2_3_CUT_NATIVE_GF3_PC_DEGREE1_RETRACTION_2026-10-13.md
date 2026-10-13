# R5 — ALL-SIZE port-free 2/3-edge-cut exact physical colour and literal degree-one ORIGINAL SCL Polynomial Calculus retraction

Date: 2026-10-13 Europe/Kyiv.
Research PR #516 (DRAFT), main unchanged.
Ultimate goal is STILL one worst-case bit-polynomial sound, complete
`SolveLinearCubicXSAT` for EVERY original square+cubic+linear positive
Exact-One system, returning SAT source witness or UNSAT.
NOT CONSTRUCTED; P versus NP OPEN.

## 1. Source-aligned theorem: no bounded-subgraph-size assumption

Let M be any colourable ordinary finite cubic sixpole with six
distinct, labelled, physical boundary semiedges. Let B be a
NONEMPTY CONNECTED set of INTERNAL vertices containing NONE of
these six semiedge roots. Suppose exactly k=|delta(B)|=2 or k=3
ordinary internal edges cross between B and M\\B, and that
replacing B by a single edge (k=2) or one trivalent vertex (k=3)
yields a connected SIMPLE cubic sixpole M_red with the SAME six
physical boundary semiedges and their exact original label order.
Let the separated k-pole B be colourable. If M is colourable,
this last premise automatically holds by restriction; this
theorem does not pretend to decide colourability efficiently
for an arbitrary isolated B.

(a) For k=2, parity requires the TWO cut semiedges of B carry
the SAME colour in EVERY proper 3-edge-colouring.
For k=3, parity requires its THREE cut semiedges carry
three DISTINCT colours in every proper colouring.

(b) As the proper three-colour constraints are invariant under
GLOBAL S3 permutation of all colours inside B, a colourable
2pole realizes EXACTLY the three physical signatures
    (0,0),(1,1),(2,2)
and a colourable 3pole realizes EXACTLY all six permutations of
(0,1,2). Thus these are precisely the state sets of a SINGLE
ordinary edge and a SINGLE cubic vertex, respectively.

(c) Hence any proper full six-port physical boundary state of M
projects to a proper state of M_red, and conversely any
six-port state of M_red can be extended INSIDE B by an S3
relabelling of any one fixed proper B colouring, with no changes
to its six actual boundary semiedge colours. Therefore the
FULL SET of SIX-PHYSICAL-COLOUR TUPLES is IDENTICAL:
    Col_6(M) = Col_6(M_red).
In particular every 15 possible disjoint three-pair encoded
Boolean equality relation is identical, and no exposed
ExactOne can be generated/destroyed by such an expansion.

(d) For k=1, a port-free separated connected 1pole cannot
be properly edge-3-coloured: cubic parity for one semiedge
requires each of the three colour-counts to be odd, impossible
with only one semiedge. Therefore no COLOURABLE sixpole
admits a port-free 1-edge-cut component at all.

No claims are made about quotients that are not SIMPLE:
for k=2 new edge could be a loop/parallel edge; for k=3
two outside attachment roots could coincide and create
parallel edges. These cases may have meaningful multigraph
identities but are outside the prior certified *simple* cubic
source class and the n<=16 census.

## 2. STRONGER source theorem: literal degree-one Polynomial Calculus retraction

Let H be ANY simple closed cubic graph obtained by attaching
a well-formed physical sixport fixture to M without
altering the port-free B cut; and H_red the corresponding
closed graph with B replaced by an edge or vertex. For
each ordinary edge h of H and color c in C={0,1,2},
write the ORIGINAL source variable x'_(h,c). Its original
Exact-One3 source equations are:
  E'_(h) = sum_c x'_(h,c)-1,
  V'_(v,c)=sum_(h incident v) x'_(h,c)-1,
  B'_(h,c)=x'_(h,c)^2-x'_(h,c).
The quotient H_red has analogous source equations without primes.
Both are legal square+cubic+linear Positive Exact-One sources
when H,H_red are SIMPLE cubic (each variable appears in one
edge row and two endpoint-vertex-colour rows).

We construct an **EXPLICIT ONE VARIABLE => ONE VARIABLE**
ring substitution Phi sending EACH E',V' original source row
LITERALLY to one original quotient source row, and EACH B'
to a single original quotient Boolean axiom.
This is NOT merely a truth table or membership in the ideal
up to arbitrary-degree multipliers.

### Case k=2, a coloured 2pole with arbitrary number of internal vertices

Fix ANY proper B edge-colouring sigma. Its two cut semiedges
have equal colour q. Let e be the new quotient edge. Every
inside or cut edge h has reference colour a_h in {0,1,2}.
Define for all colours c:
    Phi(x'_(h,c)) = x_(e, c + q - a_h mod 3).
For any retained edge h outside B:
    Phi(x'_(h,c)) = x_(h,c).
The two cut edges have a_h=q, so both map to the new edge
WITH NO colour permutation; hence all unchanged outside
vertex-colour rows map literally to their quotient analogues.

At any trivalent vertex v inside B, the three reference
colours a_h on its three incident edges/cut semiedges are
exactly {0,1,2}. Therefore, for each c,
    Phi(V'_(v,c))
      = sum_(a=0)^2 x_(e,c+q-a)-1
      = E_(e).
Every expanded old/new edge-onehot row E'_h maps to the
quotient edge-onehot row E_(e), possibly with its three
terms permuted. Every Boolean x'^2-x' maps literally to
one quotient Boolean x²-x.

### Case k=3, a coloured 3pole of arbitrary size

Fix ANY proper colouring sigma with distinct cut colours
q0,q1,q2. Let new quotient cubic vertex v attach to the
three outside cut roots by edges e0,e1,e2.

For each inside/cut edge h, its fixed reference colour
a_h equals exactly one q_i. Let i(h) be that index, and
define:
    Phi(x'_(h,c)) = x_(e_(i(h)),c).
For retained edges, Phi is identity.

Each of the 3 cut edges h_i with a_h_i=q_i maps to its
corresponding quotient edge e_i, so all old outside
vertex-colour rows map to their original quotient rows.
At any internal vertex of B its three reference edge
colours are DISTINCT q0,q1,q2, hence:
    Phi(V'_(v,c))
      = x_(e0,c)+x_(e1,c)+x_(e2,c)-1
      = V_(new v,c).
Expanded internal edge-onehot maps literally to one of
E_(e0), E_(e1), E_(e2); Boolean axioms again map literally
to source Boolean axioms. This uses no multilinear
interpolation or higher-degree identities.

### All-d degree consequence

If H,H_red are UNSAT and one has a Boolean Polynomial
Calculus refutation of F_H at total degree d over ANY field,
apply Phi to each proof line. Every initial original
source clause/Boolean axiom becomes one initial original
quotient clause/Boolean axiom, sums remain sums, and
multiplication by a target variable becomes multiplication
by ONE quotient variable. Total degree never increases.
Thus an H refutation implies a quotient refutation of
degree <=d:

   deg_PC(F_H) >= deg_PC(F_Hred).

This is a proof of an ALL-d universal retraction theorem
for arbitrary-size COLOURABLE port-free 2poles and 3poles.
No assumption of fixed gadget size, characteristic3,
or any omitted source Boolean generator.

The reverse PC direction (compressed proof -> expanded proof)
is NOT claimed. In particular this theorem does not
spontaneously increase lower bounds under repeated expansion:
it transports a bound already present in F_Hred.

## 3. FULL original source CI controls, not merely handwaving

Source:
`experiments/r5_universal_portfree_two_three_edge_cut_exact_signature_retraction.py`
`experiments/r5_universal_native_scl_two_three_cut_pc_degree1_retraction.py`.
Workflow:
`.github/workflows/r5-native-2cut-3cut-pc-degree1.yml`.

Authoritative [CI #38420079360](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38420079360)
SUCCESS on source commit
`0298045ee3e47bb366d9c4a38310839638b88d8c`.
Previous standalone full physical 6port signatures
[CI #38419466961](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38419466961)
SUCCESS.

Four exact test geometries:
- Diamond connected 4-vertex 2pole replacing one C6 edge:
  open n10 -> n6, 63 identical full physical six-colour
  boundary tuples; close to native legal SCL72 -> SCL54.
  ALL 72 original Exact-One rows and 72 Boolean axioms mapped
  literally into the smaller original generator set.
- Double diamond 8-vertex 2pole:
  open n14 -> n6, 63 identical physical sixport tuples;
  closed legal SCL90 -> SCL54, all 90 source rows and
  90 Boolean axioms mapped literally.
- Single triangle 3pole occupying an inside port-free vertex:
  open n12 -> n10, 63 physical states;
  closed SCL81 -> SCL72, 81 rows/81 Boolean axioms exact.
- Nested triangle inflation combining a larger connected
  5-vertex port-free 3pole:
  open n14 -> n10, 63 physical states;
  closed SCL90 -> SCL72, 90 rows/90 Boolean axioms exact.

In EACH closed source verifier additionally asserts:
- graph is actually simple cubic;
- number original variables = number original positive 1in3
  source rows (square);
- row size3 (positive exactone);
- every Boolean source variable in exactly 3 source rows;
- any distinct 2 rows intersect in <=1 source variable
  (original source linearity);
- every substituted original source row maps to a literal
  existing original quotient source generator.

This finite CI is a regression/checker for the full symbolic
proof above, not a leap from four examples to all n.

## 4. New STRICT structural filter for n>=18

Older exhaustive canonical n=4,6,8,10,12,14,16 sources
(**1,041,191** interior graphs combined) yielded ZERO
exposed equality-pair ExactOne (last run n16
[#38408523974](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38408523974)
SUCCESS). Therefore a hypothetical SIMPLE connected
n=18 open ExactOne with six original ports cannot
contain ANY connected port-free internal subgraph B
separated by only k=2 or k=3 ordinary edges whenever
the edge/vertex quotient is a SIMPLE connected cubic
sixpole with fewer vertices: our ALL-N exact signature
theorem would produce a forbidden n<=16 source gadget.
Nor may it have a port-free k=1 bridge branch at all,
since the gadget must be COLOURABLE.

Thus any minimal 18-vertex candidate is **boundary-core
irreducible across all port-free cuts of cardinality <=3**
for which the quotient stays simple (and k1 is
automatically impossible). This is MUCH stronger than
excluding only contractible triangles. It is not a
claim that the full internal graph is globally
4-edge-connected: small cuts may split boundary ports
on both sides, and non-simple contractions remain open.

### Literature alignment

This is an explicit original-source version of classical
multipole colour-equivalence and parity reduction ideas,
rather than an asserted new graph-theoretic discovery.
Fiol–Vilaltella (2015), *Some Results on the Structure of
Multipoles in the Study of Snarks*, EJC 22(1) #P1.45:
https://doi.org/10.37236/3629
discusses irreducibility and cut-preserving states.
Our additional source-specific statement is the **literal
native Holyer Exact-One Boolean PC generator mapping**,
fully replayed against all original source rows.

## 5. Epistemic gates

- ANY_COLORABLE_PORTFREE_TWOPOLE_EQUALS_EDGE = PROVED_ALL_SIZE
- ANY_COLORABLE_PORTFREE_THREEPOLE_EQUALS_VERTEX = PROVED_ALL_SIZE
- SIX_PHYSICAL_PORT_STATE_PRESERVATION = PROVED_ALL_SIZE_CONDITIONAL_SIMPLE
- ORIGINAL_NATIVE_SCL_ALL_GENERATOR_PC_DEGREE1_RETRACTION = PROVED_ALL_SIZE_CONDITIONAL_SIMPLE
- FOUR_SOURCE_CONSTRUCTIONS_FULL_PHYSICAL_AND_PC_REPLAY = CI_SUCCESS
- MINIMAL_N18_NO_PORTFREE_SIMPLE_K<=3_REDUCTION = PROVED
- GENERAL_EQUALITY_PAIR_EXACTONE_N<=16 = REFUTED_FINITE
- ALLSIZE_EQUALITY_PAIR_EXACTONE_EXISTENCE = OPEN
- SAME_INTERIOR_DIFFERENT_COLOUR_KEMPE_PATH_GROUPoid = OPEN
- GENERAL_HARD_CSP_TO_NATIVE_SCL_DEGREE_BOUND_BACKSIM = NOT_CONSTRUCTED
- NATIVE_GF3_PC_DEGREE_TO_INFINITY = OPEN
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
