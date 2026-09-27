# R5 E9 — Semantic Checkpoint: OET-Irreducible High-Nullity Residual

Date: 2026-09-27

Checkpoint status:
`SYNCHRONIZED_AFTER_RANK1_STITCHED_HIGH_NULLITY_THEOREM`

This is the canonical compact restart surface after the latest material mathematics.

## LIVE SCIENTIFIC STATE

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL POLYNOMIAL SAT / EXACT-ONE DECIDER = NOT PROVED

AUTHORITATIVE RESIDUAL GATE
= R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1

CURRENT PRE-GATE
= R5_E9_LEVI_SMALL_SEPARATOR_EXACT_COMPOSITION_GATE_V1

POST-SEPARATOR HARD-CORE ATTACK
= R5_E9_PRIMITIVE_NULLITY_GROWTH_GATE_V1
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

Polynomial terminals already proved:

```text
rank_Q(A)=n
=> BOOLEAN UNSAT.

nullity_Q(A)=O(log n)
=> exact 2^k poly(n,L) rational-kernel router is polynomial.

recognized one-edge-twist 2-lift tower
=> exact polynomial contraction to its root with witness reconstruction.
```

## LEVI / DUAL / TWO-PERMUTATION NORMAL FORMS

Let `L(A)` be the cubic bipartite Levi graph.

```text
Ax=1
iff
L(A) has General Factor with K(row)={1}, K(column)={0,3}
iff
selected dual 3-edges form a perfect matching / parallel class.
```

Every cubic square carrier is polynomially decomposable into three Levi perfect matchings:

```text
A=P0+P1+P2.
```

After row normalization:

```text
A'=I+P+Q,
P,Q permutation matrices,
Ax=1 iff A'x=1,
nullity_Q(A')=nullity_Q(A).
```

If `p,q` are their permutations:

```text
L(A) connected iff <p,q> acts transitively.
```

Linearity becomes the triple condition on `{i,p(i),q(i)}` and the kernel law is

```text
z_i+z_{p(i)}+z_{q(i)}=0 for every i.
```

Exact-One witnesses are exactly the special kernel points

```text
w=3x-1 in {-1,2}^n,
```

with local row multiset `(-1,-1,2)`.

## FROZEN PRIMITIVITY FALSIFIER

Explicit linear `12_3` carrier:

```text
p=[9,4,6,1,10,8,7,2,0,5,11,3]
q=[3,8,4,5,0,11,10,1,7,6,9,2]
A=I+P+Q

rank_Q(A)=10
nullity_Q(A)=2
<p,q> transitive
<p,q> primitive
unique Exact-One witness selects {0,1,6,11}
```

All 693 possible nontrivial blocks containing 0 are rejected exactly. Therefore these shortcuts are false:

```text
singular => imprimitive
nullity_Q(A)>=2 => imprimitive
SAT + singular => imprimitive
{-1,2} kernel witness => imprimitive
```

This finite falsifier does not refute an asymptotic theorem requiring `nullity_Q(A)=omega(log n)` plus extra structure.

## FROZEN HOSTILE-DONOR REJECTION — KETTANI 2025

The claimed cubic monotone 1-in-3 polynomial solver is rejected by two unconditional counterexamples.

First, every cubic square incidence matrix has `A*1=3*1`; if `A` is nonsingular its unique rational solution to `Ax=1` is `(1/3)1`, not Boolean. Explicit Fano `7_3` has `|det A|=24` and zero Boolean Exact-One witnesses. Hence `det(A)!=0 => SAT` is false; the correct rule is `rank_Q(A)=n => BOOLEAN UNSAT`.

Second, the claimed theorem

```text
Delta<=6 + induced-K1,4-free + every vertex in >=3 triangles
=> treewidth<=6
```

is false. The family

```text
T_m = Cay(Z_m^2, {±(1,0), ±(0,1), ±(1,-1)})
```

is 6-regular, induced-`K1,4`-free, every vertex lies in six triangles, and contains the ordinary `m x m` grid as a subgraph after deleting edges, hence `tw(T_m)>=m`.

Freeze:

```text
FORBIDDEN_DONOR_ROUTE
= KETTANI_2025_BOUNDED_TREEWIDTH_CUBIC_MONOTONE_1IN3
```

## NEW THEOREM — RANK-1 STITCHED `TD(3,3)` FAMILY

Let one `TD(3,3)` block have columns

```text
X={x0,x1,x2}, Y={y0,y1,y2}, Z={z0,z1,z2}
```

and rows

```text
L_ij={x_i,y_j,z_{i+j mod 3}}.
```

Its exact rational kernel is

```text
X=a, Y=b, Z=c, a+b+c=0,
```

so `rank_Q=7`, `nullity_Q=2`. Deleting source row `L00`, `L01`, or both leaves rank `7`.

Take `m` disjoint blocks and at each boundary `t|t+1` perform the degree-preserving incidence 2-switch

```text
remove (L01^t, y1^t)
remove (L00^(t+1), x0^(t+1))
add    (L01^t, x0^(t+1))
add    (L00^(t+1), y1^t).
```

The perturbation is rank one:

```text
-e_r1 e_c1^T-e_r2 e_c2^T+e_r1 e_c2^T+e_r2 e_c1^T
=(e_r1-e_r2)(e_c2-e_c1)^T.
```

The resulting `A_m` remains connected, square, cubic and linear. Every block restriction in `ker_Q(A_m)` still has two parameters `(a_t,b_t)` with `c_t=-a_t-b_t`, while boundary `t|t+1` imposes exactly one independent equality

```text
b_t = a_{t+1}.
```

Therefore

```text
n=9m
rank_Q(A_m)=8m-1
nullity_Q(A_m)=m+1=n/9+1.
```

This proves a `Theta(n)` nullity mechanism distinct from the recognized OET 2-lift tower:

```text
small singular modules + rank-1 stitching => linear nullity growth.
```

Every module boundary is also a 2-edge cut of the Levi graph. Hence this family is not evidence that the separator-resistant OET-irreducible core itself has linear nullity.

Critical interpretation:

```text
high nullity != global structural irreducibility
and
primitivity of a chosen <p,q> presentation != Levi structural irreducibility.
```

## OPEN RESIDUAL — THREE EQUIVALENT SURFACES

### Hoffman surface

```text
6-regular conflict graph
+ source-edge partition into triangles
+ lambda_min=-3
+ multiplicity(-3)=omega(log n)
+ no recognized OET quotient
+ no exact small-separator reduction remaining
+ find Hoffman coclique of size n/3 or certify none.
```

### Two-permutation surface

```text
A'=I+P+Q
+ <p,q> transitive
+ linear triple condition
+ dim_Q ker(I+P+Q)=omega(log n)
+ no recognized OET quotient
+ no exact small-separator reduction remaining
+ decide whether ker(I+P+Q) intersects {-1,2}^n.
```

### Levi-factor surface

```text
connected cubic bipartite Levi graph of girth>=6
+ square color classes
+ high rational nullity of its biadjacency matrix
+ no recognized OET quotient
+ separator-resistant after the exact composition pre-gate
+ General Factor degree sets {1}/{0,3}.
```

## FORBIDDEN / DO NOT LOOP

```text
1. generic maximum-independent-set oracle;
2. enumerate the -3 eigenspace when multiplicity is superlogarithmic;
3. lambda_min=-3 => SAT;
4. round arbitrary -3 eigenvectors to {-1,2};
5. generic LP feasibility: x=(1/3)1 is always a fractional solution;
6. unrestricted GF(3) kernel equations as Exact-One;
7. General Factor / dual matching alone as solver;
8. infer exact JANUS-carrier hardness from broader partial-STS hardness;
9. reuse OET high-nullity towers as irreducible counterfamilies;
10. singular or nullity>=2 => imprimitive;
11. SAT or {-1,2} witness => imprimitive;
12. OET-irreducible => primitive;
13. det(A)!=0 => Boolean SAT;
14. Delta<=6 + K1,4-free + >=3 triangles/vertex => bounded treewidth;
15. import Kettani-2025 as a valid P=NP donor;
16. high nullity => separator-resistant / globally irreducible;
17. primitive <p,q> => Levi separator-resistant;
18. treat the stitched TD33 family as OET-irreducible without a proof;
19. claim P=NP from any special-carrier theorem without the full E8 contract.
```

## NEXT PRE-GATE

```text
R5_E9_LEVI_SMALL_SEPARATOR_EXACT_COMPOSITION_GATE_V1
```

Prove an exact polynomial composition theorem for a constant-size Levi edge cut. The state must preserve the General-Factor semantics `K(row)={1}`, `K(column)={0,3}`, and support deterministic witness reconstruction. For cut size `c=O(1)`, the boundary alphabet is finite: edge in/out patterns plus partial degree states of touched vertices.

Required outcome:

```text
A. define exact boundary signatures;
B. prove left/right compatibility iff the original carrier has an Exact-One witness;
C. reconstruct a global witness from compatible side witnesses;
D. prove polynomial construction/composition/reconstruction for constant c;
E. recursively strip constant-separator modules before invoking high-nullity kernel enumeration or permutation-group structure.
```

After this pre-gate, return to:

```text
R5_E9_PRIMITIVE_NULLITY_GROWTH_GATE_V1
```

but only on a representation-independent separator-resistant core.

## RESTART RECEIPT

```text
TWO-PERM NORMAL-FORM THEOREM
= 667eb0743f6440f363bbd62e3043240bc189833f

NORMAL-FORM CHECKER
= dd4d1b587d0b7d902d356c0b3abe75f137ada2d5

PRIMITIVE NULLITY-2 FALSIFIER NOTE
= e779c827866f2947a02db9fc2c54b853df0490d4

PRIMITIVE NULLITY-2 CHECKER
= 374fc406865909e8c3b9788c104f0a34a8cd9e32

KETTANI-2025 HOSTILE-DONOR AUDIT
= 19b4f2724528d24ce0da61517c96d4a66657e7a2

KETTANI-2025 EXECUTABLE FALSIFIER
= bb47a3b19d2c39974afea71fbfc786f16a28f7d8

CI WITH PREVIOUS THREE R5-E9 CHECKERS
= de88fe45d8f5b061cb928c6fff70cdaf25cc964a

RANK1-STITCHED TD33 THEOREM
= 3b5e6fc63899b4e852d592779a172c0890542c5a

RANK1-STITCHED TD33 CHECKER
= 300424ce867764e0afaade7ea20aa3ef43d242f0

CURRENT SCIENTIFIC FRONTIER
= R5_E9_LEVI_SMALL_SEPARATOR_EXACT_COMPOSITION_GATE_V1
  -> then separator-resistant R5_E9_PRIMITIVE_NULLITY_GROWTH_GATE_V1

D1
= EMPTY

P_VS_NP
= OPEN
```
