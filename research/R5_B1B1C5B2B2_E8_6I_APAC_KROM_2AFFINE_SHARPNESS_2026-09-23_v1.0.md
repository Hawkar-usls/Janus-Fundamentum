# R5 E8 6I — Sharpness of the APAC + Krom + 2-Affine Tractability Island

Date: 2026-09-23

Authority: JANUS_DERIVED_SHARPNESS_THEOREM__EXACT_LINEAR_ENCODINGS__NO_D1_PROMOTION

Parents:

- R5_B1B1C5B2B2_E8_6I_KROM_DEFECT_PLANE_BRIDGE_2026-09-23_v1.0.md
- R5_E9_KROM_AFFINE_HORN_PAIRWISE_BRIDGE_AUDIT_2026-09-23_v1.0.md

Scientific ceiling:

    D1       = EMPTY
    P_VS_NP  = OPEN
    P_EQ_NP  = NOT_PROVED

## 1. Positive island recalled

The preceding theorem gives an exact deterministic polynomial solver when:

    APAC leaves NO FULL product context

and

    the exact affine projection on the live Krom boundary is 2-affine.

This note proves that both hypotheses are structurally meaningful.

Relax either one, while keeping the other coarse condition, and exact
linear-size encodings of arbitrary 3CNF reappear.

This is an expressiveness theorem, not a P-vs-NP lower bound.

---

## 2. Axis A sharpness: 2-affine + product identities already encode 3CNF when FULL products are allowed

Take an arbitrary 3CNF formula F.

For every original Boolean variable x introduce, when needed, a complement
copy xb with the binary affine equation

    x + xb = 1.

Thus every literal can be written as the negation of a positive variable:

    not x      = not x,
    x          = not xb.

For a clause

    l1 OR l2 OR l3,

choose positive variables a,b,c such that

    l1 = not a,
    l2 = not b,
    l3 = not c.

Then the clause is

    not a OR not b OR not c

or equivalently

    NOT(a b c).

Introduce two product variables

    t = a b,
    u = t c,

and the unary affine equation

    u = 0.

The clause is satisfied exactly when these constraints are satisfiable.

Therefore every 3CNF has a linear-size exact encoding using only:

- unary affine equations;
- binary parity/complement equations;
- Boolean product identities p=xy.

The affine language is 2-affine.

For a standard nondegenerate 3-clause with three distinct noncomplementary
variables, the affine over-approximation places no equation on (a,b,t), so

    pi_{a,b,t}(A) = F_2^3.

Hence a FULL product context occurs already in this elementary encoding.

Conclusion:

    2-AFFINE
    +
    ALLOW FULL PRODUCT COUPLING
    =
    UNIVERSAL 3CNF REPRESENTATION.

Thus the NO-FULL hypothesis of the positive island cannot simply be dropped
and replaced by "the affine part is still 2-affine."

---

## 3. Axis B sharpness: no FULL products + width-three affine already encode 3CNF

The existing E9 bridge audit gives, for one clause

    a OR b OR c,

the exact representation with private y,z:

    (a OR not y)
    AND
    (y + b + z = 1)
    AND
    (not z OR c).

The middle constraint is one width-three affine parity equation.
The two outer constraints are Krom clauses.

Now replace each Krom clause by its Krom defect-plane realization.

The four exact correspondences are:

    not x OR not y
      iff
    [p=xy AND p=0]

    not x OR y
      iff
    [p=xy AND p=x]

    x OR not y
      iff
    [p=xy AND p=y]

    x OR y
      iff
    [p=xy AND p=x+y+1].

Each replacement introduces one private product variable p and one affine
plane equation.

Therefore the resulting affine projection of every such product triple is
contained in a hard plane and can never be FULL.

Applying this independently to all clauses gives a linear-size exact
representation of arbitrary 3CNF using:

- product identities p=xy;
- only non-FULL defect-plane product contexts;
- affine constraints of width at most three.

Conclusion:

    NO FULL PRODUCTS
    +
    ALLOW WIDTH-3 AFFINE/KROM BOUNDARY
    =
    UNIVERSAL 3CNF REPRESENTATION.

Thus the 2-affine-boundary hypothesis of the positive island cannot simply
be relaxed to width three.

---

## 4. Two-axis sharpness diagram

The current representation landscape is therefore:

                         affine boundary
                 2-affine              width >= 3
              +----------------+----------------------+
NO FULL       | POLY ISLAND    | universal encoding   |
products      | APAC+Krom      | already at XOR3      |
              | theorem        |                      |
              +----------------+----------------------+
FULL allowed  | universal      | universal / general  |
              | encoding via   |                      |
              | AND chains     |                      |
              +----------------+----------------------+

"Universal encoding" means only that arbitrary 3CNF can be translated exactly
with polynomial, in fact linear, overhead. It does not assert P!=NP.

This identifies a genuinely sharp corner:

    NO FULL
    AND
    2-AFFINE BOUNDARY.

---

## 5. Consequence for the active frontier

A universal polynomial algorithm cannot be obtained merely by proving one of:

    affine width <= 2

or

    no FULL products.

Either property alone still coexists with an exact representation of
arbitrary 3CNF once the other axis is relaxed.

Therefore a successful representation-changing recursion must do something
stronger:

1. simultaneously eliminate FULL product coupling and high-width affine/Krom
   interaction, or
2. introduce a new compressed state in which one of those universal encodings
   is no longer representable without a certified polynomial decrease.

Freeze the sharpened gate:

    R5_E8_6I
    JOINT_FULL_PRODUCT_AND_HIGH_WIDTH_AFFINE_COMPRESSION_GATE_V1

A PASS must provide a polynomially bounded measure Phi such that every
nonterminal exact transformation strictly decreases Phi, while preserving
the ability to reconstruct a Boolean solution.

Forbidden pseudo-progress:

- remove FULL products by generating width-three-or-higher affine/Krom
  boundaries;
- reduce affine width by introducing unrestricted FULL AND chains;
- alternate these two transformations without a global decreasing potential;
- hide either transition behind selector enumeration.

The sharpness theorem shows that such cycling can move between two universal
representations without reducing the underlying difficulty.

---

## 6. Updated scientific state

    APAC + NO FULL + 2-AFFINE
    = PASS POLYNOMIAL SUBCLASS

    2-AFFINE + FULL ALLOWED
    = UNIVERSAL 3CNF REPRESENTATION

    NO FULL + WIDTH-3 AFFINE ALLOWED
    = UNIVERSAL 3CNF REPRESENTATION

    NEXT REQUIRED CURRENCY
    = JOINT POTENTIAL
      THAT CONTROLS BOTH AXES

    D1
    = EMPTY

    P_VS_NP
    = OPEN
