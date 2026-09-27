# R5 E9 — Semantic Checkpoint: OET-Irreducible High-Nullity Residual

Date: 2026-09-27

Checkpoint status:
`SYNCHRONIZED_AFTER_BOBEN_REDUCTION_SEMANTIC_AUDIT`

This is the canonical compact restart surface. It records theorem-level state, forbidden shortcuts, and the next admissible gates.

## LIVE SCIENTIFIC STATE

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL POLYNOMIAL SAT / EXACT-ONE DECIDER = NOT PROVED

AUTHORITATIVE RESIDUAL
= connected cubic-linear Exact-One / Hoffman / Levi / two-permutation carrier

ADMITTED POLYNOMIAL TERMINALS / SUBROUTERS
= FULL_RANK_BOOLEAN_UNSAT
= LOG_NULLITY_EXACT_KERNEL_ROUTER
= OET_EXACT_CONTRACTION
= FIXED_(c,B)_LEVI_LEAF_PEEL_GENERAL_FACTOR_ROUTER
= CONNECTED_COMMUTING_TWO_PERM_Z3_TERMINAL

CURRENT ALGEBRAIC HARD CORE
= R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1

CURRENT STRUCTURAL DONOR GATE
= R5_E9_BOBEN_SEMANTIC_LIFT_STATE_GROWTH_GATE_V1
```

## PROVED CORE

For a connected linear cubic square incidence matrix `A` and its conflict graph `G`:

```text
A^T A = 3I + G
lambda_min(G) >= -3
E_{-3}(G) = ker_R(A)
multiplicity_G(-3) = nullity_Q(A)
```

and

```text
Ax=1, x Boolean
iff
w=3x-1 in {-1,2}^n and Gw=-3w
iff
G has a Hoffman coclique of size n/3
iff
G has equitable quotient [[0,6],[3,3]].
```

Existing exact polynomial routes:

```text
rank_Q(A)=n
=> BOOLEAN UNSAT.

nullity_Q(A)=O(log n)
=> 2^k poly(n,L) rational-kernel router is polynomial.

recognized one-edge-twist 2-lift tower
=> exact polynomial contraction with witness reconstruction.

complete fixed-(c,B) Levi leaf decomposition
=> exact polynomial General-Factor / Exact-One decision and reconstruction.
```

## EXACT NORMAL FORMS

Levi graph `L(A)` is cubic bipartite with girth at least 6 and

```text
Ax=1
iff
L(A) has General Factor K(row)={1}, K(column)={0,3}
iff
selected dual 3-edges form a perfect matching / parallel class.
```

Every cubic square carrier admits a polynomial three-perfect-matching decomposition

```text
A=P0+P1+P2
```

and row normalization

```text
A'=I+P+Q,
Ax=1 iff A'x=1,
nullity_Q(A')=nullity_Q(A).
```

If `p,q` are the normalized permutations:

```text
L(A) connected iff <p,q> transitive,
z_i+z_{p(i)}+z_{q(i)}=0 for every kernel vector z.
```

Exact-One witnesses are exactly

```text
w=3x-1 in {-1,2}^n
```

with local row multiset `(-1,-1,2)`.

## FROZEN PRIMITIVITY FALSIFIER

There is an explicit linear `12_3` normalized carrier

```text
p=[9,4,6,1,10,8,7,2,0,5,11,3]
q=[3,8,4,5,0,11,10,1,7,6,9,2]
rank_Q(A)=10
nullity_Q(A)=2
<p,q> primitive
unique Exact-One witness={0,1,6,11}.
```

Therefore none of

```text
singular
nullity>=2
SAT+singular
existence of {-1,2} kernel witness
```

forces an imprimitive permutation action.

## FROZEN FALSE DONOR — KETTANI 2025

For every cubic square incidence matrix `A*1=3*1`; if `A` is nonsingular then the unique rational solution to `Ax=1` is `(1/3)1`, hence not Boolean. Cyclic Fano `7_3` is a full-rank explicit UNSAT control.

The donor's bounded-treewidth claim is also false; triangular torus graphs give unbounded treewidth under its stated local hypotheses.

```text
FORBIDDEN_DONOR_ROUTE
= KETTANI_2025_BOUNDED_TREEWIDTH_CUBIC_MONOTONE_1IN3
```

## RANK-1 STITCHED TD(3,3) FAMILY

A connected cubic-linear family `A_m`, obtained by rank-one incidence 2-switch stitching of `m` `TD(3,3)` modules, satisfies exactly

```text
n=9m
rank_Q(A_m)=8m-1
nullity_Q(A_m)=m+1=n/9+1.
```

Thus large nullity need not come from OET lifts. But every module boundary is a 2-edge Levi cut, so this family is not a separator-resistant obstruction.

## EXACT LEVI CUT / LEAF-PEEL COMPOSITION

For a Levi edge cut `D=delta(S)`, exact boundary state is simply

```text
y in {0,1}^D.
```

With residual degree sets obtained by subtracting selected cut-degree,

```text
L feasible
iff
exists y: FEAS(S,y) and FEAS(T,y).
```

Compatible local witnesses reconstruct the global factor exactly.

For fixed `(c,B)`, recursively peeling connected modules of at most `B` vertices behind cuts of at most `c` edges is polynomial. Failure to peel returns `CORE`, not UNSAT/hardness evidence.

The stitched TD33 family is completely `(c=2,B=18)` peelable.

## CONNECTED COMMUTING TWO-PERM TERMINAL — PROVED

For a valid connected normalization

```text
A=I+P+Q,
PQ=QP,
```

`Gamma=<p,q>` is transitive abelian and therefore regular. Fourier/character diagonalization gives

```text
lambda_chi=1+chi(p)+chi(q).
```

A kernel character exists only for

```text
(chi(p),chi(q))=(omega,omega^2) or (omega^2,omega).
```

Because `p,q` generate `Gamma`, there are at most these two characters; rational and complex nullities agree. Therefore

```text
nullity_Q(I+P+Q) in {0,2}.
```

Exact decision:

```text
nullity=0 => BOOLEAN UNSAT.
nullity=2 => SAT with exactly three Exact-One witnesses.
```

The SAT case is constructible by a `Z_3` coloring satisfying one of the two orientations

```text
c(p(i))=c(i)+1, c(q(i))=c(i)+2
or
c(p(i))=c(i)+2, c(q(i))=c(i)+1.
```

Propagation is `O(n)` after normalization.

Scope: a commuting valid normalization is solved. No theorem yet says all possible three-matching normalizations can be searched for a commuting one in polynomial time.

## BOBEN STRUCTURAL REDUCTION — ACCEPTED, NAIVE SEMANTIC IMPORT REJECTED

Boben's reduction theorem applies exactly to the Levi graph class: every connected cubic bipartite graph of girth at least 6 can be reduced through connected graphs of the same class to the Heawood/Fano graph or the Pappus graph.

However a Boben graph reduction is NOT an Exact-One-preserving single-instance reduction.

For an adjacent removed point/line pair, contracting the exact local factors produces

```text
R(a,b,c,d)
= exists s: EQ3(a,b,s) AND EXACT1_3(c,d,s)
```

with exactly the three tuples

```text
(0,0,1,0)
(0,0,0,1)
(1,1,0,0).
```

This does not factor into the two ordinary equality incidences inserted by a Boben reconnection.

Two explicit legal reductions are frozen and executable:

```text
9_3  SAT   (1 witness) -> 8_3 UNSAT (0 witnesses)
10_3 UNSAT (0 witnesses) -> 9_3 SAT   (1 witness).
```

Therefore Boben reduction changes Exact-One status in BOTH directions.

The structural theorem remains potentially valuable only if lifted with exact semantic annotations whose total state growth is polynomial.

## CURRENT HARD RESIDUAL

### Hoffman surface

```text
6-regular conflict graph
+ source-edge partition into triangles
+ lambda_min=-3
+ multiplicity(-3)=omega(log n)
+ no recognized OET quotient
+ survives admitted fixed-(c,B) leaf peeling
+ find Hoffman coclique n/3 or certify none.
```

### Two-permutation surface

For the currently chosen valid normalization:

```text
A=I+P+Q
+ <p,q> transitive
+ linear triple condition
+ nullity_Q(A)=omega(log n)
+ PQ != QP
+ no recognized OET quotient
+ separator-resistant to admitted leaf peeling
+ decide ker(A) intersect {-1,2}^n.
```

### Levi / Boben surface

```text
connected cubic bipartite girth>=6
+ K(row)={1}, K(column)={0,3}
+ Boben structural reduction sequence exists to Fano/Pappus
+ ordinary Boben steps are not SAT preserving
+ exact semantic-lift state algebra currently OPEN.
```

## FORBIDDEN / DO NOT LOOP

```text
1. generic maximum-independent-set oracle;
2. enumerate superlogarithmic -3 eigenspace;
3. lambda_min=-3 => SAT;
4. round arbitrary -3 eigenvector to {-1,2};
5. generic LP feasibility;
6. unrestricted GF(3) kernel as Exact-One;
7. General Factor / dual matching alone as solver;
8. infer exact carrier hardness from broader PSTS hardness;
9. reuse OET or stitched TD33 high-nullity families as irreducible cores;
10. singular/nullity>=2/SAT/witness => imprimitive;
11. OET-irreducible => primitive;
12. det(A)!=0 => Boolean SAT;
13. Kettani-2025 bounded-treewidth donor;
14. high nullity => separator-resistant;
15. primitive <p,q> => Levi separator-resistant;
16. fixed-(c,B) leaf peeling exhausts all separators;
17. commute in one normalization => all normalizations commute;
18. noncommuting current normalization => no commuting normalization exists;
19. Boben graph reduction preserves Exact-One SAT status;
20. reducing to Fano/Pappus without semantic state solves the source instance;
21. finite local Boben relation by itself => globally polynomial state growth;
22. claim P=NP without the full E8 sound/complete/terminate/poly contract.
```

## NEXT GATES

### Gate A — algebraic hard core

```text
R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1
```

Seek a nullity bound, exact quotient/decomposition, bounded nonabelian extension of the commuting theorem, or asymptotic counterfamily.

### Gate B — Boben semantic lift

```text
R5_E9_BOBEN_SEMANTIC_LIFT_STATE_GROWTH_GATE_V1
```

Required material outcome is one of:

```text
A. finite/polynomial-size closed signature algebra under all Boben reductions + exact reconstruction;
B. polynomial bound on signature growth for EQ3 / EXACT1_3;
C. explicit family falsifying a proposed bounded signature scheme;
D. exact source-proved Holant/tensor theorem supplying the missing bounded semantic state.
```

The graph reduction theorem alone is not an algorithmic promotion.

## RESTART RECEIPT

```text
TWO-PERM NORMAL FORM THEOREM
= 667eb0743f6440f363bbd62e3043240bc189833f
NORMAL-FORM CHECKER
= dd4d1b587d0b7d902d356c0b3abe75f137ada2d5

PRIMITIVE NULLITY-2 FALSIFIER
= e779c827866f2947a02db9fc2c54b853df0490d4

KETTANI HOSTILE-DONOR AUDIT
= 19b4f2724528d24ce0da61517c96d4a66657e7a2

RANK1-STITCHED TD33 THEOREM
= 3b5e6fc63899b4e852d592779a172c0890542c5a
RANK1-STITCHED TD33 CHECKER
= 300424ce867764e0afaade7ea20aa3ef43d242f0

EXACT LEVI CUT / LEAF-PEEL THEOREM
= 83463a0eeeb96ea037126ecb8f0911c87fa04f13
SEPARATOR CHECKER
= d506bb51324fd6e0d7cd90ca33a62b595e5e5ac7

COMMUTING TWO-PERM EXACT TERMINAL
= ba8ae11ef7e1bf03e13ea2c8220d28591ec588de
COMMUTING TERMINAL CHECKER
= 9f37b4757442630e69566e0fbddf8e4921162e15
COMMUTING TERMINAL CI
= b482f59a29a1e243af53eac9d8408ece15224297

BOBEN SEMANTIC AUDIT
= fcd8815782736802a82f215495352eda0880361c
BOBEN SEMANTIC CHECKER
= a3c10fffa3426d6cdda4f7bc4ec9259d87051b03
BOBEN SEMANTIC CI
= 43e3d0cd879de93585b946522f2daa754b62315c

CURRENT CHECKPOINT SYNC
= this commit

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
