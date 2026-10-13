# R5 — All-size ExactOne sixpole ⇔ triple heterochromatic closures and uncolourable STAR6 closure

Scientific date: 2026-10-13 (Europe/Kyiv).
Research PR #516 DRAFT; main untouched.

## 0. Primary epistemic contract

Only successful ultimate goal would be a uniform worst-case bit-polynomial,
sound-and-complete `SolveLinearCubicXSAT` for **ALL** original square,
cubic, linear Positive Exact-One SCL instances, returning SAT with a
source-verified witness or UNSAT. That solver is **NOT CONSTRUCTED**.
P versus NP remains **OPEN**. Bounded gadget reductions, finite
classifications and proof-complexity subfamilies never imply otherwise.

## 1. Definitions and exact general theorem

Let M be any *colourable or uncolourable* proper cubic sixpole with
six labelled semiedges grouped in disjoint ordered pairs
P0=(a0,b0), P1=(a1,b1), P2=(a2,b2). For any genuine proper
three-edge colouring phi of M define
    t_i(phi) = 1 iff phi(ai)=phi(bi).
Let R(M) be its exact Boolean projection in {0,1}^3.

For each i form the SINGLE-PAIR EDGE CLOSURE M_i by gluing
(ai,bi) into an ordinary edge of the same physical 3-edge colour.
Its full proper 3-edge-colourings are *bijective* to those of M
with t_i=1; edges are literally identified, no Boolean-only signal
matching is allowed.

Call M_i HETEROCHROMATIC relative to the other two couples if
it admits at least one proper edge colouring and for EVERY such
colouring each of the two remaining couples has two different
physical colours.

THEOREM (any graph size; elementary equivalence):
    R(M)={100,010,001}
    iff:
    (A) for each i=0,1,2 the closure M_i is colourable
        and heterochromatic as above; AND
    (B) M has NO proper colouring with t=(0,0,0).

Proof:
=> All three required states have a colourable single-pair
fibre and are the only states with t_i=1, hence A; absence 000
is B.
<= For any colourable phi of M with some t_i=1, the restriction
to M_i is a proper colouring, so heterochromaticity forces
t_j=t_k=0. Thus at most one bit is 1; B forces at least one bit
to be 1. Colourability of every M_i realizes each singleton.
QED. No size, planarity, girth, or Kempe assumptions.

For arbitrary sixpoles, single-pair closure may introduce a
loop/multiedge; the semantic equivalence holds as a multipole
statement. A hypothetical exact-one gadget necessarily has
each paired semiedge on DISTINCT internal vertices because it
must realize t_i=1, whereas two incident semiedges at the same
trivalent vertex can never share a colour.

## 2. A UNIVERSAL complete physical tester of 000

Let S be the 6-pole with ONE trivalent centre c, 3 degree-3
leaves u0,u1,u2, and exactly two external ports attached to
each leaf i. The centre-leaf internal edge colour h_i is
the **third** colour missing from leaf-pair ports.

At c the three h_i are exactly the distinct three colours.
At each leaf, its two external port colours are the other
two colours in arbitrary order. Therefore S has exactly
    3! * 2^3 = 48
complete proper internal colourings and exactly 48 distinct
full six-colour boundary signatures.

THEOREM (all sizes of M, no extra hypothesis):
Col(S) is EXACTLY the 48 PHYSICAL boundary colour tuples with
(a) all three port couples heterochromatic (bit 000), and
(b) all three 3-edge-colour counts at the 6 ports even, as
required by cubic colour-parity.

Proof of converse: for any three distinct-colour pairs
with even total multiplicity per colour, let their third/missing
colours h0,h1,h2 be the three NONZERO elements of GF(2)^2.
The XOR of all six external colours vanishes, hence
h0 XOR h1 XOR h2=0. Three nonzero GF2² elements sum to zero
IFF all three are distinct. Colour the star's centre-to-leaf
edges by h0,h1,h2, and copy the given port colours to the
leaves; every cubic vertex sees all three colours. QED.

Glue M and S by identifying the SIX CORRESPONDING semiedges,
creating the closed cubic graph H(M).
Exactly matching ALL SIX PHYSICAL colours gives:
    H(M) is 3-edge-colourable
    iff R(M) contains 000.

The backward implication uses S to extend ANY actual 000
colouring of M; EVERY 000 physical tuple of M automatically
has even port colour counts by the parity lemma and hence
has a matching colouring of S. The forward implication
restricts a colouring of H to M,S, so M's paired bits equal000.

COMBINED UNIVERSAL CHARACTERIZATION:
    M exposed pair-equality Exact-One
    iff:
       all M_i are colourable heterochromatic 4poles; AND
       H(M) is NOT properly 3-edge-colourable.

This is an exact bridge from the missing open gadget to the
well-developed theory of heterochromatic 4poles and snarks.
It is NOT an existence theorem or complete algorithm.

## 3. Native ORIGINAL SCL legality of the STAR closure

Let M have n internal vertices and m=(3n-6)/2 internal edges,
with a simple interior graph. S has 4 vertices and 3
internal edges; gluing adds 6 new edges. Thus
    |V(H)|=n+4, |E(H)|=m+3+6=3(n+4)/2.
If M's three intended pairs have endpoints at distinct
M vertices, the glued graph H is simple: there cannot be
two new parallel edges between a leaf and one M vertex,
and all other edges are internal to disjoint subgraphs.
For an actual exact-one M this endpoint distinctness
is already forced by the existence of singleton states.
Thus H is a simple cubic graph; Holyer's ORIGINAL source
encoding generates 3|E(H)| = 9(n+4)/2 positive exact-one
Boolean variables/rows, each row size 3, each variable
occurs in exactly three rows, and every two rows share
at most one source variable (simplicity).
For n=16, H would have 20 cubic vertices, 30 cubic edges,
and be a valid SCL90 UNSAT source. This coincides in
SIZE with J5/SCL90 but does NOT identify its graph
or import any degree lower bound from J5.

No polynomial calculus degree theorem transfers automatically
through the M->H closure, despite the exact SAT semantics.
A complete low-degree back-simulation needs exact original
source generator identities for ALL gadgets and Boolean
axioms. Existing edge-equality-bit decoder has independent
GF3 Booleanity certificate in degree<=4, insufficient alone.

## 4. Current reproducible tests and negative evidence

`experiments/r5_universal_exactone_heterochromatic_triple_closure.py`
checks the universal iff as a truth table on ALL proper full physical
port colour relations of 6,366 nonisomorphic simple connected
sixpole interiors with n=4,6,8,10,12. For 94,065 colourable
interface partitions, exactly **44** pass all 3 single-pair
colourable heterochromatic closure tests, and ALL **44**
also admit 000; hence none realizes exactone.
CI #38409513475 SUCCESS.

`experiments/r5_universal_exactone_star6_zero_tester_closure.py`
independently reconstructs all 48 physical STAR signatures
and checks the gluing equivalence for all 94,065 source
interfaces. It does not rely on merely comparing the
abstract Boolean bits of the two connected multipoles.
A CI is required before claiming executable PASS.

Separately, the exact n14 nauty census gave 69,602 interiors,
ZERO exactone, independent source controls and unified
CI #38405242305 SUCCESS.
The n16 census is an independent active workflow; a running
job is not a completed scientific claim.

## 5. Targeted literature

Classical multipole parity and state relations:
Fiol--Vilaltella, *Some Results on the Structure of Multipoles
in the Study of Snarks*, EJC 22(1), #P1.45 (2015).
https://doi.org/10.37236/3629

For colour-open, isochromatic and heterochromatic 4poles and
their snark completions, see decomposition results:
*The smallest nontrivial snarks of oddness 4*, EJC 31? see
https://backoffice.biblio.ugent.be/download/8637147/8637151
In particular, every colourable 4pole extendable to a snark
has one of the specified iso/heterochromatic structures
under the appropriate hypotheses; this does not itself force
the triple coupled condition of our present problem.

An externally maintained example database exists at:
https://github.com/knedlicka/heterochromatic_fourpoles_le_26
But its filters (snark source graphs, girth, ≤26 vertices)
do NOT exhaust arbitrary heterochromatic 4poles. Never treat
it as a universal theorem.

## 6. GATES

- ONEHOT_IFF_TRIPLE_HETERO_4POLE_AND_NO_000 = PROVED_ALL_INPUT
- STAR6_PHYSICAL_000_STATE_TESTER = PROVED_ALL_INPUT
- ONEHOT_IFF_TRIPLE_HETERO_AND_UNCOLOURABLE_STAR_CLOSURE = PROVED_ALL_INPUT
- TRIPLE_HETERO_N<=12_44_AND_ALL_HAVE_000 = CI_SUCCESS
- STAR6_N<=12_ALL_COLOR_INTERFACES_INDEPENDENT_REPLAY = CI_PENDING
- OPEN_ONEHOT_N<=14 = REFUTED_FINITE
- OPEN_ONEHOT_N16 = UNKNOWN_PENDING_CI
- ALLSIZE_EXPOSED_ONEHOT_EXISTS = OPEN
- HETEROSTAR_NATIVE_SCL_PC_DEGREE_BACKSIM = NOT_CONSTRUCTED
- UNBOUNDED_NATIVE_GF3_PC_DEGREE = OPEN
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
