# R5 E9 — Three-Translate Tiling Normal Form

Date: 2026-09-24

Authority: JANUS_DERIVED_EXACT_COMBINATORIAL_NORMAL_FORM__NO_D1_PROMOTION

Parent: R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND_2026-09-24_v1.0

## 1. From the Boolean kernel word back to support sets

Write the exact cubic equation in Boolean coordinates:

(I+P+Q)x=1,
x in {0,1}^Omega.

Let

S={i in Omega : x_i=1}.

Under the convention

(Px)_i=x_{P(i)},
(Qx)_i=x_{Q(i)},

the supports are

supp(Px)=P^{-1}S,
supp(Qx)=Q^{-1}S.

The coordinate equation

x_i+x_{P(i)}+x_{Q(i)}=1

holds iff exactly one of

i, P(i), Q(i)

lands in S.

Equivalently:

Omega = S dot-union P^{-1}S dot-union Q^{-1}S.

Thus every cubic exact-one witness is exactly a three-translate tiling/factorization of the coordinate set by the shape

{I,P^{-1},Q^{-1}}.

## 2. Kernel-word equivalence

With z=3x-1:

z_i=2 iff i in S,
z_i=-1 otherwise.

So the following objects are exactly equivalent:

- Boolean exact-one witness x;
- {-1,2} kernel word z;
- exact support tiling S with Omega=S dot-union P^{-1}S dot-union Q^{-1}S.

No relaxation or counting assumption is introduced.

## 3. Phase witnesses are homomorphic tilings

If the Z3 phase potential phi exists, choose

S_r=phi^{-1}(r).

Then

P^{-1}S_r=phi^{-1}(r-1),
Q^{-1}S_r=phi^{-1}(r+1),

so the three sets are exactly the three phase fibers.

Hence the phase island is the subclass of witnesses produced by a homomorphism/character to Z3.

These are homomorphic or phase tilings.

## 4. Phase-inconsistent SAT means nonhomomorphic tiling

The phase-inconsistent n=6 positive control from the phase checker still has exact kernel words.

Therefore it has exact three-translate tilings S even though no global Z3 phase potential exists.

So:

phase FAIL does not mean no tiling;
it means no tiling arising from the one-dimensional Z3 character sector.

The true residual object can therefore be stated combinatorially as:

find a nonhomomorphic exact three-translate tiling.

## 5. Representation-theory bridge

Representation decomposition analyzes the linear equation

(I+P+Q)z=0.

The tiling normal form keeps the coordinate alphabet exact from the start.

Any proposed higher-representation contraction should be checked against the tiling semantics:

does the transformed state still encode exactly one member of every triple / exactly one of the three translated support sets?

If not, it has only solved a linear relaxation.

## 6. Active dual view

The current hard survivor has two equivalent authoritative descriptions:

LINEAR/REPRESENTATION VIEW:

(I+P+Q)z=0, z in {-1,2}^n, no 1D zero-mode.

COMBINATORIAL/TILING VIEW:

Omega=S dot-union P^{-1}S dot-union Q^{-1}S, with no Z3 phase potential.

A valid new contraction may use either language but must preserve exact witness reconstruction between them.

## 7. Ceiling

THREE-TRANSLATE TILING NORMAL FORM = PASS
PHASE TILINGS = HOMOMORPHIC Z3 SUBCLASS
PHASE-INCONSISTENT SAT = NONHOMOMORPHIC TILING
GENERAL NONHOMOMORPHIC TILING SOLVER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
