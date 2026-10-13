# R5 — Exact n<=14 open Exact-One sixpole census; universal Kempe orbit-count and integer-cover obstruction audit

Checkpoint: 2026-10-13, Europe/Kyiv.
Branch: `research/r5-cubic-flow-smith-pair-20261011`; PR #516 DRAFT.
`main` is NOT to be modified.

## Scientific target and no-claim rule

Only one ultimate positive target: a deterministic sound-and-complete
worst-case BIT-polynomial `SolveLinearCubicXSAT` for EVERY legal original
square/cubic/linear positive Exact-One instance, producing SAT+ORIGINAL
witness or genuine UNSAT. Such a solver is **NOT CONSTRUCTED**.
P vs NP is **OPEN**. The proven J5/SCL90 native GF(3) degree>=4
and the infinite triangle-inflation retractions do not give
unbounded-degree hardness.

Current bounded-degree-back-simulation research attempts to construct
an exposed six-port `ExactOne` gate for the pair-equality encoding.
This is a necessary component of one PARTICULAR REDUCTION STRATEGY,
not a necessary condition for arbitrary polynomial SCL algorithms.

## 1. Precisely defined sixpole and exact target

A simple connected cubic sixpole with no isolated free semiedge-to-
semiedge strand has n internal vertices, m internal simple edges,
all internal degrees 1..3, and six distinct external semiedges at
the interior vertices. By handshaking,
    2m+6=3n.
Hence n is even. An interface pairs the six semiedges into three
unlabelled 2-wire connectors; 15 pairings suffice because the
target is symmetric in the three Boolean output positions.

For a complete proper physical 3-edge-colouring, signal bit t_i is
1 iff the TWO ACTUAL external colours of connector i are equal.
The exact projected target is
    EXACTONE = {100,010,001}
with ALL three patterns realized, ALL others excluded.
The FULL physical 3-colour boundary state must be kept for
any downstream compositional/native source soundness or PC proof;
the Boolean projection alone is NOT an algebraic reduction.

## 2. Complete exact n<=12 full physical signatures (prior checkpoint)

Independent nauty-geng -c -d1 -D3 n (3n-6)/2:
 n4: 2 nonisomorphic interiors, 30 pairings, zero ExactOne;
 n6: 9, 135, zero;
 n8: 63, 945, zero;
 n10: 551, 8175, zero; 6 uncolourable;
 n12: 5741, 84780, zero; 89 uncolourable.
All proper internal colourings and physical port colour orientations
for every colourable representative were enumerated to completion.
CI #38402140506 SUCCESS on frozen HEAD b0f664eba5e447456275bab78a89d5167684b8ab.
No n2 connected candidate (m=0).

## 3. Full isomorphism-free n=14 EXCLUSION (new)

New code: `experiments/r5_universal_exposed_exactone_n14_anchored_rejection.py`.
Source workflow: `.github/workflows/r5-exposed-exactone-n14-anchored.yml`.

Use `nauty-geng -c -q -d1 -D3 14 18` to stream ALL
nonisomorphic connected simple 14-vertex graphs having 18 edges,
degrees 1..3. 2*18+6=3*14 ensures exactly six deficit ports.

Exact computed output:
- Graph6 representatives: **69,602**;
- interior 3-edge-colourable: **68,523**;
- internally uncolourable: **1,079**;
- first-internal-edge-colour-zero normalized complete proper
  internal edge-colourings explored: 495,556;
- full six-port colour tuples evaluated: 851,353;
- exact onehot sixpole candidates: **ZERO**;
- SHA256 of all canonical `graph6\n` lines in stream:
  `e859cc784f8c13c7789dbaf51f8033dc5fa74685d4d541d299ef0afc4a964d9b`.

**Correctness of source-normalizing colour zero**: A global permutation
of the 3 colours maps ANY complete proper colouring to one with
the FIRST internal edge colour0; equality of port colours is
unchanged under a common injective permutation. Thus anchored
enumeration is exact for ALL fifteen equality-bit projections.

**Correctness of early rejection**: For each of the 15 pairings,
one actual complete proper colouring whose three bits are NOT
among `{100,010,001}` is a PERMANENT disqualifier of EXACTONE.
The verifier abandons exploration of the current graph ONLY after
ALL 15 pairings each have such a disqualifier. Otherwise it
exhausts all anchored complete proper colourings and verifies
that every remaining pairing either is disqualified or MISSING
a required onehot state. Therefore no candidate can be pruned.
The script counts visited full colourings/port tuples, NOT all
possible colourings for early-excluded graphs; do not conflate.

Authoritative CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38403338271
**SUCCESS** exact commit 4650aad5e120281c5f03db321088ef350946fd57.

### Independent nonanchored physical source cross-check

`experiments/r5_universal_n14_anchor_rejection_independent_control.py`
builds two distinct 14-vertex 18-edge 6-port interior graphs (a
14-cycle with four antipodal chords and a 14-cycle with four
mixed non-adjacent chords). A separately coded COMPLETE edge-3-
colouring DFS (all 3 colours on first edge) and the normalized
single-first-colour DFS reconstruct all 15 exact Boolean boundary
relations and assert equality. A separate call to the accelerated
exclusion engine must return precisely the independent result.
Latest CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38403975485
SUCCESS.
This is an independent regression of the pivotal group-symmetry
optimization, NOT a second full isomorphism-free n14 census.

### The exact new finite theorem

For the stated class of connected simple ordinary cubic sixpoles,
there exists NO exposed pair-equality onehot 6-port gate with
n<=14 internal vertices. Thus, **IF** such a gadget exists within
this class, then
    n_internal >=16.
The statement is finite/exhaustive and is NOT a universal all-size
impossibility theorem.

Across n<=14: **75,968** nonisomorphic connected interiors,
**74,794** internally colourable, **1,174** uncolourable; at least
one decisive condition assessed per relevant interface. Do not
misrepresent n14 early rejection as a completed FULL-colour
signature table for every interior.

## 4. New ALL-SIZE necessary condition: Kempe colouring multiplicity cone

For any hypothetical colourable cubic multipole M with exact
EXACTONE boundary relation, the physical colour-state set is a
fixed S of **108** port 6-tuples, each obeying the boundary parity
law and projecting to exactly one true paired equality bit.

For each colour pair {A,B} (3 choices), the A/B-coloured subgraph
of an actual internal 3-edge-colouring consists of disjoint even
cycles and alternating paths. Its boundary endpoints of colours
A/B are partitioned into pairs by these paths. Swapping colours
on any subset of the paths gives an orbit, a Boolean hypercube
of `2^k` distinct PHYSICAL boundary states. For each fixed
colour pair, ALL proper internal colourings split into disjoint
full-colouring Kempe orbit components, and every possible
physical boundary state in an orbit has the SAME number of
complete interior colourings within that orbit (path swapping
is an involution). Therefore for ALL three pairs {A,B} the
SAME positive integer count vector
    w_s = number of complete 3-edge-colourings with state s
must be a nonnegative integer combination of incidence vectors
of actual Kempe boundary hypercubes (unknown interior topology),
which lie among precisely enumerated ABSTRACT candidate
hypercubes. This is an ALL-SIZE theorem of NECESSITY,
regardless of connectedness or girth, not a sufficient graph
realization criterion.

Exact candidate hypercube enumeration over S:
- each of 3 colour pairs has **42** distinct permitted orbits;
- per pair: 12 size-2, 15 size-4 and 15 size-8 orbits;
- the joint real nonnegative orbit-cone consistency system
  has 324 state/pair linear equalities.

`experiments/r5_universal_exactone_kempe_orbit_count_cone.py`
found an explicit positive count vector `w_s=1` for ALL 108
states and nonnegative rational orbit weights satisfying
ALL 324 equations. Its fractions were reconstructed from the
numerical solver and every original integer-coefficient
equality was independently checked using exact Fraction
arithmetic. This is not numerical extrapolation.
Authoritative CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38404383660
SUCCESS. Rational witness SHA256:
`41704177462113e80261a1d05144855ab94e76a72b28fa9e8a39c677a1b59457`.

### Stronger PURE INTEGER witness without LP

`experiments/r5_universal_exactone_kempe_integral_partition_proof.py`
independently enumerates the same exact states and path-toggle
hypercubes using only standard-library integer arithmetic,
then exact-cover searches for DISJOINT hypercubes with union S.

For EACH of the three colour pairs, a partition is found using
exactly **30** hypercubes:
 12 orbits of size2;
 15 orbits of size4;
  3 orbits of size8;
 exactly 12*2+15*4+3*8=108 distinct states.

An explicit list of 30 chosen orbit indices for each pair is
printed and every selected path-matching witness and its complete
2^k toggle orbit are rebuilt. Integer masks verify that no
two selected orbits overlap and that their union is ALL S.
**NO scipy, numerical LP or SAT-guess** is required for this
independent feasibility proof.
Authoritative CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38404749319
SUCCESS. Frozen orbit-index JSON digest:
`4a03ea5e89ab02c741940ac60923801d7e093575ce581db19e43cd8ce074e44f`.

THEREFORE even the **joint, integral colouring-count necessary
conditions** from all three individually switchable colour-pair
Kempe path decompositions are mathematically compatible with
EXACTONE. They CANNOT alone certify all-size impossibility.
The missing stronger requirement is realization of ALL those
different path pairings by one FIXED cubic interior graph,
including the interactions among DIFFERENT colour pairs and
among recolourings. A successful abstract hypercube partition
is NOT a proof of a physical gadget.

## 5. Existing native GF(3) proof-carrying decoder

For two original source one-hot colour indicator triples p,q,
let `T(p,q)=sum_c p_c q_c` and the original source edge-row
`E_p=sum_c p_c-1`, plus Boolean generators `B_z=z²-z`.
The already independently verified identity
`R_ij=(p_i+p_j-p_k)E_p-B_pi-B_pj+B_pk=2p_ip_j`
implies the explicit native ideal membership
`T²-T=sum_i(B_pi*q_i²+p_i*B_qi)+sum_(i<j)R_ij*q_i*q_j`,
degree<=4 over GF(3), source proof CI #38398478856.
This does NOT derive an exposed source ExactOne gadget or
prove a general constant-cost PC BACK-SIMULATION.

## 6. Next ACTUAL decisive theorem target

Rather than naively extending the finite census without end,
the strongest remaining structural need is a **joint Kempe
path-groupoid compatibility invariant**: for all three 2-colour
subgraphs, on the SAME fixed interior graph and its complete
proper colourings, decide whether a 108-state all-onehot
boundary set can be realized. Candidate approach: encode the
switch operators at full edge-colouring level, their actual
edge-support overlap, and the induced path-pairing evolution
when switching a DIFFERENT pair of colours. The separately
realizable integer orbit covers constructed here cannot
be substituted for this same-graph compatibility proof.

Alternative route is a genuine full physical colour candidate
at n>=16 (or a multiwire/multiport encoding outside this
restricted class), followed by a native source-compliant closed
cubic composition and constant-local GF(3) PC back-simulation.

STRICT STATUS:
- SIXPOLE_EXACTONE_N<=14 = REFUTED_FINITE_CI_SUCCESS
- MINIMUM_N_IF_EXISTS_IN_THIS_CLASS = AT_LEAST_16
- ALLSIZE_SIMPLE_SIXPOLE_EXACTONE_NONEXISTENCE = OPEN
- KEMPE_108_STATE_ALL_THREE_ORBIT_COUNT_CONE = EXACT_SAT
- KEMPE_108_STATE_ALL_THREE_INTEGER_PARTITION = EXACT_SAT
- STRONG_SAME_INTERIOR_KEMPE_GROUPoid_COMPATIBILITY = OPEN
- ORIGINAL_NATIVE_GF3_BOOLEAN_EQUALITY_DECODER_D4 = PROVED
- FULL_HARD_CSP_TO_NATIVE_SCL_PC_BACKSIM = NOT_CONSTRUCTED
- UNBOUNDED_NATIVE_GF3_PC_DEGREE = OPEN
- TOTAL_POLYNOMIAL_SCL_SOLVER = NOT CONSTRUCTED
- P_VS_NP = OPEN
