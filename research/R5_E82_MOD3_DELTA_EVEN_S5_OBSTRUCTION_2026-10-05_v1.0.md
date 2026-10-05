# R5 E82 — Mod-3 Boundary Conservation, Universal Delta-Evenness, and S5 Obstruction Reduction

Date: 2026-10-05

Status:
`RXC3_EXACT_DELTA_INTERFACES_ARE_ALWAYS_EVEN__NONBINARY_FRONTIER_REDUCES_TO_S5`

Scientific ceiling:

```text
E82 PROVES A UNIVERSAL STRUCTURAL THEOREM FOR EVERY EXACT
ExactOne_3 / Equality_3 TANNER INTERFACE.

IT DOES NOT RESTORE THE STATIC PARTITION CONJECTURE FALSIFIED BY E81.
IT DOES NOT YET EXCLUDE THE FINAL S5 NONBINARY OBSTRUCTION.
IT DOES NOT CONSTRUCT A UNIVERSAL POLYNOMIAL SOLVER.

P_VS_NP = OPEN.
```

## 1. Exact signed boundary conservation

Take an arbitrary Tanner cluster `M`.  Let

```text
C = included ExactOne_3 check vertices,
V = included Equality_3 variable vertices.
```

Its cut incidences split canonically into

```text
partial_C M = cut edges incident inside M with a check vertex,
partial_V M = cut edges incident inside M with a variable vertex.
```

Let a local satisfying extension select the internal variable set

```text
Y subseteq V,
```

and let `I` be the number of selected **internal** Tanner edges.

Every selected Equality_3 variable has all three incident edge bits equal to one.
Thus counting selected incidences at included variable vertices gives

```text
3 |Y| = I + |F cap partial_V M|.          (1)
```

Every included ExactOne_3 check has exactly one selected incident edge.  Counting
selected incidences at included checks gives

```text
|C| = I + |F cap partial_C M|.            (2)
```

Subtracting (2) from (1):

```text
boxed:
|F cap partial_V M| - |F cap partial_C M|
    = 3|Y| - |C|.
```

Therefore every exact feasible boundary state satisfies the affine congruence

```text
boxed:
|F_V| - |F_C| == -|C|  (mod 3).
```

No assumption of source linearity, C4-freeness, satisfiability, bounded size, or
delta-matroid structure is used.  The identity follows only from the primitive
arity-three Equality / ExactOne semantics.

## 2. Distance-one boundary moves are impossible

Give each variable-side boundary coordinate weight `+1` and each check-side
coordinate weight `-1` in `GF(3)`.

All feasible boundary sets have the same weighted sum.

If two feasible boundary states differed in exactly one coordinate, their signed
sums would differ by either `+1` or `-1` modulo three.  This contradicts the
conservation law.

Hence for **every** exact Tanner boundary relation on this route:

```text
boxed:
there are no two feasible sets X,Y with |X xor Y| = 1.
```

This statement holds even when the boundary relation is not a delta-matroid.

## 3. Abstract delta-matroid lemma: odd implies a distance-one pair

Let `D=(E,F)` be a delta-matroid that is not even.  Then there exist feasible
sets of opposite parity.  Choose `X,Y in F` for which

```text
|X xor Y|
```

is odd and minimum.

Pick `e in X xor Y`.  By symmetric exchange there exists

```text
f in X xor Y
```

such that

```text
Z = X xor {e,f}
```

is feasible, where `f=e` is allowed.

If `f != e`, both coordinates lie in `X xor Y`, hence

```text
|Z xor Y| = |X xor Y| - 2.
```

This is a smaller odd feasible-pair distance, contradicting minimality.
Therefore

```text
f=e,
```

and

```text
X xor {e}
```

is feasible.

Thus:

```text
boxed:
EVERY ODD DELTA-MATROID CONTAINS TWO FEASIBLE SETS AT DISTANCE ONE.
```

Equivalently, a delta-matroid without a distance-one feasible pair is even.

## 4. Universal RXC3 delta-evenness theorem

Combine Sections 2 and 3.

Every exact `ExactOne_3 / Equality_3` Tanner boundary relation has no feasible
pair at distance one.  Therefore, whenever such a boundary relation satisfies
Bouchet symmetric exchange, it must be even.

```text
boxed:
RXC3 EXACT BOUNDARY + DELTA-MATROID
    =>
EVEN DELTA-MATROID.
```

This is universal.  It closes the `RXC3 DELTA-EVENNESS LEMMA` left open by E80.

The result is stronger than the q=6/q=8/q=9/q=10 finite observations: those
catalogues were not accidentally even.  Evenness is forced by the primitive
three-incidence conservation law plus symmetric exchange.

## 5. Signed-mod-3 property is twist/minor closed

Define property `P_3` for a set system `D=(E,F)`:

```text
there exist weights w_e in {+1,-1} subset GF(3)
and c in GF(3) such that
sum_{e in X} w_e = c
for every X in F.
```

Every exact Tanner boundary relation has `P_3` by Section 1.

### Twist

For a twist by `T`, a coordinate indicator transforms as

```text
x_e -> x_e            if e notin T,
x_e -> 1 - x_e        if e in T.
```

Thus twisting flips the sign of `w_e` on `T` and changes only the affine
constant.  The new weights remain in `{+1,-1}`.

Therefore `P_3` is twist invariant.

### Deletion / contraction

Deletion restricts a coordinate to zero and removes it.  Contraction restricts a
coordinate to one and removes it (equivalently twist then delete).  In either
case the remaining weights stay `+/-1` and only the constant may change.

Hence `P_3` is preserved by delta-matroid minors.

It is also invariant under coordinate relabelling.

## 6. Bouchet-Duchamp binary excluded-minor theorem

Bouchet and Duchamp characterize binary delta-matroids over `GF(2)` by five
minimal forbidden delta-matroids.  A delta-matroid is binary iff it has no minor
isomorphic to a twist of

```text
S1, S2, S3, S4, S5.
```

Reference:

* A. Bouchet and A. Duchamp,
  *Representability of Delta-matroids over GF(2)*,
  Linear Algebra and its Applications 146 (1991), 67–78,
  DOI `10.1016/0024-3795(91)90020-W`.

Use the standard representatives

```text
S1 = { empty, 12,13,23,123 }
S2 = { empty, 1,2,3,12,13,23 }
S3 = { empty, 2,3,12,13,123 }
S4 = { empty, 12,13,14,23,24,34 }
S5 = { empty, 12,14,23,34,1234 }.
```

## 7. Signed-mod-3 filter on the five excluded minors

Because `P_3` is twist/minor closed, any excluded minor of an exact RXC3 boundary
delta-matroid must itself admit a signed `+/-1` mod-3 affine invariant.

The companion checker exhausts all `2^3` or `2^4` sign vectors.

Results:

```text
S1 : no P_3 weighting
S2 : no P_3 weighting
S3 : no P_3 weighting
S4 : no P_3 weighting
S5 : exactly two, differing by global sign:
     (+,-,+,-),
     (-,+,-,+),
     affine constant 0.
```

Therefore:

```text
boxed:
IF AN EXACT RXC3 BOUNDARY DELTA-MATROID IS NONBINARY,
THEN ITS BOUCHET-DUCHAMP EXCLUDED-MINOR CERTIFICATE MUST BE
A TWIST OF S5.
```

The four other minimal nonbinary obstruction families are impossible on this
route.

This is a universal obstruction reduction, not finite evidence.

## 8. Relation to E79 / projected-linear representations

E79 showed that on all frozen q=6 and q=9 delta catalogues the relations are
binary even and reconstructed from one feasible seed plus pair flips.  E80
extended this to all 1,845 q=10 delta interfaces; E81 found all 200 q=8 delta
interfaces binary even as well.

After E82 the finite evidence becomes:

```text
q=6  :   99/99 binary even
q=8  :  200/200 binary even
q=9  :  412/412 binary even
q=10 : 1845/1845 binary even
TOTAL : 2556/2556
```

and universal theory says that **evenness is no longer conjectural**.  The only
remaining question in binary representability is the `S5` obstruction.

Note also that Koana-Wahlstrom explicitly observe that in characteristic two,
symmetric representations with nonzero diagonal correspond to projected-linear
delta-matroids.  E82 makes that odd/projected fallback unnecessary for raw RXC3
delta interfaces because those interfaces are always even, although projected
operations can still be useful in a recursive decomposition.

## 9. Interaction with E81

E82 does not rescue the static partition route.

E81 proves that the q=8 Tanner graph has no disjoint exact delta-module vertex
partition at all, even though every delta module it does possess is binary even.

So two issues are now cleanly separated:

```text
REPRESENTATION OF A DELTA INTERFACE:
    much narrower; only S5 can obstruct binary representability.

GLOBAL EXISTENCE OF A STATIC DELTA PARTITION:
    false by E81.
```

The next route must therefore use a recursive/overlapping/elimination object,
not simply search harder for a static partition.

## 10. New killer-test

The representation-side killer-test is now exact:

```text
S5 REALIZABILITY TEST

Can any exact boundary relation of an ExactOne_3/Equality_3 Tanner cluster,
after boundary conditioning/deletion/contraction/twist, realize S5?
```

A proof of impossibility would establish:

```text
RXC3 exact boundary + delta
    => binary even.
```

A concrete S5 realization would falsify the remaining binary conjecture while
leaving E82 evenness intact.

Independently, the algorithmic route must pass the E81 q=8 regression using a
non-static recursive representation scheme.

## 11. Companion replay

```text
experiments/r5_e82_mod3_delta_even_s5_obstruction.py
```

It verifies:

```text
* exact signed mod-3 conservation on all nonempty connected boundary relations
  in frozen q=6, q=8, and q=9 controls;
* every delta relation in those exhaustive catalogues is even;
* no delta boundary relation contains a distance-one feasible pair;
* S1-S4 admit no +/-1 signed mod-3 invariant;
* S5 admits exactly the two alternating sign invariants.
```

Scientific status:

```text
E82 = PROVED UNIVERSAL RXC3 DELTA-EVENNESS
      + PROVED BINARY EXCLUDED-MINOR REDUCTION TO S5.

S1-S4_NONBINARY_OBSTRUCTIONS = EXCLUDED.
S5_OBSTRUCTION = OPEN.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED (E81).
RECURSIVE/OVERLAPPING REPRESENTED DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
