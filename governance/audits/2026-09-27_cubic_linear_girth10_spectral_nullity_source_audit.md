# Source Audit — Cubic-Linear / Girth-10 Spectral Rational-Nullity Bound

Date: 2026-09-27

Decision: `PASS_SCOPED_GAP_CONFIRMED`

New-math authorization: `true`, strictly for a JANUS-derived specialization and
router binding.  No novelty or priority claim is authorized.

## Canonical object

```text
CONNECTED CUBIC-LINEAR INCIDENCE RATIONAL-NULLITY BOUNDS,
WITH A GIRTH>=10 KESTEN-MCKAY MOMENT CERTIFICATE,
BOUND TO THE EXISTING EXACT 2^k RATIONAL-KERNEL ROUTER
```

## Internal anti-loop search

Searched the current PR branch for combinations of:

- spectral nullity;
- girth 10 rational nullity;
- Kesten-McKay;
- `n/4` nullity;
- trace polynomial certificates;
- cubic-linear rational rank.

No existing artifact was found that states the exact pair of bounds

```text
k(5n-27) <= 2n(n-7)
```

and

```text
Tanner girth >= 10 => k <= n/4 - 1
```

or binds the latter directly to the existing `2^k` Exact-One router.

Existing nearby JANUS work is explicitly retained rather than duplicated:

- the rational-kernel nullity FPT router;
- the rational row-basis overlap-excess FPT router;
- the cubic binary-kernel circuit contraction;
- the prescribed-C10 fixed-girth cover program;
- the signed-trade boundary-projection route.

## External names and queries

Names checked:

- rank of incidence matrices of connected uniform hypergraphs;
- Kesten-McKay law / regular-tree spectral measure;
- closed-walk moments of regular graphs;
- rank/nullity of sparse Boolean incidence matrices;
- incidence matrices of hypergraphs.

Queries included:

- `Kesten McKay distribution moments closed walks infinite regular tree`;
- `incidence matrix rank cubic linear hypergraph nullity bound girth`;
- `rank incidence matrix linear 3-uniform 3-regular hypergraph spectral nullity girth`;
- `The mod p Rank of Incidence Matrices for Connected Uniform Hypergraphs rank formula characteristic 0`.

## Sources checked

1. A. Bjoerner, J. Karlander,
   *The mod p Rank of Incidence Matrices for Connected Uniform Hypergraphs*,
   European Journal of Combinatorics 14(3), 151-155 (1993),
   DOI `10.1006/eujc.1993.1021`.

   The published abstract states that a rank formula in characteristic `p`,
   including characteristic zero, is given for connected uniform hypergraphs.
   This is binding prior art.  Therefore JANUS does not claim incidence-rank
   theory itself as new and does not claim that the present bound is outside
   every consequence of that formula.

2. I. S. Arenas Longoria, J. A. Mingo,
   *Freely Independent Coin Tosses, Standard Young Tableaux, and the
   Kesten-McKay Law*, American Mathematical Monthly 130 (2023).

   This source treats closed walks on regular trees and the Kesten-McKay law.

3. *On the Number of Forests and Connected Spanning Subgraphs*, Graphs and
   Combinatorics (2021).

   The article explicitly records that Kesten-McKay moments count closed walks
   from a root in the infinite `d`-regular tree and that spectral power traces
   count closed walks in a finite graph.

4. C. Cooper, A. Frieze,
   *Rank of the Vertex-Edge Incidence Matrix of r-Out Hypergraphs*,
   SIAM Journal on Discrete Mathematics 36 (2022), 2238-2257,
   DOI `10.1137/21M1467572`.

   This is a random sparse-incidence rank comparison, not the deterministic
   connected cubic-linear/girth-10 theorem used here.

5. S. Parui,
   *On the Incidence matrices of hypergraphs*, arXiv:2409.16055.

   This gives modern context on ranks and null spaces of hypergraph incidence
   matrices.

6. M. Ramani,
   *Incidence Rank and Bounded Defect for Linear Hypergraphs with Cograph Line
   Graphs*, arXiv:2609.27777 (2026).

   This provides strong rank inequalities under the extra cograph-line-graph
   promise.  The promise is materially narrower than the arbitrary connected
   cubic-linear/high-girth carrier considered by JANUS.

## Collision classification

```text
CONNECTED_UNIFORM_HYPERGRAPH_INCIDENCE_RANK
= SOURCE_BOUND_PRIOR_ART

REGULAR_TREE_CLOSED_WALK_MOMENTS
= SOURCE_BOUND_PRIOR_ART

KESTEN_MCKAY_SPECTRAL_MEASURE
= SOURCE_BOUND_PRIOR_ART

RANDOM_SPARSE_INCIDENCE_RANK_RESULTS
= RELATED_NOT_IDENTICAL

CUBIC_LINEAR_TRACE_SPECIALIZATION
= JANUS_DERIVED_SPECIALIZATION__NO_NOVELTY_CLAIM

GIRTH10_Q_POLYNOMIAL_NULLITY_CERTIFICATE
= SCOPED_DERIVED_SPECIALIZATION__EXACT_FORMULATION_NOT_LOCATED_IN_CHECKED_SOURCES

BINDING_TO_EXISTING_2^k_EXACT_ROUTER
= JANUS_INTERNAL_COMPOSITION
```

The phrase `not located` is deliberately not a novelty claim.

## Authorized scope

```text
R5_E9_CUBIC_LINEAR_GIRTH10_SPECTRAL_NULLITY_GATE_V1
```

Authorized artifacts:

- `research/R5_E9_CUBIC_LINEAR_GIRTH10_SPECTRAL_NULLITY_BOUND_2026-09-27_v1.0.md`
- `experiments/r5_e9_cubic_linear_girth10_spectral_nullity_bound.py`

Authorized claims are limited to:

1. the trace/Cauchy rational-nullity upper bound for connected square
   cubic-linear incidence matrices;
2. the `k <= n/4-1` bound under connected cubic Tanner girth at least ten;
3. the resulting `2^(n/4-1) poly(n,L)` upper bound obtained by composing with
   the already-existing exact rational-kernel router;
4. the statement that all of the above remain non-polynomial and do not prove
   P=NP.

Not authorized:

- world-priority or novelty claims;
- a universal polynomial SAT/Exact-One solver claim;
- extrapolation of the finite moment calculation to an unproved arbitrary-order
  hierarchy;
- treating a smaller exponential base as polynomial time.

## Scientific boundary

```text
E8_D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT_PROVED
```
