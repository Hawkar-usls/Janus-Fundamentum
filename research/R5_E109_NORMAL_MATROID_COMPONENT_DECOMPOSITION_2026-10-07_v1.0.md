# R5 E109 — Binary Normal-Matroid Component Decomposition

Date: 2026-10-07

Status:
PURE_RANK2_AVOIDANCE_FACTORS_EXACTLY_ACROSS_BINARY_NORMAL_MATROID_COMPONENTS

Scientific ceiling:

E109 does not yet prove a universal polynomial ExactOne solver.

It proves an exact direct-sum decomposition theorem for the E108 normal-span
quotient. The active rank-2 check normals form a represented binary matroid.
Its connected components are independent solver blocks.

P_VS_NP = OPEN.

## 1. Normal vectors from the residual kernel domain

After E106-E108, translate the residual affine domain to a vector space U.

Each active rank-2 check c has three incident variable coordinate functionals

g_u, g_v, g_w in U*.

Because every zero-boundary kernel word has even parity on the check,

g_u + g_v + g_w = 0.

Rank two means these are the three distinct nonzero vectors of one
two-dimensional subspace L_c.

So every active check supplies a binary 3-circuit.

## 2. Build the represented normal matroid

Let E be the set of distinct nonzero normal vectors used by the active checks.

Represent them as vectors over GF(2).

Let M(E) be the corresponding binary vector matroid.

Compute its connected components

E_1,...,E_s.

For represented matroids, this can be done in polynomial time from a basis and
the fundamental circuits of all nonbasis elements.

Let

W_i = span(E_i).

Matroid component theory gives the direct sum

W = W_1 direct_sum ... direct_sum W_s.

## 3. Every check stays inside one component

The three nonzero normals of one active check form a circuit.

No circuit can cross two direct-sum components.

Therefore for every check c there is a unique component i such that

L_c subset W_i.

So its entire forbidden affine predicate depends only on the coordinate block
dual to W_i.

## 4. Exact solver factorization

A quotient state of the full normal span W is exactly a tuple

(t_1,...,t_s)

with t_i in W_i*.

Every active forbidden flat belongs to one component.

Therefore a global state avoids every forbidden flat iff for every i, the local
state t_i avoids every flat assigned to component i.

Hence:

GLOBAL RAW8 REPAIR EXISTS

iff

EVERY NORMAL-MATROID COMPONENT HAS A LOCAL REPAIR.

This is exact, not a relaxation.

## 5. Runtime consequence

Let r_i=dim W_i.

Solve each component independently by exhaustive quotient enumeration.

The total search is

sum_i 2^{r_i} poly(n),

rather than

2^{sum_i r_i}.

Therefore:

max_i r_i = O(log n)

is a polynomial-time terminal.

This can hold even when the total normal-span rank is linear in n.

So E108's global-rank criterion is strictly strengthened.

## 6. Synthetic replay

The checker constructs a four-dimensional quotient whose active flat normals
split into two independent two-dimensional blocks.

The represented normal matroid has two components of ranks

2 and 2.

Direct global brute force and independent component solving return exactly the
same satisfiability answer.

## 7. E104 replay

For E104's 18 surviving rank-2 flats, the checker reconstructs their dual
normal lines and computes the represented normal-matroid components.

Every active line lies wholly within one component, as required.

The four exact raw8 avoiding states are preserved under the decomposition.

The replay records the actual component-rank profile into the CI output rather
than assuming it in the theorem.

## 8. Why this matters for the universal solver

Before E109 a high global normal rank still looked like an exponential
obstruction.

After E109, the real hard parameter is

maximum rank of one connected normal-matroid component.

Thus the surviving hard core has accumulated all of the following necessary
properties:

* E106 propagation fixed point;
* only rank-2 forbidden fibers;
* at least 12 active flats if NO RAW8;
* superlogarithmic effective normal rank;
* at least one superlogarithmic connected binary normal-matroid component.

Everything else is already polynomially decidable on this route.

## 9. E110 target

Take one surviving connected component C of rank r=omega(log n).

Its elements are variable coordinate functionals and every active check is a
3-circuit.

Use the Tanner source geometry to attack this represented component.

Possible exits:

A. prove high-rank component expansion guarantees an avoiding quotient state;
B. decompose C by a low-order matroid separation and recurse;
C. convert C into represented binary-delta modules compatible with E78;
D. force an extra boundary witness/raw8;
E. construct the first exact TARGET6/no-raw8 high-rank connected obstruction.

The immediate structural question is whether the cubic Tanner incidence forces
a polynomially discoverable 1/2/3-separation of the normal matroid unless its
rank is already logarithmic.

Scientific status:

E109 = EXACT NORMAL-MATROID DIRECT-SUM DECOMPOSITION.
SMALL COMPONENT RANK = POLYNOMIAL TERMINAL.
ONLY LARGE CONNECTED NORMAL-MATROID BLOCKS REMAIN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
