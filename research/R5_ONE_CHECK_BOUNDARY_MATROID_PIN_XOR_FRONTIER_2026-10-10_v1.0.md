# R5 — One-Check Boundary Matroid Theorem and Pin/XOR Frontier

Date: 2026-10-10

Status:
PROVED ONE-CHECK BOUNDARY THEOREM
+ PROPAGATION-ONLY UNIVERSALITY REFUTED
+ PIN/PROPAGATE/XOR-CONTRACT FRONTIER OPEN

P_VS_NP = OPEN.

## 0. Anti-loop and relation to mainline

Relevant established mainline facts:

* E78: exact equality gluing across a static Tanner partition is iterated
  delta-sum.
* E81: cyclic q=8 has no static partition into nonempty exact delta modules.
* E83: every exact Tanner boundary relation that is a delta-matroid becomes an
  ordinary matroid after the canonical variable-side twist.

A separate 2026-10-10 checkpoint strengthens E78 on any static represented
delta partition: after the E83 twist, global gluing is ordinary deterministic
matroid intersection against a partition matroid.

The present theorem addresses the remaining question: is E81's q=8 static
partition obstruction relevant after the elementary arithmetic precheck needed
by the actual Exact-One solver?

Answer: not in its raw form.

## 1. Divisibility precheck

Let the carrier have n checks and n variables, every variable occurring in
exactly three checks.

Any Exact-One solution selects a variable set X such that every check is
covered exactly once. Counting selected incidences in two ways gives

    3 |X| = n.

Hence

    SAT => 3 divides n.

If n mod 3 != 0, the instance is deterministically UNSAT immediately.

Therefore q=8 is an important representation counterexample but is outside the
SAT-admissible layer after this mandatory precheck.

## 2. Delete one check

Assume henceforth

    n = 0 mod 3.

Fix ANY check c.

Create a two-piece static Tanner partition:

* singleton module {c};
* big module B containing every variable vertex and every check except c.

The big module has exactly three boundary incidences: the three Tanner edges
incident with c. Since all variable vertices belong to B, all three boundary
coordinates are variable-side.

Let Y be a local satisfying assignment of B and let s be the Hamming weight of
its three boundary bits.

Every included check contributes exactly one selected incidence, so the n-1
included checks account for n-1 selected incidences.

Each selected variable contributes three incidences total; exactly s of those
selected incidences leave B through c.

Therefore

    3 |Y| - s = n - 1,

equivalently

    s = 3 |Y| - (n-1).

Because s is one of 0,1,2,3 and n=0 mod 3,

    s = 1 mod 3,

hence necessarily

    s = 1.

This uses only square/cubic Exact-One counting; source linearity/C4-freeness is
not needed.

## 3. Consequence: the hidden boundary relation is a rank-1 matroid

Let the three boundary coordinates be e1,e2,e3.

The exact boundary family of B is therefore some subset of

    {{e1},{e2},{e3}}.

Any nonempty family of one-element sets is precisely the basis family of a
rank-1 matroid (with absent coordinates acting as loops).

Thus:

    ONE-CHECK BOUNDARY MATROID THEOREM

For every square cubic Exact-One instance with 3|n, and every deleted check c,
the exact boundary relation of the all-variable / all-other-checks module is
either empty or an ordinary rank-1 matroid.

Under the E83 canonical twist by all three variable-side boundary coordinates,
the same relation is a rank-2 matroid on the corresponding non-coloops/loops.

## 4. Stronger equivalence: nonempty iff the original instance is SAT

A local state of B has boundary weight exactly one by Section 2.

But those three boundary bits are exactly the three incidences of the omitted
check c. Boundary weight one therefore satisfies c itself.

Hence every local satisfying extension of B is already a GLOBAL Exact-One
solution.

Conversely, every global solution restricts to a local extension of B.

Therefore for every check c:

    F SAT
    iff
    boundary_relation(B_c) is nonempty.

So decomposition EXISTENCE is no longer the issue on the 3|n layer.
The hidden rank-1 matroid exists exactly when SAT does.

The missing algorithmic object is its CONSTRUCTION:

    SUPPORT_c
      = { e in delta(c) : there exists a global solution selecting e }.

Computing any one nonloop of this three-element rank-1 matroid yields a witness
choice at c and permits ordinary self-reduction.

This isolates the universal problem to a constant-arity representation
construction rather than a large static decomposition theorem.

## 5. Why this does not yet solve SAT

Although the output representation has only three entries, deciding which
entries are zero/nonzero is exactly a global extension question.

Therefore the theorem must NOT be misread as:

    "constant boundary arity => polynomial construction".

That implication is false without a new algorithm.

The correct target is:

    ONE-CHECK SUPPORT CONSTRUCTION THEOREM

Given F and check c, compute in polynomial time the 3-bit mask SUPPORT_c.

Any algorithm for this theorem gives SolveLinearCubicXSAT immediately.

## 6. First direct construction attempt: pin + unit propagation

For each of the three states of check c:

    choose one incident variable = 1,
    set the other two = 0,

then repeatedly apply Exact-One unit propagation:

* one 1 in a clause forces all other unknown variables there to 0;
* two 0s in a clause force the remaining unknown variable to 1;
* two 1s or a fully-zero clause is conflict.

On several admissible q=12 controls this closes the entire carrier and exactly
recovers the three support states.

However this is not universal.

## 7. Exact SAT counterexample to propagation-only closure

The companion checker freezes the following square/cubic/linear q=18 carrier
by column supports:

    (2,3,4)
    (5,10,11)
    (9,14,17)
    (0,7,16)
    (6,13,15)
    (1,8,12)
    (8,13,14)
    (10,12,15)
    (2,10,16)
    (3,12,14)
    (0,3,13)
    (5,15,16)
    (4,5,17)
    (0,6,11)
    (4,8,9)
    (7,11,17)
    (1,6,9)
    (1,2,7)

It has the planted Exact-One solution

    {0,1,2,3,4,5}.

At check 2, that solution selects variable 0. Pinning the corresponding exact
state and closing under unit propagation leaves

    11 variables unassigned.

Therefore

    ONE_CHECK_PIN + UNIT_PROPAGATION => COMPLETE ASSIGNMENT

is false even on a satisfiable square/cubic/linear carrier.

## 8. Residual XOR contraction on the q=18 counterexample

After the frozen pin/propagation:

* 12 unresolved clauses contain exactly two unknown variables plus one fixed 0;
  each is therefore an XOR/complement constraint x_u + x_v = 1;
* 3 unresolved clauses still contain three unknown variables.

The graph on the 11 unknown variables formed by the 12 binary XOR clauses is
connected.

Choose one component representative t. Every unknown variable is then

    t xor parity(v).

Each of the three residual ternary clauses becomes the same one-bit condition
with parity pattern

    (t, 1-t, 1-t),

which forces

    t=1.

So although raw unit propagation leaves 11 variables, XOR contraction reduces
the residual to ONE Boolean and finishes the branch in polynomial time.

This is a real algorithmic gain over propagation alone.

## 9. New universal target

Define PIN_PROPAGATE_XOR_CONTRACT:

1. choose a surviving ternary check;
2. branch over its three Exact-One states;
3. unit-propagate;
4. turn every two-unknown residual clause into the equation x_u xor x_v = 1;
5. contract every consistent XOR component to one representative bit;
6. simplify the remaining ternary constraints on those representatives.

A branch can terminate immediately on:

* contradiction;
* no remaining ternary constraints;
* a quotient of constant/bounded size;
* an already-certified polynomial terminal from the R5 ledger.

The missing theorem is now:

    QUOTIENT-SHRINK / SEPARATOR THEOREM

For every surviving branch, either

A. XOR contraction reduces the number of live Boolean degrees of freedom by a
   constant factor; or

B. the residual exposes a polynomially discoverable separator/state
   decomposition whose total memoized state count is polynomial.

If A holds recursively, the recurrence

    T(n) <= 3 T(alpha n) + poly(n),  alpha<1,

is polynomial.

If B holds with polynomial total separator state, memoized divide-and-conquer
is polynomial.

No such universal A/B theorem is proved yet.

## 10. Claim boundary

DIVISIBILITY_PRECHECK = PROVED.
Q8_E81_AS_UNIVERSAL_SOLVER_BLOCKER_AFTER_PRECHECK = NOT_VALID.
ONE_CHECK_BOUNDARY_WEIGHT_ONE = PROVED.
ONE_CHECK_BOUNDARY_IS_RANK1_MATROID_IF_NONEMPTY = PROVED.
ONE_CHECK_BOUNDARY_NONEMPTY_IFF_GLOBAL_SAT = PROVED.
STATIC_DECOMPOSITION_EXISTENCE_ON_SAT_ADMISSIBLE_LAYER = TRIVIAL_TWO_PIECE.
POLYNOMIAL_CONSTRUCTION_OF_HIDDEN_3PORT_MATROID = OPEN.
PIN_PLUS_UNIT_PROPAGATION_UNIVERSALITY = REFUTED_BY_SAT_Q18.
PIN_PROPAGATE_XOR_CONTRACT = ACTIVE.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
