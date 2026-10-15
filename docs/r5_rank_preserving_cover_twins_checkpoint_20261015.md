# R5 E4.4 — RANK_PRESERVING_COVER_TWINS
**Scientific date:** 2026-10-15.
**Source provenance:** user-proposed 2-lift SAT criterion and rank formula;
independently checked in this branch with exact integer witnesses, GF(2)
linear algebra, complete finite affine-code oracles and full 2048-class
non-gauge quotient enumeration. Stacked successor to
[Draft PR #527](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/527),
original HEAD `f8f9c98a5db7fdfa887219152d6888185d5af5e5`.
Main was separately at `62a6aa5703bfb9120b3e278b84d2acd993d37133`
when this gate was begun; no merge from this research branch.

## Theorem E4.4.A: SAT of any base persists in every graph cover (ALL n)

Each lifted incidence row contains exactly one chosen sheet copy of
each of its three original columns. Given a Boolean exact-one base
witness x, assign the same x-value to ALL p copies of each column.
Every lifted row still contains exactly one selected variable.
Thus `SAT(A)=>SAT(any p-cover A)`. In particular a SAT base
can NEVER produce an UNSAT graph 2-lift.

**Consequent research protocol:** start from a connected *UNSAT*
base and seek two differing 2-covers of opposite SAT status.

## Theorem E4.4.B: complete existence criterion for some SAT 2-lift

A graph 2-lift of original legal SCL incidence A is SAT iff
there exists `y∈{0,1,2}^n` with integer `Ay=2*1`.

Necessity: add the two lifted rows of every base row.
The number selected among the two sheet copies of original
column j is y_j, and the sum across the row is exactly2.

Sufficiency: for each j, select y_j copies: 0 -> none, 1 ->
sheet0, 2 -> both. Each original row of 3 values summing to2
must have values, up to permutation, (2,0,0) or (1,1,0).
For (2,0,0), its selected copies automatically land on
opposite lifted row sheets for arbitrary incidence signs.
For (1,1,0), assign opposite edge signs to the two selected
incidences of that particular base row. All incidence signs
are independently selectable, and every pair of lifted rows
has exact-one. Thus a SAT cover is CONSTRUCTED, not guessed.

If the base bipartite incidence graph is connected and UNSAT,
any SAT 2-lift must be connected: a disconnected degree-two
cover of a connected base is isomorphic to two identical
copies of the base, hence UNSAT.

The ternary feasibility problem is a new EXACT reduction
of existential SAT-2-lift but is NOT claimed polynomial-time
decidable for arbitrary legal SCL.

## Theorem E4.4.C: rank formula and GF(2) gauge quotient (ALL n)

Over GF2, write `A=A0+A1`, edge signs selecting A0/A1, and

`Atilde=[[A0,A1],[A1,A0]]`.

Using reversible block operations one obtains
`[[A,0],[A0,A]]`. Let r=rank A, d=n-r, and choose
n×d matrices K,L with columns spanning ker A and
ker A^T, respectively. The restriction of the lower-left
block to ker A, followed by quotienting by im A, is
represented by `L^T A0 K`. The rank identity is

`rank(Atilde)=2r+rank(L^T A0 K)`.

Define `Phi_A(delta)=L^T delta K` on GF2^(3n)
coordinate bits representing ORIGINAL EDGES only.
Every nonzero delta in ker Phi gives an explicit incidence
sign change preserving the entire d×d obstruction matrix,
hence the precise GF2 rank of the covering.

A gauge change switches sheet names independently at
each source row vertex and source column vertex:
`delta_(i,j)=p_i+q_j` for every existing incidence.
This changes ONLY the labeling of sheets, not the
cover up to graph isomorphism. Its dimension is
`2n-1` when original incidence graph is connected;
the all-constant p=q=1 transformation is the unique
linear dependence. Gauge lies in ker Phi because
`L^T diag(p)A K=0` and `L^T A diag(q)K=0`.

Rank-nullity on the 3n-edge Phi map gives

`dim(ker Phi / gauge) = (3n-rank Phi)-(2n-1)
                      = n+1-rank Phi.`

This is a complete parameterization of rank-preserving
sign changes inside the specific *fixed obstruction
matrix fiber*. It is NOT a parameterization of ALL
changes preserving only the numerical obstruction rank.

The code enumerates each exact 3n-edge basis bit,
builds Phi from left/right GF2 nullspace, validates
rank Phi independently, checks gauge dim and exact
kernel/gauge quotient, and independently Gaussian-ranks
both 2-lift incidence matrices to verify the formula.

## First NEW positive finite result: rank-matched SAT/UNSAT n72 pair

The source graph is a reproducible connected legal SCL36,
first selected UNSAT sample #2 from the already-frozen
20261015 incidence 2-switch generator:
```text
base SCL36 SHA256:
9fde1e8f629b75e75a242111a68448b2db4eb47789054fd15d9603fd14788229
nullity6, rank30, 64 parity words EXHAUSTED, exact #SAT=0.
ternary Ay=2 witness found after 14 ternary DFS nodes.
Phi rank26, gauge dimension71, nongauge quotient dimension11.
constructed SAT 2lift SCL72 rank65, nullity7, true #SAT=2.
constructed adjacent nongauge delta (10 flipped incidences):
30740527140689381346453300969473
opposite UNSAT 2lift rank65, nullity7, #SAT=0;
all 128 affine GF2 words exhausted.
```

Both 2-lifts were separately validated square/cubic/linear
and CONNECTED, and the SAT witness checked by original
integer Exact-One row sums.

SAT cover SHA256:
`7b6ac595fe7f47610797faa00986b86e0090bbd8a69d69f73f240d13b8c0be91`

Original nearest UNSAT cover SHA256:
`20e23db175e21595fbb190402ff0f331366cc95538f587379fd4afae0706b38b`

This pair shares GF2 rank and A4=A6=A8=A10=0, but is
distinguished already by low dual B0..3:
```text
SAT cover:   B0..3 = 1,0,38,656.
UNSAT cover: B0..3 = 1,2,42,702.
```
**Hence the FIRST neighbor is NOT a degree-2 spectral twin.**

## Complete finite fixed-Phi nongauge orbit: 2^11=2048 classes

File:
`experiments/r5_cover_rank_spectral_orbit_20261015.py`.

The exact gauge quotient basis has 11 vectors, allowing
a complete enumeration of all 2048 non-gauge classes
in the fixed-Phi fiber. Each representative is one
actual connected legal SCL72 covering of the same UNSAT
base; each has rank65, nullity7 by construction.
The checker nevertheless independently rebuilds its
GF2 affine system and EXHAUSTIVELY checks all 128 words,
assigning SAT iff its kernel has a word of weight
2n/3=48. Rank alone is never used for SAT/UNSAT.
All quotient representatives are examined.

```text
2048 classes
SAT 64
UNSAT 1984
```

Compute for every representative the FULL exact kernel
weight histogram (from 128 codewords), then B0..3 via
Krawtchouk, and exact kernel A4,A6,A8,A10.
Bucket by nullity, truncated B0..Bk and low anchors.

| Root features | Opposite SAT/UNSAT pair | First certified orbit indices |
|---|---|---|
| rank and A4/A6/A8/A10 | YES | 0,1 |
| above and B0..B1 | YES | 0,7 |
| above and B0..B2 | **YES** | **0,13** |
| above and B0..B3 | NO in this complete fixed-Phi orbit | none |

For k=0..3 respectively, the exhaustive orbit contains
1,2,6,26 distinct buckets. For every found opposite-status
collision, the complete independent affine oracle is rerun
on BOTH concrete 2-lifts and records their source rows,
GF2 word counts, exact SAT solution count, SHA256 and
explicit nongauge delta.

**IMPORTANT:** no k3 opposite-status collision in this
2048-class orbit does NOT show B3 universally suffices.
The result is an EXACT finite negative result scoped to this
specific base and fixed full obstruction matrix.

This is the FIRST honest SAT/UNSAT SPECTRAL TWIN for a
JOINT fixed-degree representation:
`(n,d,B0,B1,B2,A4,A6,A8,A10)` agrees, while the two exact
SAT counts differ. Since low signed root D_s=B_s and
moments M0..2 are algebraically determined by D0..2
(Pless), the moment+dual+anchor ROOT LP degree2 sees
identical mathematical input on both. The same LP
optimum follows without pretending that this proves
the LP itself can decide the instance.

## Depth-1 branch-stability gate: honest negative for this pair

File:
`experiments/r5_cover_branch_twin_check_20261015.py`.

Explicit orbit indices 0 and13:
- SAT cover #SAT=2, UNSAT cover #SAT=0.
- ROOT discriminant core k=2 identical and A4..A10
  all zero on both.
- Recompute independently the signed affine
  P/M low degree2 spectrum and GF2 row rank on
  EVERY possible x_v=0 and x_v=1 child; compare the
  SORTED multiset of unordered child-pair cores,
  invariant under variable relabeling.
- **S1 differs**, so for this exact pair and grammar
  minimal distinguishing branch depth `h*=1`.
- Both samples have 22 distinct child pair profiles,
  but the multiplicities/values do not agree.

This is a finite counterexample to universal ROOT
degree2 feature sufficiency, NOT a counterexample to
depth1 experts or an asymptotic solver lower bound.

The 2-lifts FAIL incidence girth>=12; they are NOT
high-girth adversarial examples. Big girth and
balanced-separator resistance remain separate gates.

## Reproduction and independent provenance
```bash
python3 experiments/r5_rank_preserving_cover_twins_20261015.py --self-test
python3 experiments/r5_cover_twins_independent_audit_20261015.py --self-test
python3 experiments/r5_cover_rank_spectral_orbit_20261015.py --self-test
python3 experiments/r5_cover_branch_twin_check_20261015.py --self-test
```
Workflow `.github/workflows/r5-rank-preserving-cover-twins.yml`:
- exact constructive ternary witness + rank obstruction + gauge;
- independent complete dual-cover GF2 enumeration;
- complete 2048-class quotient orbit and degree0..3 buckets;
- independent depth1 signed affine branch comparison;
- uploads JSON artifacts `r5-cover-twin-certificate`,
  `r5-cover-2048-spectral-orbit`,
  `r5-cover-depth1-certificate` (90-day retention).
The *Python scripts and frozen seeds are persistent in GitHub*;
the CI-produced JSON artifact files have explicit expiry.

**GH Actions verified on final source-level CI before this
checkpoint:** 38736775174, 38737104465, 38737556609,
38737868000 all SUCCESS, including independent replay
for both opposite-status spectral pair controls.

## Scientific ledger
| Gate | Status |
|---|---|
| SAT base lifts remain SAT | PROVED ALL n |
| Existence of some SAT 2-lift iff ternary Ay=2 | PROVED ALL n |
| Exact GF2 rank formula for two-sheet covering | PROVED ALL n |
| Gauge and quotient n+1-rank Phi | PROVED for connected bases |
| SAT/UNSAT connected same-rank 2-cover pair | FOUND / EXHAUSTIVE CI |
| SAT/UNSAT same rank + A4/A6/A8/A10 + B0..2 | **FOUND / EXHAUSTIVE CI** |
| SAT/UNSAT same above + B3 in fixed Phi fiber | **NOT FOUND in 2048 classes** |
| Depth1 branch-stable opposite-status twin at indices0/13 | **NO; h*=1** |
| Arbitrary-base universal rank-preserving spectral SAT/UNSAT transformation | NOT PROVED |
| Growing distinguishing-depth h*(n) lower bound | OPEN |
| Universal polynomial-time exact SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

**Next actual mathematical obstacle:** replace this finite
root-only collision with a family that preserves truncated
signed-affine branch signatures at depth≥1, preferably
high-girth and balanced-separator-resistant. One concrete
route is to enlarge the 2-lift base while *proving* its
nontrivial gauge quotient dimension, and derive a condition
on row/column voltage signs that preserves low-weight dual
spectrum and inherited local anchors *by construction*.
Time/budget exhaustion remains UNKNOWN, never UNSAT.
