# R5 E83 — Canonical Matroid Twist Theorem and U2,4 Frontier

Date: 2026-10-05

Status:
`EVERY_EXACT_TANNER_DELTA_INTERFACE_IS_CANONICALLY_A_MATROID_TWIST__NONBINARY_FRONTIER_IS_U24`

Scientific ceiling:

```text
E83 PROVES A UNIVERSAL CLASSIFICATION THEOREM FOR EXACT
ExactOne_3 / Equality_3 BOUNDARY RELATIONS THAT SATISFY DELTA EXCHANGE.

IT DOES NOT EXCLUDE U_{2,4} ON SQUARE-CUBIC-LINEAR SOURCES.
IT DOES NOT REPAIR THE STATIC PARTITION THEOREM FALSIFIED BY E81.
IT DOES NOT PROVE P=NP.

P_VS_NP = OPEN.
```

## 1. Starting point: the E82 signed conservation law

For any Tanner cluster `M`, split its boundary coordinates into

```text
P = variable-side boundary incidences,
N = check-side boundary incidences.
```

For every feasible exact boundary state `F`, E82 proved the integer identity

```text
phi(F)
 := |F cap P| - |F cap N|
  = 3 |Y_F| - |C|,
```

where `Y_F` is any internal selected-variable extension and `C` is the set of
included ExactOne checks.

In particular

```text
phi(F) == -|C| (mod 3)
```

for every feasible `F`.

E82 used this modulo-three statement to prove that if the exact boundary relation
is a delta-matroid, then it is even.

E83 upgrades the congruence to an **exact integer invariant** under the delta
hypothesis.

## 2. Lemma — distance-two feasible moves preserve phi exactly

Let `F` and `F'` be feasible boundary states with

```text
|F xor F'| = 2.
```

Each toggled coordinate changes `phi` by either `+1` or `-1`.  Therefore

```text
phi(F') - phi(F) in {-2,0,2}.
```

But E82 gives the same residue modulo three to every feasible state, hence

```text
phi(F') - phi(F) == 0 (mod 3).
```

The only integer in `{-2,0,2}` divisible by three is zero.  Thus

```text
boxed:
|F xor F'|=2 and F,F' feasible
=>
phi(F')=phi(F).
```

## 3. Lemma — every two feasible states of an even delta-matroid are connected by distance-two feasible moves

Let `D=(E,F)` be an even delta-matroid and let `X,Y in F`.

If `X != Y`, choose

```text
e in X xor Y.
```

By symmetric exchange there exists

```text
f in X xor Y
```

such that

```text
X' = X xor {e,f}
```

is feasible.

Because the delta-matroid is even, `f=e` is impossible: that would change the
parity of the feasible-set cardinality.  Hence `e != f`, and since both lie in
`X xor Y`, toggling them removes both from the symmetric difference:

```text
|X' xor Y| = |X xor Y| - 2.
```

Iterating produces a feasible path

```text
X=X_0, X_1, ..., X_t=Y
```

with

```text
|X_i xor X_{i+1}|=2
```

at every step.

## 4. Universal exact signed-balance theorem

Now let the exact Tanner boundary relation be a delta-matroid.

E82 makes it even.  By Section 3, all feasible states lie in one graph connected
by distance-two feasible moves.  By Section 2, `phi` is exactly preserved on
every such move.

Therefore there is an integer `k` such that

```text
boxed:
|F cap P| - |F cap N| = k
for EVERY feasible boundary state F.
```

Combining with the primitive counting identity gives another interpretation:

```text
3|Y_F|-|C| = k.
```

Hence every local extension of every feasible boundary state uses the same
number of selected internal variable vertices.

This is strictly stronger than the E82 modulo-three conservation law.

## 5. Canonical matroid twist theorem

Twist the boundary relation by the **entire variable-side boundary ground** `P`.
For any feasible `F`,

```text
|F xor P|
 = |P| - |F cap P| + |F cap N|
 = |P| - k.
```

So every feasible set of

```text
D * P
```

has exactly the same cardinality.

Twist preserves the delta-matroid symmetric-exchange axiom.  An equicardinal
delta-matroid is exactly a matroid in its basis presentation.

Therefore:

```text
boxed:
CANONICAL MATROID TWIST THEOREM

For every exact ExactOne_3 / Equality_3 Tanner boundary relation D,
if D is a delta-matroid, then

    M(D) := D * P

is a matroid,

where P is the set of all variable-side boundary coordinates.
```

No search for a twist is necessary.  The twist is supplied canonically by the
Tanner orientation itself.

This theorem does **not** require source linearity or C4-freeness.

## 6. Relation to the fundamental-graph theorem

For an even delta-matroid, the fundamental graph at a feasible set has an edge
`uv` exactly when toggling `u,v` preserves feasibility.  E82's signed invariant
forces every such pair to have opposite signed boundary orientation after the
corresponding twist.  Hence the fundamental graph is bipartite.

This agrees with the classical theorem that an even delta-matroid with a
bipartite fundamental graph is a twist of a matroid.  E83 is stronger for this
route because it identifies the twist explicitly: **all variable-side boundary
coordinates**.

## 7. Binary representability is now an ordinary matroid question

A delta-matroid is binary iff any/every matroid twist obtained from it is binary.
Thus for exact Tanner delta interfaces:

```text
D binary
iff
M(D)=D*P is a binary matroid.
```

By Tutte's classical excluded-minor theorem, a matroid is binary iff it has no
`U_{2,4}` minor.

This is the matroid version of E82's Bouchet-Duchamp reduction to `S5`:

```text
S5 * P  <->  U_{2,4}.
```

So the representation-side frontier is now simply:

```text
CAN THE CANONICAL BOUNDARY MATROID M(D)
OF A SQUARE-CUBIC-LINEAR RXC3 CLUSTER
CONTAIN U_{2,4} AS A MINOR?
```

## 8. Explicit S5 / U2,4 witness outside the linear-source class

The remaining obstruction cannot be excluded using only the primitive
ExactOne/Equality semantics.

E83 gives the connected 6-check / 6-variable internal incidence graph with
edges

```text
(0,1) (0,3) (0,4)
(1,0) (1,2) (1,5)
(2,0) (2,4)
(3,1) (3,3) (3,4)
(4,1) (4,5)
(5,0) (5,2) (5,5).
```

There are exactly four boundary stubs: two check-side followed by two
variable-side coordinates.

Its exact boundary family is

```text
{0,5,6,9,10,15}.
```

This is a twist/isomorphic copy of Bouchet-Duchamp `S5`.

The canonical variable-side boundary mask is

```text
P = 12 = 1100_2.
```

Twisting gives

```text
{3,5,6,9,10,12},
```

which is precisely **all six two-subsets of a four-element ground set**:

```text
U_{2,4}.
```

Thus the E83 theorem is exact: nonbinary exact Tanner delta interfaces really can
occur in the unrestricted Tanner class.

## 9. Why this witness does not attack the RXC3 hard-source lane

The 6x6 witness is not source-linear.  It contains Tanner four-cycles: several
pairs of internal variable vertices have two common included checks.

For example the checker records pairs such as

```text
variables 0 and 2 share two checks,
variables 0 and 5 share two checks,
variables 1 and 3 share two checks,
...
```

Therefore it cannot occur as an induced cluster of the square-cubic-linear
RXC3 sources used on the E12 hard route.

Source linearity is now seen to be an essential hypothesis for any attempted
universal binary theorem.

## 10. Finite C4-free evidence

The frozen exact source-aligned catalogues remain:

```text
q=6  :   99/99 canonical boundary matroids binary
q=8  :  200/200 canonical boundary matroids binary
q=9  :  412/412 canonical boundary matroids binary
q=10 : 1845/1845 canonical boundary matroids binary
```

In additional direct arity-four stress tests, no `S5/U2,4` interface occurs in
the complete C4-free balanced 6+6 or 7+7 four-boundary topology catalogues.
These are finite controls only and are not promoted to theorem status here.

## 11. Impact on the decomposition route

E83 sharply separates three statements:

```text
A. IF an exact interface is delta, its structure is canonically matroidal.
   PROVED.

B. On square-cubic-linear RXC3 sources, every such canonical matroid is binary
   (or at least efficiently representable over one compatible field).
   OPEN; U2,4 is the exact binary obstruction.

C. Every whole hard target admits a static disjoint delta-interface partition.
   FALSE by E81.
```

Therefore proving B alone will not establish a polynomial solver.  The global
algorithm still needs a recursive/overlapping/elimination decomposition that
survives the E81 q=8 counterexample.

## 12. Next killer-tests

Two independent fronts are now exact.

### Representation killer-test

```text
U24-LINEARITY TEST

Either realize a U_{2,4} minor in the canonical boundary matroid of a
C4-free square-cubic-linear RXC3 cluster, or prove source linearity excludes it.
```

A proof of exclusion gives a universal binary-representation theorem for every
RXC3 exact delta interface.

### Global algorithm killer-test

```text
E81 RECURSIVE DECOMPOSITION TEST

Construct a recursive composition/projection scheme for the q=8 source that
never assumes a static disjoint delta partition and keeps every represented
intermediate interface polynomially bounded.
```

Both are necessary before any P=NP claim can be considered.

## 13. Companion replay

```text
experiments/r5_e83_canonical_matroid_twist_u24_frontier.py
```

It verifies:

```text
* all 99 q=6, 200 q=8, and 412 q=9 delta interfaces have exactly constant phi;
* canonical twist by variable-side boundary coordinates is equicardinal;
* the twisted families satisfy ordinary matroid basis exchange;
* the explicit nonlinear 6x6 Tanner cluster has S5 boundary support;
* its canonical twist is exactly U_{2,4};
* the witness contains Tanner C4s and is outside the linear-source class.
```

Scientific status:

```text
E83 = PROVED CANONICAL MATROID TWIST THEOREM.
GENERAL_TANNER_U24 = REALIZABLE.
LINEAR_RXC3_U24 = OPEN.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED (E81).
RECURSIVE REPRESENTED DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
