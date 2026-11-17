# R5 — Global Hadamard Cycle-Edge Dual of E118 Primitive Phase

Date: 2026-10-11.
Repository: Hawkar-usls/Janus-Fundamentum, research branch
`research/parity-isolation-trade-checkpoint-20261009`, PR #515.
Parent: E118 exact occurrence-split hardness gadget; PR515
`R5_UNIVERSAL_PRIMITIVE_PHASE_WALSH_ELIMINATION_2026-10-11.md`
(Hall-matched two-port W, exact full histogram).

**Status: exact general algebraic duality and frozen integer checks;
NOT a polynomial universal evaluation theorem.**
P_VS_NP = OPEN.

## I. Starting point: already-proved Hall-matched E118 source sum

Let S have n source variables and n triple clauses, each source
variable occurring exactly three times. Choose a perfect matching
of clauses to variables; the exact polynomial construction is
already in PR515. In each source clause c, write v(c) for
its matched variable and {a(c),b(c)} for the other two.

Let p_v be one free GF2 kernel bit for every source variable,
and q_v=p_{a(c)} XOR p_{b(c)}, for the unique clause
matched to v. The entire half-weight enumerator of the E118
target, with a formal alpha satisfying z=alpha^2, is

    S(alpha)=
      sum_{p in F2^n} product_{v=1}^n W_{p_v,q_v(p)}(alpha),

where

    W =
       [ 1+alpha^6       2 alpha^5 ]
       [ alpha^4+alpha^6 2 alpha^7 ].

The equality in Z[alpha] is exact, and S(alpha) has only EVEN
nonzero exponents because every global target kernel word has
even weight. The coefficient [alpha^(20n/3)] S(alpha) is the
target Exact-One count when 3|n (for q90 n=9 => alpha^60).

## II. Exact all-input full Walsh transformation (no complex rounding)

Put f_v(p,a,b)=W_{p,a XOR b}, and let
H=[[1,1],[1,-1]]. Define C=H W H, indexed by bits (r,s):

    C_{r,s} =
      sum_{p,q in F2} (-1)^(rp+sq) W_{p,q}.

Then for ALL p,a,b in F2 the full 3-bit inverse Walsh
identity is

    4 f_v(p,a,b) =
       sum_{r,s in F2} C_{r,s} (-1)^(rp+s(a+b)).

The Fourier coefficient on the two other-source ports
has equal frequency s. This equality is a symbolic
identity of polynomials in alpha, not a numerical fit.

Expanding product over matched clauses, then summing
over p in F2^n independently, makes each variable p_v
contribute

    sum_{p_v in F2}
      (-1)^[p_v*(r_v+sum_{c: v in {a(c),b(c)}} s_{v(c)})]
     = 2 * [r_v = XOR_{c: v in {a(c),b(c)}} s_{v(c)}].

Since v occurs exactly THREE times as a source variable,
one as the matched clause owner, it is one of the two
non-owner ports in precisely TWO other clauses.
Call their matched owners l(v),r(v). Therefore

    r_v = s_{l(v)} XOR s_{r(v)}.

Substituting back yields the exact GLOBAL dual identity

    2^n S(alpha)
       = sum_{s in F2^n}
            product_{v=1}^n
                C_{ s_{l(v)} XOR s_{r(v)}, s_v }(alpha).

No sign approximations, determinant heuristics or hidden
continuous integration. On the left the phase is already
the full E118 target kernel enumerator; on the right
all coefficients are exact integers after dividing by 2^n.

## III. Structural theorem: the NON-OWNER graph is a 2-factor

For every source clause matched to owner v, put one graph
EDGE labelled v between the two remaining source variables
a(c),b(c). These are distinct for legal 3-clauses. Every
source variable occurs exactly twice as a NON-OWNER,
so the resulting n-vertex, n-edge undirected multigraph H
has every vertex of degree exactly 2.

Consequently H is a disjoint union of cycles (allowing
parallel-edge cycles of length two). This theorem holds
for EVERY 3-uniform cubic source, independently of
linearity, girth, planarity or SAT status.

The owner label v on an edge {a,b} is usually NEITHER
endpoint. It is a permutation between source vertices
and the edges of H. The resulting dual local factor

    C_{s_{l(v)} XOR s_{r(v)}, s_v}

couples the two edge bits incident at vertex v
to the bit on the (possibly distant) edge labelled v.
Therefore H being a union of cycles does NOT make the
full partition function a product of independent
cycle transfer matrices. The missing global elimination
is the interaction via this owner-to-edge permutation.

### Strong equivalence theorem: cubic Exact-One IS cycle-cover + permutation Exact-One

The preceding Hall-matching construction has a polynomial-time inverse.

Given n vertices and a 2-regular MULTIGRAPH H with exactly n
edges, choose a bijection owner:E(H)->V(H) such that the owner
of every edge e={a,b} is distinct from both a and b.
Create one triple check

    x_owner(e) + x_a + x_b = 1

for each edge e. Every vertex appears in exactly ONE check as
the owner, and in exactly TWO checks as an endpoint of H;
therefore every variable occurs exactly three times,
there are exactly n cubic checks and n variables,
and the result is a valid cubic monotone 1-in-3-SAT SOURCE.

Conversely, every cubic 3-uniform source has a clause-variable
perfect matching (Hall counting) and hence yields precisely
such a pair (H,owner) in polynomial time. The original
source clause sets are recovered exactly as above. The
checker performs this inverse reconstruction for all sources.

Therefore the ORIGINAL NP-complete 3-uniform, 3-regular,
monotone 1-in-3-SAT class admits a **polynomially equivalent**
presentation as:

    CYCLE_OWNER_EXACTONE(H, owner):
       decide whether exists x in {0,1}^n s.t.
       x_owner(e) + x_endpoint1(e) + x_endpoint2(e) = 1,
       for every edge e of a 2-regular H.

This class is NP-complete, assuming the E118 source
NP-completeness predecessor. It is NOT a new easier subclass:
the arbitrary owner permutation is the full source coupling.
The proof is an exact reduction in both directions.

The positive lesson: the difficult global information can be
localized entirely to a PERMUTATION between vertices and
edges of an otherwise trivial 2-factor.
The negative lesson: "H is just cycles" does NOT supply
a universal polynomial algorithm when owner labels are
unrestricted. A new theorem must exploit both the cycles
and the owner permutation, or bypass this representation.

### Explicit small CONNECTED cross-cycle witness

Take six variables v0..v5 and clauses with listed owners:

    owner v3: (v3,v0,v1)
    owner v4: (v4,v1,v2)
    owner v5: (v5,v2,v0)
    owner v0: (v0,v3,v4)
    owner v1: (v1,v4,v5)
    owner v2: (v2,v5,v3).

This is a connected square cubic 3-uniform SOURCE; it need
not be linear, since E118 makes the TARGET linear and
C4-free. The chosen owner-clause matching is valid.
H consists of TWO distinct triangles on
{v0,v1,v2} and {v3,v4,v5}.
But every owner v on the first triangle labels an edge
on the OTHER triangle. Thus in the dual, every local
factor C couples bit(s) on two DIFFERENT cycle components.

More decisively, keep EXACTLY the same two-triangle 2-factor
H and relabel ONLY the owners of the three second-triangle edges.

CASE NEGATIVE (six owner-labelled clauses):
    (v3,v0,v1), (v4,v1,v2), (v5,v2,v0),
    (v0,v3,v4), (v1,v4,v5), (v2,v5,v3).

CASE POSITIVE (the SAME underlying six undirected cycle edges):
    (v3,v0,v1), (v4,v1,v2), (v5,v2,v0),
    (v1,v3,v4), (v2,v4,v5), (v0,v5,v3).

Both cubic source hypergraphs are connected, and both have
the SAME unlabelled two-triangle H with identical cycle
components {v0,v1,v2} and {v3,v4,v5}. Complete finite
enumeration of all 2^6 source Boolean assignments gives:

    NEGATIVE source: 0 Exact-One witnesses;
    POSITIVE source: 3 Exact-One witnesses.

E118 yields connected legal square/cubic/linear target
formulas N=60, whose exact solution counts differ by
the proven extension factor 2^(2*6/3)=16:

    NEGATIVE E118 target: Z=0;
    POSITIVE E118 target: Z=48.

The new dual checker compares EVERY integer coefficient
of the full source-weight phase polynomial in both cases
between independent primal and dual calculations.

**Therefore no function of the unlabelled 2-factor H
alone, even given its full edge set, can be a universal
Exact-One decision procedure.** The owner-to-edge
permutation is essential data, and the exact dual
formula preserves it.

This is a concrete all-integer obstruction to the claim
"2-factor H -> independent cycle transfer":
such a local separation would require the nontrivial
two-port coupling matrix C to have rank 1.

## IV. Algebraic coupling survives the primitive phase

The exact matrix C satisfies

    det C = det(H)^2 det W = 4 det W
          = 8 alpha^7 (1-alpha^2)(1-alpha^4).

At the primitive phase alpha^2=zeta_Q, with Q a power of
two greater than 2n/3 and Q>=16,
neither (1-zeta_Q) nor (1-zeta_Q^2) vanishes. Hence

    det C !=0

and the owner-bit / cycle-parity-bit coupling has rank 2.
No decomposition C_{r,s}=U_r V_s (single bond channel)
is possible, even after replacing the source by its
cycle-edge dual.

This is a proof against the simplest rank-one factorization,
NOT against all matchgate transforms, determinant algorithms,
tensor contraction schedules, or arbitrary P=NP algorithms.
In particular no inference "nonplanar means hard" is made.

## V. Exact executable audit

    python experiments/r5_universal_e118_hadamard_cycle_edge_dual_attack.py

The checker computes the polynomial C=H W H; verifies all
8 three-bit Fourier inversion equations coefficient-by-
coefficient; verifies det C=4 det W exactly in Z[alpha];
constructs H, proves degree 2 and cycle decomposition;
and compares ALL coefficients of the entire primal and
dual phase polynomials on the q9 E118 UNSAT90 and SAT90
controls (n=9 dual states each).

Expected [alpha^60] target Exact-One coefficients:
UNSAT90 0; SAT90 192.

The six-variable connected two-triangle SAT/UNSAT PAIR
is an independent non-factorization control; both targets
have N=60 variables. The checker verifies every
coefficient on BOTH sources independently and confirms
target counts 0 and 48, despite identical unlabelled H.

The finite checks do NOT establish worst-case polynomial
evaluation, because the present direct dual histogram
loops over 2^n edge-bit assignments.

## V-A. Uniform exact elimination of one root spin per cycle

The 2-factor graph H also permits a SECOND, completely
non-Fourier, explicit global contraction. It eliminates
one GF2 spin per connected cycle algebraically while
keeping the full integer target weight enumerator.

Let H have c cycle components, with n vertices and n edges.
Choose a spanning tree from each cycle by deleting one
cycle edge. The forest has exactly n-c edges.

For each FOREST edge e={u,w}, introduce a free binary
edge gradient y_e=p_u XOR p_w. These n-c variables
determine a unique relative spin d_v(y) on every
vertex once the root of each component has been set
to zero. For the deleted edge e'=(u,w), its gradient
is then forced to d_u(y) XOR d_w(y) by the condition
that XOR of all gradients around a cycle equals zero.

For each matching-owner vertex v, the required q_v is
the gradient of its corresponding owner-labelled edge:

    q_v(y) = d_endpoint1(e_v)(y)
             XOR d_endpoint2(e_v)(y).

Every original p assignment is now uniquely encoded by
a forest-gradient tuple y in F2^(n-c) and one root bit
b_C per cycle component C:

    p_v=d_v(y) XOR b_{component(v)}.

Substituting this EXACT bijection into the weighted sum,
we may sum each b_C locally:

    S(alpha) =
      sum_{y in F2^(n-c)}
        product_{C in components(H)}
          [ product_{v in C}
                W_{d_v(y),q_v(y)}(alpha)
            +
            product_{v in C}
                W_{1 XOR d_v(y),q_v(y)}(alpha)
          ].

This is an exact polynomial identity for EVERY cubic
source, ALL alpha values, and in particular every
primitive cyclotomic phase. Every local product and
coefficient uses O(poly(n)) exact integer bit arithmetic
for the formal weight histogram.

**Explicit-state complexity:**
    O(2^(n-c)*poly(n))
instead of the prior 2^n source assignments. No
assumption that H's cycles are independent was made:
q_v(y) still depends on gradients of the remote edge
owned by v. The formula sums each cycle root exactly,
while preserving ALL cross-cycle interactions.

Exact frozen controls, with the canonical Hall matching
used for q9 sources and the explicit owner maps for q6:

    source                   cycles c   explicit states
    E118 UNSAT q9               1              256
    E118 SAT q9                 4               32
    connected UNSAT q6          2               16
    connected SAT q6            2               16

All coefficients are compared with an independent
2^n-source-word exact polynomial. Expected target
top coefficients remain 0/192 on q90 and 0/48
on q60 respectively.

**Sharp all-input firewall:** H has NO LOOPS because
every source clause contains 3 distinct variables.
Each cycle component therefore has at least two
vertices. Consequently c<=floor(n/2) and

    n-c >= ceil(n/2).

Thus any algorithm that still explicitly lists all
2^(n-c) gradient choices has an exponential worst-case
envelope at least 2^(ceil(n/2)) for ANY perfect matching.
Picking a better Hall matching can improve constant
exponents but CANNOT by itself make this explicit
gradient-enumeration route polynomial.

This is a strict lower bound on the number of states
of THIS CHOSEN REPRESENTATION, NOT a universal
algorithmic time lower bound or a P!=NP result.
A compressed computation exploiting cancellations,
symbolic sharing or a wholly different invariant
remains mathematically possible and is the needed
all-input theorem.

Companion:
    python experiments/r5_universal_e118_cycle_gradient_elimination.py

## VI. Exact next universal obligation

The source and dual E118 partition functions are equally
exact; both have n summation bits. A valid universal polynomial
solver via this route must prove a deterministic polynomial
contraction of

    Z_dual(C,H,owner)=2^-n sum_{s in F2^n}
                        prod_v C_{s_l XOR s_r,s_v}

for **every** cubic-source-induced 2-factor H and EVERY
valid owner-edge permutation (plus arbitrary source pins)
at the required primitive phase.

The theorem must bound intermediate tensor ranks, sizes of
cyclotomic coefficient vectors, and total arithmetic BIT cost
by a fixed n^C, not only show that H alone is a cycle cover.
The 6-variable witness explicitly refutes an automatic
independent-cycle product claim.

E118's hardness reduction ensures an all-input exact
polynomial evaluator would be a P=NP-scale breakthrough,
but does not prove that such an evaluator is impossible.

## Claim ledger

ALL_SOURCE_HADAMARD_2_FACTOR_DUAL = PROVED_BY_IDENTITY.
NON_OWNER_GRAPH_EVERY_VERTEX_DEGREE_TWO = PROVED.
CUBIC_EXACTONE_POLY_EQUIVALENT_TO_LABELLED_2_FACTOR_EXACTONE = PROVED_USING_E118_HARDNESS.
CYCLE_OWNER_PERMUTATION_MAY_COUPLE_DISTINCT_CYCLES = PROVED.
IDENTICAL_UNLABELLED_2_FACTOR_OPPOSITE_SAT_STATUS = EXACT_FINITE_CERTIFICATE.
DUAL_C_COUPLING_RANK_TWO_AT_PRIMITIVE_PHASE = PROVED.
Q90_FULL_INTEGER_POLYNOMIAL_DUAL_REPLAY = EXPECTED_CHECK.
CONNECTED_Q6_TWO_CYCLE_CROSS_OWNER_REPLAY = EXPECTED_CHECK.
CYCLE_ROOT_SPIN_SUM_ELIMINATION = PROVED_ALL_SOURCES.
EXPLICIT_GRADIENT_STATES_GE_2^(N/2) = PROVED_FOR_THIS_REPRESENTATION.
UNIVERSAL_POLYNOMIAL_DUAL_CONTRACTION = OPEN.
UNIVERSAL_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Background literature: Cai, Lu & Xia (2014),
'The complexity of complex weighted Boolean #CSP',
JCSS 80:217-236, DOI 10.1016/j.jcss.2013.07.003;
and Cai & Fu (2019), 'Holographic Algorithm with
Matchgates Is Universal for Planar #CSP over Boolean Domain',
SIAM J. Comput., DOI 10.1137/17M1131672.
These papers do NOT prove the particular E118 dual
falls within a polynomial all-input family.
