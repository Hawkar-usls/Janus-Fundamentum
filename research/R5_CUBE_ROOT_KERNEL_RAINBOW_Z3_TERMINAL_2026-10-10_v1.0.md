# R5 — Cube-Root Kernel / Rainbow Z3 SAT Terminal

Date: 2026-10-10

Status:
PROVED GLOBAL SAT TERMINAL__NO_COMMUTATIVITY_REQUIRED

P_VS_NP = OPEN.

## 1. Statement

Let A be any 0/1 Exact-One incidence matrix in which every row has exactly
three nonzero entries.

Let omega be a primitive cube root of unity:

    omega^3 = 1,
    omega != 1,
    1 + omega + omega^2 = 0.

Suppose the complex/rational-cyclotomic kernel of A contains a full-support
vector z such that for some common nonzero scalar lambda,

    z_j in lambda * {1, omega, omega^2}

for every column j.

Then A is Exact-One SAT.

Moreover the phase classes of z give three explicit Exact-One witnesses.

No commuting-permutation hypothesis is required.

## 2. Proof

Scale z by lambda^{-1}, so every coordinate lies in

    {1, omega, omega^2}.

Write

    z_j = omega^(c_j),
    c_j in Z_3.

Take any row r. It contains exactly three columns a,b,c, and Az=0 gives

    omega^(c_a) + omega^(c_b) + omega^(c_c) = 0.

For three cube roots of unity, the sum is zero iff the multiset is exactly

    {1, omega, omega^2}.

Indeed:

* three equal roots sum to 3 times a nonzero root;
* two equal and one different cannot sum to zero;
* the three distinct roots sum to zero by 1+omega+omega^2=0.

Therefore every Exact-One row is rainbow:

    {c_a,c_b,c_c} = {0,1,2}.

For each residue q in Z_3 define

    x_j^(q) = 1 iff c_j=q.

Every row contains exactly one column of phase q, so

    A x^(q) = 1

over the integers.

Hence all three phase classes are Exact-One witnesses.

## 3. Relation to E13

E13 derives a Z3 labeling in the commuting A=I+P+Q sector by Fourier
diagonalization.

The present theorem isolates the actual sufficient object:

    a full-support common-scale cube-root kernel vector.

Commutativity is merely one way to manufacture such a vector. It is not needed
for the SAT implication.

Thus this theorem strictly separates:

    CONSTRUCTION of the phase vector
from
    RECONSTRUCTION of the Exact-One witness.

## 4. Relation to the Paley 3-lift search

For the Paley-55 incidence source, assign each base arc e an arbitrary phase

    h_e in Z_3.

Create a cyclic 3-lift. For each lifted row, choose its voltage shifts so that
the three variables in that row have total phases

    0,1,2.

Then the lifted variable (e,c) has phase

    h_e + c mod 3,

and the vector

    z_(e,c) = omega^(h_e+c)

lies in the lift kernel with full support.

By the theorem, the lift is automatically SAT: selecting any one phase class
gives an Exact-One witness.

Therefore such phase-engineered lifts CANNOT serve as POST-KLOC3 UNSAT
benchmarks.

Any UNSAT lift with an additional full-support twisted kernel mode must use a
mode not contained in one common scalar multiple of the cube-root set.

This is an anti-loop for the benchmark search.

## 5. Polynomial verification

Given a proposed phase labeling c_j in Z_3, verification is linear in the
number of incidences:

for every row, check that its three phase labels are exactly {0,1,2}.

If so, any phase class is immediately returned as a witness.

So the certificate is deterministic and polynomially verifiable.

## 6. Algorithmic consequence

This does NOT make finding such a phase vector polynomial in the general hard
class.

It supplies a new exact SAT terminal and a necessary exclusion for any genuine
post-KLOC3 UNSAT benchmark:

    POST_KLOC3_UNSAT
    =>
    no common-scale cube-root kernel vector.

The remaining triple-to-pair problem must therefore handle genuinely
non-phase kernel geometry.

## Claim boundary

CUBE_ROOT_KERNEL_VECTOR => EXACT_ONE_SAT = PROVED.
RAINBOW_Z3_LABELING => THREE_EXACT_ONE_WITNESSES = PROVED.
COMMUTATIVITY_REQUIRED = FALSE.
PHASE_ENGINEERED_PALEY_3LIFT_UNSAT = IMPOSSIBLE.
GENERAL_CUBE_ROOT_VECTOR_CONSTRUCTION = OPEN.
POST_KLOC3_UNSAT_BENCHMARK = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
