# R5 E9 — Boben A-Irreducible Bounded-Width Terminal

Date: 2026-09-27

Status:
`JANUS_POLYNOMIAL_TERMINAL_CLASS__A_IRREDUCIBLE_ONLY`

Scientific ceiling:

```text
ALL BOBEN A-IRREDUCIBLE (v_3) LEVI GRAPHS = POLYNOMIAL EXACT-ONE TERMINAL
SEMANTIC TRANSPORT THROUGH A-REDUCTIONS   = OPEN
UNIVERSAL POLYNOMIAL SOLVER               = NOT PROVED
E8_D1                                      = EMPTY
P_VS_NP                                    = OPEN
```

## 1. External structural theorem

Boben's classification of connected A-irreducible `(v_3)` graphs states that every such graph is exactly one of:

```text
D(n), n>=7, with LCF notation [5,-5]^n;
T_1(n), T_2(n), T_3(n), n>=1;
Pappus graph.
```

Moreover `T_i(n)` is obtained from a chain of `n` copies of one fixed 20-vertex segment graph `G_T`, consecutive segments joined by exactly three edges, with the final/first segment joined by one of three fixed three-edge closure patterns.

Source:
- Marko Boben, `Reductions of (v_3) configurations`, arXiv:math/0505136, especially Theorem 3 and the definitions of `D(n),T_i(n)`.

## 2. Uniform bounded treewidth

### 2.1 The `T_i(n)` families

Let `V_i` be the 20 vertices of segment `i`. The only edges between different segments are the three edges between consecutive segments and the fixed three-edge closure between `V_n` and `V_1`.

A path decomposition is obtained with bags

```text
B_i = V_1 union V_i union V_{i+1}
```

for the consecutive segment interfaces, with the obvious first/last bags. Every internal segment edge lies in a bag containing its whole segment; every inter-segment edge lies in the corresponding adjacent bag; the wraparound edges lie in a bag containing `V_1` and `V_n`. For every `i>1`, occurrences of `V_i` are consecutive, while `V_1` is kept throughout.

Hence

```text
|B_i| <= 60
pathwidth(T_j(n)) <= 59
```

for `j=1,2,3`, uniformly in `n`.

### 2.2 The `D(n)` family

Boben identifies `D(n)` with the cubic Hamiltonian graph having LCF notation

```text
[5,-5]^n.
```

Thus, in its canonical cyclic order, every edge is either a cycle edge or a chord whose cyclic span is 5. A sliding-window path decomposition, keeping a constant prefix to cover wraparound edges, has constant width independent of `n`. In particular a coarse bound below 59 is immediate.

An independent stronger JANUS check is available from the configuration description: `D(n)` is the cyclic `n_3` configuration with base line `{0,1,3}`. Its incidence matrix is

```text
A_n = I + S + S^3
```

with `S` the cyclic shift. Since the shifts commute, the existing commuting terminal applies. In fact `A_n` is nonsingular for every `n`: if a unit-modulus root `z` satisfied

```text
1+z+z^3=0,
```

then the unit-circle lemma would force `{z,z^3}={omega,omega^2}`. But `z in {omega,omega^2}` implies `z^3=1`, a contradiction. Therefore

```text
rank_Q(A_n)=n
=> D(n) is Boolean UNSAT for every n>=7.
```

This stronger statement is not needed for the bounded-width terminal but supplies an independent exact route for `D(n)`.

### 2.3 Pappus

The Pappus graph has 18 vertices, so it is a fixed finite terminal.

### Theorem AIR-1

There is an absolute constant `K` (for example `K=59`) such that every connected Boben A-irreducible `(v_3)` Levi graph has

```text
treewidth <= K.
```

## 3. Exact polynomial Exact-One solver on the terminal class

The source problem on the Levi graph is the exact General-Factor instance

```text
K(row)={1}
K(column)={0,3}.
```

On a tree decomposition of fixed width `K`, use the standard exact finite-state DP. For each boundary vertex it suffices to store its currently accumulated selected factor-degree in

```text
{0,1,2,3}
```

plus the ordinary introduce/forget/join consistency data. Since both the graph degree and `K` are absolute constants, the number of states per bag is constant (`<=4^(K+1)` times a constant bookkeeping factor). Each edge is processed once and witness predecessors can be stored.

Hence decision and witness reconstruction are polynomial in the number of Levi vertices (indeed linear after a fixed-width decomposition is supplied).

A decomposition can itself be found in polynomial time for fixed `K` by the standard fixed-treewidth algorithms (Bodlaender 1996). Alternatively, Boben's explicit families can be recognized against their degree-3 templates using bounded-degree graph isomorphism (Luks 1982), after which the decompositions above are explicit.

Therefore every A-irreducible terminal is exactly polynomial-time solvable.

## 4. Consequence: nonadjacent Boben reductions are not mandatory

Every connected `(v_3)` graph is either A-reducible or A-irreducible. Repeated legal A-reductions remove one point and one line at a time and therefore terminate after `O(n)` steps. If no further A-reduction is possible, Boben's classification puts the terminal in the bounded-width class proved above.

Thus a structural route to a universal cubic-linear solver does **not** need nonadjacent B-reductions merely to guarantee termination at a tractable graph.

This removes the nonadjacent local 4-state contraction from the mandatory path. The remaining semantic bottleneck is narrower:

```text
carry Exact-One semantics exactly through an arbitrary sequence of adjacent A-reductions
with polynomial total state / representation size,
then solve the bounded-width A-irreducible terminal,
then reconstruct a source witness.
```

The already-proved adjacent local relation has minimum hidden-state/bond dimension 3, so a two-state edge annotation is impossible; but no theorem yet says the exact 3-state-derived signature algebra stays polynomial under arbitrary A-reduction sequences.

## 5. New primary structural gate

```text
R5_E9_A_REDUCTION_SIGNATURE_CLOSURE_GATE_V1
```

Required outcomes:

```text
A. define a closed exact signature representation for adjacent A-reductions and prove polynomial total size + witness reconstruction;
B. prove a finite/constant state algebra (strongest outcome);
C. prove a weaker polynomial-size canonical representation;
D. construct an explicit A-reduction sequence on which a proposed representation grows superpolynomially, thereby killing that representation only;
E. identify an exact known tensor/Holant theorem that supplies A-reduction closure.
```

Nonadjacent Boben signature closure remains interesting, but is no longer required for this structural route.

## 6. Source bindings

- M. Boben, *Reductions of (v_3) configurations*, arXiv:math/0505136: A-irreducible classification and repeated-segment/cyclic descriptions.
- H. L. Bodlaender, *A Linear-Time Algorithm for Finding Tree-Decompositions of Small Treewidth*, SIAM J. Comput. 25 (1996), 1305–1317: fixed-`k` treewidth recognition/decomposition is polynomial (indeed linear for fixed `k`).
- E. M. Luks, *Isomorphism of Graphs of Bounded Valence Can Be Tested in Polynomial Time*, JCSS 25 (1982), 42–65: alternative polynomial recognition route for trivalent templates.

## 7. Ceiling

```text
BOBEN A-IRREDUCIBLE CLASSIFICATION          = SOURCE-BOUND
UNIFORM TREEWIDTH <=59                      = PROVED FROM CLASSIFICATION
A-IRREDUCIBLE EXACT-ONE POLYNOMIAL TERMINAL = PROVED
D(n) FULL-RANK / UNSAT                       = PROVED
NONADJACENT B-REDUCTION REQUIRED             = NO
ADJACENT A-REDUCTION SEMANTIC CLOSURE         = OPEN
UNIVERSAL POLYNOMIAL SOLVER                  = NOT PROVED
E8_D1                                        = EMPTY
P_VS_NP                                      = OPEN
```
