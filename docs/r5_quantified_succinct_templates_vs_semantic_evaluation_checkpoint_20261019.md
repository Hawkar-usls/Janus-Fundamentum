# R5 — Universal succinct quantified residual templates: polynomial storage is not polynomial evaluation

**2026-10-19, Kyiv**  
**Status:** theorem on representation size **PROVED**; universal polynomial `SolveLinearCubicXSAT` **NOT CONSTRUCTED**; P versus NP **OPEN**.

## Exact construction for EVERY legal input

Let `A` be any native square+cubic+linear positive Exact-One incidence matrix of size n. Compute the affine solution `x=x0+Bt` of `Ax=1` over F3 by Gaussian elimination, or reject linear inconsistency. Let `d` be its nullity (`d<=n`) and `ell_j(t)` its affine coordinate forms.

Define the exact Boolean-point indicator on the FINITE FUNCTION domain F3^d:

    P_A(t) = product_(j=1)^n (ell_j(t)-2)^2.

For each `0<=k<=d` split parameters into `z=(t1,...,tk)` and `y=(t_(k+1),...,td)` and store the QUANTIFIED template

    T_(A,k)(y) := EXISTS z in F3^k: P_A(z,y)=1.

This is an exact syntactic representation of the semantic projection `Q_(A,k)=E_k...E_1(P_A)`. Store the original product and an integer count k (or prefix of k quantifier nodes), with shared DAG references to all input forms, rather than expanding the quantifiers into expressions without them.

**All-input uniform polynomial bound:** Gaussian elimination O(n^3) field operations, affine description O(nd)<=O(n^2) F3 coefficients, each further existential prefix is added in O(1) pointers and O(log n) bits, or O(k) prefix syntax if explicitly written. Thus the full quantified-template size is O(n^2+k) and the complete sequence of k updates takes O(n^3+n) time including initial elimination. This holds even for Holyer-hard instances. Conjunction of two quantified templates over shared parameters can also be recorded with an AND node provided their binding environments/quantifier scopes are correctly maintained, but exact projection across that conjunction CANNOT in general be inferred by separately eliminating bound variables: in general, EXISTS z (F(z) AND G(z)) != (EXISTS z F(z)) AND (EXISTS z G(z)). Reordering/dropping scopes silently would be unsound.

**CRITICAL FAILURE AS A SOLVER:** Such a template is a *succinct quantified description*, not a quantifier-free computed normal form. To test whether T_(A,d) is true requires solving EXACTLY native SCL SAT. By the explicit Holyer cubic 3-edge-colouring reduction preserved in the repository, native SCL is NP-complete. Therefore deciding nonzero existential semantics of this family of compact templates is NP-complete, and deciding zero is coNP-complete. The existence of the O(n^2) storage representation does NOT establish a uniform polynomial-time semantic evaluator, canonical zero recognizer, algorithm producing a satisfying assignment, or P=NP.

## Correct stronger universal-closure conjecture

A representation grammar `C` and executable procedures must satisfy ALL the following for every legal A:

1. Compile P_A into an EXACT `C` object in n^O(1) time/size.
2. Apply each E_i with correct shared-variable scopes and symbolic alignments in n^O(1) time/size uniformly for ALL intermediate states; for a total d<=n steps, bound the total operation count by one fixed polynomial.
3. **Evaluate semantic zero/nonzero of any resulting representation and obtain a satisfying extension when nonzero, in n^O(1) time.** Merely storing existential quantifiers does not qualify.
4. Correctly compose conjunctions on SHARED variables without assuming that the existential of conjunction equals conjunction of existentials; retain the relative affine alignments required by GRID9 delta_a examples.
5. Provide a full all-input worst-case n^C time proof, not just an abstract circuit existence theorem or a polynomial representation-size bound.

A solution meeting all five would prove P=NP via the preserved exact cubic-graph reduction; no such algorithm is currently established.

## Stress controls and remaining open gate

- Full UNSAT Petersen instance: succinct quantified T_(A,d) has O(n^2) size, but its Boolean value is FALSE.
- Full SAT K4/K3,3 instances: equally succinct quantified T_(A,d) has TRUE value.
- GRID9 k-block instance: 3^(n/9) distinct fixed-frontier residuals all represented by one parametric affine equality template, demonstrating that compact symbolic storage may be easy even when a fixed-order state table is exponentially wide.
- F3 delta_0 and delta_1: both individually satisfiable, but their conjunction is impossible; preserving common existential-variable scope is essential.

**Verdict:** Full-chain *succinct quantified storage* O(n^2) — PROVED. Full-chain polynomial-time *semantic evaluation, canonicalization, and witness reconstruction* — NOT PROVED. `SolveLinearCubicXSAT` — NOT CONSTRUCTED. P vs NP — OPEN.

**References:** Ian Holyer, The NP-Completeness of Edge-Coloring, SIAM Journal on Computing 10(4), 1981, 718–720, https://doi.org/10.1137/0210055. Previous native exact reduction and counterexamples are in experiments/r5_universal_ei_closure_holyer_npcomplete_separation_rank.py, experiments/r5_universal_aligned_residual_context_3power_n_barrier.py and docs/r5_universal_aligned_residual_context_3power_n_checkpoint_20261014.md.

This document is a mathematical checkpoint; it does not claim that a new universal algorithm was executed or that GitHub CI passed.
