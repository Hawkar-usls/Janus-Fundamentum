# R5 — Affine residual-function canonicalization: coNP-complete zero orbit, and exact Holyer/Petersen controls

**Date:** 2026-10-14 (Kyiv).  
**Main goal:** deterministic all-input polynomial `SolveLinearCubicXSAT`.  
**Status:** NOT CONSTRUCTED; `P` vs `NP` OPEN.  
**Reproducer:** [r5_universal_affine_residual_orbit_zero_canonicalization_gate.py](../experiments/r5_universal_affine_residual_orbit_zero_canonicalization_gate.py).  
**Earlier direct native Holyer reduction:** [r5_universal_ei_closure_holyer_npcomplete_separation_rank.py](../experiments/r5_universal_ei_closure_holyer_npcomplete_separation_rank.py).  
**Earlier GF3 Boolean fibre:** [r5_universal_f3_boolean_exactification_connected_nullity_barrier.py](../experiments/r5_universal_f3_boolean_exactification_connected_nullity_barrier.py).

## 1. Critical correction to the "few affine residual orbit classes" approach

For a legal square/cubic/linear positive Exact-One incidence matrix `A`, solve its affine linear equations over `F3` by Gaussian elimination:

    x=x0+Bt,   t in F3^d

and define the exact Boolean-point indicator on the finite field domain

    P_A(t)= product_j (x0_j+(Bt)_j-2)^2.

This is 1 exactly when the corresponding native Exact-One assignment is binary and 0 otherwise. It is evaluated in the FINITE FUNCTION ALGEBRA, not as a formal-polynomial identity. Because for boolean x each three-variable clause has total in {0,1,2,3}, it is exactly equivalent to the native integer one-in-three condition.

If native `A` is UNSAT, then `P_A(t)=0` for ALL t. Consequently every EXACT existential projection of `P_A` is identically zero, and every EXACT cofactor under every partial parameter assignment is identically zero. **There is exactly ONE semantic affine-equivalence class at every step on any globally UNSAT instance**, no matter how globally difficult the UNSAT certificate may be. This does NOT give an algorithm to RECOGNIZE that class in polynomial time.

The statement

    #affine-orbits of residual functions <= poly(n)

even if someday PROVED for all native legal inputs, would NOT ALONE imply a polynomial `SolveLinearCubicXSAT`: the algorithm must uniformly compute the residual semantics, detect equivalence, construct representatives, combine them on each projection, and stop within one fixed n^C bound.

## 2. UNIVERSAL hardness theorem for recognizing the ZERO affine orbit

**THEOREM.** Given as input a legal native square/cubic/linear positive Exact-One matrix `A`, represent the consistent affine `F3` system in polynomial time, and ask whether the resulting factored Boolean-point indicator `P_A` is affine-equivalent to the identically zero function on its parameter space. This decision problem is **coNP-COMPLETE**.

*Proof of semantic equivalence:* for ANY bijective affine automorphism `g:F3^d→F3^d`, `P_A∘g` vanishes at all field points iff `P_A` does. In particular a nonzero function cannot be transformed into zero by any invertible affine coordinate change. Hence

    P_A affine-equivalent to zero
        iff P_A identically zero as FUNCTION on F3^d
        iff no binary Exact-One witness exists
        iff A native UNSAT.

*Proof of coNP membership:* the complement is witnessed by an affine parameter point `t∈F3^d` (equivalently its binary vector x), which can be verified in polynomial time by checking `A*x=1` over the integers.

*Proof of coNP hardness even under the promise that the affine system is consistent:* use the prior DIRECT Holyer reduction: a simple cubic graph G becomes a legal native SCL `A_G`; it has a binary exact cover iff G admits a proper three-edge-colouring, a problem NP-complete by Holyer (SIAM Journal on Computing 10(4):718–720, 1981; DOI 10.1137/0210055). These matrices are also ALWAYS consistent over F3, even when the graph is uncolourable. To prove consistency, let D be the non-oriented vertex-edge incidence matrix over F3 and solve `D*y=1`. For every `w∈ker(D^T)` and edge uv, `w_u+w_v=0`. On any connected nonbipartite component, an odd cycle gives w=0; on any connected bipartite CUBIC component, w is ±a on the two colour classes, which have equal size by cubicity, so `w^T 1=0`. Thus `1∈im(D)`. Given this y, assign `x_(e,0)=x_(e,1)=y_e` and `x_(e,2)=1-2*y_e` over F3. The edge clauses and every vertex/colour clause equal 1 modulo 3. Thus ALL these Holyer-hard native matrices admit an affine RREF; the only obstruction is Boolean-point existence.

Therefore affine-equivalence to the ZERO function for the native factored indicator class is coNP-complete, not simply "graph isomorphism difficulty" or an unresolved canonical-labeling nuance. A UNIFORM poly-time full affine canonicalizer capable of recognizing zero for these instances would prove P=NP. This is a hardness EQUIVALENCE, **not an unconditional no-go theorem**, since P vs NP is open.

## 3. Finite independently evaluated Holyer regression

The standalone script imports the prior exact Holyer cubic-graph-to-native-SCL converter, validates square matrices, row/column degree 3 and linearity, then uses exact GF3 RREF and enumerates every affine vector of each example. For each affine point it explicitly checks ALL native SCL variable coordinates are 0/1.

| Cubic graph | Native n | rank over F3 | d | Full affine search points | Exact Boolean covers |
| --- | ---: | ---: | ---: | ---: | ---: |
| K4 | 18 | 14 | 4 | 81 | 6 |
| K3,3 | 27 | 19 | 8 | 6,561 | 12 |
| Petersen | 45 | 35 | 10 | 59,049 | **0** |

To measure literal "number of residual functions", fix the FIRST d−m Gaussian free parameters and retain a suffix function of m parameters; count its distinct exact truth tables across all 3^(d−m) prefix assignments, NOT just its number of satisfying values. For m=0,1,...,d, the complete empirically checked vectors of RAW distinct residual table counts are

    K4:       (2,4,4,3,1)                     for m=0..4
    K3,3:     (2,3,4,8,7,6,4,3,1)             for m=0..8
    Petersen: (1,1,1,1,1,1,1,1,1,1,1)         for m=0..10.

For a FULLY EXACT affine-equivalence test, at suffix dimension m=2 enumerate ALL 432 invertible affine transformations `AGL(2,3)` on the nine field points and canonicalize each table by the least transformed 9-bit support mask.

| Cubic graph | Prefix-fixed cofactors at m=2 | Raw distinct truth tables | EXACT affine orbits |
| --- | ---: | ---: | ---: |
| K4 | 9 | 4 | 2 |
| K3,3 | 729 | 4 | 2 |
| Petersen | 6,561 | 1 | **1 (zero)** |

The choice of Gaussian basis and parameter order is explicitly the deterministic RREF order of the imported source, so these FINITE raw table counts are order-specific. The exact zero statement for UNSAT instances is coordinate/order-INDEPENDENT, and the affine orbit count at each chosen suffix space is exact under all invertible transformations of that space. **No conclusion of polynomial-time canonicalization follows from these small experiments.**

## 4. Additional genuine "globally incompatible" stress test: all 386 small local Petersen subsets

On the graph Petersen, which has 10 vertices, 15 edges and girth 5, enforce every "each edge has exactly one of 3 colours" equation, but only require all three incident colours to be distinct at a chosen subset W of s<5 vertices.

Every induced G[W] is a FOREST, with s vertices and c tree components. Colour the three incident edges at one root of each component (6 choices), then each nonroot vertex has exactly two choices for its two previously uncoloured incident edges because one incoming edge colour is fixed. Hence there are `6^c * 2^(s-c)` colourings of edges incident to W, which number 2s+c. The other `15−2s−c` edges each admit any of 3 colours. The total is

    N(W)=6^c *2^(s-c) *3^(15−2s−c)
        = 2^s *3^(15−2s) > 0.

The executable independently enumerates all assignments to incident edges using depth-first proper-colouring checks, and multiplies by 3 for each unrestrained edge. It audits ALL 386 vertex subsets of size s=0,1,2,3,4:

| s | Number of subsets | Actual colourings for EACH W |
| ---: | ---: | ---: |
| 0 | 1 | 14,348,907 |
| 1 | 10 | 3,188,646 |
| 2 | 45 | 708,588 |
| 3 | 120 | 157,464 |
| 4 | 210 | 34,992 |
| **All 0≤s≤4** | **386** | **All strictly positive** |

But enforcing the colour constraints at ALL 10 vertices of Petersen gives ZERO proper 3-edge-colourings.

Thus every fixed-small collection of such local edge-colour constraints in this explicit UNSAT instance looks compatible; it is the GLOBAL conjunction that is inconsistent. The finite check is not itself an all-size lower bound against adaptive algebraic reasoning or powerful proof systems.

## 5. Second unconditional obstruction: affine-equivalence classes are NOT closed under gluing without alignments

This point is distinct from coNP-hard canonicalization. Even if a hypothetical oracle gave the exact affine orbit CLASS LABEL of every partial function at zero cost, combining two functions that share a physical/algebraic variable cannot depend on the two class labels alone.

For the GF3 point indicator
`δ_a(v)=1−(v−a)^2`, all three `δ_0,δ_1,δ_2` are AFFINELY EQUIVALENT under translations of v. Yet:

    δ_0(v) * δ_0(v) = δ_0(v)   (NONZERO),
    δ_0(v) * δ_1(v) = 0        (ZERO).

The inputs on the two lines have the SAME two affine orbit labels (point-function orbit, point-function orbit) but their products lie in DIFFERENT affine orbits (point-function, zero). Thus affine-equivalence modulo independent parameter changes is NOT A CONGRUENCE for pointwise multiplication / conjunction on a shared coordinate; there can be no universally correct operation `[f]⊗[g]=[fg]` based on bare orbit labels.

This is NOT just an artificial low-degree algebra example. The exact GRID9 Boolean indicator, after the ACTUAL existential elimination of its Gaussian parameter z, yields the physically sourced projected relation `Q(u,v)=1−(u−v)^2`. Fixing u=a produces exactly the three `δ_a(v)` functions above. The new executable calls the independently verified full GRID9 trace and explicitly reproduces these same/nonzero versus cross/zero products.

The necessary repair is to store **relative affine alignments** of shared variables (and enough provenance to update them under composition), not only canonical orbit IDs. No polynomial bound has been proved for the cost of this relative alignment data in general Holyer-hard SCL inputs. The example disproves an ORBIT-ID-ONLY dynamic programming rule, but is NOT a lower bound on dynamic programs that correctly retain transformations or on all polynomial algorithms.

## 6. Uniform construction gate — exact next theorem

The conjecture "at most n^C affine-equivalence classes of semantic residuals after any eliminations" is INSUFFICIENT by itself. For a universal polynomial SCL solver, the missing proof must supply all of:

1. A polynomial-time algorithm for computing correct residual-function representations (including detecting the zero function), not only an existential orbit bound.
2. A uniform polynomial-time algorithm to find/certify affine equivalence or canonical representatives, including functions whose native indicator is zero iff a Holyer-hard instance is UNSAT.
3. A polynomial bound on the number and total bit-size of template descriptions, affine transformations, memo/state tables and reconstruction provenance through ALL d≤n steps.
4. Soundness, completeness and a uniform fixed n^C worst-case runtime bound for ALL legal matrices, with a checkable SAT witness or correct UNSAT decision.

If such an algorithm is exhibited, it will solve the known NP-complete native SCL source and prove P=NP. This is an exact complexity consequence, not a circular proof.

**Scientific checkpoint:**
- All-input semantic zero-collapse for native UNSAT: PROVED.
- coNP-completeness of recognizing zero affine orbit of P_A: PROVED via Holyer.
- Petersen all-depth semantic cofactor counts and two-variable exact AGL orbits: VERIFIED finite experiment.
- Exact positive local vs globally negative Petersen partial-colouring 386-subset check: VERIFIED finite experiment; formula PROVED for any forest W in any cubic graph.
- Uniform polynomial affine canonicalization and update algorithm: NOT PROVED.
- All-input polynomial SolveLinearCubicXSAT: NOT CONSTRUCTED.
- P vs NP: OPEN.

**Source/CI provenance:** committed on research branch; completed successful GitHub Actions job must be checked independently before claiming CI PASS.
