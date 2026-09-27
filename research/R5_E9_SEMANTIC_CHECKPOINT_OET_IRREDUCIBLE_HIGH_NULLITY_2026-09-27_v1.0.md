# R5 E9 — Semantic Checkpoint: OET-Irreducible High-Nullity Residual

Date: 2026-09-27

Checkpoint status:
`SYNCHRONIZED_AFTER_HOSTILE_DONOR_REJECTION`

This is the canonical compact restart surface after the latest material mathematics.

## LIVE SCIENTIFIC STATE

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL POLYNOMIAL SAT / EXACT-ONE DECIDER = NOT PROVED

AUTHORITATIVE RESIDUAL GATE
= R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1

CURRENT ATTACK
= PRIMITIVE NULLITY GROWTH INSIDE THE OET-IRREDUCIBLE HIGH-NULLITY RESIDUAL
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
=> UNSAT.

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

Linearity becomes the triple condition on

```text
{i,p(i),q(i)}.
```

Kernel law:

```text
z_i+z_{p(i)}+z_{q(i)}=0 for every i.
```

Exact-One witness law:

```text
w=3x-1 in {-1,2}^n,
and every row triple has local multiset (-1,-1,2).
```

## FROZEN STRUCTURAL FALSIFIER

Explicit linear `12_3` normalized carrier:

```text
p=[9,4,6,1,10,8,7,2,0,5,11,3]
q=[3,8,4,5,0,11,10,1,7,6,9,2]
A=I+P+Q
```

Exact checks:

```text
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

## HOSTILE DONOR AUDIT — KETTANI 2025

Audited claim:

```text
Cubic Monotone 1-in-3 SAT is polynomial-time solvable
=> P=NP.
```

JANUS rejects this donor by two independent unconditional counterexamples.

### Failure A — nonsingular branch

Every cubic square incidence matrix satisfies

```text
A*1 = 3*1.
```

Hence if `A` is nonsingular,

```text
A^{-1}*1 = (1/3)*1,
```

which is not Boolean. Therefore the correct rule is

```text
rank_Q(A)=n => BOOLEAN UNSAT,
```

not SAT.

Explicit Fano `7_3` instance:

```text
row i = i+{0,1,3} mod 7
|det A|=24
unique rational solution=(1/3)1
Boolean Exact-One witnesses=0.
```

Thus the donor's `det(A)!=0` branch is falsified.

### Failure B — claimed treewidth theorem

The donor claims

```text
Delta<=6
+ induced-K1,4-free
+ every vertex in >=3 triangles
=> treewidth<=6.
```

Counterfamily for every `m>=5`:

```text
T_m = Cay(Z_m^2, {±(1,0), ±(0,1), ±(1,-1)}).
```

It is 6-regular, induced-`K1,4`-free, and every vertex belongs to six triangles. It contains the ordinary `m x m` grid as a subgraph after deleting edges, so

```text
tw(T_m) >= tw(P_m square P_m) = m.
```

Treewidth is therefore unbounded. The theorem as stated is false.

Freeze:

```text
FORBIDDEN_DONOR_ROUTE
= KETTANI_2025_BOUNDED_TREEWIDTH_CUBIC_MONOTONE_1IN3
```

The audit does not change the open frontier; it prevents a false shortcut from entering E8-D1.

## OPEN RESIDUAL — THREE EQUIVALENT SURFACES

### Hoffman surface

```text
6-regular conflict graph
+ source-edge partition into triangles
+ lambda_min=-3
+ multiplicity(-3)=omega(log n)
+ no recognized OET quotient
+ find Hoffman coclique of size n/3 or certify none.
```

### Two-permutation surface

```text
A'=I+P+Q
+ <p,q> transitive
+ linear triple condition
+ dim_Q ker(I+P+Q)=omega(log n)
+ no recognized OET quotient
+ decide whether ker(I+P+Q) intersects {-1,2}^n.
```

### Levi-factor surface

```text
connected cubic bipartite Levi graph of girth>=6
+ square color classes
+ high rational nullity of its biadjacency matrix
+ no recognized OET quotient
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
16. claim P=NP from any special-carrier theorem without the full E8 contract.
```

## NEXT GATE

```text
R5_E9_PRIMITIVE_NULLITY_GROWTH_GATE_V1
```

Question:

For linear transitive

```text
A=I+P+Q,
Gamma=<p,q> primitive,
OET quotient absent,
```

how large can

```text
nu_Q(A)=dim_Q ker(I+P+Q)
```

be as a function of `n`?

Material outcomes:

```text
A. prove primitive => nullity_Q(A)=O(log n), closing primitive side by the existing kernel router;
B. prove another polynomial nullity bound sufficient for the router after recursive decomposition;
C. construct a primitive family with nullity_Q(A)=omega(log n), falsifying this route;
D. show large nullity forces a different exact recognizable quotient/decomposition;
E. prove a direct polynomial terminal for the primitive high-nullity residual.
```

No asymptotic implication is currently assumed.

## RESTART RECEIPT

```text
TWO-PERM NORMAL-FORM THEOREM COMMIT
= 667eb0743f6440f363bbd62e3043240bc189833f

NORMAL-FORM CHECKER COMMIT
= dd4d1b587d0b7d902d356c0b3abe75f137ada2d5

PRIMITIVE NULLITY-2 FALSIFIER NOTE
= e779c827866f2947a02db9fc2c54b853df0490d4

PRIMITIVE NULLITY-2 CHECKER
= 374fc406865909e8c3b9788c104f0a34a8cd9e32

KETTANI-2025 HOSTILE-DONOR AUDIT
= 19b4f2724528d24ce0da61517c96d4a66657e7a2

KETTANI-2025 EXECUTABLE FALSIFIER
= bb47a3b19d2c39974afea71fbfc786f16a28f7d8

CI WITH ALL THREE R5-E9 CHECKERS
= de88fe45d8f5b061cb928c6fff70cdaf25cc964a

CURRENT SCIENTIFIC FRONTIER
= R5_E9_PRIMITIVE_NULLITY_GROWTH_GATE_V1

D1
= EMPTY

P_VS_NP
= OPEN
```
