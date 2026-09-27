# R5 E9 — Semantic Checkpoint: OET-Irreducible High-Nullity Residual

Date: 2026-09-27

Checkpoint status:
`SYNCHRONIZED_AFTER_COMMUTING_TWO_PERM_EXACT_TERMINAL`

This is the canonical compact restart surface after the latest material mathematics.

## LIVE SCIENTIFIC STATE

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL POLYNOMIAL SAT / EXACT-ONE DECIDER = NOT PROVED

AUTHORITATIVE RESIDUAL GATE
= R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1

ADMITTED POLYNOMIAL SUBROUTERS / TERMINALS
= FULL_RANK_BOOLEAN_UNSAT
= LOG_NULLITY_EXACT_KERNEL_ROUTER
= OET_EXACT_CONTRACTION
= FIXED_(c,B)_LEVI_LEAF_PEEL_GENERAL_FACTOR_ROUTER
= CONNECTED_COMMUTING_TWO_PERM_Z3_TERMINAL

CURRENT HARD-CORE ATTACK
= R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1
```

## PROVED CORE

For a connected linear cubic square incidence matrix `A` and conflict graph `G`:

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

Polynomial terminals already admitted:

```text
rank_Q(A)=n
=> BOOLEAN UNSAT.

nullity_Q(A)=O(log n)
=> exact 2^k poly(n,L) rational-kernel router is polynomial.

recognized one-edge-twist 2-lift tower
=> exact polynomial contraction to its root with witness reconstruction.

complete fixed-(c,B) Levi leaf decomposition
=> exact polynomial General-Factor / Exact-One decision and witness reconstruction.
```

## LEVI / DUAL / TWO-PERMUTATION NORMAL FORMS

For the cubic bipartite Levi graph `L(A)`:

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

After exact row normalization:

```text
A'=I+P+Q,
P,Q permutation matrices,
Ax=1 iff A'x=1,
nullity_Q(A')=nullity_Q(A).
```

If `p,q` are the corresponding permutations:

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

with local source-row multiset `(-1,-1,2)`.

## FROZEN PRIMITIVITY FALSIFIER

Explicit linear `12_3` normalized carrier:

```text
p=[9,4,6,1,10,8,7,2,0,5,11,3]
q=[3,8,4,5,0,11,10,1,7,6,9,2]
A=I+P+Q
rank_Q(A)=10
nullity_Q(A)=2
<p,q> transitive and primitive
unique Exact-One witness selects {0,1,6,11}
```

Therefore these shortcuts are false:

```text
singular => imprimitive
nullity_Q(A)>=2 => imprimitive
SAT + singular => imprimitive
{-1,2} kernel witness => imprimitive
```

The finite example does not refute an asymptotic theorem requiring `nullity_Q(A)=omega(log n)` plus extra hypotheses.

## FROZEN HOSTILE-DONOR REJECTION — KETTANI 2025

Every cubic square incidence matrix satisfies `A*1=3*1`. Hence if `A` is nonsingular, the unique rational solution of `Ax=1` is `(1/3)1`, not Boolean. The cyclic Fano `7_3` instance has full rational rank and zero Boolean Exact-One witnesses.

Thus

```text
det(A)!=0 => SAT
```

is false, and the correct terminal is

```text
rank_Q(A)=n => BOOLEAN UNSAT.
```

The donor's claimed bounded-treewidth theorem is also false: the 6-regular triangular torus family

```text
T_m = Cay(Z_m^2, {±(1,0), ±(0,1), ±(1,-1)})
```

is induced-`K1,4`-free, every vertex lies in six triangles, and `tw(T_m)>=m` via its ordinary `m x m` grid subgraph.

Freeze:

```text
FORBIDDEN_DONOR_ROUTE
= KETTANI_2025_BOUNDED_TREEWIDTH_CUBIC_MONOTONE_1IN3
```

## RANK-1 STITCHED `TD(3,3)` THEOREM

One `TD(3,3)` block has rational rank `7`, nullity `2`. Chaining `m` copies by the proved degree-preserving rank-one incidence 2-switch leaves a connected square cubic linear carrier `A_m` with

```text
n=9m
rank_Q(A_m)=8m-1
nullity_Q(A_m)=m+1=n/9+1.
```

So `Theta(n)` rational nullity can arise from small singular modules plus rank-1 stitching, not only from OET lifts.

Each module boundary is a 2-edge Levi cut, so this is not a separator-resistant high-nullity obstruction.

## EXACT LEVI CUT COMPOSITION — PROVED

For any Levi cut `V=S disjoint_union T` with crossing edge set `D=delta(S)`, an exact boundary state is

```text
y in {0,1}^D,
```

recording which cut factor edges are selected. Residual degree sets are obtained by subtracting the selected cut degree from `K(row)={1}` and `K(column)={0,3}`.

Exact composition:

```text
L has a valid factor
iff
exists y in {0,1}^D:
    FEAS(S,y) and FEAS(T,y).
```

Witness reconstruction is

```text
F = F_S union F_T union {e in D : y_e=1}.
```

Thus a cut of size `c` has exactly `2^c` boundary bit states.

For fixed constants `(c,B)`, recursively peeling connected modules of at most `B` Levi vertices behind cuts of size at most `c` is polynomial and exact. If the process stops on a larger root it returns `CORE`, never false UNSAT/hardness evidence.

The stitched `TD(3,3)` family is completely `(c=2,B=18)` peelable. Its direct witness transfer automaton is

```text
X -> Y or Z
Y -> X
Z -> Y or Z
```

with witness count `F_{m+3}`.

## NEW EXACT TERMINAL — CONNECTED COMMUTING TWO-PERMUTATION BRANCH

Assume a valid normalized connected carrier

```text
A=I+P+Q
```

has

```text
PQ=QP.
```

Then `Gamma=<p,q>` is transitive abelian and therefore regular. Identify coordinates with `Gamma`. Over `C`, the regular representation has character eigenbasis and

```text
lambda_chi = 1 + chi(p) + chi(q).
```

For unit complex numbers `u,v`,

```text
1+u+v=0
iff
(u,v)=(omega,omega^2) or (omega^2,omega),
omega^3=1, omega!=1.
```

Since `p,q` generate `Gamma`, a character is uniquely determined by `(chi(p),chi(q))`. Therefore at most two characters lie in the kernel, and conjugation makes the nullity even. Rank/nullity is unchanged by field extension `Q -> C`.

Hence

```text
PQ=QP and connected
=> nullity_Q(I+P+Q) in {0,2}.
```

The branch is completely decided:

```text
nullity=0
=> BOOLEAN UNSAT.

nullity=2
=> SAT with exactly three Exact-One witnesses.
```

In the `nullity=2` case there is a homomorphism

```text
phi: Gamma -> Z_3
phi(p)=1, phi(q)=2
```

or the conjugate orientation. Every source triple `{g,pg,qg}` contains the three colors `0,1,2` exactly once, so each color class is an Exact-One witness.

A direct deterministic solver does not need Fourier arithmetic: try the two orientations

```text
+ : c(p(i))=c(i)+1, c(q(i))=c(i)+2 mod 3
- : c(p(i))=c(i)+2, c(q(i))=c(i)+1 mod 3
```

and propagate on `p,q,p^-1,q^-1`. Connectedness makes this `O(n)` after normalization. Neither orientation consistent means UNSAT; a consistent orientation yields all three witnesses.

Exact controls:

```text
Fano 7_3:
  commuting, connected, linear
  rank=7, nullity=0
  Exact-One witnesses=0.

TD(3,3) 9_3:
  commuting, connected, linear
  rank=7, nullity=2
  Exact-One witnesses=3.
```

Scope ceiling: this closes a given valid commuting normalization. It does NOT prove that all possible three-matching normalizations can be searched/canonicalized for a commuting one in polynomial time.

## UPDATED HARD RESIDUAL — THREE EQUIVALENT SURFACES

### Hoffman surface

```text
6-regular conflict graph
+ source-edge partition into triangles
+ lambda_min=-3
+ multiplicity(-3)=omega(log n)
+ no recognized OET quotient
+ survives admitted fixed-(c,B) Levi leaf-peel routers
+ find Hoffman coclique of size n/3 or certify none.
```

### Two-permutation surface

For the currently chosen valid normalization:

```text
A'=I+P+Q
+ <p,q> transitive
+ linear triple condition
+ dim_Q ker(I+P+Q)=omega(log n)
+ PQ != QP
+ no recognized OET quotient
+ Levi carrier survives admitted fixed-(c,B) leaf-peel routers
+ decide whether ker(I+P+Q) intersects {-1,2}^n.
```

### Levi-factor surface

```text
connected cubic bipartite Levi graph of girth>=6
+ square color classes
+ high rational nullity of its biadjacency matrix
+ no recognized OET quotient
+ separator-resistant to admitted fixed-(c,B) leaf peeling
+ not solved by the current commuting normalization terminal
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
18. treat the stitched TD33 family as an irreducible hard family;
19. claim fixed-(c,B) leaf peeling exhausts all small/balanced separators;
20. commute in one normalization => all normalizations commute;
21. failure of current normalization to commute => carrier has no commuting normalization;
22. claim P=NP from any special-carrier theorem without the full E8 contract.
```

## NEXT GATE

```text
R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1
```

Frozen question:

Given a linear connected normalized carrier

```text
A=I+P+Q,
Gamma=<p,q> transitive,
PQ != QP,
nullity_Q(A)=omega(log n),
no recognized OET quotient,
Levi graph survives all currently admitted fixed-(c,B) leaf-peel routers,
```

find the next exact structural cause of large nullity or a direct polynomial terminal.

Admissible material outcomes:

```text
A. prove a polynomial nullity bound for an explicitly certified noncommuting separator-resistant class;
B. construct an asymptotic noncommuting separator-resistant family with omega(log n) nullity;
C. prove large nullity forces another recognizable exact quotient/decomposition;
D. generalize the commuting terminal to a rigorously bounded nonabelian/near-commuting class;
E. extend exact separator composition to another polynomially searchable width regime;
F. prove a direct polynomial Exact-One terminal for the remaining high-nullity core.
```

Do not assume `primitive` from OET-irreducibility, and do not use permutation-group primitivity as a proxy for Levi structural irreducibility.

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

RANK1-STITCHED TD33 THEOREM
= 3b5e6fc63899b4e852d592779a172c0890542c5a

RANK1-STITCHED TD33 CHECKER
= 300424ce867764e0afaade7ea20aa3ef43d242f0

EXACT LEVI CUT / LEAF-PEEL ROUTER THEOREM
= 83463a0eeeb96ea037126ecb8f0911c87fa04f13

SEPARATOR COMPOSITION CHECKER
= d506bb51324fd6e0d7cd90ca33a62b595e5e5ac7

COMMUTING TWO-PERM EXACT TERMINAL THEOREM
= ba8ae11ef7e1bf03e13ea2c8220d28591ec588de

COMMUTING TWO-PERM TERMINAL CHECKER
= 9f37b4757442630e69566e0fbddf8e4921162e15

COMMUTING TWO-PERM CI
= b482f59a29a1e243af53eac9d8408ece15224297

CURRENT SCIENTIFIC FRONTIER
= R5_E9_NONCOMMUTING_SEPARATOR_RESISTANT_HIGH_NULLITY_GATE_V1

D1
= EMPTY

P_VS_NP
= OPEN
```
