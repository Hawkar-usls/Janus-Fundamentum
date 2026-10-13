# R5 — Universal V3 quantifier attack: native cubic snarks, explicit original-source certificates, degree-three dual target

Date 2026-10-13, research PR #516, DRAFT, main untouched.

Goal: independently prove either
(A) ALL original legal square/cubic/linear Positive Exact-One (SCL) UNSAT sources F have 1 in the F3 Boolean degree-three span V3(F), **or**
(B) ONE legitimate source F with TWO certificates:
    (i) original SCL UNSAT, and
    (ii) a field-F3 source-dual y with y(1)=1 and y(E_i*x_M)=0 for EVERY original clause i and every squarefree |M|<=2.

A rank deficiency without y, a time-out, or a separately UNSAT-labeled SAT solver output does NOT satisfy B. Finite successful refutations do NOT satisfy A. No universal solver or P=NP is claimed.

## Authenticated starting point

Starting HEAD `baaf83d4000e9bafa7fbcb20fba60ca6ebc53b08`, PR research/r5-cubic-flow-smith-pair-20261011. Existing exact GF3 V2 source dual refutes degree-two sufficiency: Petersen SCL45 original UNSAT has verified V2 dual. Same original Petersen has a valid independently source-replayed V3 refutation of 1337 clause-monomial terms. Several further SCL30/45 stress instances V3 refute, but no all-source quantifier.

Published context:
- Buss–Grigoriev–Impagliazzo–Pitassi, JCSS 2001, DOI 10.1006/jcss.2000.1726: PC degree lower bounds for Tseitin/mod-p counting, with field-characteristic distinctions.
- Atserias–Ochremiak, Proof Complexity Meets Algebra, ACM TOCL 2019, arXiv:1711.07320: reductions preserving PC proof complexity for CSPs in broad settings, but no unproved transfer to native cubic/square/C4-free SCL.
- Conneryd et al, FOCS 2023 / ECCC TR25-032: linear PC degree over any field for certain graph VERTEX 3-coloring formulas, not directly legal SCL.
None is a native SCL source-dual proof unless a specific low-degree-back-simulation reduction is established.

## NEW source adversary I: odd-cut BRIDGE cubic graphs

Let H be one of K4, K3,3 and 3-cube. In TWO vertex-disjoint copies of H, subdivide one chosen original edge per copy, joining each pair of old edge endpoints to one new vertex, and connect the two new subdividing vertices by a single bridge. The result is a simple connected cubic graph with original vertex count 10/14/18.

The direct source-authenticated original Holyer encoding maps any cubic G with M edges to legal square/cubic/C4-free SCL of n=3M variables and rows, one positive exact-one colour clause per edge and one colour perfect-matching exact-one clause per vertex-colour. The correspondence from SAT to 3-edge-colouring is an exact assignment bijection, independently rechecked against ORIGINAL source IDs.

A cubic bridge graph is 3-edge-uncolourable by parity: deletion of its only crossing edge separates the graph into two ODD vertex sides, since 3|U|=2|E(U)|+1. Every colour class in a proper 3-edge colouring is a perfect matching. On an odd side it must include the only crossing edge, but all three colour classes cannot include the SAME bridge. Thus the native SCL is UNSAT with an O(n) source-backed GRAPH/ORIGINAL incidence certificate, not just the assertion of an external solver.

[CI #38330923270 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38330923270):
- Native bridge SCL45 (5+5 vertex odd cut), SCL63 (7+7), SCL81 (9+9) all source-original UNSAT.
- In all 3, exact complete GF3 V3 row-span elimination found constant polynomial 1. This is a **refutation candidate**, not yet an independently unwound original clause coefficient certificate; importantly these three sources do NOT provide a degree-three dual counterexample.

Code:
`experiments/r5_universal_bridge_cubic_graph_gf3_degree3_counterexample_gate.py`;
`.github/workflows/r5-cubic-bridge-degree3-counterexample.yml`.

## NEW source adversary II: no-bridge ISAACS flower snark J5 (SCL90)

The existing independently source-authenticated all-odd Isaacs flower 27-state transfer proves that every odd k>=5 graph flower(k) has no 3-edge colouring; `make_scl(flower(k))` is legal native SCL size n=18k.

Run full original-source F3 Boolean polynomial degree-three Gaussian and try a dual:
`experiments/r5_universal_flower_snark_gf3_degree3_dual_attack.py`,
`.github/workflows/r5-flower-gf3-degree3-dual.yml`.

First source CI #38331153843 FAILED due to harness arithmetic typo `n=9k`; this is **not** a scientific contradiction and is preserved for provenance. Fixed n=18k in commit a716ce8. First completed scientific CI #38331203838 SUCCESS with status explicitly `UNKNOWN_RESOURCE_LIMIT` on J5/SCL90 at 100,000,002 GF3 cell updates and rank 120,819 of 121,576 ambient monomials. No dual and no refutation was certified at this cut. Resource limit raised to 500M for J5 ONLY at commit `254679fa079e8dd0c679deaca5eb613564acfe0d`; the source-aligned complete run must finish before any degree3 claim.

## NEW source adversary III: Petersen dot-product BRIDGELESS snark (SCL81)

Choose two disjoint original Petersen graphs, cut two disjoint edges in the first; remove the endpoints of one original edge in the second; connect the four exposed endpoints by bijection. Construct 18-vertex simple cubic bridgeless graph, derive legal original SCL81 with make_scl, and check original satisfiability by a fully replayable independent original exact-cover DAG.

Deterministic scan found FIRST real bridgeless G18 with exact original UNSAT SCL81 source certificate consisting of 286 dead uncovered-row masks. The frozen original source 27 cubic edges are:
```
((0,4),(0,5),(0,10),(1,2),(1,6),(1,14),
(2,7),(2,12),(3,4),(3,8),(3,13),(4,9),
(5,7),(5,8),(6,8),(6,9),(7,9),(10,11),
(10,15),(11,12),(11,16),(12,17),(13,15),
(13,16),(14,16),(14,17),(15,17)).
```

[CI #38331583210 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38331583210) certifies G18 source UNSAT and exact original row DAG286; initial cubic GF3 span stops at `UNKNOWN_RESOURCE_LIMIT` after 100,000,002 updates, rank88,385 of ambient 88,642. This is NOT evidence degree3 fails, merely a promising rank-near-complete expensive case. Resource guard raised to 650M and further candidate scans disabled in commit `86dae308807d39a30c7e60b283fd6a61a3ba87ea`; wait for complete decisive source-dual/constant outcome.

Code:
`experiments/r5_universal_petersen_dot_snark_gf3_degree3_dual.py`;
`.github/workflows/r5-petersen-dot-snark-degree3.yml`.

## STRICT gate

- If either completion yields `DEGREE3_NO_REFUTATION_DUAL_CERTIFIED`, require independent source-level replay of EVERY allowed degree3 generator plus original UNSAT verification (flower transfer, or SCL81 DAG); freeze input, source proof, dual, CI and conclusion **ALL_SCL_FIXED_D3_COMPLETE=REFUTED**. This does not refute all polynomial algorithms.
- If completion yields `DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED`, it is just a primal candidate; explicitly reconstruct original source polynomial coefficient identity and verify it, or state unverified.
- If completion still yields `UNKNOWN_RESOURCE_LIMIT` or run times out, no mathematical conclusion about V3 is authorized.
- Even if both finite candidates refute at d3, this does not PROVE all-source degree3 completeness, and no P=NP conclusion is authorized.

```
ALL_SCL_FIXED_D3_COMPLETE = OPEN
PETERSEN_DOT_NATIVE_SCL81_SOURCE_UNSAT = PROVED
J5_FLOWER_NATIVE_SCL90_SOURCE_UNSAT = PROVED
PETERSEN_DOT_D3_FULL_RANK_STATUS = PENDING_GUARDED
J5_FLOWER_D3_FULL_RANK_STATUS = PENDING_GUARDED
SolveLinearCubicXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
