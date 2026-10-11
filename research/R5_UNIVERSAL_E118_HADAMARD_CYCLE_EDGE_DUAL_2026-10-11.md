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

The six-variable connected two-triangle source is an
independent non-factorization control; its target has
N=60 variables. The checker verifies every coefficient
on this source too, and reconstructs the E118 target
Exact-One count as 2^4 times the source SAT model count.

The finite checks do NOT establish worst-case polynomial
evaluation, because the present direct dual histogram
loops over 2^n edge-bit assignments.

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
CYCLE_OWNER_PERMUTATION_MAY_COUPLE_DISTINCT_CYCLES = PROVED.
DUAL_C_COUPLING_RANK_TWO_AT_PRIMITIVE_PHASE = PROVED.
Q90_FULL_INTEGER_POLYNOMIAL_DUAL_REPLAY = EXPECTED_CHECK.
CONNECTED_Q6_TWO_CYCLE_CROSS_OWNER_REPLAY = EXPECTED_CHECK.
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
