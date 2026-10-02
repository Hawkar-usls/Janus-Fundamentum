# R5 E9 — Hostile Donor Audit: Kettani 2025 Cubic Monotone 1-in-3 SAT Polynomial Claim

Date: 2026-09-27

Status:
`DONOR_REJECTED_BY_EXPLICIT_COUNTEREXAMPLES__NO_D1_PROMOTION`

Scientific firewall:

```text
THE AUDITED PAPER CLAIMS A POLYNOMIAL DECIDER FOR CUBIC MONOTONE 1-IN-3 SAT
AND THEREFORE CLAIMS P=NP.

JANUS DOES NOT IMPORT THAT CLAIM.
TWO INDEPENDENT MATHEMATICAL FAILURES ARE EXHIBITED BELOW.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Audited source:

Omar Kettani,
*Cubic Monotone 1-in-3 SAT Problem is Polynomial Time Solvable*,
International Journal of Mathematics Trends and Technology 71(9), 36–46 (2025),
DOI `10.14445/22315373/IJMTT-V71I9P105`.

The source algorithm contains the branch

```text
calculate det(A)
if det(A) != 0:
    output the unique solution x=A^{-1}b
else:
    construct the associated graph and run bounded-treewidth MIS
```

and its graph argument claims that maximum degree at most six, induced-`K_{1,4}`-freeness,
and at least three triangles through every vertex imply treewidth at most six.

Both claims needed by that route fail.

---

## 1. Fatal algebraic branch error

Let `A` be any square cubic incidence matrix: every row contains exactly three ones.
Then

\[
A\mathbf 1=3\mathbf 1.
\]

Therefore

\[
A\left(\frac13\mathbf1\right)=\mathbf1.
\]

If `A` is nonsingular over `Q`, this is the **unique rational solution** of `Ax=1`:

\[
\boxed{x=A^{-1}\mathbf1=\frac13\mathbf1.}
\]

But `1/3` is not Boolean. Hence the correct Exact-One conclusion is

\[
\boxed{\det(A)\ne0\Longrightarrow\text{UNSAT},}
\]

not “the unique linear-system solution is a satisfying Boolean assignment.”

This is exactly the full-rank terminal independently derived in the JANUS spectral/nullity route.

### 1.1 Explicit Fano `7_3` counterexample

Use the cyclic Fano-plane incidence matrix with row supports

\[
T_i=i+\{0,1,3\}\pmod 7,
\qquad i=0,\ldots,6.
\]

Explicitly:

```text
0: {0,1,3}
1: {1,2,4}
2: {2,3,5}
3: {3,4,6}
4: {4,5,0}
5: {5,6,1}
6: {6,0,2}
```

Every row and every column has weight three, and every two distinct rows meet in exactly one column.
Thus

\[
AA^T=2I+J.
\]

Its eigenvalues are `9` on the all-ones direction and `2` with multiplicity six. Therefore

\[
\det(AA^T)=9\cdot2^6=576,
\qquad
|\det A|=24\ne0.
\]

So the unique rational solution is

\[
x=\frac13\mathbf1.
\]

It is not Boolean.

There is also a one-line combinatorial contradiction to a Boolean Exact-One witness. If `S` is the selected set of columns, every selected column covers exactly three rows while all seven rows must be covered exactly once, so

\[
3|S|=7,
\]

impossible over the integers.

Thus the Fano `7_3` instance is an explicit input satisfying the cubic square conditions for which

```text
det(A) != 0
but
Boolean Exact-One = UNSAT.
```

This alone invalidates the claimed algorithm.

---

## 2. Independent failure of the bounded-treewidth theorem

The audited paper also asserts the general graph statement

```text
maximum degree <= 6
+ no induced K_{1,4}
+ every vertex belongs to at least 3 triangles
=> treewidth <= 6.
```

This statement is false by an explicit infinite family.

### 2.1 Triangular torus family

For every integer `m>=5`, define

\[
T_m=\operatorname{Cay}(\mathbb Z_m^2,
\{\pm(1,0),\pm(0,1),\pm(1,-1)\}).
\]

Equivalently, vertices are pairs `(i,j)` modulo `m`, with the six neighbors

```text
(i+1,j), (i-1,j),
(i,j+1), (i,j-1),
(i+1,j-1), (i-1,j+1).
```

#### Degree

For `m>=5` these six neighbors are distinct, so

\[
\Delta(T_m)=6.
\]

#### No induced `K_{1,4}`

The subgraph induced by the six neighbors of any vertex is a 6-cycle.
Its independence number is three. Therefore no vertex has four pairwise nonadjacent neighbors, so

\[
T_m\text{ is induced-}K_{1,4}\text{-free}.
\]

#### Triangles

The six edges of that neighborhood 6-cycle correspond to six distinct triangles through the center vertex. Hence every vertex lies in exactly six triangles, in particular at least three.

#### Unbounded treewidth

Delete the two diagonal-generator edge families and the wraparound horizontal/vertical edges as needed. The resulting graph contains the ordinary `m x m` grid `P_m square P_m` as a subgraph.
Treewidth is monotone under taking subgraphs/minors, and

\[
\operatorname{tw}(P_m\square P_m)=m.
\]

Therefore

\[
\boxed{\operatorname{tw}(T_m)\ge m,}
\]

which is unbounded and exceeds six for `m>=7`.

Thus the claimed three graph conditions do not imply bounded treewidth.

This counterfamily is used only to falsify the theorem **as stated**. It is not claimed that every `T_m` itself is the conflict graph of a JANUS linear cubic incidence structure.

---

## 3. Why the donor cannot enter E8-D1

The audited route fails independently in both branches needed by its proposed decider:

1. the nonsingular branch confuses the unique rational solution of `Ax=1` with a Boolean Exact-One solution;
2. the singular/graph branch relies on a false bounded-treewidth theorem.

Therefore

```text
KETTANI_2025_POLYNOMIAL_DECIDER
= REJECTED

KETTANI_2025_P_EQUALS_NP_CONCLUSION
= NOT ADMITTED

DONOR CONTRIBUTION TO E8_D1
= NONE
```

The correct nonsingular rule is actually useful and already belongs to the JANUS route:

```text
rank_Q(A)=n
=>
UNSAT.
```

The singular high-nullity branch remains the real frontier.

---

## 4. External consistency check

Cubic Monotone 1-in-3 SAT is standardly used as an NP-complete source problem in the literature (equivalently, the exact-cover formulation with each element occurring three times). Therefore any valid polynomial algorithm for the full class would indeed imply `P=NP`; that raises the verification bar rather than validating the claim.

This audit does not rely on that hardness fact to reject the donor: the Fano instance and triangular-torus family are unconditional mathematical counterexamples to concrete steps of the proposed proof.

---

## 5. Anti-loop rule

Freeze:

```text
FORBIDDEN_DONOR_ROUTE
= KETTANI_2025_BOUNDED_TREEWIDTH_CUBIC_MONOTONE_1IN3
```

Do not re-import any of the following without a genuinely different theorem:

```text
det(A)!=0 => Boolean SAT
Delta<=6 + induced-K1,4-free + >=3 triangles/vertex => tw<=6
generic bounded-treewidth MIS as a solver for all cubic monotone 1-in-3 instances
```

---

## 6. Ceiling after audit

```text
FULL-RANK CUBIC SQUARE A
=> UNIQUE RATIONAL SOLUTION (1/3)1
=> BOOLEAN UNSAT
= PROVED

FANO 7_3 DET(A)=24 AND BOOLEAN UNSAT
= PROVED / EXECUTABLE COUNTEREXAMPLE

KETTANI STEP-2 NONSINGULAR BRANCH
= FALSIFIED

CLAIMED GENERAL TREEWIDTH<=6 THEOREM
= FALSIFIED BY TRIANGULAR TORI

KETTANI 2025 DONOR
= REJECTED

CURRENT JANUS FRONTIER
= OET-IRREDUCIBLE HIGH-NULLITY / PRIMITIVE-NULLITY-GROWTH RESIDUAL

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
