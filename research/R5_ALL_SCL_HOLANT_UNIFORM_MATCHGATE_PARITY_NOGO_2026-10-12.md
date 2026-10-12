# R5 — Universal SCL Holant representation and global-GL2 matchgate parity NO-GO
Date: 2026-10-12 (Europe/Kyiv)
Parent research HEAD: e6187b48029296629d13407fd939643650675a14
PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516 — remains DRAFT. Main untouched.

## 0. Scientific contract

The only acceptable all-input result is a deterministic function
`SolveLinearCubicXSAT(F)` that returns SAT plus an independently
verified original binary witness or original-source-proved UNSAT for
EVERY legal square/linear/cubic Positive Exact-One source, within
ONE uniform polynomial bit complexity n^C.

This checkpoint supplies an ALL-SCL exact algebraic representation
and a GLOBAL-WIRE-BASIS impossibility theorem. It does NOT construct
any such total algorithm. `P_VS_NP=OPEN`.

Existing predecessor:
- R5 source-verified cubic Holyer Tanner G-minor and unbounded
  treewidth family: `research/R5_SOURCE_ORBIT_COMPRESSION_AND_LINEAR_TANNER_TREEWIDTH_GATE_2026-10-12.md`.
- Earlier Pfaffian cube false cancellation on SAT K3,3:
  `research/R5_UNIVERSAL_PFAFFIAN_CUBE_SQUAREFREE_PROJECTION_2026-10-11.md`.
- The new result is DISTINCT: a local tensor/matchgate parity
  obstruction over every invertible homogeneous 2x2 basis, not
  just one signed perfect-matching coefficient assignment.

## 1. Original legal SCL as an EXACT ternary Holant network

Given square n-by-n incidence matrix A with exactly three 1s in
each row and column and at most one common variable between rows,
form a Tanner graph with one row vertex r_i per original
Exact-One source clause and one variable vertex v_j per original
Boolean variable. Every node is degree three.

Place signatures:
- `W=[0,1,0,0]` at each row (ternary ExactOne);
- `GHZ=[1,0,0,1]` at each variable (ternary Equality3).

The signature index is Hamming weight of three incident edge bits.
The Holant `Z(F)` sums the product of signatures over every
assignment to all 3n Tanner wires. At every variable vertex,
GHZ forces all three incident wires equal. This gives a
bijection between surviving wire assignments and assignments
x in {0,1}^n. At each row vertex, W requires exactly one
incident bit to be 1. Thus

```
Z(F)=# { x in {0,1}^n : A x = 1 over the INTEGERS }
F SAT iff Z(F)>0
```

Every surviving term has weight exactly 1, so in this original
basis no cancellation occurs. The tensor network has O(n)
nodes and wires, but this is an exact input encoding, NOT a
polynomially evaluable contraction.

Finite independent source controls:
- Fano SCL7 gives exact 0 witnesses (exhaustive 2^7).
- Holyer K4 SCL18 gives 6 witnesses (exhaustive 2^18).
- Holyer K3,3 SCL27 source pattern verified; NO 2^27
  enumeration attempted in this particular test.
- Forged source (changed original incidence) rejected.

## 2. GLOBAL-GL2 MATCHGATE PARITY OBSTRUCTION — THEOREM

Consider the most direct holographic reduction with ONE shared
invertible 2x2 complex basis B on every Tanner wire:
`W' = B^{tensor 3} W`,
`GHZ' = (B^{-T})^{tensor 3} GHZ`.

The inverse-transpose on the opposite bipartition is necessary
to preserve the original edgewise delta contraction. The new
CI exactly verifies 1488 transformed local tensor pairings
for nonsingular small integral B and arbitrary sample tensors,
not just W/GHZ whose original contraction is zero.

It is a necessary condition of any ordinary matchgate
signature that it have uniform Hamming-weight parity:
either every odd-weight entry is zero (EVEN matchgate) or
every even-weight entry is zero (ODD matchgate).

**THEOREM.** Over every field of characteristic zero, there is
NO B in GL2 such that both W' and GHZ' obey this necessary
parity condition.

**PROOF.** Write B=[[a,b],[c,d]], with det=ad-bc != 0.
The transformed symmetric ternary ExactOne signature W' has
weight coefficients

```
(f0,f1,f2,f3)
 = (3a²b, a²d+2abc, 2acd+bc², 3c²d).
```

If W' has only ODD parity, f0=f2=0. If a=0, det=-bc !=0,
so b,c!=0 and f2=bc² !=0, contradiction. Therefore a!=0
and f0=0 implies b=0. Invertibility then gives a,d!=0,
and f2=2acd=0 gives c=0. B is DIAGONAL.

If W' has only EVEN parity, f1=f3=0. If c=0,
invertibility forces a,d!=0, so f1=a²d!=0, contradiction.
Thus c!=0 and f3=0 gives d=0. Invertibility gives b,c!=0
and then f1=2abc=0 forces a=0. B is ANTIDIAGONAL.

But the inverse transpose of a diagonal or antidiagonal
invertible matrix is likewise monomial (a nonzero scalar
times coordinate permutation and scaling). Such a transform
maps GHZ=e000+e111 to a sum of two NONZERO, separate
basis tensors at weights 0 and 3. GHZ' consequently mixes
EVEN and ODD parity, and cannot be a matchgate. QED.

The argument is symbolically valid for ALL invertible B
over characteristic-zero fields, not extrapolation from
a finite sample. The program independently expands all
eight entries and checks all 625 small rational integer
matrices B (singular matrices rejected), with explicit
diagonal, antidiagonal, Hadamard and mixed controls.

## 3. Source and literature comparison

Executable:
`experiments/r5_universal_holant_matchgate_uniform_basis_nogo.py`

GitHub Actions:
`.github/workflows/r5-holant-uniform-matchgate-nogo.yml`

Independent CI:
- First full original tensor + parity check:
  https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38296969808
  SUCCESS.
- Strengthened exact inverse-dual gauge check, 1488 cases:
  https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38297126176
  SUCCESS.

Published theoretical basis:
- Matchgate parity as a NECESSARY condition and symmetric
  signature classification:
  J.-Y. Cai, P. Lu, M. Xia, *Holographic Algorithms with
  Matchgates Capture Precisely Tractable Planar #CSP*,
  SIAM J. Comput. 46(3), 2017.
  https://doi.org/10.1137/16M1073984
  Also see *The Complexity of Planar Boolean #CSP with
  Complex Weights*, JCSS 2019, section 2.5.
  https://doi.org/10.1016/j.jcss.2019.07.005

- Independent counting-level contextual barrier:
  J.-Y. Cai, A. Z. Fan, *Planar 3-way Edge Perfect Matching
  Leads to A Holant Dichotomy*, arXiv:2303.16705 (2023).
  https://arxiv.org/abs/2303.16705
  Identifies counting Cubic Planar X3C / planar cubic monotone
  1-in-3-SAT as #P-hard. THIS IS A COUNTING RESULT,
  and is not presented as a proof of P != NP or a universal
  decision lower bound.

New local no-go theorem must not be described as the original
discovery of matchgate parity or #P hardness.

## 4. Strict scope and remaining possible advances

REFUTED:
- A single shared homogeneous invertible two-dimensional
  holographic basis that transforms *both* original
  ternary ExactOne and original Equality signatures
  directly into standard matchgate signatures.

NOT REFUTED:
- Edge-dependent/local matrix gauges, where different
  Tanner incidences receive different basis changes;
- Polynomial gadget extensions / regroupings / holographic
  transformations beyond the uniform local signature pair;
- Pfaffian sums or signed coefficient algebra with
  independently proved non-cancellation;
- Non-matchgate compact circuit/tensor encodings with
  polynomial-time implicit zero testing;
- Any conceivable uniform polynomial-time SCL solver.

Potential next experiment: formulate the exact polynomial
constraints on EDGE-DEPENDENT 2x2 gauges, preserving the
delta contraction independently on each edge and demanding
matchgate parity at ALL original nodes. Either construct
a genuine global gauge and independent contracting
algorithm, or produce a finite contradiction independent
of shared-basis assumptions. Parity alone may be inadequate:
check matchgate identities and global planarity explicitly.

For every candidate compression method, require:
  (i) original-source correctness;
  (ii) polynomial construction and encoding;
  (iii) polynomial composition/evaluation and
        original SAT witness recovery or sound UNSAT output;
  (iv) ONE uniform n^C bit runtime.

GATES:
```
ORIGINAL_SCL_W_GHZ_EXACT_HOLANT = PROVED
UNIFORM_GL2_SIMULTANEOUS_MATCHGATE_REDUCTION = REFUTED
1488_EXACT_DUAL_GAUGE_CONTRACTION_CONTROLS = CI_SUCCESS
CUBIC_PLANAR_EXACT_COUNTING = EXTERNALLY_KNOWN_#P_HARD
EDGE_DEPENDENT_MATCHGATE_BASIS = OPEN
GENERAL_ALGEBRAIC_ATOMIC_COMPRESSION = OPEN
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
