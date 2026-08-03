# C045 — Proof-Carrying Joint Affine-Basis, Decomposition, and Message Discovery

```text
P_VS_NP = OPEN
C045 = IMPLEMENTED / DRAFT / REVIEW_PENDING
```

## 1. Purpose

C044 fixes the canonical Gaussian free-variable basis before constructing its coordinate-primal decomposition. C045 tests whether a charged, assignment-independent change of affine coordinates can expose a polynomial local signed-support decomposition that the canonical basis misses.

C045 does not search all bases. It implements one fixed finite portfolio of polynomial-time constructors and freezes the complete candidate manifest before any C044 probe is run.

## 2. Candidate coordinate bases

Let the canonical C042/C044 parameterization be

\[
x_i = a_i\lambda \oplus c_i,
\qquad a_i\in GF(2)^d.
\]

Select original variables \(x_{i_1},\ldots,x_{i_d}\) whose row vectors form a basis of \(GF(2)^d\). Define new coordinates

\[
\mu_j = x_{i_j}.
\]

Writing \(A\) for the matrix with rows \(a_{i_j}\) and \(c\) for their constants,

\[
\mu=A\lambda\oplus c,
\qquad
\lambda=A^{-1}(\mu\oplus c).
\]

Every original variable receives an exact transformed coordinate form. The certificate records selected variable identifiers, their canonical coordinate rows and constants, the inverse matrix, every transformed form, and a digest binding the candidate to the canonical basis artifact.

## 3. Frozen constructor portfolio

```text
CANONICAL_FREE
CLAUSE_EXPOSED_GREEDY
SPARSE_ORIGINAL_GREEDY
REVERSE_ORIGINAL_GREEDY
```

Each greedy constructor selects independent original-variable coordinate rows with deterministic tie breaking. Duplicate coordinate systems are removed before probing, while aliases remain in the frozen manifest.

```text
canonical input
-> canonical provenance-carrying affine basis
-> generate every candidate basis
-> deduplicate and freeze manifest digest
-> exactly one complete charged C044 probe per unique candidate
-> select the least-cost replayable SAT/UNSAT terminal
-> exact OPEN when all frozen probes remain OPEN
```

No candidate may be generated or repaired after probe outcomes are visible.

## 4. Constructive theorem

For a fixed polynomial candidate portfolio \(P\), if each constructor, transform proof, and complete C044 probe is bounded by a fixed polynomial capability, then

\[
T_{C045}(I)=\operatorname{poly}(|I|)+\sum_{p\in P}T_{C044}(I,p).
\]

The committed portfolio has at most four raw and at most four unique candidates. C045 returns SAT or UNSAT only when one complete independently replayable C044 probe closes. Otherwise it returns `OPEN_PORTFOLIO_EXHAUSTED`, scoped only to the frozen constructors and capability.

## 5. Affine-arrangement invariance lemma

Let \(\phi\) be an invertible affine coordinate transformation and \(U_i'=\phi^{-1}(U_i)\). Then:

1. \(\phi^{-1}(\bigcap_{i\in S}U_i)=\bigcap_{i\in S}U_i'\);
2. emptiness, inclusion, equality, and dimension of every intersection are preserved;
3. for one fixed factor sequence, the signed recurrence is transported isomorphically;
4. live support cardinalities and coefficient values are unchanged up to renaming represented subspaces.

Therefore basis choice cannot erase intrinsic global intersection-arrangement complexity. It can change equation supports and expose a better local decomposition.

## 6. Strict positive separation

For \(n\ge1\), introduce \(x_1,\ldots,x_n,y_1,\ldots,y_n\) with

\[
x_i=y_1\oplus\cdots\oplus y_i
\]

and

\[
F_n=\bigwedge_{i=1}^n x_i.
\]

The canonical Gaussian basis frees the \(y_i\), so clause falsity is the prefix-parity family

\[
y_1\oplus\cdots\oplus y_i=0.
\]

The last factor touches every canonical coordinate and the coordinate-primal graph is a clique. Under `separator_cap=1` and `local_support_cap=8`, the 40-dimensional control returns:

```text
CANONICAL_FREE -> OPEN_LOCAL_SUPPORT / no_admitted_separator
```

The clause-exposed constructor chooses \(\mu_i=x_i\). Every forbidden factor becomes \(\mu_i=0\), and C044 discovers independent components:

```text
CLAUSE_EXPOSED_GREEDY -> SAT
```

The complete input has 80 original variables and affine dimension 40. Thus charged basis choice strictly enlarges the C044 admitted class.

## 7. Hard-image control

On the registered 24-variable C041 hard image with no affine equations, original-variable basis candidates reduce to coordinate permutations and duplicates. Every unique frozen probe returns `OPEN_LOCAL_SUPPORT`, and C045 returns `OPEN_PORTFOLIO_EXHAUSTED`.

This is not a hardness result. It proves only that the present four-constructor portfolio does not close that pressure fixture.

## 8. Independent verification and audit

The verifier does not call the C045 producer. It independently reconstructs the canonical affine basis, regenerates the frozen candidate manifest, verifies every inverse transform, reconstructs every C044 plan and result using the independent C044 replay path, repeats deterministic selection, and validates the lifted original witness or UNSAT terminal.

```text
220 random CNF + affine instances
220 exact terminals
0 SAT/UNSAT mismatches
0 false witnesses
0 independent-verifier failures

80-variable hidden-basis family:
canonical basis -> OPEN_LOCAL_SUPPORT
clause-exposed basis -> SAT

24-variable hard image:
OPEN_PORTFOLIO_EXHAUSTED

tampered manifest -> REJECTED
tampered probe -> REJECTED
```

Frozen digest:

```text
e7d4ce8cf4425c8c0cd65e2143db8d4f9640829009d84bb7861557fb9f296902
```

## 9. Claim boundary

C045 proves sound polynomial selection from one fixed polynomial portfolio. It does not prove that the portfolio contains a good basis for every CNF, that a good basis can always be found polynomially, or that basis changes alone compress the global intersection arrangement.

```text
POLYNOMIAL_BASIS_PORTFOLIO_COMPLETENESS
OR
BASIS_INVARIANT_SEMANTIC_DECOMPOSITION
```
