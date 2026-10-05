# R5 E79 — Binary Reconstruction and Uniform Matchgate Firewall

Date: 2026-10-05

Status:
`E77_DELTA_CATALOGUES_ARE_BINARY_EVEN__REPRESENTATION_RECOVERS_FROM_PAIR_FLIPS__UNIFORM_HOLOGRAPHIC_BASIS_SHORTCUT_BLOCKED`

Scientific ceiling:

```text
E79 DOES NOT PROVE A UNIVERSAL LINEAR-DELTA DECOMPOSITION.

IT REMOVES ONE CONSTRUCTIBILITY SUBGAP ON THE BINARY-EVEN LANE:
ONCE A MODULE IS KNOWN TO BE BINARY EVEN, A FEASIBLE SEED PLUS PAIR-FLIP
MEMBERSHIP ACCESS DETERMINES ITS GF(2) REPRESENTATION IN O(b^2) QUERIES.

THE UNIVERSAL PARTITION, A UNIVERSAL BINARY/LINEARITY THEOREM, AND A
POLYNOMIAL LOCAL-EXTENSION ORACLE ARE STILL OPEN.

P_VS_NP = OPEN.
```

## 1. Verified starting point

The live R5 route before E79 is E78, not E77.

E77 established source-aligned delta modules on the RXC3 quotient, including

```text
F = {5,17},
F * 5 = {0,20},
```

and the exact E53 product lift.  Its q=9 square-cubic-linear control found six
first nontrivial size-14 two-state delta relations and exact min-max complete
partitions of sizes

```text
q=6 : 1,1,10,
q=9 : 1,1,1,15.
```

E78 then proved the exact equality-gluing identity

```text
GLOBAL CONSISTENCY
iff
F_1 xor ... xor F_s = empty,
```

so a polynomially constructible represented linear-delta decomposition is a
sufficient randomized-polynomial solver criterion.

E79 asks a narrower question:

```text
IF a boundary relation is already known to be binary even,
how much extra information is actually needed to construct its matrix?
```

The answer is only one feasible seed and the pair-flip membership table.

## 2. Literature audit relevant to the global theorem

### 2.1 Linear and projected-linear delta-matroids

Koana and Wahlström, *Faster Algorithms on Linear Delta-Matroids*, STACS 2025,
LIPIcs 327, Article 62, DOI `10.4230/LIPIcs.STACS.2025.62`, use skew-symmetric
matrix representations and prove:

```text
* every linear delta-matroid is even;
* union and delta-sum preserve linearity;
* represented delta-sums admit randomized O(n^omega)-field-operation
  construction;
* projected-linear delta-matroids admit elementary-projection representations;
* several fundamental optimization/feasibility problems reduce to matrix rank.
```

A crucial qualification is that their composition construction produces an
`epsilon`-approximate representation: no false feasible set is introduced, and
each true feasible set survives with probability at least `1-epsilon`.
Therefore the E78 use is randomized/bounded-error, not an unqualified exact
deterministic matrix-construction theorem.

### 2.2 Delta composition

Bouchet/Cunningham composition glues two delta-matroids by requiring equality
on their common ground and taking symmetric difference outside it.  This is the
abstract operation behind E78's equality-cancellation identity.  See:

* A. Bouchet and W. H. Cunningham,
  *Delta-Matroids, Jump Systems, and Bisubmodular Polyhedra*,
  SIAM J. Discrete Math. 8 (1995), 17–32,
  DOI `10.1137/S0895480191222926`;
* A. Bouchet and W. Schwärzler,
  *The delta-sum of matching delta-matroids*,
  Discrete Mathematics 181 (1998), 53–63,
  DOI `10.1016/S0012-365X(97)00044-7`.

These closure statements do not supply the missing universal RXC3 module
partition.

### 2.3 Binary representation is locally recoverable around a feasible set

Bouchet and Duchamp characterize representability over `GF(2)`:

* A. Bouchet and A. Duchamp,
  *Representability of delta-matroids over GF(2)*,
  Linear Algebra and its Applications 146 (1991), 67–78,
  DOI `10.1016/0024-3795(91)90020-W`.

For a normal binary delta-matroid, feasible sets of size at most two determine
the binary representation.  Equivalently, after twisting an arbitrary binary
delta-matroid by any feasible set, the representing binary symmetric matrix is
read off from membership in the radius-two feasible neighborhood.

For the **even** case relevant to Koana-Wahlström linear delta-matroids, the
diagonal is zero, and this simplifies to a particularly sharp reconstruction
lemma proved below.

### 2.4 Edge-CSP alternative

Kazda, Kolmogorov and Rolínek,
*Even Delta-Matroids and the Complexity of Planar Boolean CSPs*, show a
polynomial algorithm for Boolean edge-CSP where every variable occurs in
exactly two constraints and every constraint is an even delta-matroid relation
**represented by an explicit list of tuples**.

This is structurally close to E78 because every Tanner cut edge occurs in
exactly two module boundary relations.  However, an explicit tuple list may be
exponential in boundary arity, whereas a matrix can represent exponentially
many feasible sets.  Thus this theorem gives a genuine alternative sufficient
route, but it does not replace the compact-representation problem.

### 2.5 Matchgates / Pfaffians

Cai and Gorenstein, *Matchgates Revisited*, Theory of Computing 10 (2014),
167–197, DOI `10.4086/toc.2014.v010a007`, prove that the Matchgate Identities
are necessary and sufficient for planar matchgate signatures and that the MGI
imply the parity condition.  This makes a single global holographic basis an
obvious shortcut worth testing.  Section 7 below proves that this shortcut
fails already on the primitive `ExactOne_3` / `Equality_3` pair over
characteristic different from 2 and 3.

### 2.6 Branch-width / parse-tree machinery

Hliněný's parse-tree theorem builds finite local descriptions for matroids that
are already representable over a fixed finite field and have bounded
branch-width:

* P. Hliněný, *Branch-width, parse trees, and monadic second-order logic for
  matroids*, JCTB 96 (2006), 325–351,
  DOI `10.1016/j.jctb.2005.08.005`.

Hliněný-Oum and later work construct branch/rank decompositions for represented
objects when a fixed width bound exists.  Oum's skew/symmetric matrix rank-width
results similarly assume bounded rank-width.  None of these theorems says that
arbitrary RXC3/E12 hard targets have bounded width or manufactures a
linear-delta representation from the ExactOne/Equality CSP itself.

### 2.7 Result of the sweep

No theorem located in the targeted literature proves any of the following
unconditionally for arbitrary E12/RXC3 hard targets:

```text
* existence of a polynomial-size linear-delta module decomposition;
* existence of bounded/sublinear branch or rank width;
* polynomial construction of the exact module boundary representations;
* a universal matchgate/Pfaffian basis for ExactOne_3 + Equality_3.
```

So the global decomposition implication remains a real theorem gap rather than
a missed standard result.

## 3. E79-A — binary-even near-seed reconstruction lemma

Let

```text
D = (B,F)
```

be an even binary delta-matroid over `GF(2)`, let `|B|=b`, and let `S in F`.
Twist by `S`:

```text
D' = D * S.
```

Then `empty` is feasible in `D'`.  Since `D` is binary, there exists a binary
symmetric matrix `A` such that

```text
D' = D(A).
```

Because `D` is even, `D'` has no feasible singleton.  Hence every diagonal
entry is zero:

```text
A_ii = 0.
```

For `i != j`, the principal `2 x 2` submatrix is

```text
[ 0     A_ij ]
[ A_ij  0    ].
```

Over `GF(2)`, its determinant is `A_ij`.  Therefore

```text
boxed:
A_ij = 1
iff
{i,j} is feasible in D'
iff
S xor {i,j} is feasible in D.
```

So the entire matrix is determined by exactly the pair-flip membership table
around one feasible set.

### Constructive form

Given:

```text
1. one feasible seed S;
2. a membership procedure for S xor {i,j}, for every pair i<j,
```

we construct the unique zero-diagonal binary matrix in

```text
O(b^2)
```

membership calls and `O(b^2)` additional work.

This is not an assumption that membership is free.  It cleanly identifies what
must still be made efficient by a global structural theorem.

## 4. E79-B — stronger replay of every E77 delta cluster

E77 tested symmetric exchange and exhibited explicit linear representations for
its first nontrivial relations.  E79 applies the reconstruction above to the
**entire** E77 delta catalogues.

### Frozen q=6

E79 re-enumerates all connected source clusters and obtains the frozen count

```text
99 delta-support clusters.
```

For every one of the 99 relations:

```text
* all feasible boundary sets have one parity;
* twist by a feasible seed is even and normal;
* the pair-flip table constructs a zero-diagonal GF(2) matrix;
* exhaustive principal-minor replay regenerates the entire feasible family.
```

Hence all 99 are not merely delta-matroids: they are **binary even**, therefore
linear in the skew/zero-diagonal GF(2) sense relevant to this route.

### Linear q=9 control

The same replay is applied independently to all

```text
412
```

connected delta-support clusters in the C4-free q=9 source.  Again all 412 are
binary even and regenerate exactly from their reconstructed GF(2) matrices.

This strengthens E77 on its frozen finite controls:

```text
E77: all counted objects satisfy delta exchange.
E79: every counted delta object on q=6 and q=9 is actually compactly
     representable over GF(2).
```

It is **not** yet a theorem that every delta-support cluster of every RXC3
source is binary.

## 5. Frozen regressions

### 5.1 Canonical q=6 source-aligned cluster

E77's family is

```text
F = {5,17}.
```

Using seed `5` gives

```text
F * 5 = {0,20}.
```

Mask `20` activates coordinates `{2,4}`.  E79 reconstructs exactly one binary
matrix edge

```text
(2,4),
```

so the direct principal-minor family is exactly `{0,20}`.

### 5.2 E53 lift

For the exact product lift `F x F`, twisting by `(5,5)` reconstructs exactly

```text
(2,4), (7,9),
```

two disjoint `2 x 2` blocks, reproducing the E77 explicit E53 representation.

### 5.3 q=9 first nontrivial relations

All six size-14/two-state q=9 relations reconstruct to exactly one nonzero
binary off-diagonal pair after twisting, agreeing with E77's one-block
representation argument.

### 5.4 Complete E77 partitions

The optimal E77 partitions remain

```text
q=6 : [1,1,10],
q=9 : [1,1,1,15].
```

E79 reconstructs a binary-even representation for **every module in both
partitions**, not just the illustrative nontrivial cluster.

Thus on these two finite controls, E78's representation premise is completely
satisfied at the input-module level.

## 6. Minimal missing theorem after E79

E78 stated a sufficient theorem whose premise directly outputs represented
linear-delta modules.  On the binary-even lane E79 weakens that premise.

A sufficient global statement is now:

```text
GLOBAL BINARY-DELTA CONSTRUCTIBILITY THEOREM

For every E12 hard target, equivalently its exact RXC3 source quotient,
construct in polynomial time a Tanner-vertex partition M_1,...,M_s such that
for every exact projected boundary relation D_t=(B_t,F_t):

A. D_t is an even binary delta-matroid;
B. one feasible seed S_t in F_t is produced;
C. all pair-flip extension questions
       S_t xor {i,j} in F_t
   can be answered in polynomial TOTAL time.
```

Then E79 reconstructs all module matrices using

```text
sum_t O(|B_t|^2)
```

pair queries, and E78 + Koana-Wahlström composes them by delta-sum to decide
global feasibility in randomized polynomial time with a standard polynomial
error budget.

This separates three notions that must not be conflated:

```text
EXISTENCE:
    some linear/binary representation exists.

IDENTIFICATION:
    enough local boundary membership information is available to recover it.

EFFICIENT CONSTRUCTION:
    the partition, seed, and required membership information are all obtained
    in polynomial total time.
```

Existence alone is insufficient.

For projected-linear but non-even relations, the binary pair-reconstruction
lemma does not apply; that lane still requires an explicit projected-linear
representation or another constructive theorem.

## 7. E79-C — uniform holographic-basis obstruction

The literature sweep suggests one possible escape: perhaps a single invertible
`2 x 2` holographic basis transforms both primitive ternary signatures into
matchgate signatures globally, eliminating the need for clustering.

E79 rules out that shortcut over every field of characteristic different from
`2` and `3`.

Let

```text
B = [ a b ]
    [ c d ]
```

with

```text
ad-bc != 0.
```

Apply `B` on each of the three legs.  Because both primitive signatures are
symmetric, write transformed values by Hamming weight `0,1,2,3`.

For `ExactOne_3`:

```text
f0 = 3 c a^2
f1 = d a^2 + 2 a b c
f2 = c b^2 + 2 a b d
f3 = 3 d b^2.
```

For `Equality_3`:

```text
g0 = a^3 + c^3
g1 = a^2 b + c^2 d
g2 = a b^2 + c d^2
g3 = b^3 + d^3.
```

The Matchgate Identities imply the parity condition, so `f` itself must have
support on only one parity.

### Case 1 — transformed ExactOne has odd parity

Then

```text
f0=f2=0.
```

Since characteristic is not `3`, `f0=0` gives `c=0` or `a=0`.
If `a=0`, invertibility gives `b,c != 0`, but then `f2=c b^2 != 0`, a
contradiction.  Hence `c=0`.

Invertibility now gives `a,d != 0`.  Since characteristic is not `2`,
`f2=2abd=0` forces `b=0`.  Thus `B` is diagonal.

But then

```text
g0=a^3 != 0,
g3=d^3 != 0,
```

so transformed Equality has nonzero entries of both parities and cannot be a
matchgate signature.

### Case 2 — transformed ExactOne has even parity

Then

```text
f1=f3=0.
```

The symmetric argument gives `d=0`, then `a=0`; hence `B` is anti-diagonal.
But now

```text
g0=c^3 != 0,
g3=b^3 != 0,
```

again violating parity.

Therefore

```text
boxed:
NO SINGLE INVERTIBLE 2x2 BASIS SIMULTANEOUSLY TRANSFORMS
ExactOne_3 AND Equality_3 INTO MATCHGATE-PARITY SIGNATURES
OVER char != 2,3.
```

The companion checker exhaustively confirms the formula/case outcome over
`GF(5), GF(7), GF(11), GF(13)`.

This does **not** rule out:

```text
* characteristics 2 or 3;
* module-dependent basis changes with compatible interfaces;
* clustered Pfaffian/matchgate representations;
* E77/E79 binary GF(2) delta modules.
```

So it is an anti-loop against the strongest uniform-basis shortcut, not a
barrier to the active decomposition route.

## 8. Branch-width is conditional, not global

The Hliněný/Oum parse-tree machinery becomes algorithmically valuable if a
bounded-width represented object is already available.  The current controls do
not justify extrapolating such a bound: E77's exact min-max delta partitions are
near-global (`10/12` and `15/18`).

Those two finite values do not prove unbounded width, but they do reject the
claim that the existing evidence already implies a bounded-radius/local
partition theorem.

## 9. New frontier

The representation-search problem has split cleanly:

```text
CLOSED ON FROZEN E77 CONTROLS:
    delta-support => binary-even for all 99 + 412 catalogued clusters;
    all module matrices recover exactly from one seed + pair flips.

PROVED GENERALLY FOR THE BINARY-EVEN LANE:
    representation recovery from seed + pair-flip membership is O(b^2).

REFUTED SHORTCUT:
    one global holographic basis cannot matchgate-realize both primitive
    signatures over char !=2,3.

OPEN:
    universal polynomial construction of a suitable partition;
    universal theorem that every needed exact boundary relation is binary/linear;
    polynomial total-time generation of seeds and pair-flip extension answers;
    projected-linear fallback if even binary fails.
```

Scientific status:

```text
E79 = PROVED CONSTRUCTIBILITY-REDUCTION LEMMA
      + VERIFIED BINARY-EVEN STRENGTHENING OF ALL E77 q6/q9 DELTA CLUSTERS
      + PROVED UNIFORM MATCHGATE-BASIS FIREWALL (char !=2,3).

GLOBAL_LINEAR_DELTA_DECOMPOSITION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACT_ONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
```

## 10. Companion replay

```text
experiments/r5_e79_binary_reconstruction_matchgate_firewall.py
```

It verifies:

```text
* q=6: all 99 E77 connected delta-support clusters are even binary;
* q=9: all 412 E77 connected delta-support clusters are even binary;
* every reconstructed GF(2) matrix regenerates the entire exact family;
* E77 F={5,17}, twist {0,20};
* exact E53 two-block lift;
* all six q=9 first nontrivial size-14 relations;
* every module in the E77 optimal q6/q9 full partitions;
* exhaustive no-uniform-parity-basis regressions over GF(5,7,11,13).
```

### Next killer-test

Do not search another representation theorem first.  Attack the only empirical
step that could collapse the frontier:

```text
E80 BINARY-DELTA UNIVERSALITY ATTACK
```

Generate source-aligned connected square-cubic-linear RXC3 controls beyond q=9
(prefer high-girth / expander-like q=10,11,12 instances), enumerate or
branch-and-bound their exact connected boundary relations, and search for the
first relation satisfying symmetric exchange but failing the Bouchet-Duchamp
binary reconstruction test.

One witness would kill the conjecture

```text
RXC3 exact boundary + delta exchange => binary even.
```

If no witness appears, simultaneously measure the exact min-max complete
binary-delta partition size.  Growth toward `2q-O(1)` would attack bounded-local
construction; a uniformly bounded/sublinear pattern would support a genuine
global decomposition conjecture.
