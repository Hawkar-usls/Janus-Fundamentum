# R5 E10 — Dual-Cubic Crossed Edge-Cover Hard Core

Date: 2026-09-23

Authority: DERIVED_EXACT_NORMAL_FORM_FOR_MONOTONE_3SAT_22__SOURCE_HARD_CONTROL__NO_D1_PROMOTION

Checker: research/tools/r5_e10_dual_cubic_edge_cover_core_checker.py

## 1. Source-hard subclass

Döcker proves that Monotone 3-SAT-(2,2) is NP-complete: every clause has exactly three distinct literals, every clause is monotone, and every variable appears exactly twice positively and twice negatively.

This source-hard subclass is used only as a universal stress control.

## 2. Two cubic graphs on one edge-label set

Let F be a Monotone 3-SAT-(2,2) instance.

Create G_plus:
- one vertex for every positive clause;
- one edge e_x for every Boolean variable x;
- the two endpoints of e_x are the two positive clauses in which x occurs.

Every positive clause contains three variables, so every G_plus vertex has degree three. Thus G_plus is a cubic multigraph (simple when no two variables join the same clause pair).

Create G_minus analogously from the negative clauses. The same variable x gives the same edge label e_x, but generally different endpoints in G_minus.

Thus the formula is represented by two cubic graphs G_plus and G_minus sharing one common edge-label set E.

## 3. Assignment semantics

For an assignment define T subset E to be the edges/variables set to true.

A positive clause is satisfied iff at least one of its three incident edge labels lies in T. Therefore T is an edge cover of G_plus.

A negative clause is satisfied iff at least one of its variables is false. Therefore E minus T is an edge cover of G_minus.

Hence:

F is satisfiable
iff
there exists T subset E such that T is an edge cover of G_plus and E\T is an edge cover of G_minus.

Equivalently, there exist two disjoint edge covers R_plus of G_plus and R_minus of G_minus:

- forward: take R_plus=T and R_minus=E\T;
- backward: given disjoint covers, take T=R_plus; then E\T contains R_minus and therefore covers G_minus.

Call this CROSSED DISJOINT EDGE COVER on a pair of cubic graphs with common edge labels.

## 4. Complexity classification

The transformation is linear and reversible. A candidate pair of disjoint covers is polynomially checkable.

Therefore CROSSED DISJOINT EDGE COVER for such cubic graph pairs is NP-complete by the source hardness of Monotone 3-SAT-(2,2).

This is not the ordinary problem of finding two disjoint edge covers in one graph. The same-graph problem has polynomial algorithms/characterizations in classical edge-cover packing theory. The hardness here comes from the mismatch of two different incidence structures carried by the same edge labels.

## 5. Perfect-matching shortcut falsifier

A tempting sufficient condition is to seek a perfect matching of G_plus and a perfect matching of G_minus that are disjoint in edge labels.

That condition is not necessary.

The checker freezes a pair of simple cubic graphs on eight vertices each and twelve shared edge labels. It exhaustively checks all 4096 assignments.

There is a satisfying assignment with true-label mask 279. It gives an edge cover of G_plus and its complement gives an edge cover of G_minus.

Each graph has exactly five perfect matchings, yet no perfect matching of G_plus is edge-label-disjoint from any perfect matching of G_minus.

Therefore:

DISJOINT PERFECT MATCHINGS = sufficient but not complete.

Any matching-based Phase B algorithm must use the full edge-cover structure or prove an additional transformation theorem.

## 6. Why this representation matters

The singular-DP phase removes all variables with one sparse polarity. The balanced (2,2) source-hard family survives that admission rule immediately.

In this family the remaining difficulty is no longer clause width, occurrence paths, or local fanout. It is exactly the incompatibility between two cubic incidence structures on the same set of Boolean choices.

This gives a cleaner target for nonlocal quotient design:

compress / contract the mismatch between G_plus and G_minus while preserving the existence of complementary edge covers.

## 7. New Phase-B gate

R5_E10_CROSSED_CUBIC_EDGE_COVER_QUOTIENT_GATE_V1

Seek a polynomially constructible exact quotient for a pair (G_plus,G_minus) on common edge labels E such that:

1. existence of complementary/disjoint edge covers is preserved exactly;
2. witnesses lift in polynomial time;
3. quotient size and all intermediate state are polynomial;
4. a certified joint potential on the pair strictly decreases;
5. the operation is not merely a choice/selector encoding of T;
6. the operation makes progress on source-hard (2,2) instances, not only on aligned or low-width pairs.

Candidate positive controls include common low-order separations of both graph structures and aligned/same-incidence cases. Neither is claimed universal.

## 8. Ceiling

SINGULAR DP PHASE = PASS
BALANCED (2,2) HARD CORE = SURVIVES
DUAL-CUBIC CROSSED EDGE-COVER NORMAL FORM = PASS
DISJOINT PERFECT-MATCHING SHORTCUT = FALSIFIED
CROSSED-GRAPH QUOTIENT = OPEN <<< ACTIVE PHASE-B OBJECT
D1 = EMPTY
P_VS_NP = OPEN
