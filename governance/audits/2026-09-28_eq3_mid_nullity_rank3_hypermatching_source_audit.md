# Source audit — EQ3 middle-nullity slab and rank-3 row-basis hypermatching quotient

Date: 2026-09-28

Scope:
- `research/R5_E9_EQ3_MID_NULLITY_HARDNESS_SLAB_2026-09-28_v1.0.md`
- `research/R5_E9_ROW_BASIS_RANK3_HYPERMATCHING_QUOTIENT_2026-09-28_v1.0.md`

Decision:
`PASS_SCOPED_GAP_CONFIRMED__INTERNAL_COROLLARY_PLUS_EXACT_QUOTIENT__NO_NOVELTY_CLAIM__NO_D1_PROMOTION`

## G0 — exact object

The canonical object is Boolean Exact-One feasibility on a square row/column-weight-three incidence matrix `A`, with the additional linearity promise where inherited from the E9 hard carrier.

Two claims are audited:

1. the already-frozen EQ3 Karp image lies in a constant-ratio rational-nullity slab;
2. an actual-row rational basis induces an exact rank-at-most-three hypergraph perfect-matching quotient, and fixing all size-three quotient hyperedges leaves a polynomial general-graph matching residual.

Neither claim asserts a universal polynomial SAT solver.

## G1 — internal history

Internal predecessors located and reused rather than duplicated:

- `R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md` supplies the exact constant-factor reduction into the linear cubic square carrier and the frozen EQ3 gadget;
- `R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md` supplies the `2^k poly(n,L)` low-nullity route;
- `R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md` supplies actual-row basis coverage, the affine row-span identity `Bx=1 iff Ax=1`, and `delta=2n-3k`;
- `R5_E9_TWO_EDGE_2LIFT_3CUT_IRREDUCIBLE_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md` already falsifies the idea that small-cut exhaustion forces low rational nullity.

The new work is therefore explicitly a derived rank accounting theorem and a stricter semantic quotient of the existing row-basis representation, not a renamed recurrence or a new hardness source.

## G2 — canonical external names

External standard objects used by the proof:

- Restricted Exact Cover by 3-Sets (RX3C), equivalently a 3-uniform 3-regular exact-cover source;
- maximum-weight matching in a general graph / Edmonds blossom family of algorithms;
- rank/nullity over `Q` and ordinary Gaussian elimination.

No nonstandard external complexity class or uncharged oracle is introduced.

## G3 — public source exhaustion

Public-source check confirms the two imported complexity facts only:

1. RX3C remains NP-complete when every universe element occurs in exactly three 3-sets. This restriction is attributed in the literature to T. F. Gonzalez (1985). A modern secondary source states the restriction explicitly and notes that in RX3C the number of sets equals the number of elements.
2. Maximum-weight matching in a general graph is polynomial-time solvable; classical Edmonds/blossom algorithms and later Galil–Micali–Gabow improvements provide polynomial bounds.

No external source located in the scoped search states the JANUS-specific identities

```text
K_out = m + kappa,
Delta_out = 17m - 3kappa,
3k = 2p+s,
delta = s+2t,
t-p = n-3k,
```

for this frozen EQ3 construction / actual-row basis quotient. This absence is not promoted as a novelty claim.

## G4 — collision matrix

| Candidate claim | Known/internal collision | Decision |
|---|---|---|
| Cubic / 3-occurrence exact cover is NP-hard | source-bound RX3C / Gonzalez | `SOURCE_BOUND_REUSE` |
| General maximum-weight graph matching is polynomial | source-bound Edmonds / Galil–Micali–Gabow | `SOURCE_BOUND_REUSE` |
| EQ3 regularization is an exact Karp reduction into linear cubic square Exact-One | existing JANUS E9 theorem | `INTERNAL_REUSE` |
| EQ3 image has exact nullity `m+kappa` and lies in `N/10 <= K <= N/6` | not present in internal predecessors before 2026-09-28; follows by exact quotient rank accounting | `JANUS_COROLLARY` |
| Actual-row basis gives rank<=3 hypergraph exact cover | semantic reformulation of `Bx=1`; not a new hardness theorem | `JANUS_COROLLARY` |
| Fixing size-3 hyperedges leaves a mandatory-vertex graph-matching residual | uses source-bound polynomial weighted matching | `JANUS_COROLLARY` |
| `t_B >= n/2` for every actual-row basis on the hard slab | derived from `t-p=n-3k` and the slab bound | `JANUS_COROLLARY` |
| Universal polynomial quotient exists | not established | `HOLD_NEW_MATH` |
| `P=NP` | not established | `HOLD_NEW_MATH` |

## Imported-source boundary

The source audit deliberately imports only standard facts needed for correctness:

- Gonzalez 1985 / RX3C: NP-completeness under exact-three occurrence;
- Edmonds and later weighted-blossom work: polynomial maximum-weight matching in general graphs.

The exact rank identities, hardness-slab placement, basis multiplicity identities, and the `2^t_B poly(n,L)` composition are checked algebraically and by finite replay in the companion JANUS artifacts.

## Promotion boundary

```text
MIDDLE-NULLITY CONSTANT-RATIO HARDNESS SLAB
= SEALED AS A DERIVED EXACT CONSEQUENCE OF THE EXISTING REDUCTION

ROW-BASIS RANK-3 HYPERMATCHING QUOTIENT
= SEALED AS AN EXACT SEMANTIC REFORMULATION

2^t_B POLY ROUTER
= DERIVED EXACT FPT ROUTER

UNIVERSAL POLYNOMIAL SOLVER
= NOT SUPPLIED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```

Next authorized scientific question:

```text
R5_E9_LINEAR_DENSITY_RANK3_HYPERMATCHING_GLOBAL_QUOTIENT_GATE_V1
```

The target must handle the linear-density size-three quotient core on the exact NP-complete slab, rather than attempting to force either rational nullity or the number of size-three basis hyperedges down to logarithmic size.