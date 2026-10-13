# R5 — Every Fixed Modulus Loses SAT on the Cubic 4-Flow Count

Date: 2026-10-12. Target: deterministic worst-case polynomial
`SolveLinearCubicXSAT` for ALL square+cubic+linear exact-one inputs.
**NOT CONSTRUCTED. P_VS_NP = OPEN.**

Authority: R5 PR #515 gadget-free simple cubic 3-edge-colouring
to legal SCL reduction; successor PR #516 exact cubic 3-edge-cut
count factorization and independent flow-count tests.

## I. Targeted global-algorithm attack, NOT a partial terminal

The previous SCL->cubic-graph bridge shows that counting labelled
3-edge-colourings equals the number F_G(4) of nowhere-zero
F2^2-flows, and SAT iff F_G(4)>0.

An attractive proposed shortcut is:
  "Compute F_G(4) modulo a small fixed integer q, divide out the
   known S3 symmetry, and test whether the residue is nonzero."

**Theorem: this decision criterion fails for EVERY fixed q>=2,
even for connected simple cubic graphs, irrespective of which
finite moduli are chosen in advance.**

The statement is stronger than observing that every labelled
count is a multiple of 6: we normalize by that six FIRST.

Precisely, for each q>=2 there exists a connected, simple,
properly 3-edge-colourable cubic graph G_q with

   C(G_q) := F_{G_q}(4)/6 > 0,
   C(G_q) == 0 (mod q).

The Petersen graph P is connected simple cubic with
C(P)=0. Hence computing ONLY C mod q gives the SAME zero
output on G_q (SAT) and P (UNSAT).

For any *finite* family of fixed moduli q1,...,qs,
apply the theorem to q=lcm(q1,...,qs); the same
SAT graph collides with Petersen on all residues.

This does NOT refute methods that use unbounded, input-dependent
moduli whose product exceeds an a priori count bound, symbolic
variables, random isolation, full incidence structure, or any
other non-modular data. It does not imply a time lower bound
on all Turing machines or rule out P=NP.

## II. Exact labelled colour count of cycle prisms

Let P_k=C_k square K2 be the prism graph on 2k vertices,
for k>=3. There are k vertical rung edges, k top and k
bottom cycle edges.

At each rung i, let t_{i-1},t_i be the top incoming/outgoing
horizontal edge colours and b_{i-1},b_i the bottom pair,
each in {0,1,2}. A proper edge colouring requires:

  t_{i-1} != t_i,       b_{i-1} != b_i,
  {t_{i-1}, t_i} == {b_{i-1}, b_i};

the rung colour is the unique third colour absent from
both horizontal pairs.

Thus the horizontal *state* (t_i,b_i) evolves under a
9-state transfer relation. This decomposes into:

(1) three diagonal states (a,a): transition from (a,a)
    to (c,c) for any c!=a; adjacency matrix J3-I3.
    Its eigenvalues are 2, -1, -1, so the number of
    cyclic length-k walks is 2^k+2(-1)^k.

(2) six off-diagonal states (a,b), a!=b:
    the ONLY successor is (b,a), forming THREE
    independent 2-cycles. Their contribution to trace
    is six when k is even and zero when k is odd.

**Exact identity for every k>=3:**

  F_{P_k}(4) = #Col3(P_k)
             = 2^k + 2(-1)^k + 6*[k even].

In particular, for every ODD k>=3:

  F_{P_k}(4) = 2^k-2,
  C(P_k) = (2^(k-1)-1)/3.

This 9-state transfer calculation is independent of
all graph 3-sum/gadget decisions, and is reimplemented
as an independent exact 9x9 integer-matrix program.

This formula is classical/elementary chromatic-polynomial
transfer machinery and is NOT claimed as new mathematical
priority or as a universal cubic 3-edge-colouring solver.

## III. Full explicit modular counterexample for arbitrary q

Write the input modulus in its unique form

   q=2^a * u, where u>=1 is ODD.

Choose an even integer e>=2 such that

   2^e == 1 (mod 3u).

It exists because gcd(2,3u)=1. One can use the
smallest such even e, found constructively by repeated
modular squaring, with e<=2*phi(3u)<=6u.
Set k=e+1, so k>=3 is odd and

   C(P_k)=(2^e-1)/3 >0,
   C(P_k) ==0 (mod u).

Take a copies of K3,3, which has 12 proper labelled
3-edge-colourings, and iteratively construct the
*cubic vertex 3-edge-sum* with the prism. The graph
remains connected, simple and cubic with precisely

   N(G_q)=2k+4a

vertices. The 3-edge-sum counting identity, proved
in the predecessor PR516 checkpoint, is

   F_{G1+_3G2}(4) = F_{G1}(4)*F_{G2}(4)/6.

Hence each K3,3 multiplies the normalized count
C(F)=F(4)/6 by C(K3,3)=12/6=2, yielding

   C(G_q)=2^a * (2^e-1)/3 >0.

Since u divides the right-hand odd factor,
q=2^a u divides C(G_q). Yet G_q is SAT.
This completes the all-q theorem.

The construction runs in time polynomial in the
*numeric* value of q, and creates O(q+log q)
graph vertices. No claim of polynomial size in the
binary bitlength log q is made.

**Infinite strengthened 2-adic family**:
take q=2^t, u=1 and k=3. For each t>=1 one gets
a connected simple SAT graph on 6+4t vertices with

   C(G_(2^t)) = 2^t.

Thus not even computing the S3-normalized count
mod 2^t can distinguish it from UNSAT if t is only
proportional to the number of joined gadgets.

Because the direct cubic graph->SCL incidence map
preserves Boolean witnesses bijectively, EVERY one
of these graphs produces a fully legal SCL instance
with the same SAT-vs-UNSAT modular ambiguity.

## III-A. Explicit all-q witness construction

The entire SAT collision family is now **constructively witnessed**,
not merely shown colourable by positive count.

For an odd prism P_k, choose top rail colour t_i=i mod 2 for
i=0,...,k-2, but assign the final horizontal rail edge
t_(k-1)=2. Assign each bottom horizontal edge the SAME colour
as its corresponding top edge. At rung vertex i, the previous
and next rail colours are unequal, so give the vertical rung
the unique third colour in {0,1,2}. The same holds on the bottom.
This constructs a proper labelled 3-edge-colouring in O(k).

For K3,3 with bipartitions {0,1,2} and {3,4,5}, colour edge
(i,3+j) with (i+j) mod 3. All incident colours are distinct.

To perform each cubic 3-edge-sum, list the three neighbours of
the two deleted vertices in the boundary order induced by
the join. The three boundary edge colours in each input are
different. There is a UNIQUE S3 colour permutation on the
second component matching them in that order. Apply it globally
to the second component and copy all remaining edge colours.
The resulting cubic graph's three incident edge colours are
exactly {0,1,2} at every vertex.

The executable constructs this colouring on ALL requested q,
checks it independently against every original cubic vertex,
and, for small q, also maps it through the 3-edge-colour->SCL
bijection and validates every positive exact-one row.

Thus the statement `C(G_q)>0` is supported by a uniform explicit
witness constructor AND the separate all-input counting proof.

## IV. Reproducible adversarial tests

Executable (standard library and existing tested R5 imports):

    python experiments/r5_universal_modular_flow_count_all_q_no_go.py

Checks:
- exact diagonal/off-diagonal 9-state transfer independently
  against the closed form for k=3,4,5,6,7,9,11;
- exhaustive direct edge-colouring for small prisms;
- graph constructor legality and count by 3-sum theorem
  for q in {2,3,4,5,6,7,8,9,10,11,12,17,31,60,125,256};
- direct finite enumeration on all small constructed G_q;
- explicit constructive proper 3-edge colouring on EVERY G_q;
- independent legal SCL rows with exact-one witness on small q;
- 2-adic connected SAT family t=1,2,4,8,16 with
  N=6+4t and C=2^t.

No loop over all colourings on arbitrarily large graphs
is claimed polynomial; the exact all-q proof is analytical.
CI PASS proves finite replay only.

## V. Global-solver gate

FIXED_MODULUS_NORMALIZED_COLOUR_COUNT_SAT_DECIDER = REFUTED_ALL_Q.
CONNECTED_CUBIC_MODULAR_SAT_COLLISION_CONSTRUCTION = PROVED_ALL_Q.
ODD_PRISM_LABELLED_3EDGE_COLOUR_COUNT = PROVED_ALL_ODD_K.
THREE_EDGE_SUM_NORMALIZED_COUNT_MULTIPLICATION = PREDECESSOR_PROVED.
CONSTRUCTED_GRAPH_IS_LEGAL_SCL = PREDECESSOR_PROVED.
ALL_Q_EXPLICIT_SAT_WITNESS_CONSTRUCTION = PROVED.
UNIFORM_POLYNOMIAL_FLOW_NONZERO_TEST = NOT_CONSTRUCTED.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Interpretation: A successful universal algebraic method must
contain a genuinely input-global anti-zero mechanism, not
merely arithmetic counting modulo finitely many preselected
small moduli. This is a falsified shortcut, not evidence
that a different polynomial method cannot exist.

Literature context:
- Ian Holyer, The NP-Completeness of Edge-Coloring,
  SIAM J. Comput. 10(4):718-720 (1981), DOI 10.1137/0210055.
- Classical Tutte flow polynomial: 3-edge-colourings of
  cubic graphs correspond exactly to nowhere-zero 4-flows.
