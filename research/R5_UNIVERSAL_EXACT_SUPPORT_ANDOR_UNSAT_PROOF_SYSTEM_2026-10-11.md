# R5 — ExactSupport Residual-DAG UNSAT Proof System: Polynomial Verification, Open Proof-Size Lower Bound

Date: 2026-10-11. Repository Hawkar-usls/Janus-Fundamentum,
branch research/parity-isolation-trade-checkpoint-20261009, PR #515.

**Final-status contract:**
- EXACT AND/OR memoized residual UNSAT proof verification: PROVED sound;
- verification time polynomial in INPUT + CERTIFICATE length: PROVED;
- deterministic worst-case polynomial certificate CONSTRUCTION: NOT PROVED;
- worst-case polynomial certificate SIZE for all SCL UNSAT inputs: NOT PROVED;
- unconditional super-polynomial minimum certificate-size lower bound for this exact proof system: NOT PROVED;
- universal polynomial `ExactSupport` / `SolveLinearCubicXSAT`: NOT CONSTRUCTED;
- P_VS_NP: OPEN.

## 1. Exact refutation system defined by the actual frozen source code

Let F be an exact-one hypergraph whose clauses are nonempty
sets of at most three variable IDs. A state is a canonical
sorted tuple of such clauses with variable IDs preserved;
a negative residual state cannot be empty because the empty
hypergraph is SAT.

There are TWO inference rules. Each node claims UNSAT.

**OR node:**
Choose the exact smallest-cardinality clause C, breaking
ties lexicographically, exactly as in the existing
`ExactSupportResidualDAG_sparse` implementation. For EVERY
v in C, compute the canonical residual F/v obtained by
choosing v=1, deleting all clauses containing v, forbidding
all co-occurring variables, and deleting these forbidden
variables from the remaining clauses.

If any remaining clause becomes empty, that branch has an
immediate, independently verifiable contradiction.
Otherwise require a certificate of UNSAT(F/v).
When EVERY v in C has been rejected:

    (AND_{v in C} UNSAT(F/v)) -> UNSAT(F).

Every possible exact-one completion of C assigns
one—and only one—v in C to 1. The OR rule therefore is sound
and complete as an exhaustive branching step.

**AND node:**
Compute the exact connected components F_1,...,F_k of the
variable-clause incidence graph with k>=2. These components
have disjoint variable sets, so

    SAT(F) iff AND_i SAT(F_i).

Thus an independently certified UNSAT(F_i) for ANY one
component suffices to prove UNSAT(F). A proof node names
one component, which is checked for exact membership in
the graph decomposition. It need not evaluate other
already-SAT components.

**Memo-sharing:** Same exact LABELLED residual state is a
single shared node across many inference edges. The proof
is a DAG, not an expanded search tree.

Each OR child is strictly smaller in clause count, and
each AND-selected component is a strict subset of the
parent's clauses. Thus this proof graph is acyclic
and supports independent bottom-up verification.

There is no rule allowing an unverified SAT inference
or accepting UNKNOWN as a negative certificate.

## 2. Deterministic independent verification theorem

Let the original SCL input size be n and let a proposed
refutation DAG contain S nodes. Every node stores at most n
clauses with each clause of length at most three and
variable identifiers <=n. Its bit representation has
length O(n log n) per node (or an equivalent shared
representation). Every inference is verified by:

 - exact input and pin validation;
 - recomputing `residual_normalize` and each claimed
   `residual_choose_one` from first principles;
 - computing connected components for AND nodes;
 - checking all local child references exist and strictly
   decrease in clause count;
 - following only the nodes reachable from the root and
   rejecting additional orphan nodes.

The verifier runs in poly(n,S) BIT time and uses
poly(n,S) BIT memory. For concreteness a naive
straightforward implementation is bounded by
O(S*n^3*polylog n) worst-case bit operations;
no effort is made to optimize this polynomial.
The actual source uses tuple/dictionary operations;
no uncertain floating-point comparisons are made.

**Soundness** follows by induction on decreasing clause
count and the two sound rules. It is NOT necessary to
recompute an NP-complete SAT predicate to verify the
certificate.

Constructing the certificate still involves recursive
SAT search; it may take exponential time or produce
exponentially many nodes. A polynomial verifier by itself
is not a polynomial SAT solver.

## 3. Conditional complexity theorem: polynomial UNSAT certificates imply NP=coNP

Assume there exists an absolute C such that EVERY
unsatisfiable legal square/cubic/linear positive exact-one
instance has an AND/OR residual-DAG refutation of at
most n^C nodes (possibly found by an expensive algorithm).

Then UNSAT for this SCL language belongs to NP:
a purported O(n^(C+1) log n)-bit refutation is a
polynomial-size witness, and the deterministic verifier
above checks it in polynomial time.

Because the corresponding SCL SAT language is NP-complete
by the already independently verified E118 reduction,
every NP language L many-one reduces in polynomial time
to SCL SAT. On NO instances of L, the reduction's
output has such a polynomially checkable UNSAT certificate.
Therefore complement(L) belongs to NP, for EVERY
L in NP, yielding

    NP = coNP.

This is a **conditional implication**, not a contradiction
and not a proof that polynomial certificates do not exist:
NP versus coNP is open.

The stronger assumption that the FIXED deterministic
`ExactSupportResidualDAG` actually discovers at most
n^C distinct states on every UNSAT input and every pinned
slice implies P=NP by the pinned self-reduction proved in
the previous checkpoint. The two assumptions are
NOT EQUIVALENT:
having a short proof (NP=coNP-style certificate existence)
is weaker than being able to find it in deterministic
polynomial time (P=NP).

If one instead proves a superpolynomial lower bound on
MINIMUM refutation size for this exact AND/OR proof system,
then no execution of the frozen algorithm can refute the
corresponding family in polynomial time. That would be
a genuine algorithm-specific lower bound, but would NOT
prove P!=NP because a different polynomial SAT algorithm
could exist.

## 4. Why a Tseitin/regular-resolution bound is not plug-and-play

Known recent literature:

Itsykson, Riazanov, Smirnov, *Tight Bounds for Tseitin
Formulas*, SAT 2022, DOI 10.4230/LIPIcs.SAT.2022.6:
exponential-in-treewidth lower bounds for regular resolution
and OBDD(AND,reordering) refutations on the stated Tseitin
formulas.

Beame, Impagliazzo, Pitassi, Segerlind,
*Formula Caching in DPLL*,
ACM Transactions on Computation Theory 1(3), 2010,
https://eccc.weizmann.ac.il/report/2006/140/:
different formula-caching proof systems have nontrivial
simulations and separations from usual resolution; an
argument about ordinary DPLL/regular resolution cannot
be inherited merely because both methods branch on variables.

There are TWO missing theorems needed to transfer a
relevant lower bound to our concrete proof system:

  (i) a proof-complexity-preserving bounded-degree
      Tseitin-to-LEGAL square+cubic+linear positive exact-one
      reduction (E118 supplies equisatisfiability, but
      equisatisfiability alone is NOT proof-size preservation);

  (ii) a polynomial-time reduction of every legal
       AND/OR residual-DAG refutation of the target to a
       proof in the exact source system whose lower bound
       is established, including arbitrary memo-sharing
       and component decomposition.

Neither is proved here; no imported exponential bound
is claimed.

## 5. Actual certified finite experiments and independent proof verification

Script:
    experiments/r5_universal_exact_support_unsat_andor_certificate.py

Focused CI run:
    #38141654240 = SUCCESS

The script generates a refutation using an independent
recursive search that follows the SAME canonical residual
semantics. It then constructs a completely separate
verifier that NEVER calls recursive SAT search and verifies
EVERY proof node and EVERY branch by exact local rules.
It also checks the same instance with the frozen original
residual-DAG implementation.

Observed distinct counts on four independent controls:

    E61 UNSAT12:           proof 4 nodes; original DAG visited 4
    E123 UNSAT63:          proof 157;     original DAG visited 164
    E123 random 2-lift 126 proof 575;     original DAG visited 585
    E118 UNSAT90:          proof 63;      original DAG visited 75

The refutation may contain fewer nodes than the full
decision trace because a single false component suffices
to prove the conjunction UNSAT, and other SAT components
need no witness in a negative certificate.

These are finite exact certificates, not a
uniform certificate-size upper bound.

## 6. Next necessary all-input target

To refute a polynomial runtime claim for THIS frozen DAG,
construct an infinite legal SCL UNSAT family F_n and prove
S_actual(F_n)>=n^(omega(1)), e.g. from a sound minimal
proof-size lower bound for these AND/OR certificates.

To prove a universal polynomial solver by this method,
constructively show S_actual(F_n,pi)<=n^C
for EVERY legal F_n and EVERY pins pi, with verified
n^C-bit cost and witness self-reduction.

The current finite 2-lift sizes 63/126/252/504 are
NOT either proof, and a polynomial verifier is
NOT the missing polynomial evaluator.

## Scientific gate ledger

EXACT_SCL_ANDOR_UNSAT_CERTIFICATE_SYSTEM = DEFINED.
EXACT_SCL_ANDOR_CERTIFICATE_SOUNDNESS = PROVED_ALL_INPUTS.
CERTIFICATE_VERIFICATION_BIT_RUNTIME_POLYNOMIAL_IN_CERT_LENGTH = PROVED.
E61_E123_E118_ANDOR_FINITE_PROOF_REPLAY = PASSED_FOCUSED_CI.
POLY_UNSAT_CERT_SIZE_FOR_ALL_SCL_IMPLIES_NP_EQ_CONP = PROVED_CONDITIONAL.
POLY_UNSAT_VISITED_FOR_ALL_PINS_IMPLIES_P_EQ_NP = PREDECESSOR_CONDITIONAL.
ALL_INPUT_POLY_UNSAT_CERTIFICATE_SIZE = OPEN.
ALL_INPUT_SUPERPOLYNOMIAL_UNSAT_CERTIFICATE_LOWER_BOUND = OPEN.
ALL_INPUT_POLYNOMIAL_ExactSupport = OPEN.
P_VS_NP = OPEN.
