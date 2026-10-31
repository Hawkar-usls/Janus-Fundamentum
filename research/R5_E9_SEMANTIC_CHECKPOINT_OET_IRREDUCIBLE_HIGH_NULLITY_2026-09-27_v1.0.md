# R5 E9 — Canonical Semantic Restart Checkpoint

Date: 2026-09-27

Status:
`SYNCHRONIZED_AFTER_A_IRREDUCIBLE_TERMINAL_CLOSURE`

Purpose: minimal authoritative restart surface. Detailed proofs/checkers live in the bound artifacts below.

## 0. Scientific ceiling

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL_POLYNOMIAL_SAT_DECIDER = NOT_PROVED
```

No promotion to `P=NP` without a universal exact algorithm satisfying E8 SOUND / COMPLETE / TERMINATES / POLY, including construction, state size, reconstruction and verification.

## 1. Frozen exact forms

Connected square cubic-linear Exact-One carrier `A`:

```text
A^T A = 3I+G
lambda_min(G)>=-3
E_{-3}(G)=ker_R(A)
multiplicity_G(-3)=nullity_Q(A)

Ax=1, x Boolean
iff w=3x-1 in {-1,2}^n and Gw=-3w
iff Hoffman coclique of size n/3.
```

Levi/dual:

```text
Exact-One
iff General Factor K(row)={1}, K(column)={0,3}
iff dual perfect matching / parallel class.
```

Two-permutation normalization:

```text
A'=I+P+Q
Ax=1 iff A'x=1
nullity preserved
connected Levi iff <p,q> transitive.
```

Directed perfect-code form:
choose the normalization matching and orient the two nonmatching incidences from row-pair `i` to column-pairs `p(i),q(i)`. This gives a loopless 2-in/2-out digraph `D` and

```text
Ax=1
iff
for every i: |{i,p(i),q(i)} intersect S|=1
iff
S is a directed perfect code / efficient dominating set of D.
```

This is NOT ordinary digraph-kernel semantics.

## 2. Admitted exact polynomial terminals / subrouters

```text
rank_Q(A)=n
=> BOOLEAN UNSAT.

nullity_Q(A)=O(log n)
=> exact 2^k poly(n,L) kernel router.

recognized OET 2-lift tower
=> exact polynomial contraction + reconstruction.

complete fixed-(c,B) Levi leaf decomposition
=> exact polynomial General-Factor decision + reconstruction.

valid connected normalization with PQ=QP
=> nullity_Q in {0,2};
   0 => UNSAT;
   2 => SAT with exactly 3 witnesses via O(n) Z3 propagation.

Boben A-irreducible Levi graph
=> exact polynomial terminal by uniform bounded treewidth.
```

External corroboration for the commuting branch: Yu–Yang–Fan–Ma (Discrete Applied Mathematics 357, 2024) classify perfect codes in strongly connected 2-valent Cayley digraphs on abelian groups.

## 3. Boben A-only structural closure — NEW

Boben's Theorem 3 classifies every connected A-irreducible `(v_3)` graph as exactly one of

```text
D(n), n>=7, LCF [5,-5]^n;
T_1(n), T_2(n), T_3(n), n>=1;
Pappus.
```

The `T_i(n)` graphs are cycles of fixed 20-vertex segments joined by three-edge interfaces. Bags

```text
V_1 union V_i union V_{i+1}
```

give pathwidth at most `59`, uniformly in `n`. The cyclic `D(n)` family also has constant width because all chords have cyclic span 5; Pappus is finite. Therefore every connected A-irreducible Levi graph has treewidth at most 59.

The exact General-Factor problem `{1}/{0,3}` is solved by fixed-width degree-state DP with witness reconstruction. A fixed-width decomposition is polynomially constructible by standard fixed-treewidth algorithms.

Stronger independent route for `D(n)`:

```text
A_n=I+S+S^3.
```

If `1+z+z^3=0` with `|z|=1`, the unit-circle lemma would require `{z,z^3}={omega,omega^2}`, impossible because `z=omega` or `omega^2` gives `z^3=1`. Hence `A_n` is nonsingular for every n and

```text
D(n) => BOOLEAN UNSAT.
```

### Consequence

Nonadjacent Boben B-reductions are no longer mandatory for a universal structural route.

Repeated legal adjacent/A-reductions always terminate after O(n) removals. When A-reduction stops, the remaining graph is already in the polynomial A-irreducible terminal class above.

Therefore the primary Boben bottleneck is now only:

```text
EXACT SEMANTIC TRANSPORT THROUGH ARBITRARY ADJACENT A-REDUCTION SEQUENCES.
```

## 4. A-reduction semantic barrier

A naive Boben graph reduction is not Exact-One preserving; frozen legal examples include both

```text
SAT -> UNSAT
UNSAT -> SAT.
```

For one adjacent reduction the exact contracted relation is

```text
R(a,b,c,d)=exists s: EQ3(a,b,s) AND EXACT1_3(c,d,s)
```

with tuples

```text
0001
0010
1100.
```

Across either Boben pairing its relation matrix has ordinary rank and Boolean rank 3. Hence an exact one-hidden-state factorization needs at least 3 states; ordinary 2-state edge semantics is not closed even under one A-step.

The previously derived nonadjacent 4-state lower bound remains valid, but it is not required on the new A-only route.

## 5. Other frozen anti-loop results

```text
primitive linear 12_3 carrier with nullity_Q=2 and a unique witness
=> singular/nullity/SAT/witness does NOT imply imprimitive.

rank-1 stitched TD33 family:
n=9m, rank=8m-1, nullity=m+1=n/9+1
=> linear nullity can arise outside OET,
but this family has 2-edge Levi cuts and is handled by fixed-(2,18) leaf peeling.

Kettani-2025 cubic-monotone donor
=> rejected: full rank means Boolean UNSAT, not SAT;
its claimed bounded-treewidth theorem is independently false.
```

## 6. Current hard surfaces

Algebraic:

```text
A=I+P+Q
<p,q> transitive
linear triple system
PQ != QP
nullity_Q(A)=omega(log n)
no admitted OET / fixed-leaf reduction
find ker(A) intersect {-1,2}^n or certify none.
```

Directed perfect-code:

```text
loopless 2-in/2-out permutation digraph
+ closed out-neighborhoods of size 3 are the source triples
+ linear Levi origin
+ noncommuting chosen generators
+ decide existence of S with |N^+[v] intersect S|=1 for every v.
```

A-reduction structural route:

```text
perform legal adjacent A-reductions structurally until A-irreducible terminal;
terminal is polynomial;
OPEN: carry exact source semantics through the reduction sequence with polynomial total state.
```

## 7. Primary next gate

```text
R5_E9_A_REDUCTION_SIGNATURE_CLOSURE_GATE_V1
```

Required material outcome:

```text
A. finite/constant exact signature algebra closed under all legal A-reductions + reconstruction; or
B. weaker canonical representation with polynomial total size and polynomial update/reconstruction; or
C. exact growing counterfamily killing a proposed representation only; or
D. source-proved tensor/Holant theorem supplying the closure.
```

Secondary gate remains

```text
R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1.
```

## 8. Forbidden shortcuts

```text
ordinary digraph kernel = directed perfect code
generic perfect-code hardness/tractability imported without exact carrier match
generic MIS oracle
superlog kernel enumeration
lambda_min=-3 => SAT
arbitrary spectral rounding
LP x=1/3 as Boolean evidence
unrestricted GF(3) kernel as Exact-One
General Factor name alone as solver
singular/nullity/SAT => imprimitive
OET-irreducible => primitive
primitive permutation action => Levi irreducibility
full rank => SAT
high nullity => separator-resistant
fixed leaf peeling => all separators exhausted
one commuting normalization => all normalizations commute
current noncommuting normalization => no commuting normalization exists
Boben graph step => SAT preserving
Boben reduction to Fano/Pappus without semantic state => source solved
2-state A-reduction annotation
local 3-state relation => globally bounded state without proof
P=NP before full E8 closure
```

## 9. Artifact receipt

```text
TWO-PERM NORMAL FORM
  667eb0743f6440f363bbd62e3043240bc189833f

RANK1-STITCHED TD33
  theorem 3b5e6fc63899b4e852d592779a172c0890542c5a
  checker 300424ce867764e0afaade7ea20aa3ef43d242f0

EXACT LEVI CUT / LEAF PEEL
  theorem 83463a0eeeb96ea037126ecb8f0911c87fa04f13
  checker d506bb51324fd6e0d7cd90ca33a62b595e5e5ac7

COMMUTING TWO-PERM TERMINAL
  theorem ba8ae11ef7e1bf03e13ea2c8220d28591ec588de
  checker 9f37b4757442630e69566e0fbddf8e4921162e15

BOBEN SEMANTIC AUDIT
  fcd8815782736802a82f215495352eda0880361c

BOBEN LOCAL STATE BARRIER
  theorem ec00bb9c8181685cd004f90964c4dc1d02cc13bc
  checker 53906e11c112e926830d123b156c7d5d617ca813

DIRECTED PERFECT-CODE NORMAL FORM
  theorem 245704dee8372849e5a09e780254f4c26e6930dd
  checker ca73ad6b8e62d93571d506eb0d806f63ae75ad9f

A-IRREDUCIBLE BOUNDED-WIDTH TERMINAL
  theorem cec70a4d9708405c5d5d9a899d7f86b69168ecaa
  controls 60351fa4c091aca0e20f65732d55c0132bf24dab
  CI de9c9fb16500de7718f9c5a8a4ea3f0637fddef5

CURRENT_CHECKPOINT_SYNC
= this commit
```
