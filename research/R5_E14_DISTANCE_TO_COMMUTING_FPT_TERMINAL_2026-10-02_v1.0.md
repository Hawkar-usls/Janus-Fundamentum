# R5 E14 — Distance-to-Commuting FPT Terminal

Date: 2026-10-02

Status:
`EXACT_FPT_TERMINAL__POLYNOMIALLY_COMPUTABLE_DISTANCE_TO_CENTRALIZER__O(2^(3t)_POLY_N)`

Scientific ceiling:

```text
THIS NOTE EXTENDS THE R5 E13 COMMUTING TERMINAL TO INSTANCES
THAT ARE CLOSE TO A COMMUTING PERMUTATION PAIR.

THE PARAMETER t IS COMPUTABLE IN POLYNOMIAL TIME FOR A FIXED NORMAL FORM A=I+P+Q.
IF t=O(log n), THE RESULTING EXACT ALGORITHM IS POLYNOMIAL.

THIS DOES NOT BOUND t FOR GENERAL NP-HARD INSTANCES.
P_VS_NP = OPEN.
```

## 1. Input normal form

Let a square cubic Exact-One source be written after a 3-perfect-matching decomposition as

```text
A = I + P + Q,
```

where `P,Q` are permutation matrices.

R5 E13 completely solves the case `PQ=QP`.

We now measure how far `Q` is from the centralizer of `P`.

## 2. Distance to the centralizer

Define

```text
C(P) = {R permutation : RP=PR}
```

and

```text
t = min_{R in C(P)} d_H(Q,R),
```

where

```text
d_H(Q,R) = |{i : Q(i) != R(i)}|.
```

Let `Q0` attain the minimum, and set

```text
A0 = I + P + Q0.
```

Then `P,Q0` commute, so R5 E13 applies to `A0`.

## 3. Computing Q0 in polynomial time

The centralizer structure of a permutation is explicit.

Decompose `P` into directed cycles.  A permutation `R` commutes with `P` iff it maps every `P`-cycle to another `P`-cycle of the same length and, inside the chosen target cycle, acts by a cyclic shift preserving the `P` orientation.

Fix a cycle length `ell` and two `P`-cycles

```text
C=(c_0,...,c_{ell-1}),
D=(d_0,...,d_{ell-1}),
```

where `P(c_r)=c_{r+1}` and similarly for `D`.

For each shift `s`, the commuting map from `C` to `D` is

```text
c_r -> d_{r+s mod ell}.
```

Give the ordered pair `(C,D)` weight

```text
w(C,D) = max_s |{r : Q(c_r)=d_{r+s}}|.
```

For all `P`-cycles of a fixed length, choose a bijection from source cycles to target cycles maximizing total weight.  This is a maximum-weight bipartite assignment problem and is polynomial-time solvable.  Retain the best shift for every chosen cycle pair.

Perform this independently for every cycle length.

The resulting permutation `Q0` commutes with `P` and maximizes the number of agreements with `Q`; therefore it minimizes `d_H(Q,Q0)` exactly.

So `t` is not an existential parameter requiring exponential search: it is computable in polynomial time for the chosen `I+P+Q` representation.

## 4. Defect set and commuting orbits

Let

```text
D = {i : Q(i) != Q0(i)},
|D|=t.
```

Decompose the index set into orbits under the commuting group `<P,Q0>`.

Call an orbit active if it contains a point of `D`.

Every inactive orbit is also closed under the original `Q`, because on all of its points `Q=Q0`.  Hence the original matrix `A` restricts there exactly to the commuting matrix `A0`, and R5 E13 solves that component in linear time.

### Lemma: defect images stay in active orbits

If `i in D` and `v=Q(i)`, let

```text
j = Q0^{-1}(v).
```

If `j` were not in `D`, then

```text
Q(j)=Q0(j)=v=Q(i),
```

contradicting injectivity of `Q`, unless `j=i`; but `j=i` would imply `Q0(i)=Q(i)`, contradicting `i in D`.

Therefore `j in D`.

Since `j` and `v=Q0(j)` lie in the same `<P,Q0>` orbit, the target `Q(i)` of every defect edge lies in an active orbit.

Thus the union `W` of active orbits is closed under all of

```text
I, P, Q0, Q.
```

So `A_W` is a square independent subinstance.

Also, because every active orbit contains at least one defect point,

```text
number of active orbits <= t.
```

## 5. Nullity bound on the active core

On each commuting orbit, R5 E13 proves

```text
nullity_Q(I+P+Q0) <= 2.
```

If there are at most `t` active orbits, then

```text
nullity_Q((A0)_W) <= 2t.
```

Now `A_W` differs from `(A0)_W` only in the rows indexed by `D`.
Therefore

```text
rank(A_W - (A0)_W) <= t.
```

For matrices of the same size,

```text
rank(A_W) >= rank((A0)_W) - t.
```

Equivalently,

```text
nullity_Q(A_W)
<= nullity_Q((A0)_W) + t
<= 3t.
```

Hence

```text
boxed:  nullity_Q(A_active) <= 3t.
```

## 6. Exact FPT algorithm

Algorithm for a fixed permutation normal form `A=I+P+Q`:

```text
1. Compute the nearest Q0 in C(P) by cycle matching + cyclic shifts.
2. Let D={i:Q(i)!=Q0(i)}, t=|D|.
3. Decompose <P,Q0> into orbits.
4. Every inactive orbit:
     solve by the R5 E13 commuting Z3 propagation terminal.
     If any is UNSAT -> global UNSAT.
5. Let W be the union of active orbits.
6. Compute exact rational row reduction of A_W.
7. Its nullity d satisfies d<=3t.
8. Enumerate the 2^d Boolean assignments to free coordinates,
   reconstruct pivot coordinates exactly,
   and test A_W x=1.
9. Combine an active-core witness with witnesses on inactive orbits.
```

Running time:

```text
O(2^(3t) poly(n)).
```

The algorithm is exact: every SAT result reconstructs a Boolean witness and every UNSAT result exhausts the complete rational solution space of the only unresolved active component.

## 7. Polynomial corollary

If

```text
t = O(log n),
```

then

```text
2^(3t) = n^O(1),
```

so the entire instance is decidable in deterministic polynomial time.

Thus all square cubic instances that are logarithmically close, in this precise computable sense, to the centralizer of one permutation matching are in P.

## 8. Representation dependence

A square cubic incidence graph may have multiple 3-perfect-matching decompositions and hence multiple normal forms `I+P+Q`.

The parameter `t` above is defined for a fixed normal form.  Therefore a practical router may try several cheaply available decompositions and retain the smallest certified `t`, but this note does not claim that globally minimizing `t` over all 1-factorizations is polynomial.

The theorem needs only one decomposition with small `t` to terminate the instance.

## 9. Frozen-control observation

The existing R5 E9 singular PG15_UNSAT normal form has a strongly noncommuting displayed pair `P,Q`; all 15 indices violate the local equality `PQ(i)=QP(i)`, and its nearest-centralizer distance for that fixed `P` is not small enough to improve on the already superior rational-nullity terminal (`d=1`).

This is expected and useful: the router chooses the cheapest exact terminal per instance rather than forcing every instance through the commuting branch.

## 10. New universal frontier

The current hard core can now be required to evade all of:

```text
full-rank rejection,
small rational nullity,
clique-LP rejection,
exact commuting structure,
logarithmic distance to a commuting permutation normal form.
```

For an unresolved hard family, every useful normal form must therefore exhibit genuine extensive noncommutativity while also maintaining a large rational kernel.

The next high-value question is a dichotomy of the form

```text
large nullity
=>
small distance-to-commuting
OR
another polynomially detectable obstruction/decomposition.
```

Proving such a statement with an `O(log n)` threshold would produce a polynomial router for the NP-complete linear class of R5 E12 and hence imply `P=NP`.

That implication is a target, not a claimed result.

P_VS_NP = OPEN.
