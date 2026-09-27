# R5 E9 — Canonical Semantic Restart Checkpoint

Date: 2026-09-27

Status:
`SYNCHRONIZED_AFTER_BOBEN_LOCAL_BOND_DIMENSION_BARRIER`

Purpose: minimal authoritative restart surface. Detailed proofs/checkers live in the bound artifacts below; do not reconstruct state from chat text when this file is available.

## 0. Scientific ceiling

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL_POLYNOMIAL_SAT_DECIDER = NOT_PROVED
```

No special-carrier theorem may be promoted to `P=NP` without the full E8 sound / complete / terminate / polynomial accounting contract.

## 1. Frozen carrier and exact normal forms

Source residual: connected square cubic-linear 3-uniform Exact-One incidence matrix `A`.

```text
Ax=1, x Boolean
iff
w=3x-1 in {-1,2}^n and Gw=-3w
iff
G has a Hoffman coclique of size n/3.
```

For the conflict graph `G`:

```text
A^T A = 3I+G
lambda_min(G)>=-3
E_{-3}(G)=ker_R(A)
multiplicity_G(-3)=nullity_Q(A).
```

Levi/dual forms:

```text
Exact-One
iff General Factor on L(A) with K(row)={1}, K(column)={0,3}
iff perfect matching / parallel class in the dual linear 3-uniform hypergraph.
```

Two-permutation normalization:

```text
A' = I+P+Q
Ax=1 iff A'x=1
nullity_Q(A')=nullity_Q(A)
L(A) connected iff <p,q> transitive
kernel law: z_i+z_{p(i)}+z_{q(i)}=0.
```

## 2. Admitted exact polynomial terminals / subrouters

```text
FULL_RANK_BOOLEAN_UNSAT:
  rank_Q(A)=n => UNSAT.

LOG_NULLITY_KERNEL_ROUTER:
  k=nullity_Q(A)=O(log n) => exact 2^k poly(n,L) router.

OET_EXACT_CONTRACTION:
  recognized one-edge-twist 2-lift tower => exact contraction + reconstruction.

FIXED_(c,B)_LEVI_LEAF_PEEL:
  complete fixed-size leaf decomposition => exact polynomial General-Factor decision + reconstruction.

CONNECTED_COMMUTING_TWO_PERM_Z3_TERMINAL:
  for a valid connected normalization with PQ=QP,
  nullity_Q(I+P+Q) in {0,2};
  0 => UNSAT;
  2 => SAT with exactly three witnesses, constructible by Z3 propagation in O(n).
```

## 3. Frozen falsifiers / anti-loop

### Primitive nullity-2 falsifier

There exists an explicit linear `12_3` SAT carrier with

```text
nullity_Q=2
<p,q> primitive
unique Exact-One witness.
```

Therefore singularity, fixed positive nullity, SAT, or a `{-1,2}` kernel witness do NOT imply imprimitivity.

### Kettani-2025 donor rejected

```text
A*1=3*1.
```

If `A` is nonsingular, the unique rational solution of `Ax=1` is `(1/3)1`, so full rank means Boolean UNSAT, not SAT. The donor's bounded-treewidth theorem is independently falsified by a triangular-torus counterfamily.

### Rank-1 stitched TD33 family

There is a connected cubic-linear family with

```text
n=9m
rank_Q=8m-1
nullity_Q=m+1=n/9+1.
```

Thus linear nullity can arise outside OET. But the family has 2-edge Levi module cuts and is completely handled by the admitted fixed-(2,18) leaf-peel router.

## 4. Exact Levi separator theorem

For a Levi edge cut `D`, exact boundary state is

```text
y in {0,1}^D.
```

Composition is exact:

```text
L feasible
iff
exists y: FEAS(S,y) and FEAS(T,y),
```

with deterministic witness reconstruction. Fixed `(c,B)` leaf peeling is polynomial; a nonpeelable remainder returns `CORE`, never false UNSAT.

## 5. Boben structural donor — current status

External theorem (Marko Boben, arXiv:math/0505136): every connected cubic bipartite graph of girth at least 6 can be reduced through connected graphs of the same class to the Heawood/Fano graph or the Pappus graph.

This theorem applies exactly to the frozen Levi graph class.

### Naive semantic import is false

A Boben graph reduction is NOT an Exact-One-preserving single-instance reduction. Frozen executable controls include

```text
legal 9_3  step: SAT   -> UNSAT
legal 10_3 step: UNSAT -> SAT.
```

For an adjacent removed point/line pair the contracted local relation is

```text
R(a,b,c,d)=exists s: EQ3(a,b,s) AND EXACT1_3(c,d,s)
```

with tuples

```text
0001
0010
1100.
```

It does not factor into the two ordinary Boolean equality edges inserted by the graph reduction.

### Local semantic-state lower bound

Across either legal adjacent Boben pairing the exact relation matrix is, up to row/column permutation,

```text
[0 1 0 0
 1 0 0 0
 0 0 1 0
 0 0 0 0]
```

and has both ordinary rank and Boolean rank `3`.

Hence an exact hidden-state factorization requires at least

```text
3 states
```

already for an adjacent reduction.

For a nonadjacent reduction, pair each point-side and line-side dangling bit into a symbol in `{00,01,10,11}`. The six allowed triples are

```text
(00,00,01)
(00,01,00)
(01,00,00)
(10,10,11)
(10,11,10)
(11,10,10).
```

The `1 | 2` flattening has ordinary rank and Boolean rank `4`.

Therefore

```text
2-state exact Boben semantic lift = FALSIFIED.
```

What remains OPEN is whether a richer signature algebra stays globally bounded / polynomial under arbitrary Boben reduction sequences.

## 6. Current hard core

Algebraic surface, for the currently chosen valid normalization:

```text
A=I+P+Q
<p,q> transitive
linear triple system
PQ != QP
nullity_Q(A)=omega(log n)
no recognized OET contraction
Levi graph survives admitted fixed-(c,B) leaf peeling
find ker(A) intersect {-1,2}^n or certify none.
```

Representation-independent surface:

```text
connected cubic bipartite girth>=6 Levi graph
+ high rational biadjacency nullity
+ no admitted OET / small-leaf decomposition
+ General Factor {1}/{0,3}
+ Boben structural reduction exists
+ exact Boben semantic state growth unresolved.
```

## 7. Active gates

```text
GATE_A
= R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1

Goal:
  nullity bound / new exact quotient / bounded nonabelian extension of commuting theorem / genuine asymptotic counterfamily.

GATE_B
= R5_E9_BOBEN_SIGNATURE_CLOSURE_GATE_V1

Goal:
  choose an explicit exact signature representation;
  close it under adjacent + nonadjacent Boben contractions;
  canonical-compress after each step;
  prove polynomial total state size + reconstruction,
  OR freeze a growing counterfamily for that representation.
```

## 8. Forbidden shortcuts

```text
generic MIS oracle
superlog kernel enumeration
lambda_min=-3 => SAT
round arbitrary -3 eigenvector
LP x=1/3 as Boolean evidence
unrestricted GF(3) kernel as Exact-One
General Factor name alone as a solver
singular/nullity/SAT => imprimitive
OET-irreducible => primitive
primitive permutation action => Levi irreducibility
full rank => SAT
Kettani bounded-treewidth donor
high nullity => separator-resistant
fixed leaf peeling => all separators exhausted
one commuting normalization => all normalizations commute
current noncommuting normalization => no commuting normalization exists
Boben graph reduction => SAT-preserving reduction
Boben reduction to Fano/Pappus => source solved
finite first-step Boben signature => globally bounded state
2-state Boben semantic annotation
P=NP claim before E8 closure
```

## 9. Artifact receipt

```text
TWO-PERM NORMAL FORM
  theorem 667eb0743f6440f363bbd62e3043240bc189833f
  checker dd4d1b587d0b7d902d356c0b3abe75f137ada2d5

PRIMITIVE NULLITY-2 FALSIFIER
  e779c827866f2947a02db9fc2c54b853df0490d4

KETTANI HOSTILE-DONOR AUDIT
  19b4f2724528d24ce0da61517c96d4a66657e7a2

RANK1-STITCHED TD33
  theorem 3b5e6fc63899b4e852d592779a172c0890542c5a
  checker 300424ce867764e0afaade7ea20aa3ef43d242f0

EXACT LEVI CUT / LEAF PEEL
  theorem 83463a0eeeb96ea037126ecb8f0911c87fa04f13
  checker d506bb51324fd6e0d7cd90ca33a62b595e5e5ac7

COMMUTING TWO-PERM EXACT TERMINAL
  theorem ba8ae11ef7e1bf03e13ea2c8220d28591ec588de
  checker 9f37b4757442630e69566e0fbddf8e4921162e15
  CI b482f59a29a1e243af53eac9d8408ece15224297

BOBEN SEMANTIC AUDIT
  theorem/audit fcd8815782736802a82f215495352eda0880361c
  checker a3c10fffa3426d6cdda4f7bc4ec9259d87051b03
  CI 43e3d0cd879de93585b946522f2daa754b62315c

BOBEN LOCAL BOND-DIMENSION BARRIER
  theorem ec00bb9c8181685cd004f90964c4dc1d02cc13bc
  checker 53906e11c112e926830d123b156c7d5d617ca813
  CI 12951a37424086410f52736541601c02b3ebeb4a

CURRENT_CHECKPOINT_SYNC
= this commit
```
