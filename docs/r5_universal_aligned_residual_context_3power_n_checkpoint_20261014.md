# R5 — Coordinate-aligned residual-context states after exact GF(3) projection

**Date:** 2026-10-14.  
**Main goal:** Construct and prove one universal polynomial-time `SolveLinearCubicXSAT` for every native square+cubic+linear positive Exact-One instance.  
**Status:** **NOT CONSTRUCTED**. (P) versus (NP) **OPEN**.

**Executable certificate:** [`r5_universal_aligned_residual_context_3power_n_barrier.py`](../experiments/r5_universal_aligned_residual_context_3power_n_barrier.py)  
**Earlier Holyer zero-class theorem:** [`r5_universal_affine_residual_orbit_zero_canonicalization_gate.py`](../experiments/r5_universal_affine_residual_orbit_zero_canonicalization_gate.py).

## 1. Exact statement — a lower bound against a SPECIFIED explicit state registry

**THEOREM (all k, fully legal native SCL family).** For every integer `k>=1`, there exists a native legal square/cubic/linear positive Exact-One input on `n=9k` variables, with `k` blocks each of which is the genuine connected `GRID9`, and an explicit sequence of `k` exact field-3 existential projections after Gaussian elimination, whose projected Boolean function is

```
Q_k(u_1,...,u_k,v_1,...,v_k)
  = PRODUCT_{i=1}^k [1-(u_i-v_i)^2]
  = 1 if and only if u=v over F3^k.
```

At the **fixed coordinate frontier** after assigning **all** `u_1,..,u_k` and before reading any `v_i`, the exact remaining functions are

```
R_a(v) = 1[v=a],   a in F3^k.
```

There are **exactly `3^k=3^{n/9}` pairwise distinct coordinate-aligned residual functions**, even though all of them are in the **same** affine-equivalence class under translation `v -> v-a`.

Furthermore, this distinction remains necessary under the coarser **existential-conjunction contextual equivalence** that only asks whether two functions can be distinguished by a future constraint on the same shared coordinates:

```
exists v: R_a(v)*R_b(v) = 1 if a=b, else 0.
```

Choosing the context `R_b` distinguishes `R_b` from every `R_a` with `a≠b`. Equivalently, simply assigning `v=b` distinguishes all the cofactors. Thus any **unparameterized deterministic fixed-frontier state-table** that merges only contextually equivalent states cannot be universally bounded by `n^C`, no matter which fixed C is proposed.

**Limit of theorem:** this is a lower bound on the number of *individually instantiated, coordinate-aligned residual states at the specified split/order*. It is NOT a lower bound for general arithmetic circuits, adaptive elimination order, symbolic parameterized templates, or polynomial-time SAT for these legal but disconnected instances. It does NOT disprove a universal polynomial `SolveLinearCubicXSAT` and does NOT resolve P versus NP.

## 2. Actual legal GRID9 origin and exact existential elimination

The nine row/column-3, pairwise-linear incidence triples of the genuine GRID9 block are

```
(0,1,2),(0,3,6),(0,4,8),
(3,4,5),(1,4,7),(1,5,6),
(6,7,8),(2,5,8),(2,3,7).
```

The block has rank 6 over F3 and 3 affine free parameters. Let `x=x0+B*t` be its actual RREF solution, with the natural free entries `t=(x_5,x_7,x_8)`. Apply the explicit invertible coordinate change

```
u=2*t0+t2,
v=2*t1+t2,
z=t0.
```

Its 27 affine points include exactly THREE Boolean covers; transformed support is

```
(0,0,0), (1,1,0), (2,2,1)
```

in `(u,v,z)` order. Therefore the ACTUAL finite-field Boolean-point indicator satisfies

```
(E_z P_GRID9)(u,v) = 1-(u-v)^2.
```

`k` independent copies are also legal SCL matrices, now `n=9k`; exact existential projections of the distinct `z_i` commute with the product because each `z_i` belongs to its own independent block. Therefore the product expression for `Q_k` is a result of **actual** `E_{z_1},...,E_{z_k}`, not a fabricated function that merely resembles a projected native input.

## 3. Contextual separability and precise complexity interpretation

At the split `u=(u_1,..,u_k)` then `v=(v_1,..,v_k)`, each assignment `u=a` induces `R_a(v)=1[v=a]`. Any two distinct contexts are mutually exclusive:

```
R_a * R_b = 0                    if a != b,
R_a * R_a = R_a != 0             if a == b.
```

The right-continuation `v=b` (or conjunction with `R_b`) is a finite exact witness that states labelled a and b **cannot be merged as one fixed-coordinate semantic state** if the algorithm must correctly answer every possible subsequent exact gluing/evaluation.

If an explicit fixed-variable-order ternary decision diagram reads `u_1,..,u_k` before any `v_i`, the 3^k distinct residual functions force width at least 3^k at that layer (a standard Myhill–Nerode/remainder argument). This is a direct, elementary instance of the strong **variable-order dependence** of ordered decision diagrams, historically studied by R. E. Bryant in *Graph-Based Algorithms for Boolean Function Manipulation*, IEEE Trans. Computers 35(8), 1986, DOI 10.1109/TC.1986.1676819.

However, the very same function has a compact `O(k)` arithmetic expression:

```
Q_k = product_i (1-(u_i-v_i)^2),
```

and an **interleaved** order `u_1,v_1,u_2,v_2,...` admits constant control-state width: store one expected ternary value, compare it with the adjacent v, and reject on inequality. An entirely different exact elimination schedule, existentially projecting all `u_i`, produces the **constant TRUE**, because `u=v` is always a legal choice.

Therefore no general lower bound for all polynomial-time solvers, all DAG arithmetic circuits, or optimal/adaptive variable ordering follows. The conclusion only eliminates the conjecture

> “The number of distinct unparameterized coordinate-aligned exact residual states at EVERY fixed frontier in ALL legal SCL systems is at most n^C.”

This conjecture is **FALSE**, even though the stronger desired universal solver theorem remains OPEN.

## 4. Reproducible all-size proof / independent finite regression

The source imports the genuine legal GRID9 and F3 RREF routine, verifies the complete `3^3=27` coordinate change, exactly three Boolean points and the `E_z` equality identity at all nine `(u,v)` pairs.

For `k=1..6`, it explicitly constructs the `3^k` cofactor truth masks over the `3^k` right-coordinate states and checks:

| GRID9 copies k | Native n | Distinct aligned cofactor functions | Abstract affine orbit count |
| ---: | ---: | ---: | ---: |
| 1 | 9 | 3 | 1 |
| 2 | 18 | 9 | 1 |
| 3 | 27 | 27 | 1 |
| 4 | 36 | 81 | 1 |
| 5 | 45 | 243 | 1 |
| 6 | 54 | 729 | 1 |

Every cofactor mask is exactly one singleton over the right-domain values and the pairwise existential-conjunction compatibility matrix is the `3^k × 3^k` identity. All-size validity follows from the exact product identity and does not depend on these finite checks.

## 5. What a viable universal n^C theorem must supply

The correct high-level representation cannot be an **unparameterized list of aligned states at a fixed bad split**, and cannot be a **bare list of abstract affine orbit IDs**. It must retain symbolic relative shifts `a` and an executable law for how they transform during conjunction and existential projection. That alone is NOT enough: the source SCL decision problem is NP-complete via the exact Holyer cubic-edge-colouring reduction.

A proposed `CanonicalEliminate` must now explicitly define its state language and present:
1. A uniform, polynomial-time compiler from every legal native `A` to a correct exact symbolic representation.
2. Uniform procedures for attaching **relative affine alignments**, exact conjunction, exact existential projection and zero-test.
3. A single fixed `n^C` worst-case bound on **all** symbolic representation sizes, intermediate constructions, memoization, comparison and provenance for **all** legal inputs and all elimination steps.
4. Polynomial-time recovery of an actual binary SAT witness, or correct UNSAT decision, including hard Holyer reductions.

**Scientific verdict:** fixed-order unparameterized aligned-state bound `n^C` **REFUTED** by legal GRID9 family; symbolic affine-parametric compression demonstrably bypasses this particular counterexample; universal adaptive parametric closure **NOT PROVED**; universal polynomial `SolveLinearCubicXSAT` **NOT CONSTRUCTED**; P versus NP **OPEN**. CI SUCCESS must not be claimed without independent observed job result.
