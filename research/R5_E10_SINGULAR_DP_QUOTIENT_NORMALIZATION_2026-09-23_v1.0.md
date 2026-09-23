# R5 E10 — Singular Davis–Putnam Quotient Normalization

Date: 2026-09-23

Authority: EXACT_POLYNOMIAL_PREPROCESSING_PASS__WITNESS_PRESERVING__TERMINAL_CORE_OPEN

## 1. Exact elimination identity

Let x occur positively in clauses (x OR A_i), i=1..p, and negatively in clauses (NOT x OR B_j), j=1..q, where A_i and B_j are disjunctions not containing x.

Davis–Putnam elimination gives the exact existential projection:

exists x [ AND_i (x OR A_i) AND AND_j (NOT x OR B_j) ]
iff
AND_{i,j} (A_i OR B_j),

after deleting tautological resolvents. This is exact satisfiability projection, not a heuristic.

## 2. Singular-polarity strict progress

If p,q>0 and min(p,q)=1, eliminating x removes p+q parent clauses and creates at most p*q=max(p,q) resolvents.

Hence the clause count drops by at least one.

The variable count also drops by one.

For the potential Phi = number_of_variables + number_of_clauses, every such step decreases Phi by at least two.

Pure variables (p=0 or q=0) are even easier: choose the satisfying polarity, delete every incident clause, and record the witness choice.

## 3. Polynomial total representation bound

Repeat pure/singular elimination until no such variable remains.

During the run the clause count never exceeds its initial value m0. Every clause contains at most the current number of variables, hence at most n0 literals.

Therefore the explicit CNF representation is always O(m0*n0), polynomial in the original input length.

There are at most n0 variable eliminations. Straightforward resolvent generation, tautology removal, and witness metadata are therefore polynomial-time overall.

Clause width may increase, but this does not invalidate polynomiality because m is monotone decreasing and width is at most n0.

## 4. Witness reconstruction

Suppose q=1 with unique negative parent (NOT x OR B).

If B evaluates true under a satisfying assignment of the projected formula, choose x=1; all positive parents are satisfied and the negative parent is already satisfied by B.

If B evaluates false, every resolvent (A_i OR B) forces every A_i true; choose x=0. Then the negative parent is satisfied by NOT x and every positive parent is satisfied by A_i.

The p=1 case is symmetric. Pure-variable reconstruction is immediate.

Thus a satisfying assignment of the terminal core lifts through the elimination stack in polynomial time.

## 5. Algorithm

SINGULAR_DP_QUOTIENT_NORMALIZE(F):

1. remove tautological clauses and apply ordinary unit/pure simplifications;
2. while a variable x has one polarity absent or has min(pos(x),neg(x))=1:
   - apply the exact DP projection above;
   - record one reconstruction frame;
   - simplify tautologies/subsumption when available;
3. return the residual CNF K plus the reconstruction stack.

Contract:

SAT(F) iff SAT(K).

Any model of K lifts in polynomial time to a model of F.

Construction, total intermediate state, reconstruction and verification are polynomial.

## 6. Terminal core

At termination every remaining variable has at least two positive and at least two negative occurrences.

This is a genuine narrowing, but it is not a tractability theorem.

A source-hard control exists exactly at this boundary: 3-SAT-(2,2), where every variable appears exactly twice positively and twice negatively, is NP-complete. Döcker (arXiv:1912.08032) proves the stronger monotone 3-SAT-(2,2) NP-completeness result.

Therefore the singular-DP algorithm is a polynomial exact normalization phase, not a universal SAT solver.

## 7. Relation to the JANUS quotient goal

This is the first explicit witness-preserving quotient step in the current E10 normalization program with a proved decreasing global potential.

It genuinely removes semantic distinctions: x is existentially projected away, not merely renamed or rerouted.

The price is that resolvents can become wider. The singular-polarity condition is precisely what prevents clause-count explosion during this phase.

## 8. New active gate

R5_E10_BALANCED_CORE_GROUPED_QUOTIENT_GATE_V1

Input: a singular-DP irreducible CNF in which every remaining variable has at least two occurrences of each polarity.

Seek a grouped/nonlocal exact elimination or quotient that:

- preserves SAT exactly;
- has polynomial witness lift;
- keeps total representation polynomial;
- strictly decreases a certified potential;
- does not rely on bounded backdoor enumeration or generic semantic equivalence;
- makes progress on the balanced (2,2) hard control rather than stalling immediately.

## 9. Ceiling

SINGULAR_DP_QUOTIENT_NORMALIZATION = PASS
STRICT POTENTIAL DROP = PASS
POLY TOTAL STATE = PASS
WITNESS LIFT = PASS
BALANCED CORE SOLVER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
