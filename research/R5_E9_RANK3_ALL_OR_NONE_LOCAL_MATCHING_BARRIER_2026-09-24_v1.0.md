# R5 E9 — Rank-3 All-or-None Local Matching-Gadget Barrier

Date: 2026-09-24

Authority: JANUS_DERIVED_EXACT_LOCAL_REPRESENTATION_BARRIER + SOURCE_BOUND_MATCHING/MATCHGATE_THEORY__NO_P_NE_NP_ASSUMPTION__NO_D1_PROMOTION

Parent: R5_E9_RANK3_EXACT_COVER_TO_MATCHING_CONTRACTION_GATE_V1

Checker: experiments/r5_e9_rank3_all_or_none_matching_barrier.py

## 1. Frozen cubic exact-cover atom

In the dual exact-cover representation of cubic Positive 1-in-3-SAT, every source variable occurs in exactly three clauses.

One variable x therefore exposes a three-terminal boundary behavior:

x=0 -> covers no incident clause terminals -> 000
x=1 -> covers all three incident clause terminals -> 111.

Thus the exact local boundary relation is

R_all/none = {000,111}.

Any local graph-matching replacement for one rank-3 hyperedge with the same three exposed terminals must realize exactly this relation.

## 2. Delta-matroid symmetric-exchange failure

Identify a Boolean tuple with its support set.

For R_all/none the feasible sets are

F = { emptyset, {1,2,3} }.

Take

X=emptyset,
Y={1,2,3}.

The delta-matroid symmetric-exchange axiom requires that for every e in X symmetric-difference Y there is some f in X symmetric-difference Y such that

X symmetric-difference {e,f}

is feasible, with the usual single-toggle interpretation when e=f.

Fix e=1.

The only candidates are

{1}, {1,2}, {1,3}.

None belongs to F.

Therefore R_all/none is not a delta-matroid.

## 3. Matching-realizability consequence

Kazda, Kolmogorov and Rolinek define matching-realizable Boolean boundary relations through perfect-matching gadgets and state that every matching-realizable relation is an even delta-matroid.

Source: Even Delta-Matroids and the Complexity of Planar Boolean CSPs, arXiv:1602.03124 / TALG.

Since R_all/none is not even a delta-matroid, it cannot be matching realizable.

Hence:

NO ordinary local matching gadget with the same three-terminal exact boundary relation can replace one cubic rank-3 hyperedge.

This is unconditional and representation-specific. It does not assume P != NP and does not rule out nonlocal reductions or a different target representation.

## 4. Independent pure-matchgate parity barrier

Cai and Gorenstein, Matchgates Revisited, arXiv:1303.6729, prove that matchgate identities imply the Parity Condition.

A nonzero matchgate signature has support entirely on one parity class of Hamming weights.

But R_all/none has nonzero support at:

000, weight 0 (even),
111, weight 3 (odd).

Therefore no pure matchgate signature can realize R_all/none.

This gives an independent, shorter obstruction for the planar/pure matchgate subclass.

## 5. Scope

Blocked:

- replacing each cubic rank-3 variable independently by any ordinary graph-matching gadget that preserves the same three exposed terminal bits exactly;
- pure matchgate realization of the atom;
- any argument that graph matching can express the all-or-none rank-3 choice locally without extra nonlocal structure.

Not blocked:

- grouping several rank-3 hyperedges before transformation;
- a global quotient or basis change that changes the exposed interface;
- reductions to a polynomial carrier other than ordinary matching;
- instance-level global certificates;
- a universal polynomial algorithm for the whole cubic hypermatching problem.

## 6. Why fresh local selector gadgets are not progress

One can trivially encode the choice x=0/1 by a fresh hidden selector and force three terminal occurrences to follow it.

That preserves the original all-or-none bit rather than eliminating it.

Such a construction is forbidden as algorithmic progress: it renames the rank-3 choice but does not reduce the exact-cover interaction.

## 7. Cubic hard-core normalization

Exact Positive 1-in-3 SAT remains NP-complete when every variable occurs exactly three times and every clause contains exactly three variables.

In the dual formulation this freezes the hard core as:

3-uniform variable hyperedges,
3-regular clause vertices,
perfect exact cover / perfect hypermatching.

Thus rank-1 and rank-2 hyperedges are not needed for hardness.

## 8. New global gate

Freeze:

R5_E9_CUBIC_3UNIFORM_GLOBAL_CONTRACTION_GATE_V1

Input:

a 3-uniform, 3-regular exact-cover hypergraph representing cubic monotone Positive 1-in-3-SAT.

Allowed PASS exits:

A. a deterministic polynomial transformation strictly decreasing
   mu_rank = sum_e max(0, |e|-2),
   with exact witness encode/decode;

B. grouping multiple rank-3 hyperedges into a proved polynomial carrier;

C. a nonlocal basis/quotient transformation with polynomial total state and exact witness reconstruction;

D. a direct polynomial component solver with a full proof.

Forbidden:

- local hyperedge-by-hyperedge matching gadget;
- hidden ON/OFF selector that merely stores the same variable choice;
- branch on selected/not-selected state;
- enumeration of rank-3 hyperedge states;
- a replacement whose boundary relation is again {000,111} inside ordinary matching.

## 9. Negative-control audit lane

Kettani (IJMTT 2025) claims a polynomial algorithm for Cubic Monotone 1-in-3 SAT via reduction to maximum independent set on a claimed bounded-treewidth graph.

The publisher itself states that further verification is required.

This route is not authority for JANUS.

It should be treated only as a negative-control audit: isolate the exact theorem/lemma that claims a uniform polynomial treewidth bound and test it against cubic hard families / expanders.

Until that step is independently proved, no bounded-treewidth promotion is permitted.

## 10. Ceiling

JANUS 1-IN-3 REALIZABILITY = PASS
CUBIC 3-UNIFORM 3-REGULAR HARD CORE = FROZEN
R_ALL_OR_NONE = {000,111}
R_ALL_OR_NONE DELTA-MATROID = FALSE
LOCAL ORDINARY MATCHING REALIZATION = BLOCKED
PURE MATCHGATE REALIZATION = BLOCKED BY PARITY
NONLOCAL GLOBAL CONTRACTION = OPEN
D1 = EMPTY
P_VS_NP = OPEN
