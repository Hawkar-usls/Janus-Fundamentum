# R5 — Uniform Holographic Basis Firewall in Characteristics 2 and 3

Date: 2026-10-10

Status:
E79_CHARACTERISTIC_2_3_LOOPHOLE_CLOSED

P_VS_NP = OPEN.

## 0. Starting point

E79 proved that no single invertible 2x2 basis simultaneously transforms the
primitive ternary signatures

    ExactOne_3 = {100,010,001}
    Equality_3 = {000,111}

into matchgate-parity signatures over fields of characteristic different from
2 and 3.

The proof deliberately left characteristics 2 and 3 open because it divided by
2 and 3.

This checkpoint closes exactly those two remaining characteristics.

For arity three, matchgate parity is a necessary condition: a transformed
signature must vanish on either all even-Hamming-weight inputs or all
odd-Hamming-weight inputs. It is therefore enough to show that no invertible
basis makes BOTH primitive signatures parity-supported.

## 1. Transformation formulas

Let

    B = [[a,b],[c,d]]

with determinant ad-bc nonzero.

As in E79, after applying B on all three legs, the symmetric transformed
ExactOne signature has Hamming-weight values

    f0 = 3 c a^2
    f1 = d a^2 + 2abc
    f2 = c b^2 + 2abd
    f3 = 3 d b^2.

The transformed Equality signature has

    g0 = a^3 + c^3
    g1 = a^2 b + c^2 d
    g2 = a b^2 + c d^2
    g3 = b^3 + d^3.

## 2. Characteristic 3

Modulo 3,

    f0=f3=0,
    f1=a(ad-bc),
    f2=-b(ad-bc).

Since det(B) != 0:

* ExactOne can have odd parity support only if b=0.
* ExactOne can have even parity support only if a=0.

### Case b=0

Invertibility gives a,d !=0. Then

    g0=a+c,
    g1=c^2 d,
    g2=c d^2,
    g3=d.

Because g3 !=0, Equality cannot have even parity support.
For odd parity support one needs g0=g2=0. But g2=0 forces c=0, after which
g0=a !=0.

Contradiction.

### Case a=0

Invertibility gives b,c !=0. Then

    g0=c,
    g1=c^2 d,
    g2=c d^2,
    g3=b+d.

Because g0 !=0, Equality cannot have odd parity support.
For even parity support one needs g1=g3=0. g1=0 forces d=0, after which
g3=b !=0.

Contradiction.

Hence no invertible basis works in characteristic 3.

## 3. Characteristic 2

There are exactly

    |GL(2,2)| = 6

invertible 2x2 matrices.

The companion checker enumerates all six exactly and evaluates the formulas
above modulo 2.

For every one of the six matrices, at least one of ExactOne_3 or Equality_3 has
nonzero entries on BOTH Hamming parities.

Therefore no invertible basis works in characteristic 2.

This is a complete finite proof.

## 4. Combined E79 strengthening

E79 already proves the same obstruction in every characteristic other than
2 and 3.

Together:

    boxed:
    NO FIELD CHARACTERISTIC ADMITS A SINGLE INVERTIBLE 2x2 BASIS THAT
    SIMULTANEOUSLY MAPS ExactOne_3 AND Equality_3 TO MATCHGATE-PARITY
    SIGNATURES.

This is stronger than a failed gadget search: parity support is necessary for
matchgate realizability, so the universal single-basis holographic shortcut is
closed over every field.

## 5. Algorithmic consequence

The desired TRIPLE->PAIR collapse cannot be a uniform one-basis holographic
transformation of the primitive Tanner language.

Any surviving pair/matching route must be genuinely nonlocal, module-dependent,
or use a state class strictly stronger than ordinary matchgate parity.

This does not exclude:

* nonuniform/module-dependent transformations;
* global cancellations coupling many constraints;
* non-matchgate linear-matroid-parity constructions;
* the SAT-admissible three-port extension route.

## Claim boundary

UNIFORM_HOLOGRAPHIC_BASIS_ALL_CHARACTERISTICS = REFUTED.
CHAR2_LOOPHOLE = CLOSED.
CHAR3_LOOPHOLE = CLOSED.
NONLOCAL_PAIR_COLLAPSE = OPEN.
THREE_PORT_EXTENDIBILITY = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
