# R5 E120 — SAT-Admissible Full Rational Three-Port Projection Counterexample

Date: 2026-10-10

Status:
FULL_ROW_RATIONAL_PROJECTION_NOT_SUFFICIENT__CONNECTED_Q15_UNSAT_WITNESS

Scientific ceiling:

This checkpoint gives a new exact SAT-admissible hard benchmark.

It does NOT construct the universal polynomial Exact-One solver.

P_VS_NP = OPEN.

## 1. Why this benchmark is decisive

The SAT-admissible one-check theorem on this branch proves that for 3|n the
exact boundary relation obtained by deleting one check is either empty or a
rank-1 matroid on its three ports.

A natural polynomial relaxation is therefore:

For a check c with incident variables i,j,k, compute the rational kernel

    K = ker_Q(A)

and ask which centered Exact-One corners

    (2,-1,-1), (-1,2,-1), (-1,-1,2)

lie in the coordinate projection pi_{i,j,k}(K).

If no corner survives, UNSAT is certified.
If one survives, that port is locally forced.
If the projection has rank two, all three corners survive.

The strongest possible optimistic theorem would be:

    if every source row has full rank-two rational projection,
    then an Exact-One witness exists.

E120 refutes that theorem inside the actual square+cubic+linear,
SAT-admissible class.

## 2. Explicit q=15 carrier

Use row convention

    row i has columns {i, P[i], Q[i]}.

Set

    P = [12,13,9,8,5,2,11,1,0,10,7,4,14,3,6]

    Q = [3,4,14,10,7,13,5,0,2,12,6,9,8,11,1].

The companion checker verifies exactly:

    n = 15,
    every row has weight 3,
    every column has weight 3,
    every two columns meet in at most one row,
    Tanner graph connected.

Thus this is a connected square+cubic+linear source with

    3 divides n.

It cannot be dismissed by the q8 cardinality precheck.

## 3. Rational kernel

Exact rational Gaussian elimination gives

    rank_Q(A)=13,
    dim ker_Q(A)=2.

One primitive integer basis is

    z1 =
    (2,-2,-4,0,-1,1,2,0,2,4,-2,-3,-2,3,0)

    z2 =
    (5,-2,-1,-3,2,1,-4,-3,-4,-5,7,3,-2,0,6).

For every source row c, take its three incident coordinate rows from a kernel
basis matrix.

The resulting 3 x 2 projection matrix has rank exactly two.

Because every kernel vector satisfies the row sum-zero equation, this projected
two-space is exactly

    H = {(a,b,c) in Q^3 : a+b+c=0}.

Therefore all three centered Exact-One corners belong to every row projection:

    (2,-1,-1),
    (-1,2,-1),
    (-1,-1,2).

Equivalently, every one of the three ports of every check is rationally
extendible.

So all 15 local three-port relaxation tables are maximally permissive:

    111.

## 4. But Exact-One is UNSAT

The checker exhausts all

    2^15 = 32768

Boolean assignments.

It finds

    exact Exact-One solutions = 0.

Thus:

    boxed:
    FULL RATIONAL THREE-PORT EXTENDIBILITY AT EVERY CHECK
    DOES NOT IMPLY GLOBAL BOOLEAN EXTENDIBILITY.

This is a stronger negative control than E57 for the new three-port route.

E57 had rational nullity one and one locally forced port per check.
E120 has rational nullity two and ALL THREE locally allowed ports per check.

There is no rational-port forcing left at all.

## 5. Binary-kernel replay

Over GF(2), the kernel has dimension two.

Its four codewords have weight distribution

    weight 0 : 1
    weight 4 : 1
    weight 8 : 2.

The E58 cap is

    2n/3 = 10.

So

    w_max = 8 < 10,

independently confirming UNSAT through the exact E58 endpoint theorem.

This makes E120 a useful bridge between the rational and binary frontiers:

RATIONAL:
    every source-row projection is completely permissive.

BINARY:
    the global kernel still misses the exact cap.

BOOLEAN:
    no Exact-One witness exists.

## 6. Noncommutativity

For the displayed P,Q, the permutation commutator

    Kc = P Q P^{-1} Q^{-1}

moves 14 of the 15 indices.

So this is also a high-noncommutativity negative control.

In particular, large commutator support does not force SAT.

## 7. Consequence for the universal route

The following shortcut is now refuted:

    compute rational three-port extendibility on every check;
    if all checks admit all three ports, declare SAT.

The surviving theorem must synchronize information across multiple checks.

Fixed one-row projection information is insufficient even in the strongest
possible local state.

The next admissible attacks include:

A. multi-check kernel projections of growing but structured shape;
B. an exact separator/branch decomposition of the rank-two projection coupling;
C. a binary-rational synchronization invariant that detects why E120 has
   full rational local freedom but binary max weight only 8 instead of 10;
D. a global determinant/Pfaffian construction exploiting the exact P,Q
   interaction rather than local port tables.

E120 should be retained as a mandatory negative control for every proposed
ThreePortExtendibility or rational-projection solver.

## Claim boundary

SAT_ADMISSIBLE = YES.
CONNECTED_SQUARE_CUBIC_LINEAR = YES.
RATIONAL_NULLITY = 2.
EVERY_ROW_PROJECTION_RANK = 2.
EVERY_RATIONAL_THREE_PORT_TABLE = 111.
EXACT_ONE = UNSAT.
BINARY_KERNEL_MAX_WEIGHT = 8 < 10.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
