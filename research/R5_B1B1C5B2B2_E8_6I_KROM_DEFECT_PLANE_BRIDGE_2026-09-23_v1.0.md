# R5 E8 6I — Krom Defect-Plane Bridge for Boolean Rank-One Minors

Date: 2026-09-23

Authority: JANUS_DERIVED_THEOREM__LOCAL_CLASSIFICATION_EXHAUSTIVE__POLY_SUBCLASS_BRIDGE__NO_D1_PROMOTION

Parents:

- R5_E8_6I_RAIL_MINOR_ABSORPTION_GATE_V1
- R5_B1B1C5B2B2_E8_6I_RAIL_BOOLEAN_RANK1_MINOR_OBSTRUCTION_BASIS_2026-09-23_v1.0.md
- R5_E9_KROM_AFFINE_HORN_PAIRWISE_BRIDGE_AUDIT_2026-09-23_v1.0.md

Scientific ceiling:

    D1       = EMPTY
    P_VS_NP  = OPEN
    P_EQ_NP  = NOT_PROVED

## 1. Local object

Fix one anchored multiplicative identity

    p = x y

over F_2.

Its exact Boolean graph is

    AND =
    {
      (0,0,0),
      (0,1,0),
      (1,0,0),
      (1,1,1)
    }
    subset F_2^3.

Let A be the current global affine over-approximation and let

    T = pi_{x,y,p}(A)

be its exact affine projection to this triple.

The local exact refinement is

    T cap AND.

The question is when that refinement is still affine, and what remains when
it is not.

---

## 2. Complete affine-context classification

### Theorem KDP-1

Among all affine subspaces T of F_2^3, the intersection

    T cap AND

is non-affine in exactly five cases:

1. T = F_2^3;
2. T is the plane p = 0;
3. T is the plane p = x;
4. T is the plane p = y;
5. T is the plane p = x + y + 1.

For every other affine T, T cap AND is empty or affine.

### Proof

An affine subspace of F_2^3 has size 1, 2, 4, or 8.

If |T| <= 2, then |T cap AND| <= 2. Empty sets represent contradiction,
singletons are affine, and every two-point set over F_2 is an affine line.

If |T| = 8, then T is the full cube. AND itself is not affine, since for
example

    (0,1,0) + (1,0,0) + (1,1,1)
    =
    (0,0,1)

is not in AND.

It remains to consider affine planes |T|=4. A subset of a four-point affine
plane is non-affine only when it has exactly three points. Therefore a hard
plane must contain exactly three of the four AND points.

There are exactly four such triples. Their affine hulls are:

    AND minus (1,1,1)  ->  p = 0
    AND minus (1,0,0)  ->  p = x
    AND minus (0,1,0)  ->  p = y
    AND minus (0,0,0)  ->  p = x + y + 1.

Each plane contains its three listed genuine AND points plus one spurious
point, so its intersection with AND has exactly three points and is
non-affine.

No other affine plane can have a non-affine intersection. QED.

The exhaustive checker independently enumerates all 51 affine subspaces of
F_2^3 and confirms that exactly these five contexts are non-affine.

---

## 3. Four hard planes are exactly four Krom clauses

Inside each of the four hard planes, the exact product identity becomes one
binary clause on x,y.

### Plane P00

    p = 0

Together with p=xy this is

    xy = 0

or equivalently

    not x OR not y.

### Plane P10

    p = x

Together with p=xy this is

    x = xy

or equivalently

    not x OR y.

### Plane P01

    p = y

Together with p=xy this is

    y = xy

or equivalently

    x OR not y.

### Plane P11

    p = x + y + 1

Together with p=xy this excludes only x=y=0 and is equivalent to

    x OR y.

Therefore the four maximal non-affine codimension-one defects are in
bijection with the four possible binary clauses on x,y.

This gives a finite compression currency:

    AFFINE DEFECT PLANE
    ->
    ONE KROM CLAUSE.

No selector variable is introduced.

---

## 4. Maximality of the local affine rule

For a given current affine projection T:

- if T cap AND is empty, the current global affine state is incompatible with
  the exact product constraint and the branch is UNSAT;
- if T cap AND is affine, add linear equations defining T cap AND exactly;
- if T is one of the four hard planes, retain the already implied plane
  equation and replace the remaining nonlinearity by its one Krom clause;
- if T=F_2^3, no exact same-triple affine or Krom-defect-plane reduction is
  obtained from local context alone.

Because every affine T is covered by Theorem KDP-1, this rule is complete for
all same-triple affine-context information.

The rule is polynomial: projection to three coordinates, enumeration of at
most eight tuples, affine-hull testing, and equation reconstruction are all
polynomial, in fact constant-size after Gaussian elimination of the global
affine system.

---

## 5. Affine Product Absorption Closure

Define APAC(A,E), where A is an affine relation and E is a set of identities

    p_e = x_e y_e.

Repeat:

1. compute the exact affine triple projection T_e for every unresolved e;
2. if T_e cap AND is empty, return UNSAT;
3. if T_e cap AND is affine and is a proper refinement of T_e, add its exact
   linear equations to A;
4. continue until no new affine equation is added.

Every successful affine absorption strictly shrinks the affine solution space,
so at most polynomially many independent linear equations can be added.
Gaussian elimination maintains the closure in polynomial time.

At the fixed point, every unresolved product is of one of only five local
types:

    FULL,
    p=0,
    p=x,
    p=y,
    p=x+y+1.

The four plane types are converted to Krom clauses. FULL is retained as a
separate unresolved global-coupling type.

---

## 6. Composition with the existing E9 bridge

Suppose APAC reaches a fixed point with no FULL product.

Let K be the conjunction of all Krom clauses produced from the four defect
planes.

Let X be the set of endpoint variables occurring in K and compute the exact
affine projection

    B = pi_X(A).

If B is 2-affine, equivalently if its affine annihilator/rowspace is generated
by equations of weight at most two, then the existing E9 theorem converts B
to polynomial-size 2-CNF.

Hence

    B AND K

is 2-CNF and is solved in polynomial time.

Any satisfying boundary assignment lifts by Gaussian elimination to a
solution of A. For every absorbed product, A already contains the exact local
graph restriction. For every defect-plane product, the plane equation plus
its Krom clause is exactly p=xy. Therefore the lifted assignment satisfies
all original product identities.

### Theorem KDP-2 — exact polynomial subclass

The following class has a deterministic exact polynomial-time decision and
search algorithm:

    affine + Boolean rank-one-product systems
    for which
      APAC leaves no FULL product
    and
      the projected Krom boundary is 2-affine.

Construction, closure, projection, 2-affine recognition, 2-CNF solving,
affine lifting, reconstruction, and verification are all polynomial.

This is a real positive solver theorem for a strict subclass. It is not a
solver for arbitrary 3SAT.

---

## 7. New hard-core dichotomy

After APAC, failure of Theorem KDP-2 can occur only through at least one of:

### Hard core A — FULL product coupling

    pi_{x,y,p}(A) = F_2^3

for an unresolved product.

Local affine context gives no relation among x,y,p. Any useful refinement
must exploit correlations of p with remote variables or introduce a new
representation.

### Hard core B — high-width affine/Krom boundary

There is no FULL product, but

    pi_X(A)

is not 2-affine.

Then the system has been reduced exactly to

    Krom
    +
    genuinely higher-width affine boundary.

The existing E9 audit already shows why this cannot be called tractable in
general: Krom plus unrestricted affine constraints is expressive enough to
encode arbitrary 3CNF once width-three parity is allowed.

Thus the new active frontier is strictly sharper than generic
minor absorption:

    R5_E8_6I_RAIL_KROM_DEFECT_HARD_CORE_GATE_V1

Question:

Can every JANUS-generated hard core be transformed, without exponential
branching, so that either

    FULL product coupling decreases under a certified polynomial potential,

or

    the live affine/Krom boundary becomes 2-affine,

while preserving exact semantics and polynomial total state?

---

## 8. Updated ledger

    THREE-SHEET -> SPARSE F2 AFFINE RANK1
    = PASS

    POLYNOMIAL RANK1 OBSTRUCTION BASIS
    = PASS

    SAME-COORDINATE UNIVERSAL AFFINE CUTS
    = BLOCKED

    LOCAL AFFINE PRODUCT ABSORPTION CLASSIFICATION
    = PASS COMPLETE

    FOUR CODIMENSION-ONE HARD DEFECTS
    = EXACTLY KROM

    APAC + NO FULL + 2-AFFINE BOUNDARY
    = PASS POLYNOMIAL SUBCLASS

    REMAINING HARD CORE
    = FULL PRODUCT
      OR
      HIGH-WIDTH AFFINE/KROM

    D1
    = EMPTY

    P_VS_NP
    = OPEN
