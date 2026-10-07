# R5 E111 — Constructible sqrt(log n) Branchwidth Terminal

Date: 2026-10-07

Status:
CONNECTIVITY_FUNCTION_BRANCHWIDTH_ALGORITHM_PLUS_E110_GIVES_CONSTRUCTIVE_SQRTLOG_WIDTH_POLYNOMIAL_TERMINAL

Scientific ceiling:

E111 does not prove that every residual Tanner-derived subspace arrangement has
branchwidth O(sqrt(log n)).

It proves that whenever the branchwidth is O(sqrt(log n)), the decomposition
can be found in polynomial time by an existing connectivity-function
branchwidth algorithm, and the resulting decomposition can then be solved
exactly by E110.

P_VS_NP = OPEN.

## 1. The exact connectivity function

For active check subspaces L_1,...,L_m <= W and X subseteq [m], define

W_X = sum_{c in X} L_c,
W_barX = sum_{c notin X} L_c.

Set

lambda(X)
  = dim W_X + dim W_barX - dim W.

By the dimension formula,

lambda(X)=dim(W_X intersect W_barX).

So lambda is exactly the cut width used by E110.

It is symmetric and submodular because it is the standard connectivity
function induced by the rank function of a family of subspaces.

Each oracle evaluation needs only GF(2) rank computations and is polynomial.

## 2. External constructive theorem

Korhonen and Oum, "Branch-width of connectivity functions is fixed-parameter
tractable" (2026), give an algorithm for a symmetric submodular connectivity
function supplied by an oracle with running time

2^{O(k^2)} * gamma * m^6 * log m,

where gamma is the oracle-evaluation time.

The algorithm finds a branch-decomposition of width at most k when one exists
(or decides the corresponding branch-width question according to the theorem's
specification).

Our lambda is directly in this model.

## 3. Growing-width polynomial terminal

Assume

k <= C sqrt(log_2 n)

for a fixed constant C.

Then

2^{O(k^2)} = 2^{O(log n)} = n^{O(1)}.

The lambda oracle is polynomial and m<=n in the residual carrier size.

Therefore the decomposition-construction phase is polynomial.

E110 then solves a supplied width-k decomposition in

n * 2^{O(k)} * poly(n),

which is also polynomial for k=O(sqrt(log n)).

Hence:

branchwidth O(sqrt(log n))
=> fully constructive polynomial exact residual solver.

This is stronger than E110's fixed-width constructive statement and stronger
than a merely supplied O(log n)-width DP.

## 4. Why E111 is not the universal theorem yet

E111 does not prove a width bound for the Tanner-derived arrangement.

Large-width subspace arrangements exist in general.

Thus the remaining implication is structural:

EXACT TARGET6 / NO RAW8
=> either branchwidth O(sqrt(log n))
   or another polynomially solvable / contradictory structure.

Without that implication, P=NP is not established.

## 5. Checker

The checker exhaustively verifies on a small binary subspace arrangement:

* lambda(empty)=0;
* symmetry;
* submodularity;
* lambda equals the explicit intersection dimension.

It also replays E104's 18 active rank-2 check subspaces. A balanced
decomposition has width at most three, and E110 solves it exactly.

## 6. Solver architecture through E111

The current exact algorithmic pipeline is:

1. E105 — full zero-boundary kernel / one forbidden local fiber per check.
2. E106 — polynomial affine unit propagation; remove rank-0/rank-1 fibers.
3. E107 — defect multiplicity is 0 mod 3; NO RAW8 needs at least 12 flats.
4. E108 — quotient by the active normal span.
5. E109 — split direct-sum normal-matroid components.
6. E110 — exact branch-DP on 2D check-subspace arrangements.
7. E111 — construct the branch decomposition itself in polynomial time whenever
   branchwidth is O(sqrt(log n)).

So the residual asymptotic hard core must have at least one connected
Tanner-derived arrangement with branchwidth omega(sqrt(log n)).

## 7. E112 target

E112 HIGH-BRANCHWIDTH RAW8 ATTACK

Assume one connected E109/E110 component has branchwidth
omega(sqrt(log n)).

Use the additional structure not present in arbitrary subspace arrangements:

* every leaf is rank exactly two and comes from one cubic ExactOne check;
* its three nonzero vectors are actual variable-coordinate functionals;
* every original variable occurs in exactly three Tanner checks;
* Tanner geometry is C4-free;
* E107 defect multiplicity is divisible by three;
* forbidden characters come from six TARGET6 witnesses.

Goal:

A. show high branchwidth forces enough independent local freedom to construct
   an avoiding functional/raw8;
B. or find a polynomial decomposition of the high-width carrier into E78
   represented linear-delta modules;
C. or construct the first exact TARGET6/no-raw8 high-branchwidth obstruction.

Scientific status:

E111 = FULLY CONSTRUCTIVE POLYNOMIAL TERMINAL FOR
       BRANCHWIDTH O(sqrt(log n)).
HIGH-BRANCHWIDTH TARGET6/NO-RAW8 CASE = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
