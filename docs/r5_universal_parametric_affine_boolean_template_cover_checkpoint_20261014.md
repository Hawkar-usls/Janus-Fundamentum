# R5 — Universal parametrized-template frontier: exact affine-Boolean exponential cover barrier

**Date:** 2026-10-14 (Kyiv). **Goal:** universal deterministic polynomial-time SolveLinearCubicXSAT on EVERY square+cubic+linear positive Exact-One incidence matrix. **Status:** NOT CONSTRUCTED, P vs NP OPEN.

**Standalone verifier:** [r5_universal_parametric_affine_boolean_template_cover_barrier.py](../experiments/r5_universal_parametric_affine_boolean_template_cover_barrier.py).
**Prior source:** [r5_universal_f3_boolean_exactification_connected_nullity_barrier.py](../experiments/r5_universal_f3_boolean_exactification_connected_nullity_barrier.py).

## 1. Syntactic polynomial compression is not a polynomial-time solver

The words *polynomial-sized parametrized template* can hide three independent complexity claims: (a) succinct syntax, (b) effective construction and updating under existential elimination, and (c) effective semantic zero-testing, conjunction and witness recovery.

For EVERY legal matrix A, Gaussian elimination over GF3 produces the full affine solution family x=x0+B t with d<=n. Its Boolean-point indicator is

\[
P_A(t)=\prod_{j=1}^n\left(x0_j+\sum_{i=1}^d B_{ij}t_i-2\right)^2.
\]

The initial factored arithmetic DAG needs O(nd) gates and polynomial-time elimination. At EVERY stage k, an unexpanded quantified template

\[
Q_{A,k}(t_{k+1},\ldots,t_d)
=\exists t_1,\ldots,t_k\ [P_A(t)=1]
\]

has the SAME shared O(nd) body and an O(k) quantifier prefix; adding a quantifier is an O(1) syntax update. Thus polynomial-size representations for EVERY stage are trivial if existential quantifiers are allowed to remain **UNEVALUATED**.

But deciding the value of the closed Q_{A,d} is EXACTLY native SCL SAT, which is NP-complete by the direct Holyer simple cubic 3-edge-colouring reduction. Small syntax does NOT yield polynomial-time zero-testing. Similarly one original template with parameter t and nonlinear guard P_A(t)=1 describes all SAT solutions but provides no efficient decision procedure for whether the guard is satisfiable.

## 2. Universal affine-line-free geometry

**THEOREM.** Let x=x0+B t be ANY injective GF3 affine parametrization of a native SCL instance (B has full column rank). Its Boolean-support parameter set

\[
S_A=\{t\in GF(3)^d : x0+B t\in\{0,1\}^n\}
\]

contains no nontrivial affine line.

**Proof.** If t,t+w,t+2w with w≠0 all belonged to S_A, the corresponding points x,x+B w,x+2B w would all be binary. B w≠0; choose a coordinate j with (B w)_j≠0. That coordinate runs through ALL THREE field elements under these 3 points, including 2, contradicting Boolean membership.

Thus S_A is a cap set in GF(3)^d. The classical cap-set bound of Ellenberg–Gijswijt, *Annals of Mathematics* 185 (2017), DOI 10.4007/annals.2017.185.1.8, is relevant as finite geometry, but its exponential upper bounds do NOT give a polynomial SAT decision test.

**Corollary for a precise representation class:** a positive union of GF3 affine subspaces, in which every summand contains ONLY satisfying parameter points, requires every subspace to be a SINGLETON (any positive-dimensional affine subspace contains an affine line). Such a grammar needs at least #SAT summands.

## 3. Stronger exact theorem: AFFINE-BOOLEAN parameter templates need exponentially many copies

Take the actual legal 9×9 GRID9 positive Exact-One matrix. Its nine row triples are:

    (0,1,2),(0,3,6),(0,4,8),
    (3,4,5),(1,4,7),(1,5,6),
    (6,7,8),(2,5,8),(2,3,7).

It has exactly THREE binary SAT covers as nine-coordinate column indicator vectors:

    p=(0,0,1,0,1,0,1,0,0)
    q=(0,1,0,1,0,0,0,0,1)
    r=(1,0,0,0,0,1,0,1,0).

These three points are NONCOLLINEAR over GF3: any line through two distinct binary points has a third point containing 2.

For k independent GRID9 blocks (native n=9k, fully square/cubic/linear although disconnected across blocks), the complete solution set is

\[
S_k=\{p,q,r\}^k,\qquad |S_k|=3^k.
\]

**Grammar definition:** An AFFINE-BOOLEAN-TEMPLATE is any full image

\[
T=\{b+M a:\ a\in\{0,1\}^{s}\}\subseteq S_k
\]

for ARBITRARY s and GF3 affine map b+M a, required to output ONLY legal SAT points (no extra guard constraining the binary parameters). M can be non-injective; a template may use polynomially many parameters and output exponentially many points.

**THEOREM:** Every T has at most 2^k output points, and covering all S_k by m sound such templates requires

\[
m\ge\left\lceil\frac{3^k}{2^k}\right\rceil
=\left\lceil(3/2)^{n/9}\right\rceil.
\]

**Proof:** Restrict the template to any one GRID9 block. Its output must always belong to {p,q,r}. If two distinct Boolean parameters have nonzero effect v,w on this block, restricting all others to 0 yields a GF3 parallelogram b,b+v,b+w,b+v+w inside that 3-point NONCOLLINEAR set. If v≠w and v≠−w the parallelogram has four distinct vertices; if v=w or v=−w, the image contains a 3-point affine line. Both contradict the 3-point noncollinear set. Hence at most ONE Boolean parameter may affect each block; each block contributes at most TWO possible values. The full k-block image therefore has ≤2^k points. Any exact positive union covering 3^k points requires m*2^k≥3^k. QED.

This is an EXPONENTIAL LOWER BOUND for a **specific parametrized template language**, beyond a mere count of separately instantiated interface states. It is NOT a lower bound for nonlinear parameter maps, nonlinear guards, general arithmetic circuits or adaptive SAT algorithms: one O(k) nonlinear ternary-selector program assigning p/q/r per block describes S_k exactly. P versus NP remains OPEN.

## 4. Reproducible finite controls

The committed verifier independently enumerates all 512 binary assignments of GRID9 and confirms EXACT three supports p,q,r, 3-regular columns/rows and linearity. For k=1..7 it records 3^k total solutions, 2^k maximal per-template image bound, and ceil((3/2)^k) minimum required templates.

For k=1 and k=2 it exhausts ALL nonzero affine cube generators drawn from legitimate solution differences, INCLUDING repeated generators, and checks each entire Boolean parameter cube. Exact maximum sound image sizes:
- k=1, s=1: 2; k=1, s=2: 0 (no maps with BOTH nonzero generators).
- k=2, s=1: 2; k=2, s=2: 4; k=2, s=3: 0.

The numerical tests only validate the proof on finite samples. The all-k lower bound is the independent parallelogram/projection argument. A separate tiny quantified-template check demonstrates polynomial syntax on k=1,2 while deliberately not claiming efficient general evaluation.

## 5. Next exact theorem and scientific firewall

A viable universal solver representation must be MORE expressive than affine images of unconstrained Boolean cubes, and MORE algorithmically evaluable than unevaluated quantified circuits. Its definition must include one uniform polynomial constructor, exact interface conjunction/gluing, existential projection, semantic-zero decision, canonicalization and witness recovery, with a single worst-case n^C bound ALL native Holyer-hard inputs and ALL elimination stages.

**Scientifically proved:** initial SAT point set affine-line-free; affine-Boolean parametrized-template cover exponentially large on GRID9^k; polynomial quantified syntax possible for all stages but NP-hard to interpret generally. **Not proved:** polynomial uniform quantifier elimination/evaluable nonlinear templates for all native inputs; universal polynomial SolveLinearCubicXSAT. P vs NP OPEN. GitHub Actions CI successful run must be independently observed before asserting PASS.
