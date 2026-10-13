# R5 — Boolean pair equality wire, C6 odd-XOR gate and the saturated-Tseitin trap

Date: 2026-10-13 (Europe/Kyiv).
Branch: research/r5-cubic-flow-smith-pair-20261011; PR #516 DRAFT; main untouched.
Executable:
`experiments/r5_universal_boolean_pair_xor6_tseitin_saturation_falsifier.py`
Workflow:
`.github/workflows/r5-boolean-pair-xor6-tseitin-saturation.yml`

## 0. Scope, exact primary goal, scientific limits

The sole ultimate positive goal remains a **uniform** worst-case bit-polynomial
sound-and-complete `SolveLinearCubicXSAT` deciding ALL original positive
square/cubic/linear Exact-One systems, returning SAT witness or UNSAT.
NOT CONSTRUCTED; P vs NP OPEN. Independently frozen J5/SCL90 UNSAT
GF3 degree-3 dual already proves native degree>=4 and the triangle
inflation family preserves only this *constant* lower bound; it does not
give degree-to-infinity.

Known external hard families include:
- Buss, Grigoriev, Impagliazzo, Pitassi, JCSS 62(2), 2001,
  "Linear Gaps between Degrees for the Polynomial Calculus Modulo
  Distinct Primes"; expander Tseitin contradictions require linear
  PC degree over characteristic !=2 for the appropriate encoding:
  https://doi.org/10.1006/jcss.2000.1726 .
- Conneryd et al., FOCS 2023 / ECCC TR25-032, linear PC degree for
  certain hard *vertex* 3-colouring families:
  https://eccc.weizmann.ac.il/report/2025/032/ .
Neither lower bound transfers to native SCL without an explicit
degree-controlled back-simulation and semantically correct gadgets.

## 1. The new Boolean bit: equality, not a copied colour

Each edge-colour wire in a cubic graph carries one of three labels
0,1,2. Two dangling ports p,q carry a Boolean bit
    T(p,q)=1 if colour(p)=colour(q), otherwise 0.
This is DISTINCT from the earlier "missing colour of two DISTINCT
ports" code, whose >=3-way copying is impossible by Kempe switching.
The prior negative theorem does not directly ban replication of
the new equality BIT.

In ORIGINAL GF3 Boolean Holyer indicators X_(e,c), the Boolean
signal is represented by the degree-TWO polynomial
    T(p,q)=sum_(c=0)^2 X_(p,c)*X_(q,c).
When both port edges satisfy original edge one-hot conditions, T
evaluates exactly as the equality predicate (0 or1).

For ANY cubic 4-pole, the boundary colours have even multiplicity
per colour (equivalently boundary XOR=0 in F2^2). Hence for arbitrary
paired ports (a,b), (c,d),
    T(a,b)=T(c,d).
Proof: if a=b, the remaining two boundary colours must be equal;
if a!=b, the remaining colours are the same TWO distinct labels,
so c!=d. This is a symbolic all-topologies implication.

## 2. Exact C4 4-pole Boolean wire, both truth values achieved

Take an internally simple 4-cycle with one dangling port p_i at
each vertex i (0<=i<4), and pair ports (p0,p1) and (p2,p3).
A proper colouring of the cycle internal edges e_i=(i,i+1 mod4)
requires e_(i-1)!=e_i; the external port is the remaining third
colour. There are 18 choices for internal colourings:
    (T(p0,p1),T(p2,p3))=(1,1): 12
    (T(p0,p1),T(p2,p3))=(0,0): 6
No unequal bits occur, and BOTH truth values exist.

Frozen extension choices, in order (ring edges e0,e1,e2,e3;
ports p0,p1,p2,p3):
    bit0: (0,1,0,2 ; 1,2,2,1)
    bit1: (0,1,0,1 ; 2,2,2,2)

For each of the EIGHT local edges h and original colour c, let
    P_(h,c)(b) =
       (1-b)*1[colour_bit0(h)=c] + b*1[colour_bit1(h)=c].
This is an explicit degree-ONE polynomial in a base Boolean b.
For EVERY original target local edge Exact-One row and EVERY internal
vertex-colour Exact-One row, substitution makes the polynomial
IDENTICALLY ZERO in F3[b] (constant and linear coefficients separately
zero). For EVERY target Boolean equation P²-P, substitution is either
zero or exactly b²-b. Thus there is an **explicit complete local
degree<=2 PC simulation** of this gadget from a free Boolean bit.
This is not a closed SCL instance in isolation: its ports must be
connected to other properly constructed gadgets.

## 3. Universal 6-port relation and exact C6 odd XOR

For ANY cubic six-pole with three designated disjoint pairs of dangling
ports, the colour-XOR conservation law forbids exactly ONE
DIFFERENT-colour pair. Hence if t_i=T(pair_i), universally allowed
Boolean signatures are contained in
    {111, 100, 010, 001, 000}.
Patterns 110,101,011 cannot occur because the one unequal-colour
pair contributes a nonzero F2² boundary sum.

Construct a connected simple C6 ring, with a dangling port at each of
its six vertices; pair opposite ports
    (p0,p3), (p1,p4), (p2,p5).
A complete independent enumeration over 3^6 internal ring colour
assignments (valid iff adjacent internal ring colours differ) gives
EXACT pattern multiplicities:
    (1,1,1): 12
    (1,0,0): 18
    (0,1,0): 18
    (0,0,1): 18
TOTAL: 66 valid internal colourings and 63 DISTINCT boundary
six-tuples. In particular pattern 000 is IMPOSSIBLE on the C6 ring.
All four odd-parity Boolean assignments are realized, none else.

Therefore this exact cubic six-pole realizes
    t0 XOR t1 XOR t2 = 1.
Over GF3 for Boolean t_i this is the local polynomial condition
    (1+t0)(1+t1)(1+t2)+1=0.
Here T is degree2 in ORIGINAL source edge-colour indicators, so
the displayed pulled-back polynomial has degree <=6. The exact
local derivation into the source ideal follows from finite
interpolation; a short explicit clause combination is NOT YET
frozen and should NOT be claimed. The truth table is not itself
a source-PC certificate.

## 4. Crucial global obstruction: connecting C6 XOR gates NEVER gives UNSAT

Take ANY simple cubic graph H=(V,E), including a snark, and replace
every vertex v of H by a six-cycle. Index the three original edges
incident to v by i=0,1,2 and assign them opposite port pairs
(i,i+3). For every old edge e=uv connect the TWO corresponding
dangling port ends by two distinct new edges, preserving pairing.
The resulting graph G(H):
    has 6|V| vertices and 9|V| edges;
    is simple, connected if H is, and 3-regular;
    its ORIGINAL Holyer SCL source has n=27|V| rows/variables;
    each row/column degree=3 and pairwise row intersection<=1.

UNIVERSAL EXPLICIT SAT WITNESS INDEPENDENT OF H:
- Give EVERY inter-cycle connecting edge colour 2.
- Around EVERY even six-cycle alternate internal edge colours 0,1.
At each cycle vertex its two internal edges have 0 and1 and its
external connecting edge has2, so ALL vertex constraints hold,
including matching across each old base edge. Thus the target
graph admits a proper 3-edge colouring for EVERY cubic H.
Its original source has a verified exact-one SAT witness.

In particular if H=Petersen (base cubic graph NOT 3-edge colourable),
the expanded G(H) IS 3-edge colourable, and native SCL270 is SAT.
Therefore the naive attempt to import an *inconsistent* cubic
Tseitin charge by glueing identical C6 odd-XOR gates is FALSE.
The all-ones bit assignment t_e=1 satisfies every odd-XOR equation
because cubic base graphs have even vertex count; the complete
wire colours also synchronize (all pair port colours2).

This is a genuine **semantic counterexample** to the naive
SAT/UNSAT-preserving reduction, not just a PC-degree weakness.

## 5. More precise target for genuine hard-family import

Use expander Tseitin instances of bounded degree with vertex
parity charges whose global XOR is ODD, i.e. genuinely UNSAT.
The C6 sixpole realizes ONLY odd local charge (t0 XOR t1 XOR t2=1).
A pure cubic sixpole can never realize the full even-parity
relation {000,011,101,110} for three equality bits, because 011,
101,110 are each excluded by the universal boundary theorem.

To import Tseitin hardness, we need **new architecture** that
implements opposite local charge via a different wire/gate
interpretation (e.g. auxiliary state, nontrivial global interface,
higher-arity mixed coding), *not* merely more C6 gates or
a pure cubic sixpole on three equality bits.

The absolute simplest valid global theorem is NOT "C6 yields
unbounded degree." The proved theorem is the opposite: pure C6
gluing yields a SAT witness even when the input cubic graph is
a non-3-edge-colourable snark.

## 6. Conditional finite-local PC back-simulation compiler lemma

Let a base Boolean polynomial CSP H have constraints g_j of degree
<=r (here r<=2) over GF3. Suppose we build a bounded-size family of
target native SCL gadgets, and for EVERY legal global base assignment
there is a **consistent target-edge-colour assignment** defined
by fixed local functions P_i(b) of at most s=O(1) original base
Boolean variables. For EACH substituted target source axiom Q with local support U,
we require **local completeness**: Q vanishes on EVERY Boolean assignment
to U satisfying the designated local base constraints, NOT merely
on those partial assignments that extend to some global model.
The support U and the complete list of designated base constraints
are of size at most s=O(1); the constraints contain no base variables
outside U. This is a strong locality/interpretation hypothesis and
cannot be inferred from global SAT-preservation alone.

For a finite support U of m<=s local base Boolean variables,
define projectors
    delta_a(b) = product_{i in U}
       (b_i if a_i=1 else 1-b_i)
for each a in {0,1}^U. Modulo original Boolean axioms,
    delta_a f(b) = delta_a f(a),
    sum_a delta_a = 1.
Let Q(b) be any substituted native target source axiom
(row polynomial or Boolean polynomial); it vanishes at each
local satisfying base assignment a.
For each INVALID a choose a base original generator g_j with
g_j(a)!=0. Then (mod Boolean axioms)
    Q = sum_{a invalid} Q(a) / g_j(a) * delta_a * g_j.
This gives an explicit, finite, original-generator certificate
of bounded PC degree C=O(s+r), since support m is constant.
Any target degree-d refutation then pulls back to a base
refutation of degree <=k*d+C, where k is the uniform max degree
of variable substitutions P_i (<=s).

IMPORTANT: This finite-local lemma is a standard-type finite-domain
interpolation/back-simulation, in the spirit of Atserias–Ochremiak
(CSP proof complexity reductions), NOT a complete construction of the
missing SCL reduction. It CANNOT apply to arbitrary global
extension maps that need unbounded support, and it CANNOT import an
UNSAT hard instance into an ALWAYS-SAT C6 expansion.

## 7. Reproducible executable gates and standing statuses

Run:
```
python -u experiments/r5_universal_boolean_pair_xor6_tseitin_saturation_falsifier.py
```

The checker:
1. enumerates all C4 valid internal edge colourings and both Boolean
   phases;
2. validates complete explicit degree-one P_(edge,col)(b) substitutions
   on all 8 edge and 12 internal vertex-colour source rows and checks
   each Boolean axiom against the original base b²-b;
3. enumerates all C6 internal colourings and the exact Boolean XOR
   truth table / distinct signatures;
4. constructs expanded cubic graphs of K4, K3,3 and PETERSEN,
   verifies EVERY original SCL row, square-cubic-linear promise and
   the GLOBAL universal SAT colouring in each case.

GATES:
    C4_BOOLEAN_PAIR_WIRE_BOTH_VALUES = PROVED_EXACT
    C4_GF3_AFFINE_NATIVE_LOCAL_PC_LIFT = PROVED_EXPLICIT
    C6_BOOLEAN_PAIR_ODD_XOR = PROVED_EXACT
    UNIVERSAL_6POLE_THREE_PAIR_PARITY_RESTRICTION = PROVED
    PURE_EVEN_CHARGE_6POLE_XOR_GATE = IMPOSSIBLE
    IDENTICAL_C6_GLOBAL_TSEITIN_REDUCTION = REFUTED_BY_SAT_WITNESS
    LOCAL_CONSTANT_DEGREE_PC_INTERPOLATION_LEMMA = PROVED_CONDITIONAL
    GLOBAL_TSEITIN_OR_3COLOUR_TO_NATIVE_SCL_BACKSIM = OPEN
    UNBOUNDED_NATIVE_GF3_PC_DEGREE = OPEN
    SolveLinearCubicXSAT = NOT_CONSTRUCTED
    P_VS_NP = OPEN

## 8. NEW Petersen 6-pole: at-most-one equality, not a reusable closed gate

Research code:
`experiments/r5_universal_petersen_6pole_boolean_atmostone_exact_source.py`;
workflow: `.github/workflows/r5-petersen-sixpole-boolean-atmostone.yml`.

Take the Petersen cubic graph (10 vertices, 15 edges). Remove THREE
pairwise vertex-disjoint edges on a six-cycle:
    (0,1), (2,3), (5,8).
The remaining internal 10-vertex graph has 12 ordinary edges plus
six dangling semiedges, paired according to each severed edge.
Define Boolean T_i=1 if the two semiedges at endpoints of old cut
edge i have the SAME colour.

UNCONDITIONAL symbolic negative case: the state 111 cannot occur.
If all three pairs were equal, the three removed Petersen edges
could be re-inserted in those corresponding colours, giving a
proper 3-edge colouring of the Petersen snark, contradiction.
As for ANY cubic 6-pole, the 011,101,110 boundary equality
patterns are excluded by GF2² parity.
Therefore only {000,100,010,001} can occur.

Finite exact exhaustive result:
- All four allowed patterns ARE REALIZED.
- 108 complete colourings of the 12 ordinary internal edges
  (36 for 000 and 24 for each of 100,010,001).
- 84 DISTINCT six-port colour signatures.
This yields an **AT-MOST-ONE** Boolean ternary relation on
equality bits for this open multipole.

Composing with the C6 opposite-pair odd-XOR multipole by gluing
all six corresponding pairs of semiedges gives a closed,
simple cubic graph with 16 vertices, 24 edges and an ORIGINAL
square+cubic+linear SCL72 source.
Intersection of local Boolean signatures is EXACTLY {100,010,001}.
The executable enumerates, builds and independently checks all
36 proper edge-colourings against EVERY original SCL row.

CRITICAL: The 3 Boolean values are **INTERNAL**: all six ports
are consumed when the two multipoles are glued. This is NOT yet
a reusable standalone three-input Exact-One gate with three external
pair interfaces. Claiming a global native SCL reduction from this
closed SAT72 would be invalid.

Published structural context: Petersen 4-/6-poles, isochromatic
connectors and the colour parity lemma are classical snark tools,
not invented here. Example reference:
https://www.combinatorics.org/ojs/index.php/eljc/article/download/v31i2p6/pdf/

NEW GATES:
    PETERSEN_SIXPOLE_T_EQ_ATMOSTONE = PROVED_EXACT
    C6_PLUS_PETERSEN_INTERNAL_T_EXACTONE = PROVED_EXACT
    CLOSED_NATIVE_SCL72_36_SAT_WITNESSES = TESTED
    EXPOSED_T_EXACTONE_THREE_INPUT_GATE = NOT_CONSTRUCTED
    GENERAL_HARD_PC_REDUCTION = OPEN
