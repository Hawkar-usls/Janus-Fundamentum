# R5 — SAT-Admissible One-Check Redundancy and Three-Port Linear-Matroid Interface

Date: 2026-10-10

Status:
PROVED UNIVERSAL SAT-ADMISSIBLE REDUNDANCY / E81 SCOPE CORRECTION

P_VS_NP = OPEN.

## 0. Why this checkpoint is necessary

E81 falsified the unrestricted statement

    every square-cubic-linear RXC3 Tanner graph admits a static disjoint
    partition into exact delta-boundary modules

using the cyclic q=8 control.

But q=8 is not SAT-admissible for square+cubic Exact-One.

For any square cubic instance with n checks and n variables, every satisfying
assignment selects exactly n/3 variables, because every selected variable covers
three checks and every check is covered exactly once.

Hence

    SAT => 3 divides n.

A universal solver may therefore reject 3∤n immediately in polynomial time.
So E81 q=8 does not by itself refute a decomposition theorem whose premise is
restricted to the only sizes that can actually be SAT.

This note proves a stronger structural fact on the admissible lane.

## 1. One-check redundancy theorem

Let A be any n x n 0/1 matrix whose every column has weight exactly 3.
Assume 3 divides n.

Fix any check c.

Let x in {0,1}^n satisfy every Exact-One equation except possibly c:

    (Ax)_i = 1  for all i != c.

Write

    t_c = (Ax)_c.

Because row c has weight three in the square+cubic setting,

    t_c in {0,1,2,3}.

Now sum the n-1 satisfied equations:

    n-1
      = sum_{i != c} (Ax)_i
      = sum_j (3 - A_{cj}) x_j
      = 3|x| - t_c.

Reducing modulo 3 gives

    t_c == 1 (mod 3).

Since t_c is one of 0,1,2,3,

    t_c = 1.

Therefore x also satisfies check c.

So:

    boxed:
    IF 3|n, ANY ONE Exact-One CHECK IS BOOLEAN-LOGICALLY REDUNDANT
    GIVEN THE OTHER n-1 CHECKS.

No source linearity / C4-freeness is needed for this theorem; column degree 3
and 3|n suffice.

## 2. Near-global three-port boundary relation

Partition Tanner vertices into:

    S = {the single check c},
    B = {all n variables and all other n-1 checks}.

The singleton check module S has exact boundary relation

    ExactOne_3 = {{1},{2},{3}},

the basis family of U_{1,3}.

The big module B has exactly three boundary incidences, namely the three
incidences from the variables of check c into c.

For any local extension of B, Section 1 forces exactly one of these three
boundary bits to be one.

Hence its exact boundary family F_B satisfies

    F_B subseteq {{1},{2},{3}}.

If F_B is nonempty, it is exactly the basis family of a rank-1 matroid on the
three ports, with absent singleton states represented as loops.

Therefore:

    boxed:
    ON EVERY 3|n INSTANCE,
    THE ONE-CHECK NEAR-GLOBAL INTERFACE IS EITHER
      * EMPTY, or
      * A LINEAR RANK-1 MATROID ON THREE PORTS.

A representation, once the surviving ports are known, is the 1 x 3 matrix
whose column is nonzero exactly on the feasible singleton states.

## 3. Exact relation to satisfiability

Because the deleted check is logically redundant,

    F_B is nonempty
    iff
    the original Exact-One instance is SAT.

Thus existence of the representation is trivial, but IDENTIFYING which of the
three ports are nonloops remains computationally nontrivial.

This is the precise remaining gap.

Define

    ThreePortExtendibility(A,c)
      = (b_1,b_2,b_3),

where b_j=1 iff there exists a global Exact-One solution selecting the j-th
variable of check c.

Then:

    A is SAT iff ThreePortExtendibility(A,c) != 000.

If this vector can be computed in deterministic polynomial time for one check,
decision is solved. Repeating under standard exact pinning/self-reduction gives
a witness.

## 4. E81 scope correction

E81 remains correct as stated for unrestricted RXC3 geometry:

    q=8 has no static disjoint exact-delta partition.

But q=8 satisfies 3∤8 and is therefore immediately UNSAT before any
decomposition is needed.

So E81 does NOT refute the solver-relevant statement:

    for every SAT-admissible size 3|n, a useful polynomially constructible
    represented interface/decomposition exists.

Indeed the theorem above proves a universal static two-module EXISTENCE
statement on 3|n:

    singleton check U_{1,3}
    +
    near-global rank-1 three-port matroid, if SAT.

What remains open is efficient identification/construction of the near-global
matroid, not abstract delta/matroid existence.

## 5. Frozen controls

The companion replay verifies:

* q=6 frozen RXC3: every one-check deletion preserves the full Boolean solution
  set (both are empty because q6 is UNSAT).
* E77 q=9 connected SAT control: every one-check deletion preserves its unique
  global solution.
* E119 PERFECT-SAT9: there are exactly three global perfect matchings
  {A_0,A_1,A_2}, {B_0,B_1,B_2}, {C_0,C_1,C_2}; deleting one check leaves the
  same three solutions, and the big module boundary relation is the full
  U_{1,3}.
* q=8 cyclic E81 control is excluded by the 3∤n precheck.

## 6. Algorithmic frontier

The delta-existence question is no longer the right bottleneck on the
SAT-admissible lane.

The sharpened target is:

    THREE-PORT EXTENDIBILITY THEOREM

Input:
    square+cubic+linear Exact-One instance A with 3|n,
    one check c.

Output in polynomial time:
    the subset of the three incident variables that occur in at least one
    global Exact-One solution.

Any polynomial algorithm for this target gives SolveLinearCubicXSAT by testing
whether the subset is empty and then self-reducing to a witness.

Equivalently, the target is to construct the three-column rank-1 matroid
representation of the near-global module without enumerating global solutions.

This is strictly narrower than generic delta-sum composition, generic PIT, or
generic triple-to-pair matching.

## Claim boundary

ONE_CHECK_REDUNDANCY_FOR_3_DIVIDES_N = PROVED.
SAT_ADMISSIBLE_NEAR_GLOBAL_INTERFACE = EMPTY_OR_LINEAR_RANK1_MATROID.
E81_UNRESTRICTED_Q8_COUNTEREXAMPLE = STILL VALID.
E81_AS_BARRIER_TO_3_DIVIDES_N_SOLVER_LANE = REMOVED.
THREE_PORT_EXTENDIBILITY = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
