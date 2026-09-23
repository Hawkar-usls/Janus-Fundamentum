# R5 E9 — Positive 1-in-3 Dual Hypergraph Matching Threshold

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_DUAL_NORMAL_FORM + SOURCE_BOUND_OCCURRENCE_THRESHOLD__NO_D1_PROMOTION

Parent: R5_E9_FULL_NP_CORE_GLOBAL_CONTRACTION_GATE_V1

Checker: experiments/r5_e9_1in3_dual_matching_threshold_checker.py

## 1. Dual exact-cover normal form

Let J be a Positive 1-in-3-SAT instance.

Build the clause-dual hypergraph H_J:

- one vertex c for every source clause;
- one hyperedge e_x for every Boolean variable x;
- e_x contains exactly the clauses in which x occurs.

Choosing x=true covers every clause-vertex in e_x.

The 1-in-3 condition says:

every clause-vertex is covered by exactly one chosen variable-hyperedge.

Therefore:

J is satisfiable
iff
H_J has an exact hyperedge cover / perfect hypermatching of its clause vertices.

Witness maps are identity on chosen variable names.

## 2. Occurrence <=2 collapses to ordinary matching

If every source variable occurs at most twice, every dual hyperedge has size at most two.

Represent:

- a size-2 variable occurrence as an ordinary graph edge between its two clause vertices;
- a size-1 occurrence as an edge from its clause vertex to a private dummy vertex.

Then a set of variables is a valid 1-in-3 witness exactly when the corresponding graph edges form a matching that saturates every clause vertex.

Private dummy vertices need not be saturated.

This is an ordinary polynomial matching problem: compute a maximum matching and test whether all designated clause vertices can be saturated.

Equivalently, reduce designated-vertex saturation to standard matching by the usual augmenting-path/matching machinery.

Thus:

Positive 1-in-3 with variable occurrence <=2 is in P.

## 3. Exact witness reconstruction

For every matched clause-clause edge, set its variable true.
For every matched clause-dummy edge, set its singleton variable true.
Set every other source variable false.

Matching ensures no clause receives two true variables.
Saturation of all clause vertices ensures no clause receives zero.

Hence every clause has exactly one true variable.

The reverse map sends a 1-in-3 witness to the set of true-variable dual edges, which is a matching saturating all clause vertices.

## 4. Published sharpness

Known bounded-occurrence results for positive 1-in-3-SAT give the exact complexity boundary:

- occurrence bound k<=2: polynomial;
- occurrence bound k>=3: NP-complete.

In the dual language, the transition is:

rank <=2 exact cover
-> ordinary graph matching

versus

rank 3 exact cover
-> NP-complete hypergraph matching/exact-cover layer.

This is the first hard rank after the JANUS orientation embedding.

## 5. Why this normal form matters for JANUS

The realizability PASS shows that arbitrary Positive 1-in-3 already lives inside the admissible JANUS row-side network class.

The dual transformation removes all row-side and torsion presentation details and exposes the same hard core as:

EXACT PERFECT COVER BY VARIABLE HYPEREDGES.

So any universal JANUS contraction for the realized NP-complete layer must eventually do something equivalent to reducing rank-3 exact cover to a polynomial carrier.

Representation-only changes that preserve the rank-3 choice structure do not constitute algorithmic progress.

## 6. New progress measure

A natural structural diagnostic is the excess hyperedge rank above graph matching:

mu_rank(J) = sum_x max(0, |e_x|-2).

For occurrence<=2, mu_rank=0 and matching solves the instance.

A candidate contraction is genuine only if it either:

- strictly decreases mu_rank with polynomial witness reconstruction;
- removes an entire rank-3 component into another proved tractable carrier;
- or proves a different global invariant that bypasses rank reduction.

This is diagnostic until a contraction theorem proves monotonicity.

## 7. Exact local rank-3 atom

A variable occurring in exactly three clauses is one dual 3-hyperedge.

Selecting it simultaneously satisfies one position in all three clauses.

Replacing that one 3-hyperedge by pairwise graph edges is not sound in general because graph matching would permit partial selection of its three incidences.

Therefore any rank-3-to-rank-2 replacement must carry an all-or-nothing witness-preserving coupling without reintroducing a hidden three-way selector.

This is the dual form of the contextual no-free-merge barrier.

## 8. Updated active gate

Freeze:

R5_E9_RANK3_EXACT_COVER_TO_MATCHING_CONTRACTION_GATE_V1

Input:

the dual clause hypergraph of an arbitrary Positive 1-in-3 instance embedded in JANUS.

Target:

a deterministic polynomial transformation that either

1. reduces total rank-excess mu_rank;
2. contracts a rank-3 interaction block into ordinary matching / another globally tractable carrier;
3. or produces a polynomial global certificate solving the component directly,

with exact SAT equivalence and polynomial witness reconstruction.

Forbidden:

- branch on whether a 3-hyperedge is selected;
- replace one 3-hyperedge by three independent graph edges;
- encode the same all-or-nothing choice by a fresh hidden selector;
- enumerate rank-3 hyperedge states;
- assume a source witness.

## 9. Ceiling

JANUS 1-IN-3 REALIZABILITY = PASS
DUAL EXACT-COVER NORMAL FORM = PASS
OCCURRENCE <=2 / DUAL RANK<=2 = P VIA MATCHING
OCCURRENCE 3 / DUAL RANK3 = ALREADY NP-COMPLETE
RANK3 EXACT-COVER TO POLY CARRIER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
