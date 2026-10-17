# R5 E9 high-girth cubic conflict local MIS reduction extinction — source audit

Status: `SOURCE_AUDIT_ONLY__NEW_MATH_AUTHORIZED_WITHIN_SCOPE__NOT_A_P_VS_NP_PROOF`

Global firewall:

```text
E8_D1 = EMPTY
UNIVERSAL_SELECTOR = OPEN
P_VS_NP = OPEN
```

## Scoped question

On the conflict graph (2-section) of an untouched **linear, 3-uniform, 3-regular Exact-One** source, which standard Maximum-Independent-Set kernel reductions are provably unable to fire, and which additional reductions disappear once the source incidence graph has girth at least 8?

This audit authorizes only a negative-control theorem for the following imported R5 donors:

- degree-2 folding,
- half-integral edge-LP / Nemhauser–Trotter persistency,
- closed-neighborhood domination,
- the standard/simple unconfined reduction.

It also permits re-use of the already materialized JANUS critical-set/crown extinction theorem. It does **not** authorize a claim that all MIS reductions, all R5 rules, R6 ranked/SR macros, SAT, or P vs NP are closed.

## Internal anti-loop search

Checked the existing JANUS route before new mathematics:

1. `research/R5_E9_CONTEXTUAL_CONFLICT_GRAPH_MIS_KERNELIZATION_SOURCE_AUDIT_2026-09-26_v1.0.md`
   - already source-binds folding, unconfined, LP, domination, crown, critical-set, struction and related MIS donors;
   - explicitly leaves the general `MIS_KERNEL_LEAN_GATE` open.
2. `research/R5_E9_REGULAR_UNIFORM_CONFLICT_EXPANSION_AND_CRITICAL_SET_EXTINCTION_2026-09-26_v1.0.md`
   - already proves 6-regularity in the cubic case and extinction of nonempty critical-set/crown entry objects.
3. `research/R5_E9_CUBIC_CONFLICT_GRAPH_PERFECT_ISLAND_AND_OBSTRUCTION_2026-09-25_v1.0.md`
   - already records the genuine odd-hole/9-antihole obstruction; no duplicate finite obstruction is claimed here.
4. `research/R5_E9_HIGH_GIRTH_ODD_HOLE_SPARSE_ATTACHMENT_NEGATIVE_CONTROL_2026-09-26_v1.0.md` and the fixed-girth/prescribed-C10 cover chain
   - provide the high-girth survivor context; the present theorem only derives extra local-kernel extinction from that geometry.
5. `research/R5_E9_UNIVERSAL_SELECTOR_INTERNAL_ANTI_LOOP_BINDING_2026-09-27_v1.0.md`
   - places structural dominance in WDR lane R5 and keeps R6/universal selection open.

Collision verdict:

```text
6_REGULAR_CONFLICT_GRAPH = EXISTING_INTERNAL_RESULT
CRITICAL_SET_CROWN_EXTINCTION = EXISTING_INTERNAL_RESULT
STANDARD_MIS_REDUCTION_DEFINITIONS = SOURCE_BOUND_DONORS
UNIQUE_ALL_HALF_EDGE_LP_ON_CUBIC_LINEAR_CONFLICT = SCOPED_GAP_SURVIVES
HIGH_GIRTH_DOMINATION_EXTINCTION = SCOPED_GAP_SURVIVES
HIGH_GIRTH_SIMPLE_UNCONFINED_EXTINCTION = SCOPED_GAP_SURVIVES
ALL_R5_OR_R6_CLOSED = NOT_AUTHORIZED
```

## External sources checked

- Takuya Akiba and Yoichi Iwata, **Branch-and-reduce exponential/FPT algorithms in practice: A case study of vertex cover**, *Theoretical Computer Science* 609 (2016), 211–225, DOI `10.1016/j.tcs.2015.09.023`. Section 5.3 gives the standard/simple `unconfined` procedure used by the theorem below.
- Sebastian Lamm, Christian Schulz, Darren Strash, Robert Williger, and collaborators' MIS kernelization line; in particular **Scalable Kernelization for Maximum Independent Sets** (SEA 2018 / arXiv:1708.06151), which records degree folding, the half-integral LP reduction, and the Akiba–Iwata simple unconfined rule as practical exact MIS reductions.
- Nemhauser–Trotter half-integral vertex-cover/MIS persistency is treated only as the classical donor theorem. The JANUS contribution in this scope is the source-derived proof that the relevant relaxation has no integral persistent coordinates on the untouched cubic-linear conflict carrier.

No checked source was used to claim novelty of the standard reductions themselves.

## Authorized new proof scope

The new theorem may prove:

1. a linear 3-uniform 3-regular source has a simple 6-regular conflict graph containing source-triangles;
2. the standard edge relaxation
   \[
   \max \sum_v x_v,\qquad x_u+x_v\le 1\;(uv\in E),\qquad x_v\ge0
   \]
   has unique optimum `x_v = 1/2` on every connected component, hence LP persistency fixes no vertex;
3. degree-2 folding cannot fire;
4. if source incidence girth is at least 8, adjacent conflict vertices have exactly one common open neighbor;
5. therefore strict closed-neighborhood domination cannot occur;
6. therefore the standard/simple Akiba–Iwata unconfined procedure terminates immediately as `confined` from every singleton start, because every eligible first neighbor has four vertices outside the current closed neighborhood;
7. combining these facts with the already-proved critical-set/crown extinction yields a stronger **R5 negative control**, not a solver.

## Forbidden promotion

The following statements remain forbidden:

```text
R5_ALL_RULES_CLOSED
R6_RANKED_SR_MACRO_CLOSED
UNIVERSAL_SELECTOR_FOUND
UNIVERSAL_POLYNOMIAL_SAT_SOLVER_FOUND
P_EQUALS_NP
```

The source audit decision is:

```text
DECISION = PASS_SCOPED_GAP_CONFIRMED
NEW_MATH_AUTHORIZED = TRUE_WITHIN_THIS_SCOPE_ONLY
P_VS_NP = OPEN
```
