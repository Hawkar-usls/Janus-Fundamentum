# R5 E106 — Affine Unit Propagation and Pure Rank-2 Cover Core

Date: 2026-10-07

Status:
POLYNOMIAL_RANK0_RANK1_ELIMINATION__ONLY_PURE_CODIM2_COVER_REMAINS

Scientific ceiling:

E106 is not a universal polynomial ExactOne solver.

It gives an exact polynomial preprocessing theorem for the E105 full-kernel
flat-cover formulation. Every rank-0/rank-1 forbidden fiber is eliminated by
linear algebra. At the fixed point, every active forbidden set has relative
codimension exactly two in the current affine domain.

P_VS_NP = OPEN.

## 1. Input from E105

E105 rewrites raw8 feasibility as follows.

Let D initially be the complete zero-boundary kernel K0, represented as an
affine space over GF(2).

Every ordinary check c contributes one forbidden affine fiber B_c of
codimension at most two.

The goal is to find a point in

D minus union B_c.

NO RAW8 means the forbidden fibers cover D.

## 2. Relative rank matters after restrictions

During solving, D may be restricted to an affine subspace.

For one forbidden fiber B, compute I=D cap B.

Because B is defined by at most two affine linear equations, relative to D only
four cases matter:

1. I is empty.
   The constraint can never be violated and is deleted.

2. I=D.
   Every remaining point violates this check. This is an immediate NO-RAW8
   certificate for the current raw8 parity fiber.

3. I has size |D|/2.
   Inside D the bad set is one affine hyperplane. Avoiding it forces the
   complementary parallel hyperplane. Therefore add one affine equation and
   replace D by D-I.

4. I has size |D|/4.
   This is the genuine rank-2 case and remains active.

After case 3, restart because another active fiber may drop from relative rank
two to rank one.

## 3. Exact unit-propagation theorem

Repeat the above operation until no new rank-one restriction occurs.

Each propagation step lowers affine dimension by one, so there are at most
dim(K0) such steps.

Every step is Gaussian elimination / affine rank computation.

Therefore the entire propagation phase is polynomial.

At the fixed point D*:

* every surviving B_c is nonempty;
* every surviving B_c occupies exactly one quarter of D*;
* every rank-0/rank-1 implication has already been absorbed into D*.

Hence all remaining difficulty is a pure codimension-two affine cover.

## 4. Immediate polynomial terminals

Several exact terminals follow.

If propagation reaches an empty domain or a rank-0 nonempty forbidden fiber,
NO RAW8 is certified.

If no active forbidden fibers remain, any point of D* gives raw8.

If fewer than four rank-2 fibers remain, raw8 must exist because

|union B_c| <= m |D*|/4 < |D*|

for m<4.

If dim(D*)=O(log n), exact enumeration of all points of D* is polynomial.

These are genuine solver sectors, though not yet universal.

## 5. E104 replay

On the pairwise-minimal E104 five-port cluster:

dim K0 = 3,
|K0| = 8.

The checker computes all check fibers exactly.

Every rank-0/rank-1 check fiber is empty.

Exactly 18 nonempty forbidden fibers remain, each with two of the eight kernel
points, hence relative codimension two.

Their union covers exactly four kernel points.

The other four kernel points repair the E95 parity candidate, and independent
exact-cover enumeration confirms that they are exactly the four raw8
witnesses found in E104.

So the E105/E106 solver representation matches the nonlinear repair example
point-for-point.

## 6. Why this is algorithmically useful

Before E105-E106 the active route was organized around a handful of
target-derived kernel corrections.

After E106 the complete raw8 search has a canonical solver pipeline:

1. construct a basis of K0;
2. construct the forbidden local fiber for every ordinary check;
3. run affine rank-0/rank-1 propagation to fixed point;
4. solve only the residual pure rank-2 cover.

No exact solution can be lost in steps 1-3.

Thus any universal P-time theorem on this branch only needs to solve one
precisely specified object:

PURE STRUCTURED CODIM-2 COVER

The ambient space is an affine subspace of a zero-boundary kernel of a square
cubic C4-free ExactOne carrier. Every surviving check removes exactly one
quarter of that space.

## 7. E107 target

Generic codim-2 affine covers exist, so the next theorem must use incidence
structure.

For each active check c, let L_c be the two-dimensional quotient map whose one
forbidden value defines B_c.

The E107 target is:

STRUCTURED RANK-2 COVER KILLER

Assume the rank-2 fibers cover D*.

Use:

* C4-freeness: two checks share at most one source variable;
* cubicity: each selectable variable occurs in exactly three checks;
* exact TARGET6 origin of the forbidden translates;
* E99-E101 contraction of rigid B3 regions.

Prove that an irredundant pure rank-2 cover forces one of:

A. a reducible low-dimensional quotient;
B. an extra raw boundary witness;
C. a repeated Tanner pair / C4;
D. a polynomial decomposition into represented binary-delta modules;

or freeze the first exact TARGET6/no-raw8 structured rank-2 cover.

Scientific status:

E106 = POLYNOMIAL AFFINE UNIT PROPAGATION.
RANK0_RANK1 OBSTRUCTIONS = ELIMINATED EXACTLY.
RESIDUAL HARD CORE = PURE STRUCTURED CODIM2 AFFINE COVER.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
