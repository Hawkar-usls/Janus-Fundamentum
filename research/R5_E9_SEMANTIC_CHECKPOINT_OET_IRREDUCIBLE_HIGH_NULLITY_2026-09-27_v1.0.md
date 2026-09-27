# R5 E9 — Semantic Checkpoint: OET-Irreducible High-Nullity Residual

Date: 2026-09-27

Checkpoint status:
`SYNCHRONIZED_AFTER_MATERIAL_THEOREM`

Purpose: this file is the compact restart surface for a new chat or a new proof-search process. It records only theorem-level state, explicit prohibitions, and the next admissible gate.

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

## OPEN RESIDUAL

The remaining targeted carrier is now exactly expressible as either of the following equivalent surfaces.

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

Open literature confirms that the generic representation is not a free polynomial donor:

- bipartite General Factor remains NP-hard in the singleton-list setting; the standard `{1}/{0,3}` case is a known hard General-Factor pattern;
- existence of a parallel class is NP-complete for general partial Steiner triple systems;
- these facts are hardness warnings only and are NOT imported as a proof of hardness for the stricter regular high-nullity OET-irreducible JANUS residual.

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
10. assume high nullity => imprimitive permutation group;
11. assume OET-irreducible => primitive permutation group;
12. claim P=NP from any special-carrier theorem without the full E8 contract.
```

## NEXT GATE

Primary attack:

```text
R5_E9_HIGH_NULLITY_TWO_PERM_STRUCTURE_ATTACK_V1
```

Question:

Given

```text
A'=I+P+Q,
Gamma=<p,q> transitive,
linear row-triple system,
nullity_Q(A')=omega(log n),
OET quotient absent,
```

prove or falsify a polynomial structural split based on permutation-group block systems / exact quotients.

Admissible progress is one of:

```text
A. PROVE a recognizable nontrivial block system yields an exact dimension-dropping quotient with polynomial witness reconstruction;
B. PROVE high nullity forces such a quotient under additional explicitly checked hypotheses;
C. BUILD a primitive high-nullity counterfamily, thereby killing the naive block-system route;
D. PROVE a polynomial terminal for the primitive residual;
E. import a source-proved theorem that exactly applies to this stricter carrier.
```

The first immediate falsification test is intentionally conservative:

```text
DO NOT try to prove high-nullity => imprimitive first.
Search for primitive singular/high-nullity examples under the exact linearity constraints.
A finite counterexample kills the naive implication; an asymptotic theorem requires proof.
```

## RESTART RECEIPT

```text
LAST MATERIAL THEOREM
= LEVI GENERAL-FACTOR / DUAL MATCHING / TWO-PERMUTATION NORMAL FORM

THEOREM COMMIT
= 667eb0743f6440f363bbd62e3043240bc189833f

EXECUTABLE REGRESSION COMMIT
= dd4d1b587d0b7d902d356c0b3abe75f137ada2d5

CURRENT SCIENTIFIC FRONTIER
= OET-IRREDUCIBLE HIGH-NULLITY TWO-PERMUTATION / HOFFMAN RESIDUAL

D1
= EMPTY

P_VS_NP
= OPEN
```
