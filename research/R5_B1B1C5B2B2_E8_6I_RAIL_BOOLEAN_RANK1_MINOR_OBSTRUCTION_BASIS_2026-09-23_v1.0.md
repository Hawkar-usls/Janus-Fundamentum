# R5 E8 6I — RAIL Boolean Rank-One Minor Obstruction Basis

Date: 2026-09-23

Authority: JANUS_DERIVED_THEOREM__R5_OBSTRUCTION_BASIS_PASS__AFFINE_ONLY_ABSORPTION_BARRIER__NO_D1_PROMOTION

Parents:

- R5_E8_6I_SPARSE_BOOLEAN_RANK1_COMPLETION_GATE_V1
- R5_E8_6I_THREE_SHEET_RAIL_POLYNOMIAL_OBSTRUCTION_BASIS_GATE_V1
- R5_B1B1C5B2B2_E8_6I_RAIL_RECURSIVE_AFFINE_INTERFACE_LIFTING_META_THEOREM_2026-09-23_v0.1.md
- R5_B1B1C5B2B2_E8_6I_THREE_SHEET_QUADRATIC_RANK1_NORMAL_FORM_2026-09-23_v1.0.md

Scientific ceiling:

    D1       = EMPTY
    P_VS_NP  = OPEN
    P_EQ_NP  = NOT_PROVED

This note closes only the polynomial obstruction-basis obligation for the
current Boolean rank-one moment representation. It does not provide the
missing polynomial solver for the refined nonlinear states.

---

## 1. Frozen representation

The already proved exact representation constructs, from the frozen
three-sheet instance, an affine matrix space

    L_F = { Z : A_F(vec Z)=b_F, Z=Z^T, Z_00=1 }

over F_2, with

    F SAT
    iff
    L_F contains a rank-one Z.

For every genuine lift there is a Boolean vector

    w=(1,z_1,...,z_N)

such that

    Z = w w^T.

The remaining semantic obligation is therefore exactly multiplicative
consistency of the moment entries.

---

## 2. Anchored rank-one characterization

### Theorem R1 — anchored Boolean rank-one identities

Let Z be a symmetric (N+1) x (N+1) matrix over F_2 with Z_00=1. Then

    rank_F2(Z)=1

if and only if, for all 1 <= i <= j <= N,

    Z_ij = Z_0i Z_0j.                    (STAR_ij)

#### Proof

If rank(Z)=1 and Z_00=1, the nonzero zeroth row/column spans every row/column.
Symmetry and the anchored entry force

    Z = w w^T

with w_i=Z_0i, hence every STAR_ij holds.

Conversely, suppose every STAR_ij holds. Put

    w=(1,Z_01,...,Z_0N).

The zeroth row and column already agree with w w^T; the identities STAR_ij
give every remaining entry. Thus

    Z = w w^T.

Because w_0=1, w is nonzero and rank(Z)=1. QED.

For i=j, the identity is simply

    Z_ii = Z_0i

because a^2=a in F_2.

---

## 3. Polynomial canonical obstruction basis

Define

    B_rank1(N) = { c_ij : 1 <= i <= j <= N },

where c_ij is the valid cut STAR_ij.

Then

    |B_rank1(N)| = N(N+1)/2 = O(N^2).

Every genuine Boolean rank-one lift satisfies every member of the family.

By Theorem R1, every symmetric anchored matrix which is not rank one violates
at least one member of the family. A violated member is found by a direct
O(N^2) scan.

Hence the current rank-one representation has a canonical polynomial
separation basis for all failed lifts.

### RAIL consequence

For the current representation:

    R3  polynomial lift-or-obstruction test
        = PASS

    R4  sound obstruction validity
        = PASS

    R5  polynomial complete obstruction basis
        = PASS

    R6  polynomial encoding/storage of learned cuts
        = PASS (representation-size component only)

Freshness is automatic: a current abstract witness satisfies all previously
installed cuts; therefore any violated c_ij returned by the scan was not
already installed.

This closes the old question

    are there only polynomially many canonical failed-lift obstruction types?

for this representation.

It does not close the recursive solver obligation.

---

## 4. Equivalent anchored-minor view

Rank at most one is characterized by vanishing 2 x 2 minors.

Because Z_00=1, it is sufficient to use only the anchored minors on rows
{0,i} and columns {0,j}:

    det [[Z_00,Z_0j],
         [Z_i0,Z_ij]]
    =
    Z_ij + Z_0i Z_0j
    =
    0.

Thus the full O(N^4) minor vocabulary collapses, in the anchored Boolean
moment representation, to the O(N^2) family above.

This is a genuine compression of the obstruction vocabulary.

---

## 5. Why the basis is not already a polynomial SAT solver

Each cut

    p = x y

is nonlinear over F_2.

As a Boolean relation it is the graph of AND and can be written as Horn CNF:

    (not x OR not y OR p)
    AND
    (x OR not p)
    AND
    (y OR not p).

Therefore simply appending all rank-one cuts to the affine system does not
leave us inside Gaussian elimination.

The local E9 pairwise-bridge audit already supplies the required negative
control: Horn plus 2-affine is expressive enough to encode arbitrary CNF
satisfiability.

So the statement

    the nonlinear obstruction basis is polynomially small

must never be promoted to

    the refined system is polynomial-time solvable.

The latter remains exactly the missing brick.

---

## 6. Affine-only cut barrier in the same moment coordinates

A natural attempted escape is to search for linear cuts, valid for all genuine
Boolean rank-one points, which eliminate spurious matrices while preserving a
pure affine target.

That route is blocked.

Use reduced moment coordinates

    Phi(x)
    =
    (
      x_i,
      x_i x_j for 1 <= i < j <= N
    )
    in F_2^D,

where

    D = N + binom(N,2).

Diagonal moments are omitted because x_i^2=x_i; symmetry is also already
quotiented out.

### Theorem R2 — full affine hull of Boolean degree-2 moments

The set

    { Phi(x) : x in {0,1}^N }

affinely spans all of F_2^D.

Equivalently, if an affine linear equation

    c
    + sum_i a_i x_i
    + sum_{i<j} b_ij x_i x_j
    =
    0

holds for every Boolean x, then every coefficient is zero.

#### Proof

The displayed expression is the algebraic normal form of a Boolean function
of degree at most two. Algebraic normal form over F_2 is unique.
The identically zero Boolean function therefore has all ANF coefficients
equal to zero. QED.

### Consequence

After quotienting the obvious universal identities

    Z = Z^T,
    Z_00 = 1,
    Z_ii = Z_0i,

there is no additional nontrivial affine equation satisfied by every Boolean
rank-one moment point.

Therefore a RAIL instantiation which:

1. drops rank one,
2. stays in these same moment coordinates, and
3. attempts to recover rank one using only universal affine linear cuts

cannot be separation-complete.

This is an unconditional representation barrier; it does not assume P != NP.

### Exact scope

The theorem does not block:

- instance-specific linear equations valid only for the solution set of a
  particular input;
- nonlinear rank-one cuts;
- a different representation with new auxiliary state;
- a recursive quotient/fibre construction with a proved decreasing measure.

It blocks only the tempting same-coordinate universal-affine repair.

---

## 7. New exact frontier: minor absorption

Freeze:

    R5_E8_6I_RAIL_MINOR_ABSORPTION_GATE_V1

Input:

    SPARSE_F2_AFFINE_RANK1_COMPLETION
    +
    a growing subset C of B_rank1(N).

Required PASS:

1. Abs(I,C) has polynomial encoding size.
2. Solve(I,C) is exact and deterministic polynomial time, either directly
   or by a recursion with an independently proved polynomial total bound.
3. Every failed lift returns one fresh violated anchored minor in polynomial
   time.
4. The solver remains closed under adding such cuts, or recursion maps the
   refined state to a strictly simpler certified class.
5. There is no branching over all values of x_i, sheet selectors, fibres, or
   violated-minor truth cases unless a global polynomial bound is proved.
6. Reconstruction of a rank-one witness and the original Boolean assignment
   is polynomial.
7. The full lifecycle construct + refine + solve + reconstruct + verify +
   history is polynomial.

Immediate falsifiers:

- compiling the cuts to unrestricted Horn+affine and calling the mixture
  tractable;
- replacing each product by a guessed Boolean selector;
- input-dependent recursion depth with no global potential;
- a separation oracle that itself solves the original SAT instance;
- an exponential catalogue of partial products or fibres.

---

## 8. Updated frontier

    REPRESENTATION CHANGE
    THREE-SHEET -> SPARSE F2 AFFINE RANK1
    =
    PASS EXACT

    RAIL GENERIC META-THEOREM
    =
    PASS CONDITIONAL

    BOOLEAN RANK1 POLYNOMIAL OBSTRUCTION BASIS
    =
    PASS

    SAME-COORDINATE UNIVERSAL AFFINE CUT COMPLETION
    =
    BLOCKED

    TRACTABLE ABSORPTION / RECURSION OF RANK1 MINORS
    =
    OPEN
    <<< ACTIVE MATHEMATICAL BRICK

    D1
    =
    EMPTY

    P_VS_NP
    =
    OPEN
