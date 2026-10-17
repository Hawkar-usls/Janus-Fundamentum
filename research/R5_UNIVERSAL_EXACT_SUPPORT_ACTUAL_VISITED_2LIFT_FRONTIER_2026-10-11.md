# R5 — Actually Visited ExactSupport DAG States on E123 Incidence 2-Lifts

Date: 2026-10-11.
Base predecessor: PR #515 `R5_UNIVERSAL_EXACT_SUPPORT_RESIDUAL_DAG_2026-10-11.md`
and `R5_UNIVERSAL_EXACT_SUPPORT_EXPONENTIAL_REACHABLE_RESIDUALS_2026-10-11.md`.
Current target: deterministic polynomial-bit-time **ExactSupport for EVERY legal
square+cubic+linear Positive Exact-One matrix and EVERY Boolean pin set**.

**Scientific verdict: exact preservation theorem for the 2-lift input class,
new focused reproducible REAL VISITED-state stress, and explicit resource
UNKNOWN. NO worst-case polynomial proof and NO proven exponential
ACTUAL-VISITED lower bound. P_VS_NP=OPEN.**

## 1. The proof obligation distinguishes three different quantities

Let R(A,pi) denote all distinct exact labelled canonical residual
hypergraphs that are **POSSIBLE** following SOME valid sequence of
selected-one variable decisions. Prior theorem establishes that
|R(A)|>=2^(n/111) on EVERY SAT SCL input and |R(A_L)|>=2^(n/9)
for the infinite SAT toroidal carriers.

Let S_actual(A,pi) be the number of states actually EXPANDED by
the specific frozen min-shortest-clause/component-sharing
`ExactSupportResidualDAG` search, terminating on the first
SAT witness, or fully exploring an UNSAT input.

The prior possible-reachable lower bound **DOES NOT** imply
a superpolynomial lower bound on S_actual.

Conversely, a finite trial on inputs 63,126,252,504 cannot
prove a uniform polynomial upper bound S_actual<=n^C
or a superpolynomial asymptotic lower bound. BOTH gates
remain OPEN. Their mathematical quantifiers differ.

## 2. Structural 2-lift theorem (all legal base inputs)

Let A be an n-by-n square/cubic/linear binary incidence
matrix. For each original 1-entry A_{i,j}=1 choose a sign
sigma_{i,j} in F2. Define 2n by 2n incidence A' by

    A'_{(i,t),(j,t XOR sigma_{i,j})}=1
        for t=0,1 and every A_{i,j}=1,

and all other entries zero.

Then:
* each lifted row (i,t) has exactly three ones;
* each lifted column (j,t) appears once per each of
  its 3 original incident checks, hence weight three;
* if two lifted rows correspond to two DIFFERENT base
  rows, two shared lifted columns would project to
  two shared base columns, contradicting linearity;
* if two lifted rows correspond to the SAME base row,
  they are disjoint because each base incidence connects
  one different column in each sheet.

Therefore A' is again square+cubic/linear/C4-free
for EVERY choice of signs, uniformly and constructibly
in polynomial time. The proof does NOT infer any
SAT/UNSAT-preserving property from lifting; the checker
obtains genuine decisions only by a complete exact
solver run or returns UNKNOWN at the resource cap.

## 3. Actually visited measurements (new, not just reachability)

Executable:
    experiments/r5_universal_exact_support_2lift_visited_dag_frontier.py

Starting with the exact q63 E123 Tutte-12 incidence matrix, use
`random.Random(9421)` to choose deterministic signs, repeatedly
2-lift to q126, q252 and q504. Every output is independently
validated for square/cubic/C4-free structure. Pass every
instance into the FROZEN existing deterministic
`ExactSupportResidualDAG_sparse` implementation; its cache
state counter, not a separate heuristic proxy, is measured.

Focused workflow:
    R5 ExactSupport Focused Audit, run #38140812215 = SUCCESS

Actual runner log:

    n= 63: S_actual= 164, cap= 2000, UNSAT,
              transitions=179, cache_hits=6,  component_splits=7.
    n=126: S_actual= 585, cap= 8000, UNSAT,
              transitions=626, cache_hits=8,  component_splits=9.
    n=252: S_actual=3775, cap=10000, UNSAT,
              transitions=3983, cache_hits=11, component_splits=13.
    n=504: S_actual=1500, cap= 1500, UNKNOWN,
              transitions=1557, cache_hits=0,  component_splits=1.

The three UNSAT verdicts are EXACT finite complete-search
results of the existing algorithm; they are not inferred
from E123's original UNSAT by any invalid cover implication.
No UNSAT statement is made for n504, whose solver was
stopped exactly at its configured 1500-state guard.
Each outcome, including UNKNOWN, is an intentional
regression check and may not be promoted to a
universal statement.

## 4. Why the published proof-complexity literature does not automatically close this gate

Known theorem:
Itsykson, Riazanov and Smirnov, *Tight Bounds for Tseitin
Formulas*, SAT 2022, DOI 10.4230/LIPIcs.SAT.2022.6,
prove an exponential-in-treewidth lower bound for
regular resolution and specified OBDD(AND,reordering)
refutations of TSEITIN formulas. Proof complexity
sources also establish exponential resolution size
on bounded-degree expander Tseitin contradictions.

These are SERIOUS candidates for a technique to
lower-bound S_actual on the frozen ExactSupport DAG.
However the literature theorem's subjects are
TSEITIN CNF contradictions, not E123 incidence
2-lifts or the square/cubic/linear Exact-One
CSP and this particular memoized branching protocol.
A valid transfer requires BOTH:

  (i) an explicit polynomial-size reduction from those
      particular hard Tseitin formulas into legal SCL
      positive Exact-One carriers, PRESERVING proof
      complexity (NP-hardness/SAT equisatisfiability
      alone is not enough);

  (ii) a polynomial-cost simulation from our actual
       memoized residual-state UNSAT search trace to
       the exact proof system for which the hard
       lower bound is established. Formula caching
       can be stronger than ordinary DPLL tree search;
       the simulation must account for shared states
       and AND component factorization.

Neither of these missing transfer lemmas is supplied
or silently assumed here. Hence no unconditional
exponential lower bound on S_actual is claimed.

Relevant sources:
  https://doi.org/10.4230/LIPIcs.SAT.2022.6
  https://doi.org/10.1137/S0097539703436485
  https://www.cs.columbia.edu/~rocco/papers/stoc16frege.html

## 4-A. Stronger CONDITIONAL implication: uniform UNSAT-only bound suffices

A precise, useful reduction in the remaining theorem obligation
does NOT require showing that the frozen algorithm is fast on
positive search traces.

Suppose there exist fixed C and c such that, for EVERY legal
SCL incidence matrix A, for EVERY pinned Boolean slice pi
that is UNSAT, the COMPLETE frozen residual-DAG algorithm
finishes in at most B(n)=c*n^C distinct memo states.

Then a deterministic polynomial SAT decision procedure follows:
run `ExactSupportResidualDAG(A,pi,max_states=B(n))`.
If it returns UNSAT, that is correct. If it returns SAT with
verified witness, correct. If it returns UNKNOWN, the
uniform UNSAT-only hypothesis rules out UNSAT; therefore
the pinned formula MUST be SAT.

For witness recovery, first establish SAT at no pins,
then for each unpinned coordinate j query the slice
pi union {x_j=0} under that same budget. If the
bounded run says UNSAT, fix x_j=1 (necessarily safe
because the parent is SAT); otherwise, whether the
bounded run returns SAT or UNKNOWN, fix x_j=0.
By induction every pinned prefix remains extendible.
After n steps verify the reconstructed Boolean Ax=1.

At most n+1 bounded exact runs use O(B(n)*poly(n))
bit operations. This would prove P=NP by the
already validated E118 NP-hardness bridge.

**THE UNSAT-ONLY BOUND HAS NOT BEEN PROVED.** This is
an implication, not a proposed real-time procedure:
WITHOUT a valid uniform bound, treating UNKNOWN as
SAT is MATHEMATICALLY UNSOUND and strictly forbidden.
The implemented production solver continues to
return UNKNOWN under any finite resource guard.

This sharpening also shows why one cannot infer that
a small SAT witness alone proves the whole search fast.
The difficulty may live specifically in provably
UNSAT pinned subinstances.

### Caching-proof-system caution

Beame, Impagliazzo and Segerlind,
*Formula Caching in DPLL* (2006/2010),
https://eccc.weizmann.ac.il/eccc-reports/2006/TR06-140/index.html
explicitly prove that different formula-caching proof
systems have substantially different power, including
separations from resolution for some variants.
The 2022 Tseitin resolution lower bound cannot simply
be transplanted to THIS exact residual-DAG solver;
one first needs a rigorous simulation in the
correct direction and a hardness-preserving
SCL gadget reduction. Both remain unproved here.

## 5. Correct mathematical next target

The ONLY remaining success gate is an all-input exact
support implementation with sound SAT/witness and UNSAT,
and a proof of the total BIT-runtime bound n^C.

A polynomial bound on S_actual of the FROZEN algorithm
would suffice, but is not logically necessary for
P=NP: a completely different polynomial algorithm
could succeed even if this algorithm has exponential
traces. Proving a worst-case exponential lower bound
on S_actual would only refute THIS heuristic/DAG
algorithm, not P=NP or all other algorithms.

Do not claim new scientific progress toward P=NP
merely because 2-lift sizes grow or finite
UNSAT certificates are confirmed.

## Checkpoint gate ledger

BINARY_TWO_LIFT_PRESERVES_SCL = PROVED_ALL_INPUTS.
E123_2LIFT_N63_N126_N252_COMPLETE_SEARCH_UNSAT = VERIFIED_FINITE.
E123_2LIFT_N504 = UNKNOWN_RESOURCE_GUARD.
REAL_VISITED_DAG_GROWTH = OBSERVATION_NO_ASYMPTOTIC_PROOF.
POSSIBLE_REACHABLE_STATES_EXPONENTIAL = PREDECESSOR_PROVED.
ACTUAL_SEARCH_EXPONENTIAL_LOWER_BOUND = OPEN.
ACTUAL_SEARCH_POLYNOMIAL_UPPER_BOUND = OPEN.
SYMBOLIC_POLYNOMIAL_EXACT_SUPPORT = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
