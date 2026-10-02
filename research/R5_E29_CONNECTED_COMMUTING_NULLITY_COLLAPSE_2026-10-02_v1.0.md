# R5 E29 — Connected Commuting Nullity Collapse

Date: 2026-10-02

Status:
`EXACT_CONNECTED_COMMUTING_NULLITY_BOUND__SINGULAR_SECTOR_HAS_THREE_PROJECTIVE_CLASSES__HIGH_Q_REQUIRES_NONCOMMUTATIVITY_OR_DECOMPOSITION`

Scientific ceiling:

```text
FOR EVERY CONNECTED COMMUTING CARRIER

  A = I + P + Q,
  PQ = QP,

THE RATIONAL NULLITY IS AT MOST TWO.

MORE PRECISELY,

  nullity_Q(A) in {0,2}.

IN THE SINGULAR CASE THE KERNEL IS THE REAL/RATIONAL FORM OF ONE
CUBE-ROOT CHARACTER PAIR AND THE KERNEL COORDINATE ROWS FALL INTO
EXACTLY THREE PROJECTIVE CLASSES OF EQUAL SIZE n/3.

THEREFORE A CONNECTED HIGH-NULLITY OR HIGH-PROJECTIVE-DIVERSITY
SURVIVOR CANNOT LIVE IN THE COMMUTING SECTOR.

THIS SHARPENS THE POST-E28 FRONTIER BUT DOES NOT PROVE P=NP.
P_VS_NP = OPEN.
```

## 1. Setting

Let `P,Q` be permutations of the same finite set `Omega`, with

```text
PQ=QP.
```

Consider

```text
A = I + P + Q.
```

Assume the corresponding Exact-One source is connected.
Because identity incidences identify row and variable labels, connectedness is
equivalent to transitivity of the permutation group

```text
H=<P,Q>
```

on `Omega`.

Since `P` and `Q` commute, `H` is abelian.

## 2. A transitive abelian action reduces to a regular abelian quotient

Fix a point `omega in Omega` and let

```text
K = Stab_H(omega).
```

Because `H` is abelian, every point stabilizer equals `K`; in particular `K` is the
kernel of the action.

Therefore the faithful action is the regular translation action of the finite
abelian quotient

```text
G = H/K
```

on itself.

Let

```text
p,q in G
```

be the images of `P,Q`.  Since `H` acts transitively,

```text
G=<p,q>.
```

Thus the connected commuting carrier is Fourier-diagonalizable by the characters
of the finite abelian group `G`.

## 3. Character eigenvalues

For every complex character

```text
chi : G -> C^*,
```

the corresponding Fourier vector is a simultaneous eigenvector of `P` and `Q`:

```text
P -> chi(p),
Q -> chi(q).
```

Hence its `A`-eigenvalue is

```text
lambda_chi = 1 + chi(p) + chi(q).
```

Because `G` is finite, `chi(p)` and `chi(q)` lie on the complex unit circle.

The only way three unit complex numbers

```text
1, u, v
```

can sum to zero is that they are the three cube roots of unity.  Therefore

```text
lambda_chi=0
```

if and only if

```text
{chi(p),chi(q)} = {omega,omega^2},
```

where

```text
omega^3=1,
omega != 1.
```

## 4. At most two zero characters

Since `p,q` generate `G`, a character of `G` is completely determined by the pair

```text
(chi(p),chi(q)).
```

There are only two ordered zero-eigenvalue possibilities:

```text
(omega,omega^2),
(omega^2,omega).
```

Therefore over `C`

```text
nullity_C(A) <= 2.
```

Because `A` has rational entries,

```text
rank_Q(A)=rank_C(A),
```

so

```text
boxed:
nullity_Q(A) <= 2.
```

A one-dimensional rational kernel cannot occur here.  Any nonreal zero character
appears together with its complex conjugate, and the two displayed zero-character
possibilities are conjugate to one another.

Hence

```text
boxed:
nullity_Q(A) in {0,2}.
```

## 5. Singular case: exactly three kernel-projective classes

Assume now

```text
nullity_Q(A)=2.
```

Let `chi` be the zero character with

```text
chi(p)=omega,
chi(q)=omega^2.
```

Because `p,q` generate `G`, the image of `chi` is exactly

```text
{1,omega,omega^2}.
```

The complex kernel is spanned by `chi` and its conjugate.  Taking real and imaginary
parts gives a real two-dimensional kernel model.

At coordinate `g in G`, the kernel coordinate functional is represented by the
phase

```text
chi(g) in {1,omega,omega^2}.
```

Thus there are exactly three possible coordinate-row directions in the
basis-invariant projective row matroid of the kernel.

No two of the three cube-root phase vectors are real/rational scalar multiples of
one another, so they form three distinct projective classes.

Therefore

```text
boxed:
q=3.
```

## 6. Equal class sizes

The character `chi` is a surjective homomorphism

```text
G -> C_3.
```

Its kernel has index three.  Hence each of the three character values occurs on
exactly

```text
|G|/3 = n/3
```

coordinates.

Therefore the singular connected commuting carrier has projective-class sizes

```text
boxed:
n/3, n/3, n/3.
```

In particular `3|n` automatically in the singular case.

## 7. Relation to the toroidal controls

The R5 E10/E25 toroidal family is the standard example:

```text
G = Z_k x Z_k,
p=(1,0),
q=(0,1).
```

When `3|k`, exactly the two conjugate cube-root characters vanish, giving

```text
nullity_Q=2
```

and the three residue classes

```text
i-j mod 3
```

are exactly the three kernel-projective classes.

When `3` does not divide the relevant character quotient, the carrier is full
rational rank.

Thus the familiar torus behavior is not accidental: it is forced throughout the
entire connected commuting sector.

## 8. Consequence for the universal router

R5 E13 already gives an exact polynomial algorithm for commuting carriers.
E29 adds a sharper structural reason why the commuting branch can never contain the
post-E28 high-description hard core.

For a connected source,

```text
commuting
=>
nullity_Q <= 2
=>
q <= 3.
```

Therefore any survivor satisfying

```text
effective nullity = omega(log n)
```

or

```text
q = omega(log n)
```

must be outside the connected commuting sector.

Equivalently, a future high-q/high-PQ-width firewall must be genuinely
noncommutative, not merely a disguised abelian translation family.

## 9. Disconnected caveat

If `<P,Q>` has several orbits, each orbit is an independent commuting component and
may contribute its own zero-character pair.  Large total nullity can then be
obtained by taking many components.

That is not a counterexample to the theorem: it is exactly the decomposition branch
already present in the JANUS router.

So the correct statement is specifically

```text
CONNECTED + COMMUTING
=>
nullity_Q in {0,2} and q in {0,3}.
```

## 10. Updated high-description frontier

After E28 and E29, a genuine survivor must now be sought among carriers with all of

```text
connected,
genuinely noncommuting,
large effective nullity,
large projective diversity q,
large certified projective-quotient width,
no bounded-interface decomposition,
no KPROJ/KLOC reduction,
integer feasibility,
no source-aligned/clique obstruction,
and no compact known trade normal form.
```

This removes the entire connected abelian/commuting translation world from the
high-description hunt.

The next firewall target is therefore:

```text
NONCOMMUTATIVE HIGH-q / HIGH-PQ-WIDTH CARRIER REALIZATION.
```

```text
P_VS_NP = OPEN.
```

Companion finite checker:

```text
experiments/r5_e29_connected_commuting_nullity_collapse.py
```
