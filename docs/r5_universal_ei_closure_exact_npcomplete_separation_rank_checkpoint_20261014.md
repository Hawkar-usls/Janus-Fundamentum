# R5 — Universal existential closure: exact cubic-edge-colour NP-completeness and exponential separable-rank obstruction

**Date:** 2026-10-14 (Kyiv).  
**Research branch:** \`research/r5-kempe-coupled-involutions-20261013\`.  
**Reproducer:** [r5_universal_ei_closure_holyer_npcomplete_separation_rank.py](../experiments/r5_universal_ei_closure_holyer_npcomplete_separation_rank.py).  
**Current status:** universal deterministic polynomial-time \`SolveLinearCubicXSAT\` **NOT CONSTRUCTED**; \`P\` versus \`NP\` **OPEN**.

## 1. All-size NP-completeness of the exact native SCL source: DIRECT cubic edge-colouring reduction

Let \`G=(V,E)\` be ANY simple cubic graph. Proper 3-edge-colourability is NP-complete (Holyer 1981, DOI: https://doi.org/10.1137/0210055).

Create a Boolean variable \`x_(e,c)\` for each \`e∈E\`, \`c∈{0,1,2}\`. Introduce TWO families of positive Exact-One equations:
- For each edge \`e\`: \`sum_c x_(e,c)=1\`.
- For each vertex \`v\` and colour \`c\`: \`sum_(e incident to v) x_(e,c)=1\`.

Because \`G\` is cubic, all clauses have length three. There are \`3|E|\` variables and \`|E|+3|V| = 3|E|\` clauses, using \`2|E|=3|V|\`. Thus the incidence matrix is SQUARE. Each variable occurs in exactly THREE clauses: its edge-colour choice and its two incident vertex-colour uniqueness clauses. Two different clauses intersect in at most one variable because \`G\` is simple. In particular, the native SCL row/column cubicity and linearity are NOT lost.

A satisfying Exact-One assignment selects one colour for each edge, and the vertex-colour clauses force the three incident edges at every cubic vertex to have all distinct colours. This is precisely a proper three-edge-colouring. Conversely any proper colouring gives a Boolean cover. The construction is linear in graph size. Membership of the native source decision problem in NP is immediate by checking a Boolean witness against its matrix rows.

**Therefore the exact native \`SolveLinearCubicXSAT\` decision problem is NP-complete, not merely a conjecturally difficult subset.** A universal deterministic \`n^C\` algorithm would prove \`P=NP\` (and thereby solve the open problem). It is NOT acceptable to claim such an algorithm by leaving any unhandled branch or using an unproved polynomial closure lemma.

The exact script independently checks full row and column degree three, all pairwise row and column intersections <=1, and exhaustive edge colouring for three reference instances:
- \`K4\`: 4 cubic graph vertices, 6 graph edges → native SCL \`n=18\`, 6 proper colourings → SAT;
- \`K3,3\`: 6 cubic graph vertices, 9 graph edges → native SCL \`n=27\`, 12 proper colourings → SAT;
- \`Petersen\`: 10 cubic graph vertices, 15 graph edges → native SCL \`n=45\`, 0 proper colourings → UNSAT.

The exact number of proper colourings is an independent combinatorial test; any selected colouring gives a directly checkable native Boolean Exact-One witness. The NP-completeness theorem itself relies on Holyer's published theorem; these finite checks do not replace the external universal hardness result.

## 2. Existential projection \`E_i\` is exact but does not have a proved polynomial normal form

Given the Gaussian affine solution \`x=x0+B*t\` over GF(3), the exact Boolean-point indicator is the polynomial function

    P_A(t) = product_{j=1}^n (ell_j(t)-2)^2

in the finite-function algebra \`F3[t]/(t_1^3-t_1,...,t_d^3-t_d)\`. For each \`t\`, \`P_A(t)∈{0,1}\` and it is 1 iff the chosen affine vector is Boolean. Define the exact existential projection

    E_z Q = 1 - (1-Q(z=0))(1-Q(z=1))(1-Q(z=2)).

For Boolean-valued functions \`Q\` this equals the existential OR over the three possible z values and remains Boolean-valued. After eliminating all d Gaussian parameters, a constant 1/0 results, correctly deciding native SAT/UNSAT. This proves **soundness/completeness only**. The symbolic syntax may grow exponentially unless an additional all-input compression theorem is proved.

If a representation scheme provides (i) polynomial-time initial compilation for EVERY native input, (ii) uniformly polynomial-time exact \`E_z\` update on ALL intermediate projected functions with a uniform \`n^C\` size limit, and (iii) polynomial-time evaluation of the final constant, then the direct cubic-edge-colouring reduction makes its existence a constructive proof of \`P=NP\`. One cannot use this desired closure as a premise without providing the missing universal theorem.

**Essential distinction: existence versus efficient construction.** A statement of the form "for each intermediate projected function, SOME algebraic circuit of size n^C exists" is NOT yet a solver, because no algorithm has been given to find the circuit or to update it after the next E_z. The required theorem must specify a UNIFORM polynomial-time procedure to construct each next representation, plus a single polynomial size bound valid along arbitrary legal inputs and all d<=n sequential projections. Even a polynomial-circuit existence theorem with no constructor is insufficient to infer P=NP or provide the user a working SolveLinearCubicXSAT.


## 3. Concrete unconditional barrier: exponential bipartition separable rank, AFTER a real \`E\` projection, on fully legal native instances

Take the legal square, cubic, linear GRID9 block, whose nine Exact-One row clauses are

    (0,1,2),(0,3,6),(0,4,8),
    (3,4,5),(1,4,7),(1,5,6),
    (6,7,8),(2,5,8),(2,3,7).

Its incidence matrix has GF(3) rank 6 and affine solution dimension 3. Its **exact three Boolean solutions** select columns \`{2,4,6}\`, \`{1,3,8}\`, or \`{0,5,7}\`. A reproducible GF(3) reduced-row-echelon form uses free coordinates \`t=(x_5,x_7,x_8)\`. The three Boolean covers occur exactly at t values

    (0,0,0), (0,0,1), (1,1,0).

Apply the explicit GF(3) INVERTIBLE linear parameter change

    u = 2*t_0 + t_2,
    v = 2*t_1 + t_2,
    z = t_0.

Its 3×3 determinant equals 1 mod3. The exact SAT-support triples in these new coordinates are

    (u,v,z) = (0,0,0),(1,1,0),(2,2,1).

Now existentially eliminate z using the ACTUAL Boolean indicator P_GRID9, i.e. apply the exact \`E_z\` formula:

    (E_z P_GRID9)(u,v) = 1 iff u=v
                       = 1-(u-v)^2 over GF(3).

This is checked exhaustively for all 27 affine inputs and all 9 projected inputs.

Build k independent copies of GRID9 (n=9k). The complete native instance is STILL a legal square/cubic/linear positive Exact-One instance, although its bipartite incidence graph is DISCONNECTED. Its affine parameter space is a product of k three-dimensional spaces. Apply the above invertible change independently in each block, and existentially eliminate \`z_1,...,z_k\`. Since the blocks are independent, the exact resulting Boolean polynomial-function is

    Q_k(u_1,...,u_k ; v_1,...,v_k)
      = product_{i=1}^k (1-(u_i-v_i)^2)
      = 1 iff (u_1,...,u_k)=(v_1,...,v_k).

Write its \`3^k × 3^k\` evaluation matrix \`M_k[u,v]=Q_k(u,v)\`. This is the IDENTITY MATRIX \`I_{3^k}\`; hence its linear algebra rank over GF(3) is EXACTLY \`3^k=3^{n/9}\`, not polynomial in native input size.

For a representation of a projected function as a SUM OF SEPARABLE TERMS across THIS specified split,

    Q_k(u,v) = sum_{r=1}^{w} f_r(u) g_r(v),

each summand contributes a rank-at-most-one evaluation matrix, so rank subadditivity forces

    w >= rank_GF3(M_k) = 3^k.

**Second exact normal-form lower bound on the SAME post-projection polynomial.** For one block,
`1-(u-v)^2 = 1+2u^2+2uv+2v^2` over GF(3). These FOUR monomials are distinct in the finite-function quotient (all exponents are <=2), and all have NONZERO coefficients. In k blocks, the variable sets are disjoint; multiplying the k factors yields precisely `4^k=4^{n/9}` distinct NONZERO monomials, without cancellation or finite-field reduction. Therefore any algorithm that insists on explicitly materializing every coefficient of the unique reduced polynomial normal form after these actual existential eliminations needs exponentially large output. The same function still has an `O(k)` factored circuit and trivial SAT status. This is an unconditional lower bound on a REPRESENTATION FORMAT, **not** on general arithmetic circuits or decision algorithms.

**This is a rigorous exponential lower bound for that specific representation family after exact existential elimination.** It refutes any proposed universal theorem claiming every projected native indicator has polynomial separable rank for every split of Gaussian coordinates, including disconnected legal native inputs.

**EXTREMELY IMPORTANT NON-CLAIMS:** The same Q_k has an O(k)-SIZE FACTORIZED ARITHMETIC CIRCUIT, namely its above product of k local equalities. Therefore the large evaluation rank says **NOTHING** by itself about general arithmetic circuit size, adaptive network representations, polynomial-time satisfiability of this easy family, or the still-open P vs NP question. Nor does a disconnected counterexample prove the same property for the more restricted connected promise. This barrier is meaningful ONLY against a proposed polynomial-separable-rank **normal form**, not against all compact representations.

## 4. What an actual all-input closure theorem now has to prove

The native SCL class is NP-complete. To meet the user's sole goal, an explicit \`SolveLinearCubicXSAT\` algorithm must provide ALL of:

1. A polynomial-time, polynomial-output-size method to compile \`P_A\` into one well-defined representation class \`C\`, uniformly for every native legal A, without a \`3^d\` enumeration.
2. An actual uniform algorithm computing \`E_i Q\` in \`C\` on every intermediate function produced, within worst-case \`n^C\` time (C fixed independent of n, rank, width, input).
3. A strict all-step size bound \`n^C\`, including DAG sharing, memo tables, preprocessing, and all hidden intermediate representations; not just a small final symbolic expression.
4. Polynomial-time evaluation of final SAT/UNSAT and the ability to self-reduce to recover a Boolean witness.
5. A proof of soundness and completeness for ALL native square/cubic/linear matrices, including Holyer-reduced hard instances and previously frozen n12 rank-matched SAT/UNSAT controls.

The rank witness already forbids invoking "bounded separated-term width across arbitrary cuts" as an unproved shortcut. The generic quantifier formula proves semantic correctness, not polynomial complexity. Both issues have reproducible tests.

**Status:** direct NP-completeness bridge PROVED (Holyer + elementary exact native reduction); projected separable-rank exponential lower bound PROVED; universal polynomial \`E_i\` size closure NOT PROVED; polynomial \`SolveLinearCubicXSAT\` NOT CONSTRUCTED; \`P\) versus \`NP\` OPEN.
