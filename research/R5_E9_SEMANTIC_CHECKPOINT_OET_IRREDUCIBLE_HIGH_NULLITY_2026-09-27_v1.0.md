# R5 E9 — Semantic Checkpoint: OET-Irreducible High-Nullity Residual

Date: 2026-09-27

Checkpoint status:
`SYNCHRONIZED_AFTER_MATERIAL_FALSIFIER`

Purpose: compact restart surface for a new chat or proof-search process. It records theorem-level state, falsified shortcuts, explicit prohibitions, and the next admissible gate.

## LIVE SCIENTIFIC STATE

```text
P_VS_NP = OPEN
E8_D1 = EMPTY

UNIVERSAL POLYNOMIAL SAT / EXACT-ONE DECIDER = NOT PROVED

AUTHORITATIVE RESIDUAL GATE
= R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1
```

## PROVED

### Spectral / conflict-graph bridge

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

### Existing polynomial terminals

```text
rank_Q(A)=n
=> UNSAT.

nullity_Q(A)=O(log n)
=> exact 2^k poly(n,L) rational-kernel router is polynomial.

recognized one-edge-twist 2-lift tower
=> exact polynomial contraction to its root with witness reconstruction.
```

### Levi / dual exact forms

Let `L(A)` be the cubic bipartite Levi graph.

```text
Ax=1
iff
L(A) has General Factor with
  K(row)={1},
  K(column)={0,3}.
```

Dualizing the incidence structure:

```text
Ax=1
iff
selected dual 3-edges form a perfect matching / parallel class.
```

### Two-permutation normal form

Every cubic square carrier is polynomially decomposable into three disjoint perfect matchings of its Levi graph:

```text
A = P0 + P1 + P2.
```

After exact row normalization:

```text
A' = I + P + Q,
P,Q permutation matrices,
Ax=1 iff A'x=1,
nullity_Q(A')=nullity_Q(A).
```

If `p,q` are the corresponding permutations, then:

```text
L(A) connected
iff
<p,q> acts transitively on [n].
```

For the linear carrier, the row triples

```text
{i,p(i),q(i)}
```

have distinct entries and no unordered pair appears twice.

The kernel law is

```text
z_i + z_{p(i)} + z_{q(i)} = 0 for every i.
```

An Exact-One witness is the special kernel vector

```text
w=3x-1 in {-1,2}^n,
```

and every normalized source triple carries exactly the local multiset

```text
(-1,-1,2).
```

## MATERIAL FALSIFIER NOW FROZEN

An explicit normalized linear `12_3` carrier is fixed by

```text
p = [9,4,6,1,10,8,7,2,0,5,11,3]
q = [3,8,4,5,0,11,10,1,7,6,9,2]
A = I + P + Q.
```

Exact checks give

```text
rank_Q(A)=10
nullity_Q(A)=2
<p,q> transitive
<p,q> primitive
Exact-One witness exists and is unique:
  selected columns {0,1,6,11}.
```

Primitivity is certified without third-party algebra software: in degree 12, every nontrivial block containing 0 must have size in `{2,3,4,6}`; all 693 candidates are exhaustively rejected under the orbit action of `p,q,p^-1,q^-1`.

Therefore the following implications are now mathematically false and must not be revisited:

```text
singular => imprimitive
nullity_Q(A)>=2 => imprimitive
SAT + singular => imprimitive
{-1,2} kernel witness => imprimitive
```

This finite falsifier does NOT refute an asymptotic theorem requiring `nullity_Q(A)=omega(log n)` plus additional structure.

## OPEN RESIDUAL

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
+ linear triple condition on {i,p(i),q(i)}
+ dim_Q ker(I+P+Q)=omega(log n)
+ no recognized OET quotient
+ decide whether ker(I+P+Q) intersects {-1,2}^n.
```

### Levi-factor surface

```text
connected cubic bipartite Levi graph of girth >= 6
+ square color classes
+ high rational nullity of its biadjacency matrix
+ no recognized OET quotient
+ General Factor degree sets {1}/{0,3}.
```

## EXTERNAL ANTI-LOOP

Open literature confirms that the generic representations are not free polynomial donors:

- bipartite General Factor remains NP-hard in the singleton-list setting; `{1}/{0,3}` is a standard hard General-Factor pattern;
- existence of a parallel class is NP-complete for general partial Steiner triple systems;
- neither source is imported as an NP-hardness proof for the stricter regular high-nullity OET-irreducible JANUS residual.

Relevant sources:
- Gutin et al., Algorithmica 64(1), 112–125 (2012), DOI `10.1007/s00453-011-9548-8`, preprint `https://arxiv.org/abs/1106.3527`.
- Li & Toulouse, Ars Combinatoria 80 (2006), 45–51.

## FORBIDDEN / DO NOT LOOP

```text
1. generic maximum-independent-set oracle;
2. enumerate the -3 eigenspace when multiplicity is superlogarithmic;
3. lambda_min=-3 => SAT;
4. round an arbitrary -3 eigenvector into {-1,2};
5. generic LP feasibility (x=1/3 * 1 is always a fractional solution);
6. relax kernel equations to unrestricted GF(3) and call that Exact-One;
7. call General Factor / dual perfect matching itself a solver;
8. infer exact regular-carrier NP-hardness from general partial-STS hardness;
9. reuse the OET high-nullity tower as an irreducible counterfamily;
10. singular => imprimitive;
11. nullity>=2 => imprimitive;
12. SAT or {-1,2} kernel witness => imprimitive;
13. assume OET-irreducible => primitive;
14. claim P=NP from any special-carrier theorem without the full E8 contract.
```

## NEXT GATE

Primary attack remains

```text
R5_E9_HIGH_NULLITY_TWO_PERM_STRUCTURE_ATTACK_V1
```

but the naive block-system route has been narrowed.

Given

```text
A'=I+P+Q,
Gamma=<p,q> transitive,
linear row-triple system,
nullity_Q(A')=omega(log n),
OET quotient absent,
```

admissible next progress is now one of:

```text
A. find an asymptotically scalable invariant tying large nullity to an exact quotient/decomposition;
B. prove a block-system theorem only with additional explicit hypotheses not falsified by the 12_3 primitive example;
C. construct a primitive family with unbounded/superlogarithmic rational nullity, killing the broader block-system route;
D. prove an upper bound on nullity for primitive linear two-permutation carriers strong enough to force a quotient in the hard branch;
E. prove a polynomial terminal directly for the primitive high-nullity residual;
F. import a source-proved theorem that applies exactly to this stricter carrier.
```

Most promising immediate mathematical target:

```text
PRIMITIVE NULLITY GROWTH QUESTION

For linear transitive A=I+P+Q with <p,q> primitive,
how large can nullity_Q(A) be as a function of n?
```

A theorem `primitive => nullity_Q(A)=O(log n)` would close the primitive side immediately by the existing kernel router. A primitive family with `nullity_Q(A)=omega(log n)` would falsify that route and force a different invariant. No such theorem is currently assumed.

## RESTART RECEIPT

```text
LAST MATERIAL THEOREM
= LEVI GENERAL-FACTOR / DUAL MATCHING / TWO-PERMUTATION NORMAL FORM
THEOREM COMMIT
= 667eb0743f6440f363bbd62e3043240bc189833f

NORMAL-FORM REGRESSION COMMIT
= dd4d1b587d0b7d902d356c0b3abe75f137ada2d5

LAST MATERIAL FALSIFIER
= PRIMITIVE LINEAR 12_3 CARRIER WITH nullity_Q=2 AND SAT WITNESS
FALSIFIER NOTE COMMIT
= e779c827866f2947a02db9fc2c54b853df0490d4
FALSIFIER CHECKER COMMIT
= 374fc406865909e8c3b9788c104f0a34a8cd9e32
CI WIRING COMMIT
= e21328ab452c34d3a4f25dbd9b056cf6469963b6

CURRENT SCIENTIFIC FRONTIER
= PRIMITIVE NULLITY GROWTH INSIDE OET-IRREDUCIBLE HIGH-NULLITY RESIDUAL

D1
= EMPTY

P_VS_NP
= OPEN
```
