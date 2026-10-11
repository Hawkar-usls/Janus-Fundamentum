# R5 — Exponential REACHABLE Residuals for EVERY SAT Square-Cubic-Linear Carrier

Date: 2026-10-11. PR #515.
Parent: `R5_UNIVERSAL_EXACT_SUPPORT_RESIDUAL_DAG_2026-10-11.md`.

**PROVED (all legal SAT inputs): exponentially many DISTINCT FEASIBLE
canonical LABELLED residual systems can be reached under SOME legal
sequence of selected-variable decisions.**

**NOT PROVED:** the ACTUAL number of states expanded by our
specific deterministic shortest-clause `ExactSupportResidualDAG`
has an exponential lower bound. It exits on a first SAT witness,
and the toroidal SAT family shows the striking opposite contrast.

This theorem refutes a purported polynomial bound on the FULL
POSSIBLE REACHABLE STATE SPACE, NOT a polynomial-time SAT solver
or a conjectured polynomial bound on VISITED states.
P_VS_NP remains OPEN.

## Theorem 1. ALL SAT SCL inputs have at least 2^(n/111) distinct feasible reachable residual keys

Let A be any legal n-by-n SQUARE + CUBIC + LINEAR positive
Exact-One carrier with a Boolean model x. Each column and row has
three ones. Let G be its column-conflict graph (variables are
adjacent iff they share a row). Its maximum degree is <=6; for
the linear input class it is exactly 6.

Because Ax=1 and every column has exactly three ones, summing
all clauses yields

    3*|supp(x)| = n.

Thus |supp(x)|=n/3.

For any vertex v in G, its closed 2-ball has at most
    1 + 6 + 6*5 = 37
vertices. Greedily choose vertices from supp(x), removing the
entire closed 2-ball of each selected vertex. The chosen set I
has pairwise conflict distance at least 3, and each greedy
step removes at most 37 available witness-selected vertices.
Consequently

    |I| >= ceil( (n/3)/37 ) = ceil(n/111).

For EVERY subset T of I, set x_v=1 for all v in T and apply
the exact residual deletion operator `S/v` from the existing
`ExactSupportResidualDAG` implementation; do NOT constrain the
other vertices in I. This is a legal succession of variable
selections because the chosen centers are pairwise distance>=3.

1. **Feasibility.** All these selected-one assignments are part
   of the SAME original full witness x. In particular they
   cannot create a clause with no remaining allowed variable,
   so every residual state R_T is feasible.

2. **Injectivity of T -> R_T.** For each v in I, choose any
   distinguished ORIGINAL 3-variable clause C_v containing v.
   If v in T, the branch v=1 satisfies and deletes C_v.
   If v not in T, then every chosen center w in T has
   conflict distance at least 3 from v. Such a w is neither
   a member of C_v nor adjacent to any member of C_v: an
   adjacency would give a path w-u-v of length <=2.
   Hence C_v is left completely untouched in the residual
   hypergraph, with all three of its variable IDs.
   Thus C_v belongs to R_T iff v is NOT in T.
   These clause-membership bits recover the complete subset T.
   Every two different T produce different EXACT LABELLED keys.

Therefore the family {R_T : T subseteq I} contains exactly
2^|I| distinct feasible reachable canonical residuals, and

    #possible_reachable_labelled_residual_states(A)
       >= 2^(ceil(n/111)).

This is unconditional, constructive, and true for EVERY
satisfiable SCL input. There are infinitely many such inputs
(e.g. the explicit toroidal carriers below). The argument
uses only bounded degree 6 and the witness cardinality,
not hidden heuristics or an NP-hard decision oracle.

## Theorem 2. Explicit SAT toroidal instances improve the exponent to n/9

Take L>=9 divisible by 3 and the toroidal square-cubic-linear
carrier on n=L^2 variables

    x_(i,j) + x_(i+1,j) + x_(i,j+1) = 1

for every (i,j) in Z_L^2. The complete torus audit already
proves its 3-regular C4-free property, connectedness,
growing primal treewidth and EXACTLY THREE SAT assignments.

One assignment is

    x_(i,j)=1  iff  (i-j) mod3=0.

Let

    I_L = {(3a,3b): 0<=a,b<L/3}.

Each member lies in the witness support, and

    |I_L| = (L/3)^2 = n/9.

The conflict edges displace lattice coordinates by
the six vectors

    (+1,0), (-1,0), (0,+1), (0,-1),
    (+1,-1), (-1,+1).

On Z_L^2, for L>=9, no path of <=2 such steps joins
distinct points of I_L (their coordinate differences
are divisible by 3 and nonzero mod L). Therefore I_L
has pairwise conflict distance >=3.

The same original-clause membership proof shows
that its 2^(n/9) subsets give distinct feasible LABELLED
canonical residual systems:

    #possible_reachable_labelled_residual_states(A_L)
       >= 2^(n/9).

The SAT count is exactly THREE, yet the possible
reachable residual-state space is exponentially large.
In particular a claim that 'few global SAT models'
bounds the raw set of possible partial-support states
is false, even on this fully explicit family.

## What this does / does not mean for universal polynomial runtime

Let

    R(A,pi) = all canonical residual keys REACHABLE
              under some correct sequence of branch selections,
    S_DAG(A,pi) = distinct canonical residual keys
              ACTUALLY EXPANDED by the frozen
              shortest-clause + component-factor algorithm.

Always S_DAG<=|R| but the inequality may be VERY loose.
The just-proved lower bound concerns |R|, not S_DAG.
The deterministic SAT solver is allowed to terminate as
soon as ONE witness is found; it may visit O(n) states
while |R|>=2^(n/9).

Thus NO general exponential time lower bound on
`ExactSupportResidualDAG` or arbitrary algorithms follows.
To complete the user's objective, one still needs an
all-input proof

    S_DAG(A,pi) <= n^C

for some fixed C, or a completely different deterministic
polynomial exact-support evaluator with witness extraction.
Bounding the entire reachability set R polynomially is not
a viable proof route; the theorem directly refutes it.
Canonical isomorphism quotienting, symbolic sharing and
different branching are not excluded by this proof.

Known proof-complexity context: Itsykson, Riazanov &
Smirnov, *Tight Bounds for Tseitin Formulas*, SAT 2022,
DOI 10.4230/LIPIcs.SAT.2022.6 proves 2^Omega(treewidth)
bounds for specified proof systems on Tseitin formulas.
Those bounds must NOT be imported directly to this
different exact-cover search without a certified
complexity-preserving translation.

## Reproducible exact regression and provenance

    python experiments/r5_universal_exact_support_exponential_reachable_residual_firewall.py

- Checks toroidal L=9,12,15,18 SAT witnesses and
  square/cubic/C4-free structural promises.
- Constructs the explicit packed set I_L of n/9 sites.
- Checks distance-3 separation and greedy witness
  packing size >=n/111.
- Enumerates all 512 possible subsets for L=9 and
  exactly 4096 fixed subsets for each larger L,
  testing the exact CANONICAL residual operator and
  full clause-membership reconstruction injectivity.
- Reports the exact theoretical number 2^(n/9)
  of POSSIBLE states derived mathematically, rather
  than pretending to enumerate them when enormous.
- Independently runs the frozen deterministic SAT DAG
  and reports its ACTUAL state counts; tests only
  that they are much smaller on the finite torus controls.

Citations and previous derivations:
    research/R5_UNIVERSAL_KETTANI_2025_TW_AND_DETERMINANT_AUDIT_2026-10-11.md
    research/R5_UNIVERSAL_EXACT_SUPPORT_RESIDUAL_DAG_2026-10-11.md

## Gate ledger

ALL_SAT_SCL_EXPONENTIAL_POSSIBLE_REACHABLE_LABELLED_STATES = PROVED.
TOROIDAL_SAT_2^(N/9)_POSSIBLE_REACHABLE_STATES = PROVED.
TOROIDAL_TINY_ACTUAL_SEARCH_STATES = FINITE_OBSERVATION.
ALL_REACHABLE_STATE_SPACE_POLYNOMIAL_BOUND = REFUTED.
DETERMINISTIC_VISITED_DAG_STATES_POLYNOMIAL_BOUND = OPEN.
SYMBOLIC_POLYNOMIAL_SUPPORT_EVALUATOR = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
