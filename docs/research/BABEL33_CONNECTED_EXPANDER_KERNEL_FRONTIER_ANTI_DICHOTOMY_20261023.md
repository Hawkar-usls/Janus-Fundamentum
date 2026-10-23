# BABEL-33 — connected SCL anti-dichotomy: large rational nullity AND large separator frontier

**2026-10-23, research-only.** Stacked on BABEL-32 PR #558, source head \`5475802bbb8c7a03cd902f877082db92b8e8f397\`. Goal: attack the ACTUAL universality obstruction, not to count more easy SAT instances. This document proves that simply choosing between the BABEL31 bounded-frontier method and BABEL32 logarithmic rational-kernel enumeration **cannot guarantee a polynomial regime on every legal connected SCL input**. This is a **parameter-bound counterexample**, NOT a proof of SAT hardness, P≠NP or a superpolynomial runtime lower bound for all algorithms.

## Input block and three certified incidence ports

Let U be the frozen 27-row, 27-variable legal connected SCL-27 from BABEL24 (#550). It has an exact unique physical SAT model with one-indices

    (2,3,7,9,13,17,19,23,24)

and exact rational incidence rank **25**, hence k_Q(U)=2 (BABEL32 exact Fraction control).

Select THREE distinct row-variable incidences

    port 0: (row0, variable0)
    port 1: (row1, variable6)
    port 2: (row2, variable5).

These row and variable indices are pairwise distinct, and all three variables have Boolean value ZERO in the certified original SAT model. Delete these three edges from the bipartite 54-vertex incidence graph of U. The resulting graph remains **CONNECTED**; this finite graph fact is exhaustively verified by an independent BFS in the checker. It is a fixed finite condition, not an asymptotic assumption.

## All-n construction from ANY simple 3-regular connected macro graph H_t

Let H_t be ANY simple 3-regular connected graph on t even vertices. Replace each macro vertex by an independent copy U of 54 bipartite incidence vertices. At every macro vertex, assign its three incident macro edges bijectively to U's three distinct ports. For every macro edge {a,b}, **swap the occurrence endpoints** of the two assigned port incidences: if its assigned occurrences were (row r_a, local variable v_a) and (row r_b, local variable v_b), remove both and insert (r_a,v_b),(r_b,v_a).

The resulting J(H_t) has n=27t original variables and n=27t Exact-One rows.

### Structural and SAT theorem, all simple cubic macro graphs

1. Every row retains exactly 3 distinct variables, every variable retains exactly 3 occurrences. All original pairs of variables within a block occur together in at most one row (U linear). Importing across distinct macro edges cannot create a repeated pair because the macro graph is simple, each block uses **distinct imported variables/ports**, and any given pair of distinct blocks is joined by at most one macro edge. These properties can be checked combinatorially case-by-case based on whether both candidate rows belong to one block, adjacent blocks or nonadjacent blocks. Thus the new SCL is legal cubic, square and linear.
2. Because U with its three assigned incidences deleted remains connected, and each macro edge adds two cross-incidence edges connecting its endpoint blocks, connected H_t implies connected J(H_t).
3. The concatenated t copies of U's unique original SAT model remain a SAT assignment: every swapped literal has value 0 before and after swapping. **At least one SAT assignment exists.** Uniqueness is NOT claimed or required.
4. Each incidence swap is a rank-ONE update over Q:

       ΔA=(e_r−e_s)(e_b−e_a)^T.

   Starting from a block diagonal A(U)^⊕t of rational rank 25t, and performing exactly |E(H)|=3t/2 swaps, subadditivity of rank gives

       rank_Q(A(J(H))) <= 25t + 3t/2 = 53t/2,
       dim_Q ker A(J(H)) >= 27t−53t/2 = t/2 = n/54.

   This proves **LINEAR rational kernel dimension** for EVERY admissible macro graph, independent of random seeds, actual observed rank or GF2 dimension. Therefore the BABEL32 \`2^k\` Boolean-projection bound is not polynomial on these inputs.

## All-n FRONTIER theorem for an infinite cubic-expander macro family

Established expander-graph theory guarantees the existence of infinite families of **simple 3-regular** graphs H_t with constant positive edge-expansion h>0, e.g. via the standard random-regular-graph existence theorem.

**External background (the existence statement is not proved here):**
- Tim Roughgarden, expander notes, Fact 1.1: https://www.timroughgarden.algorithmsilluminated.org/s17/l/l19.pdf — for every d>=3, d-regular expander families exist.
- Oded Goldreich, expander construction with a cycle and random matching: https://www.wisdom.weizmann.ac.il/~oded/PDF/rnd.pdf.
- Böttcher et al., bounded-degree separator/width equivalences: https://doi.org/10.1016/j.ejc.2009.10.010.

For such a macro family, take ANY subset S of the full bipartite incidence vertices with |S| between N/3 and 2N/3, N=54t, and let B=|∂S| be its number of ORIGINAL incidence edges crossing S.

Call a macro block "partially split" if it has at least one internal factor vertex inside S and at least one outside. As the fixed U with the three port edges removed is connected, every partially split block contributes at least ONE distinct **internal** crossing incidence. Thus the number p of partially split blocks satisfies p<=B.

Let F be the set of full-inside macro blocks, O full-outside macro blocks. Since each block has exactly 54 factor vertices, and S and its complement each have >=N/3 vertices,

    |F| >= t/3-p >= t/3-B,
    |O| >= t/3-p >= t/3-B.

For any subset X of an edge h-expander, \`|E_H(X,V\X)| >= h*min(|X|,|V\X|)\`. Apply to X=F:

    macro edges F -> (O union P) >= h (t/3-B).

At most 3p<=3B of these reach partially split blocks P (macro degree 3), so

    e_H(F,O) >= h(t/3-B)-3B.

For every macro edge joining F to O, **BOTH** associated exchanged incidence edges cross S. Therefore

    B >= 2e_H(F,O) >= 2h(t/3-B)-6B,

yielding the rigorous **balanced-incidence-frontier lower bound**

    B >= [2h / (3(7+2h))] * t = Omega(t) = Omega(n).

Any binary decomposition of the N=54t factor vertices into leaves of maximum fixed W, where W<=N/3, has at least one node whose leaf-union contains between N/3 and 2N/3 vertices (descend through a child larger than 2N/3 until reaching a balanced child). Therefore **every complete decomposition with bounded leaf width** must have some frontier size B=Omega(n) on this family.

This is a proved absence of uniformly bounded separator FRONTIER parameters for the family. It does NOT imply its SAT problem is computationally hard, that the actual number of NONZERO table signatures is exponential, that sparse/compressed tables are impossible, nor that generic SAT requires exponential time. The displayed planted SAT witness is known by construction.

## Combined universal portfolio NO-GO

On the same infinite connected legal SAT family J(H_t) for genuine cubic expander macros:

    dim_Q ker A = Omega(n)         [unconditional rank-one bound]
    necessary incidence frontier = Omega(n)   [expansion + finite U port connectivity].

Therefore the proposed logical dichotomy

    For every connected legal SCL:
      (rational nullity O(log n)) OR (bounded-frontier small-atom tree)

is FALSE. A procedure that merely alternates between the BABEL31 and BABEL32 parameterized guarantees has no proved polynomial worst-case bound on ALL connected SCL. This conclusion is about the **guaranteed parameters of those techniques**, not an impossibility theorem for a future universal algorithm.

**Required actual frontier:** develop a third, globally polynomial **compressed** carrier that can handle both large kernels and large separators, with polynomial certificate discovery, exact count-independent SAT/UNSAT decision, constructive witnesses, and full accounting of all intermediate descriptions. A certificate found on finite samples, an unproved compression hypothesis, or renaming variables does not discharge the universal polynomial-composition theorem.

## Independent finite tests and evidence ceiling

\`experiments/babel33/macroexpander_falsifier.py\` builds deterministic sample 3-regular connected macro graphs using two cycles plus a seeded perfect matching, constructs each full original SCL, and independently checks every legal row, regularity, linearity, connectedness, all physical SAT rows, inverse splice restore, all-port deletion connectivity, and symbolic k_Q>=t/2 rank-one bound for macro block counts t=8,12,16,24,40.

For t<=16 the code also **exhaustively** computes the macro's actual finite edge expansion as a rational minimum over every nontrivial vertex subset of size<=t/2. This finite check is NOT claimed to establish a uniform h>0 for the particular seeded matching sequence. The **infinite** theorem uses the independently established existence of genuine cubic expander macro families. No exact all-n SAT solution count or hard-runtime claim is invented.

\`\`\`
BABEL33_ALL_CUBIC_MACRO_LEGAL_CONNECTED_AND_SAT = PROVED
BABEL33_ALL_CUBIC_MACRO_Q_NULLITY_GE_t_OVER_2 = PROVED
BABEL33_EXPANDER_MACRO_BALANCED_FRONTIER_OMEGA_n = PROVED_USING_KNOWN_EXPANDER_EXISTENCE
BABEL33_Q_KERNEL_OR_BOUNDED_FRONTIER_UNIVERSAL_DICHOTOMY = DISPROVED
BABEL33_GENERAL_SAT_COMPLEXITY_LOWER_BOUND = NOT_CLAIMED
BABEL33_UNIVERSAL_POLYNOMIAL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
