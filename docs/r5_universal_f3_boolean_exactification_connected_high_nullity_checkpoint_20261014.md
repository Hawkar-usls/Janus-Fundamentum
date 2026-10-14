# R5 — Universal exact `F3` Boolean fibre, and connected linear-cubic high-nullity obstruction

**Date:** 2026-10-14. **Goal:** a single proven polynomial-time `SolveLinearCubicXSAT` valid for every legal source. **Status:** NOT CONSTRUCTED. P versus NP is OPEN.

**Runnable exact experiment and regression:** [r5_universal_f3_boolean_exactification_connected_nullity_barrier.py](../experiments/r5_universal_f3_boolean_exactification_connected_nullity_barrier.py).

## 1. All-input exact reduction (not an algorithmic complexity breakthrough)

Let `A` be an `n×n` 0–1 incidence matrix with exactly three 1s in each row and each column, and with any two rows/columns intersecting in at most one 1. The native task is to find `x∈{0,1}^n` satisfying `Ax=1` **over the integers**, or correctly report UNSAT. Every row's integer sum lies in `{0,1,2,3}`; the only one congruent to 1 modulo 3 is 1. Therefore, for **every legal input**, indeed for every positive three-literal Exact-One formula,

    Ax=1 over integers, x binary
        IFF
    Ax=1 over GF(3), x binary.

The binary-domain restriction is indispensable. The finite-field affine equation alone is only a necessary condition. The earlier GF(2) relaxation has the trivial solution `x=all-ones` because each row sum is three, which equals one modulo two; GF(3) has no analogous universally valid all-ones solution.

With column sums three and row RHS ones, `3|supp(x)|=n` for any integer witness. Thus `n%3!=0` is an O(n) UNSAT gate. Over GF(3), this also follows from multiplying the equations by all-ones: `0=n (mod3)`.

Gaussian elimination over GF(3) yields in polynomial time either an inconsistent affine system (safe UNSAT), or its full affine solution family

    x = x0 + B*t, t∈GF(3)^d, d = n − rank_GF3(A).

**Unproved universal step:** find a binary point in this affine family, or prove no such point exists, with worst-case time `n^C` for a FIXED constant C independent of F, without enumerating all `3^d` possibilities. This step is still NP-hard for the accepted restricted exact-cover source; no universal polynomial bound has been established here.

## 2. Connected SAT family refutes a small-corank or naive full-enumeration argument

Construct the 9×9 base matrix `B` using these **NINE ROW TRIPLES**, with column indices 0..8:

    (0,1,2) (0,3,6) (0,4,8)
    (3,4,5) (1,4,7) (1,5,6)
    (6,7,8) (2,5,8) (2,3,7)

Each row and column has exactly three 1s. Any two distinct rows and any two distinct columns share at most one 1. The bipartite incidence graph is connected. A direct minor/nullspace computation certifies `rank_GF3(B)=6`, so `dim ker_GF3(B)=3`. One GF(3) nullspace basis, in column order, is

    (2,2,2,1,1,1,0,0,0)
    (2,1,0,2,1,0,2,1,0)
    (0,1,2,1,2,0,2,0,1).

A SAT witness is the column set `W={2,4,6}`: each of the nine row triples contains exactly one member of W.

For arbitrary `k>=3`, start with `k` disconnected copies of B indexed `i∈Z/kZ`. To connect copy i to copy i+1, do a **two-incidence switch** replacing entries

    A[(i,3),(i,3)]=1, A[(i+1,0),(i+1,0)]=1

by

    A[(i,3),(i+1,0)]=1, A[(i+1,0),(i,3)]=1.

Here `(i,r)` is the global row `9*i+r` and similarly for columns. Each of the k switches uses distinct rows and columns; every switched column is one of local `0,3`, both **zero** in the base SAT witness W. Therefore no Boolean row sum changes and the concatenation of the k chosen W is a valid EXACT-ONE witness of size `3k`.

**Legality for every k>=3.** Each switch preserves all row/column degrees. Within a base block, new foreign columns are incident to only one row each and their target rows are distinct; pairwise row intersection cannot rise above one. Between different blocks, an exchanged column connects only a single foreign row, and at most one adjacent-block switch pair can affect any fixed pair of blocks when `k>=3`; the two exchanged incidence edges go to different rows, while their original incidences were removed. Thus no two rows acquire two common columns. The dual column argument is symmetric. Each switch places physical incidences between neighboring blocks, so the bipartite incidence graph of the resulting k-block ring is connected.

**All-size rank bound:** Each switch replaces two 1s by the corresponding cross 1s, so its matrix difference has the rank-one outer-product form

    Δ_i=(e_(i,3)−e_(i+1,0)) (e_(i+1,0)−e_(i,3))^T.

Indeed it contributes -1 on two original diagonal entries, +1 on the two crossed entries. It has rank one over GF(3). Before the switches the block-diagonal matrix has rank `6k`; applying k rank-one changes increases rank by **at most k**. Therefore

    rank_GF3(A_k) <= 7k,
    dim ker_GF3(A_k) >= 9k-7k = 2k = 2n/9.

This proves an **infinite family of CONNECTED, LINEAR, cubic square, SAT instances** on which naive enumeration of **all** GF(3) affine parameters requires examining an exponentially large search set `3^{Ω(n)}`. It does NOT rule out clever exploitation of their graph structure or any other polynomial algorithm.

Independent full finite checks for k=3,4,5,6 establish legality, connectivity, explicit SAT witness and actual ranks `21,28,35,42`, respectively (equal to `7k`). The all-size theorem needs only the rigorously proved lower bound on nullity, not the observed rank equality.

## 3. Matched n=12 SAT and UNSAT controls with identical GF(3) rank

Two explicit legal connected 12×12 linear cubic square incidence matrices are frozen as rows of three column indices each in the runnable file. Both have `rank_GF3(A)=11` and consistent `Ax=1 mod3`. Their Boolean statuses differ.

**SAT12:** the exact 4-column cover is `{0,5,6,11}`:

    (0,2,7),(0,1,9),(1,2,5),(0,3,10),
    (4,10,11),(4,5,9),(3,4,6),(1,7,11),
    (3,5,8),(6,7,9),(6,8,10),(2,8,11).

**UNSAT12:** all three affine GF(3) solutions are NON-binary:

    (0,7,9),(1,4,11),(1,2,9),(3,5,6),
    (4,5,7),(5,10,11),(2,4,6),(1,6,7),
    (0,2,8),(8,9,10),(0,3,10),(3,8,11).

An explicit GF(3) solution for UNSAT12 in column order is

    x0=(2,2,2,1,2,0,0,2,0,0,1,0).

Because `rank(A)=11` and `A*1=0 (mod3)`, its ENTIRE GF(3) affine fibre is exactly

    {x0, x0+1, x0+2} mod3.

Each vector necessarily contains some value 2 (indeed x0 contains all symbols 0,1,2, and cyclic shifts only permute them), so **no binary solution exists**. This proves UNSAT12 without trusting an exponential brute-force negative.

Both matrices are fully legal positive cubic linear square source instances, connected, have n divisible by 3 and GF(3)-consistent. Thus **GF(3) rank or consistency alone cannot decide native Exact-One**.

## 4. Reference solver is exact but NOT polynomial

The script includes a deliberately exponential `exact_reference_solver(A)` that obtains the GF(3) affine basis and enumerates its `3^d` parameter choices, checking binary candidates and the original integer equations. This reference solver has soundness and completeness for the native class, but its worst-case running time is NOT shown polynomial; the connected ring family proves that the affine enumerator's parameter space can be exponentially large.

This reference is an oracle for checking future polynomial solver candidates, **not** the requested final algorithm. No special subclass, rank bound or sufficient condition should be rebranded as success toward the user's sole objective.

## 5. Next admissible universal theorem

The required theorem now has a precise all-input form:

> For every `n×n` 0–1 matrix A with row/column sums exactly three and pairwise row/column intersections at most one, determine in worst-case `n^C` time whether the consistent affine GF(3) system `Ax=1` contains a point in `{0,1}^n`, and return a binary witness when one exists (or a sound complete deterministic UNSAT decision).

This is **still unproved**; merely constructing an affine basis is not enough. Candidates should be measured against BOTH matched n12 instances and the connected high-nullity ring family, and against irreducible high-width hard instances to prevent accidental bounded-separator specialization.

**Epistemic verdict:** exact all-input GF(3) reduction PROVED; explicit SAT/UNSAT same-rank controls PROVED; connected linear GF(3) high-nullity family PROVED; general `n^{O(1)}` binary-fibre decision theorem NOT PROVED; universal polynomial `SolveLinearCubicXSAT` NOT CONSTRUCTED; P vs NP OPEN.

**Provenance:** source and proof checkpoint committed in R5 research branch; local independent mathematical probes checked examples. New CI successful completed job not claimed without observation.
