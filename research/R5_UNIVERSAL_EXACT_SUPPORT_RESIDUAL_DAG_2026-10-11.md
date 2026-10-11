# JANUS R5 — Universal ExactSupport via Canonical Residual Hypergraph DAG: All-Input Identity and Polynomial-Size Gate

Date: 2026-10-11.
Authority before this attack: PR #515 at 291e1c41a99269a61eb900261714ea6195821019,
focused ExactSupport run 38138020738 SUCCESS, full R5 run
38138020663 (check workflow status for exact timestamp).

**Goal:** a genuinely universal deterministic n^O(1)-bit-time
`SolveLinearCubicXSAT(A,pins)` for ALL n x n square/cubic/C4-free
Positive Exact-One carriers, with sound/complete SAT+verified witness
or UNSAT. `P_VS_NP=OPEN`.

**Checkpoint verdict:** exact all-input residual-state contraction,
connected-component factoring, exact labelled-state sharing,
arbitrary Boolean pins and guarded UNKNOWN have been IMPLEMENTED.
A short finite suite is independently green. The polynomial-size
bound on the set of reachable unique states is OPEN. Therefore this
IS NOT the demanded polynomial-time algorithm and is not a claimed
advance in the final P-vs-NP complexity gate.

## 1. Canonical residual state

Represent the remaining Exact-One formula as a sorted tuple S
of distinct sorted nonempty finite sets of variable IDs. Each set C
enforces

    sum_{v in C} x_v = 1, with x_v binary.

After branching/pinning, a residual clause may contain one, two or
three variables, even though every source row has size three.

If a variable v is selected as 1, the result MUST assign every other
variable co-occurring with v in ANY remaining clause to 0 and delete
every clause containing v. Delete all newly forbidden variables from
every other clause; if any clause becomes empty, this branch is
contradictory. Delete duplicate clauses without changing semantics.

Let S/v denote precisely this canonical residual. Then the
following is an all-input EXACT Boolean identity:

    Support(S) = OR_{v in C} Support(S/v)

for ANY residual clause C in S, with

    Support(empty)=TRUE,
    Support(state containing empty clause)=FALSE.

Proof: a satisfying model has exactly one 1 in C, so it belongs to
exactly one of the enumerated branches. Conversely, any satisfying
model of S/v extends to a model of S by choosing v=1 and all other
forbidden variables zero; deleted clauses contain precisely v and
are therefore satisfied. No partial assignment or SAT state is
counted twice when all variables in C are distinct.

If the incidence graph of S decomposes into variable-disjoint
connected components S_1,...,S_k, then

    Support(S) = AND_i Support(S_i).

A complete witness is obtained by UNION of the selected-variable
sets from each component/branch, with every other original variable
assigned zero. Contradictory pinned-one states are rejected before
the recursion, and the final model is checked against EVERY original
row and EVERY pin, NOT just against the reduced residual clauses.

The program records a cache keyed by the EXACT labelled canonical
S. Caching is sound since every earlier variable outside S is
already assigned and ALL of its incident checks were satisfied or
its banned status was propagated. Equal S has exactly the same
remaining truth predicate even when reached through different
paths. No probabilistic hash collisions or unjustified graph
isomorphism tests are used.

## 2. Constructive algorithm and mathematically accounted cost

The executable
    experiments/r5_universal_exact_support_residual_dag_attack.py

implements:

1. validate n x n square/cubic/C4-free incidence with polynomial
   exact counts (sparse form avoids constructing huge dense matrices);
2. consume all pinned x=1 and x=0, immediately propagate forbidden
   variables and reject inconsistent pins;
3. canonicalize the remaining hypergraph;
4. check the cache by its exact labelled clause tuples;
5. factor independent connected components;
6. choose a smallest-size nonempty clause, branch on its 1-variable
   choices, canonicalize and recurse;
7. cache either a sorted selected-variable witness or UNSAT;
8. verify any returned model x is binary, Ax=1, |x|=n/3 and all
   Boolean pins hold;
9. with a finite `max_states`, return UNKNOWN on exceeding the
   budget, never a speculative UNSAT.

Let S(A,pi) be the number of distinct reachable canonical
residual states ACTUALLY expanded by this solver. Each state
contains at most n rows, each of length <=3; its representation,
connectivity test and at most three transition evaluations have
polynomial bit cost. On any input:

    total bit runtime = S(A,pi) * poly(n),
    space = S(A,pi) * poly(n).

This is a genuine all-input runtime theorem *in terms of the
actual number of cache states*, not the requested polynomial
worst-case theorem. In the absence of an upper bound
S(A,pi)<=n^C valid for ALL legal matrices and all pins,
`S(A,pi)` may in principle be exponential. The state space
can be bounded crudely by the 3^n partial assignments;
the current research provides NO general polynomial bound.

One could substitute an exact compressed circuit or quotient
state key, but then BOTH its construction/canonicalization
cost and its exact evaluation time require a separate all-input
polynomial theorem. A short symbolic representation is not
enough if its evaluation remains exponential.

## 3. Exact focused CI evidence, properly scoped

Focused CI run 38138630307:
    R5 ExactSupport Focused Audit = SUCCESS,
    including the independent previously green pinned
    ExactSupport checker and this residual DAG attack.

Exact finite observations from runner logs:

    E61 SAT12       n=12   distinct S=8    SAT
    E61 UNSAT12     n=12   distinct S=4    UNSAT
    E123 UNSAT63    n=63   distinct S=164  UNSAT
    E65 R^T SAT63   n=63   distinct S=25   SAT
    E118 UNSAT90    n=90   distinct S=75   UNSAT
    E118 SAT90      n=90   distinct S=37   SAT
    E125 t=2       n=252  distinct S=163  UNSAT
    E125 t=3       n=567  distinct S=163  UNSAT
    torus L=9       n=81   distinct S=31   SAT
    torus L=12      n=144  distinct S=53   SAT
    torus L=15      n=225  distinct S=81   SAT

The tested E125 carriers are connected legal square/cubic/linear
UNSAT constructions with growing grid minors, and the toroidal
carriers are legal SAT instances with growing primal width.
Low state counts here do not imply that arbitrary SCL instances
admit polynomial S; known E118 NP-hardness means any such
general theorem would constitute the essential P=NP advance.

The oracle also verifies pinned E61 SAT/UNSAT slices against the
prior GF2-Gauss `ExactSupport`, q63/q90 outcome consistency,
and returns UNKNOWN when zero distinct states are authorized
for a still-open SAT12 search. E118 q9 source truth values
are independently exhaustive finite certificates, not general
polynomial support routines.

These are fixed checks. No statistical extrapolation of the
number of DAG states is considered mathematical proof.

## 4. Exactly what would open the UNIVERSAL gate

A valid all-input successor must do one of the following:

A) Prove, WITHOUT assuming P=NP, a fixed C and an explicit
   deterministic state selection/quotient rule satisfying
       S(A,pi) <= n^C
   for every SCL A and every pin set pi, with total state
   construction and cache operations also polynomial;
   OR

B) Give an entirely different exact symbolic support evaluator,
   with formal worst-case n^C BIT runtime, no NP-complete oracle,
   and a rigorous self-reduction for witness.

For a positive case the solver already verifies the complete
Boolean witness; for a negative case completion of the finite
state DAG is a sound exhaustive UNSAT argument. But absent (A)
or (B), the algorithm only yields `O(S poly(n))` and cannot
be called a universal polynomial solver.

**Do NOT relabel a terminal, heuristic, special family, or
finite CI result as `SolveLinearCubicXSAT` worst-case n^O(1).**

## Claim ledger

EXACT_RESIDUAL_DELETION_CONTRACTION = PROVED_ALL_INPUTS.
CANONICAL_LABELLED_STATE_MEMOIZATION = SOUND.
COMPONENT_AND_FACTOR = PROVED_ALL_INPUTS.
PINNED_BOOLEAN_WITNESS_VERIFY = IMPLEMENTED_AND_SOUND.
RESOURCE_BUDGET_UNKNOWN = IMPLEMENTED.
RUNTIME_S_TIMES_POLYNOMIAL = PROVED.
FOCUSED_CI_38138630307 = SUCCESS_FINITE_REPLAY.
SCL_E125_N252_N567_DAG_STATE_COUNTS = FINITE_OBSERVATION.
UNIVERSAL_POLYNOMIAL_STATE_BOUND = OPEN.
UNIVERSAL_POLYNOMIAL_EXACT_SUPPORT = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
