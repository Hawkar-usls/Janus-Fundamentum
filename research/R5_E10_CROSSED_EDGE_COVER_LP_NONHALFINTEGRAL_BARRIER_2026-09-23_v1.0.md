# R5 E10 — Crossed Edge-Cover LP Non-Half-Integrality Barrier

Date: 2026-09-23

Authority: EXACT_FINITE_POLYHEDRAL_COUNTEREXAMPLE__LP_ROUNDING_SHORTCUT_ONLY__NO_D1_PROMOTION

Parent: R5_E10_DUAL_CUBIC_CROSSED_EDGE_COVER_HARD_CORE_2026-09-23_v1.0

Checker: research/tools/r5_e10_crossed_edge_cover_lp_nonhalfintegral_checker.py

## 1. Natural LP

For a crossed cubic pair (G_plus,G_minus) on common edge labels E, use one variable x_e in [0,1] per label.

Positive-cover constraints:
sum_{e incident to v in G_plus} x_e >= 1.

Negative-complement-cover constraints:
sum_{e incident to w in G_minus} x_e <= 2.

Every integral feasible point is a satisfying edge-coloring. The all-half point x_e=1/2 is always feasible on cubic pairs, so feasibility alone cannot decide SAT.

## 2. Exact non-half-integral extreme point

The checker freezes two simple cubic graphs on six vertices and nine common edge labels:

G_plus edges:
(0,1),(0,2),(0,5),(1,2),(1,3),(2,4),(3,4),(3,5),(4,5).

G_minus edges:
(0,3),(2,3),(2,5),(1,2),(1,4),(4,5),(0,4),(0,5),(1,3).

The rational point

x = (0,1,0,1,1/3,0,1/3,1/3,2/3)

satisfies all cover/packing inequalities and box constraints.

The set of tight star constraints together with tight 0/1 bounds has exact rational rank 9, equal to the number of variables. Hence x is a polyhedral vertex.

Because coordinates 1/3 and 2/3 occur, the relaxation is not half-integral.

## 3. Consequence

The following Phase-B shortcut is falsified:

crossed edge-cover LP
-> every extreme point is in {0,1/2,1}
-> fractional support decomposes into alternating cycles
-> exact deterministic cycle rounding.

The first implication is false even on a tiny cubic pair.

This does not block stronger LP/SDP hierarchies, cutting planes, or a different extended formulation. It blocks only a generic half-integral rounding theorem for the native star-inequality LP.

## 4. Updated Phase-B state

DUAL-CUBIC CROSSED EDGE-COVER NORMAL FORM = PASS
DISJOINT PERFECT-MATCHING SHORTCUT = FALSIFIED
NATIVE LP HALF-INTEGRALITY = FALSIFIED
JOINT ALGEBRAIC / SEMANTIC QUOTIENT = OPEN <<< SURVIVOR
D1 = EMPTY
P_VS_NP = OPEN
