# R5 E9 — Boundary Myhill–Nerode Semantics and NAE Stress Frontier

**Date:** 2026-09-23  
**Status:** exact semantic lemma + source-backed diagnostic stress family. No universal polynomial bound claimed.  
**Scientific firewall:** D1=EMPTY; P_VS_NP=OPEN; P_EQ_NP=NOT_PROVED.

## 1. Exact boundary semantics

Let G be a CNF whose variables are partitioned into a labeled boundary X and internal variables Y.

Define the **boundary extension relation**

[
R_G subseteq {0,1}^{X}
]

by

[
ain R_G
iff
exists bin{0,1}^{Y};G(a,b)=1.
]

Equivalently,

[
R_G = operatorname{Mod}(exists Y,G).
]

Let H be any context whose internal variables are disjoint from those of G and which shares with G only the same labeled boundary X.

Then

[
operatorname{SAT}(Gwedge H)
iff
R_Gcap R_H
eqarnothing.
]

### Theorem E9-BMN1 — canonical context equivalence

For two X-boundaried CNFs G and G',

[
orall Hquad
operatorname{SAT}(Gwedge H)
iff
operatorname{SAT}(G'wedge H)
]

if and only if

[
R_G=R_{G'}.
]

#### Proof

If the extension relations are equal, every glued context H is satisfiable with G exactly when there is a boundary assignment in (R_Gcap R_H), which is exactly the same condition for G'.

Conversely, if (R_G
eq R_{G'}), choose a boundary assignment a in their symmetric difference. Let H_a be the conjunction of unit clauses fixing every boundary variable to a. Then one of G∧H_a and G'∧H_a is satisfiable and the other is not.

Thus the exact Myhill–Nerode state of SAT across a boundary is not mysterious: it is the projected Boolean relation on that boundary.

## 2. Number of exact context classes

For a boundary of size t there are exactly

[
2^{2^t}
]

possible extension relations and hence exactly that many semantic context classes if arbitrary-size boundaried CNFs are allowed.

Every relation (Rsubseteq{0,1}^t) is realizable by a CNF over the boundary variables: for each assignment (a
otin R), include the single clause falsified exactly by a. Long clauses can be replaced by standard equisatisfiable 3CNF chains using internal auxiliaries while preserving the projected relation on the boundary.

### Important ceiling

This does **not** imply a SAT lower bound.

A relation requiring exponentially many bits as a function of boundary size t may have an input description whose own size is already exponential in t. The universal Janus contract measures polynomiality in original input length L, not in boundary size alone.

What this does rule out is a proposed exact state code of size poly(t) that is claimed to represent **all** boundaried CNFs independently of their input size.

## 3. Correction to the previous contextual-state quotient framing

The previous gate

`R5_E9_TYPED_CONTEXTUAL_STATE_QUOTIENT_GATE_V1`

was too broad if "contextual" meant **all** future conditioning/gluing contexts.

Under all contexts, context equivalence is exactly equality of (R_G), i.e. logical equivalence of the projected Boolean functions.

Therefore a generic polynomial key for complete contextual equivalence would simply hide the semantic-equivalence problem.

The correct universal task is representational:

> find, for every boundary encountered by a polynomially constructible decomposition, a polynomial-size **native representation** of (R_G) together with polynomial exact join/projection/conditioning operations.

This is projected knowledge compilation with a heterogeneous native representation library.

## 4. Source connections

### Projected knowledge compilation

Bryant–Nawrocki–Avigad–Heule, SAT 2025, explicitly treat projected knowledge compilation as representing the restriction of a Boolean formula to designated data variables after existentially eliminating the remaining variables. Their framework provides checkable equivalence/projection certificates with Skolem information.

This is a proof-carrying donor for validating a proposed (R_G) representation.

It does not give a universal polynomial-size compiler.

### PS-width

Sæther–Telle–Vatshelle define precisely satisfiable clause sets and ps-width. Their dynamic programming propagates which clause obligations can be realized across a cut; formulas with polynomial ps-width and a suitable decomposition admit polynomial algorithms for weighted MaxSAT and #SAT.

For a fixed assigned variable cut, a residual CNF is determined by which clauses are already satisfied and the fixed projections of unsatisfied clauses to the remaining variables. Thus ps-style signatures are an extensional boundary currency closely related to residual-state counting.

Polynomial ps-width is a tractable special case, not a universal theorem.

### Finite-index / Myhill–Nerode methods

Boundaried-graph finite-index frameworks define states by indistinguishability under all gluing contexts. Their representative counts can be enormous as boundary size grows. The theorem above is the SAT/CNF specialization: the canonical semantic representative is the boundary extension relation itself.

## 5. Minimal Horn × dual-Horn unsafe atom: NAE3

For three variables,

[
operatorname{NAE}_3(x,y,z)
equiv
(xee yee z)wedge(
eg xee
eg yee
eg z).
]

The first clause is dual-Horn; the second is Horn.

The relation consists of all assignments except 000 and 111.

It is not closed under the standard Schaefer tractable polymorphisms AND, OR, majority, or affine minority/XOR. Hence it is a minimal three-variable witness that a Horn×dual-Horn join can leave all four principal tractable Boolean clones.

One Shannon decision on any variable reduces a single NAE atom to one binary clause, hence to Krom/q-Horn. The difficulty is therefore not a single atom but the interaction of many overlapping NAE atoms.

## 6. Source-backed hard stress family

Darmann–Döcker–Dorn (2024) show that monotone NAE-3SAT remains NP-complete even when:

1. clauses are the disjoint union of k partitions of the variable set into triples, for every fixed k>=4;
2. the hypergraph is linear: two distinct clauses share at most one variable.

For k=4 every variable occurs in exactly four NAE constraints.

Encoding each NAE hyperedge {x,y,z} as

[
(xee yee z)wedge(
eg xee
eg yee
eg z)
]

gives a highly regular source-backed Horn×dual-Horn stress class.

This is ideal for testing whether q-Horn stopping + decomposable components + typed bridges actually create polynomial residual compression.

## 7. Frozen diagnostic census

A deterministic generator sampled linear four-partition NAE hypergraphs and encoded every edge as the Horn/dual-Horn pair above.

The q-Horn-stopped CSBC diagnostic used:

- exact quadratic-cover/SCC q-Horn recognition;
- branch variable chosen from one violating triple;
- exact residual memoization;
- variable-disjoint component decomposition.

Finite medians observed:

| variables n | samples | median reachable states |
|---:|---:|---:|
| 15 | 5 successful generators | 207 |
| 18 | 6 | 495 |
| 21 | 6 | 1631 |
| 24 | 6 | 2047 |
| 27 | 6 | 6143 |
| 30 | 6 | 16639 |

Some individual counts were near (2^r-1), indicating almost-tree-like behavior under this frozen heuristic.

### Interpretation ceiling

This is **diagnostic only**.

It is not:
- an asymptotic lower bound;
- evidence that every CSBC is exponential;
- evidence against P=NP.

It does show that the current q-Horn violating-triple branch rule plus exact residual memoization/component decomposition does not automatically collapse this source-backed hard family.

## 8. New active gate

### R5_E9_PROJECTED_NATIVE_BOUNDARY_COMPILATION_GATE_V1

For arbitrary 3CNF F of length L, find in poly(L) time a decomposition/CSBC such that for every live boundary X:

1. the exact extension relation (R_G=operatorname{Mod}(exists Y,G)) has a native representation of size poly(L);
2. that representation carries a polynomially checkable projection/equivalence certificate;
3. every join is either decomposable or a typed exact polynomial bridge;
4. conditioning and projection remain poly(L);
5. total cumulative representation state is poly(L);
6. a satisfying assignment can be reconstructed in poly(L);
7. no generic semantic-equivalence oracle is invoked.

This replaces the vague generic contextual-quotient target.

### Immediate next subgate

`R5_E9_NAE4PART_BOUNDARY_RELATION_TYPE_CENSUS_V1`

For the four-partition linear NAE family, enumerate exact projected boundary relations on small instances and classify them by:

- Horn / AND closure;
- dual-Horn / OR closure;
- bijunctive / majority closure;
- affine / minority closure;
- q-Horn definability where feasible;
- factorization into independent components;
- pair-specific typed bridges already in the library.

Purpose: identify the **first boundary at which all existing native currencies fail**, then attack that exact relation rather than branching blindly.

D1 = EMPTY.  
P_VS_NP = OPEN.
