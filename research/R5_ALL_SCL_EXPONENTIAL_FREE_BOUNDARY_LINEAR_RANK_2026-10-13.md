# R5 — Exact exponentially large free-boundary linear rank on EVERY legal SCL: a precise restricted LoopZeroTest no-go

Date: 2026-10-13 (Europe/Kyiv).
Research branch: `research/r5-cubic-flow-smith-pair-20261011`.
PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516, DRAFT. Main unchanged.
Starting verified HEAD: `66eec352b73f3e12b1e262f4be6d1dc8953bf45e`.

## 0. Strict scientific goal and scope

Ultimate goal remains ONE deterministic original-source sound, complete uniform bit-polynomial `SolveLinearCubicXSAT(F)`, every square+cubic+linear positive Exact-One source, SAT with original Boolean witness or sound UNSAT. Neither P=NP nor P!=NP is established; P vs NP OPEN.

The new all-input theorem rules out ONE precise attempted global loop closure: an explicit polynomial-dimensional FLAT LINEAR INTERFACE channel preserving every possible assignment of a naturally occurring open boundary. It does NOT rule out general succinct tensor circuits, implicit nonlinear encodings, context-sensitive evaluation, polynomial algorithms that never materialize a flat interface, or P=NP.

## 1. Source proof: there are linearly many separated identical quartic cells

For ANY legal original SCL source with n rows/variables, take the source-audited bipartite 3-regular Tanner graph, compute its source-verified perfect matching (Hall's theorem), and contract matching wires. The previous theorem constructs in deterministic polynomial time the n-node 2n-edge 4-regular quotient multigraph Q, each cell carrying the SAME tensor

```
T4 = |1000> + |0100> + |0011>.
```

A quotient cell has four incident wires and at most four DISTINCT neighbours (parallel quotient edges do not increase degree in the simple support graph).

Construct a greedy independent vertex set I by repeatedly selecting any remaining cell and deleting it plus all its neighbours. Each selection deletes at MOST FIVE cells. Therefore

```
k=|I| >= ceil(n/5).
```

No two chosen cells share a quotient wire. Open all 4k external incidence ports around these selected cells, before contracting the rest of Q. The exact 4k-boundary tensor of the selected region has NO internal contractions and is

```
T_boundary = T4^(tensor k).
```

This formula is source-authenticated: each chosen cell has original source row and matched variable provenance, and all its four exposed ports retain original source incidence-wire IDs. It holds for SAT and UNSAT sources alike.

## 2. Exact local boundary rank and exponential tensor-product theorem

Split EACH T4 cell's ports into LEFT local bits (port0,port2) and RIGHT local bits (port1,port3). The exact four-by-four flattened matrix in binary pair order 00,01,10,11 is

```
     right=00 01 10 11
left
00           0  0  1  0
01           0  1  0  0
10           1  0  0  0
11           0  0  0  0
```

It has rank EXACTLY THREE (its upper left 3x3 submatrix is an anti-diagonal permutation matrix with determinant -1; last row and column zero).

For the k-cell open boundary with left-port pairs vs right-port pairs, flattening tensor products gives the Kronecker product

```
B_I = B(T4)^(Kronecker k).
```

Over any field of characteristic zero, matrix rank multiplies under Kronecker products, hence the exact all-input theorem

```
rank(B_I) = 3^k >= 3^ceil(n/5).
```

Equivalently, the product of k local invertible 3x3 minors gives a concrete nonzero 3^k-by-3^k minor, while each local 4x4 factor has rank<=3 so the whole product has rank<=3^k.

For ANY flat linear representation of this exact arbitrary-boundary matrix as `B_I=UV` with intermediate dimension d, `rank(B_I)<=d`. Thus d MUST satisfy `d>=3^ceil(n/5)`, exponentially growing in source size.

The same holds for nonnegative factorizations (ordinary rank lower bounds nonnegative rank), for signed rational or complex linear channels, and for an arbitrary independent invertible 2x2 gauge on each external wire that does not mix the chosen LEFT and RIGHT sets: such gauges only left/right multiply B_I by invertible Kronecker products.

## 3. Exact SIGNED LOOP boundary tensor obeys the same lower bound

The previously independently source-audited reversible basis theorem established:

```
H=[[1,1],[-1,2]], det(H)=3,
M4 = (H^tensor4) T4 / 3.
```

Hence its 2|2 flattening along the SAME chosen two-port split has EXACTLY rank3. The k-cell isolated loop-moment boundary tensor is `M4^tensor k` and has rank `3^k` by the same argument.

This means renaming the local signature as the exact signed-loop moments does NOT reduce the dimension of an explicit full free-boundary linear factorization. It says nothing against an implicit short tensor product; indeed, `T4^tensor k` and `M4^tensor k` themselves have O(k) symbolic descriptions.

## 4. Independently executed finite controls and honest interpretation

Executable:
`experiments/r5_universal_loop_free_boundary_exponential_flat_rank.py`
CI:
`.github/workflows/r5-free-boundary-exp-rank.yml`.

Original first CI [#38322030433 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38322030433):
- Independently builds T4 from original ExactOne3--Equality3 source contraction;
- Checks 4x4 integer flattening rank3 and explicit unit-determinant 3x3 minor;
- Builds 16 signed-loop moments from the earlier exact algebra;
- Direct 4x4, 16x16 and 64x64 rational Gaussian-elimination checks give ranks 3,9,27 for BOTH T4 and loop moments;
- Constructs source-audited quotient graph and independent cell set for Fano7 (k=2, rank9), K4/SCL18 (k=6, rank729), K33/SCL27 (k=9, rank19683), Petersen/SCL45 (k=16, rank43046721), J5/SCL90 (k=31, rank617673396283947), non-Holyer E61 SAT12 (k=4, rank81) and UNSAT12 (k=3, rank27);
- Larger connected flower J63/SCL1134 has independent set k=408, rank exactly `3^408`, with 1632 open boundary ports, certified WITHOUT allocating the exponentially large boundary tensor.

Strengthened source adversarial control:
- Independently construct actual free-boundary matrices using the original source's quotient incidence ports on three selected cells in non-Holyer E61 SAT12 AND E61 UNSAT12. BOTH have exact rank27 while the original source solution counts differ, respectively 1 and0. Therefore even this strong local-rank observable does NOT discriminate SAT from UNSAT.
- The strengthened independent source-matrix replay [#38322154776 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38322154776) ran on commit `b5fe67197b974a5e75a014879a61570f4b7c19ea`. Both SAT12 and UNSAT12 direct source-boundary matrices have rank 27 while original exact solution counts are 1 and 0.

These controls corroborate the all-input proof; no finite extrapolation is necessary for the rank theorem.

## 5. Literature placement and limitation of any hardness claim

Tensor rank lower bounds are standard algebraic tools; the mathematical novelty claimed here, if any, is this direct source-authenticated universal SCL/T4 realization, not the rank-of-Kronecker-product identity itself.

Recent related tensor-network contraction work:
- `Exponential time complexity for contracting tensor networks`, *The Computer Journal*, published 29 March 2026, DOI 10.1093/comjnl/bxaf082. This paper gives conditional #ETH lower bounds for several broader tensor-network classes. DO NOT transfer those lower bounds automatically to the particular original SCL/T4 zero/nonzero DECISION problem, which retains its own unproved P vs NP status.
- `Bipartite 3-regular counting problems with mixed signs`, Cai–Fan–Liu, *JCSS* 135 (2023), DOI 10.1016/j.jcss.2023.01.006. It investigates counting Holant problems on general 3-regular bipartite graphs. Its general complexity dichotomy does not automatically establish hardness under extra source linearity/C4-free restrictions. We already have independently source-authenticated Holyer reduction for DECISION NP-hardness.

No source cited here claims the rank of disconnected partial boundary subnets is a universal running-time lower bound.

## 6. Actual next positive theorem gate, still unresolved

To solve P=NP-level target, one would still need an EXPLICITLY SPECIFIED class of IMPLICIT representations C, a uniform polynomial-time contraction/zero operation on C for EVERY original legal SCL, and a worst-case n^C bit bound, including high-treewidth/girth/genus and low-symmetry sources. Previous constant-size G10/G11 3-switch gadgets already prove that a polynomial UNPINNED source zero-test automatically yields original SAT witness in n+1 legal source calls. The new rank obstruction merely rules out replacing the required algebra with a polynomial-dimensional explicit linear boundary table that preserves all arbitrary boundary assignments.

Possible successor:
- Define a genuine non-flat implicit algebra with proved polynomial-time ZERO test (not just an O(n)-size unevaluated tensor circuit).
- For each proposed composition law, expose an arbitrary-boundary selected set I and show exactly WHERE/how it avoids this explicit-rank bottleneck.
- Test any candidate on original E61 SAT/UNSAT of equal size, K4/Petersen, and Cayley high-genus sources, WITHOUT treating SAT/UNSAT heuristics as proof.

```
ALL_SCL_N_OVER5_INDEPENDENT_T4_SOURCE_CELLS = PROVED
ALL_SCL_EXACT_FREE_BOUNDARY_LINEAR_RANK_GE_3POWER_N_OVER5 = PROVED
SIGNED_LOOP_MOMENT_FREE_BOUNDARY_SAME_RANK = PROVED
POLY_DIMENSIONAL_EXPLICIT_FLAT_LINEAR_BOUNDARY = REFUTED
RANK_OBSERVABLE_DECIDES_SAT = FALSE (E61 SAT/UNSAT CONTROL)
POLY_IMPLICIT_GLOBAL_LOOP_ZERO = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
