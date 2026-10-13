# R5 — Isaacs J5/J7 certified orbit-complete barrier to the CURRENT two-ply closure

Date: 2026-10-12. Research branch: `research/r5-cubic-flow-smith-pair-20261011`.
PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516 (DRAFT).
Original audited HEAD before this extension: `c24f978c58a685b688dcc9bcf399ade55f1a39bc`.
Reproducible experiment: `experiments/r5_universal_two_ply_flower_orbit_complete_gate.py`.
CI: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38291137567
Both J5 and J7 matrix jobs: SUCCESS at the workflow's source HEAD.

## 1. Independent source ground truth

The implemented `flower(k)` creates Isaacs's J_k with 4k vertices and 6k edges.
For odd k >= 5, these are snarks with chromatic index 4, hence have NO proper
3-edge-colouring. Isaacs (1975) established this; a survey explicitly references
Theorem 4.1.1:
https://www.sciencedirect.com/science/article/pii/S0166218X15001298
This **external mathematical result** plus the independently implemented
Holyer edge-colouring <=> legal original square/cubic/linear Positive Exact-One
reduction makes J5/SCL90 and J7/SCL126 UNSAT.

The orbit CI itself does NOT generate a stand-alone original-source UNSAT
certificate for J5/J7; it generates *proof-checked UNKNOWN* from the limited
two-ply expert. Keep ground truth's published provenance separate from the
negative test of an incomplete solver.

## 2. Exact four variable orbits

Set `a_i=4i`, `b_i=4i+1`, `c_i=4i+2`, `d_i=4i+3`, indices modulo k.
The explicitly computed bijection T preserves the FULL edge set:
- T(a_i) = a_(i+1), T(b_i) = b_(i+1);
- for i < k-1: T(c_i)=c_(i+1), T(d_i)=d_(i+1);
- across the seam: T(c_(k-1))=d_0, T(d_(k-1))=c_0.

The four edge orbits under T have these tested representatives and sizes:

| Edge rep | Source x_(edge,colour0) | J5 orbit edges | J7 orbit edges |
|---|---:|---:|---:|
| (0,1), spoke a-b | x0 | 5 | 7 |
| (0,2), spoke a-c/d | x3 | 10 | 14 |
| (1,5), b-cycle | x9 | 5 | 7 |
| (2,6), c/d-cycle | x15 | 10 | 14 |

The program verifies a bijective vertex permutation, full edge-set
preservation, exact pairwise-disjoint edge orbits, and union of all edges.
Global colour renaming S3 acts transitively on the three colours and
preserves every original Holyer clause; thus there are exactly four
variable orbits covering n=18k SCL variables. Verified orbit variable
sizes: J5=(15,30,15,30), J7=(21,42,21,42).

The full GF2 forced-unit space and Exact-One propagation consequences
are invariant under variable and source-clause permutations.
`certified_failed_literal_closure` exhausts every available single-bit
probe at each pass and repeats after a newly forced bit; it is a
saturated closure, not first-in-index decision branching. Its final
status SAT/UNSAT/UNKNOWN therefore inherits this equivariance.
Event ordering and choice of source-row XOR provenance need not agree;
the status and existence of implications do. These semantic facts,
not a heuristic about 'similar looking' edges, justify using
representatives to cover all source variables.

## 3. Frozen exact replay

At each representative x_i both assumptions were supplied to the
existing certified *single-ply* procedure and the returned proof
was independently replayed. No PC3, exact complete AND/OR
enumeration, or growing-depth subroutine is involved.

| Graph | Rep x | x=0 | x=1 | Inner probes b=0/b=1 |
|---|---|---|---|---|
| J5, SCL90 | 0,3,9,15 | UNKNOWN for all | UNKNOWN for all | 178 / 166, one pass |
| J7, SCL126 | 0,3,9,15 | UNKNOWN for all | UNKNOWN for all | 250 / 238, one pass |

Both unpinned roots are UNKNOWN with no certified pins.
Every edge-colour variable is in one of the four orbits. Hence
**for every variable** the present fixed-depth TWO-ply conditional
mechanism sees two UNKNOWN single-ply branches; it can neither
construct an original SAT witness nor discharge both branches
as original UNSAT.

Consequently:

```
EXACT_CURRENT_TWO_PLY(J5_SCL90) = UNKNOWN    (true status UNSAT)
EXACT_CURRENT_TWO_PLY(J7_SCL126) = UNKNOWN   (true status UNSAT)
CURRENT_TWO_PLY_UNIVERSAL_COMPLETENESS = REFUTED
```

This is a sound obstruction to a CLAIM ABOUT THIS SPECIFIC PROCEDURE.
It is NOT a counterexample to existence of a different polynomial
algorithm and it proves no lower bound for arbitrary proof systems.

## 4. Fixed-depth and global status

An arbitrary additional depth level does not automatically repair
completeness. A concrete next experiment is an exact **three-ply**
source-proved check on these graph orbits, explicitly limiting depth
to 3 and recording certificate size and work. But results at any
finite handful of depths are no universal guarantee.

To close the stated all-SCL theorem, prove an all-input SAT+witness
or UNSAT terminating decision mechanism with ONE exponent C or
find a fundamentally stronger algebraic compression. If J5/J7
are handled by graph-specific experts, other legal SCL atoms
still need uniform proof-carrying coverage.

```
J5_ORBIT_COVERAGE=PROVED
J7_ORBIT_COVERAGE=PROVED
J5_TWO_PLY_STATUS=UNKNOWN
J7_TWO_PLY_STATUS=UNKNOWN
CURRENT_TWO_PLY_UNIVERSAL_COMPLETENESS=REFUTED
GLOBAL_UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED
P_VS_NP=OPEN
```

No changes to main. Do not merge draft PR #516 on finite CI evidence.
