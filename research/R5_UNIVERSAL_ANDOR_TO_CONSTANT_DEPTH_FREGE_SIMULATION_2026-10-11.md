# R5 — Polynomial Simulation of JANUS ExactCover AND/OR Refutations by Constant-Depth Frege

Date: 2026-10-11
Research branch: research/parity-isolation-trade-checkpoint-20261009, PR #515
Scope: the exact **labelled residual-DAG AND/OR refutation system**
in `experiments/r5_universal_exact_support_unsat_andor_certificate.py`,
NOT other caching proof systems with additional substitution/extension rules.

**PROVED THEOREM:** A size-S valid JANUS exact-cover AND/OR refutation
of an n-variable 3-uniform source can be translated in
`poly(n,S)` bit time into a constant-depth Frege
refutation of the standard 3-CNF exact-one encoding.
A safe depth upper bound is a fixed constant (e.g. 6)
and the translation uses a polynomial number of formula symbols.

**CRITICAL LIMIT:** This theorem supplies ONE SIMULATION
direction. It does not itself exhibit a legal SCL family
which is exponentially hard for constant-depth Frege,
nor does it prove a large minimum JANUS proof.
A proof-complexity-preserving Tseitin/graph-tautology
gadget reduction INTO LEGAL square+cubic+linear
positive Exact-One remains OPEN.

Universal polynomial ExactSupport: NOT CONSTRUCTED.
Superpolynomial JANUS AND/OR minimum proof lower bound: OPEN.
P_VS_NP: OPEN.

## 1. Every residual state has a small depth-2 violation formula

Let `S` be the residual hypergraph with at most n clauses,
each an Exact-One constraint on 1, 2 or 3 Boolean variables.

Encode one exact-one row C={x_1,...,x_k}, 1<=k<=3, by

    E_C := (x_1 OR ... OR x_k)
           AND_{i<j} (NOT x_i OR NOT x_j).

The whole residual formula is the bounded-width CNF

    F_S := AND_{C in S} E_C.

It has at most 4n clauses, each of width<=3.
Define the **violation DNF**

    D_S := NOT F_S.

After De Morgan expansion, D_S is a disjunction of at most
4n conjunctions of <=3 literals, hence constant depth=2
and length O(n). Note that proving UNSAT(S) is exactly
proving the propositional tautology D_S.

The refutation DAG contains S distinct labelled-state nodes.
The same literal *text* D_S is reused in the Frege proof
for every cache reference to S. It is NEVER expanded into
a separate copy of a whole subtree just because the search
graph has multiple incoming edges.

## 2. AND rule is a polynomial constant-depth step

For a parent state S with disjoint components S_1,...,S_k,
a certificate may name any unsatisfiable component S_i.
Because S_i is a literal subset of S,

    F_S -> F_{S_i}

and therefore

    D_{S_i} -> D_S.

In fact D_{S_i} is a sub-disjunction of the same
constant-width violation terms appearing in D_S.
Adding the remaining disjuncts is ordinary DNF
weakening. The derivation uses O(n) constant-depth
Frege lines/symbols and requires no repeated
derivation of the already proved D_{S_i}.

## 3. OR rule is an explicit bounded-local case split

Let S be connected and C a selected clause (size k<=3).
For each v in C, define the local assignment term

    A_v = x_v AND AND_{u in N_S(v)} NOT x_u,

where N_S(v) denotes every variable sharing any
remaining clause with v. Every original variable
has degree at most three (the residual operation
only deletes clauses/variables); thus

    |N_S(v)| <= 6.

The term A_v is a conjunction of at most seven literals.

If v is chosen, every S-clause containing v is satisfied
and removed; all N_S(v) variables are set to zero.
Every other clause is shortened by these zeros; if
some shortened clause is empty, that branch is
immediately contradictory. The remaining formula
is exactly F_(S/v).

This yields a syntactically checkable local implication:

    F_S AND A_v -> F_(S/v).                     (1)

No SAT solver or global semantic inference is needed to
derive (1): every child exact-one clause comes from a
single parent exact-one clause by substituting 0 for
the explicitly listed forbidden variables. Every
relevant CNF clause is a constant-width consequence
under A_v. At most O(n) such substitutions are required.

Contraposition of (1) yields

    D_(S/v) -> (D_S OR NOT A_v).                (2)

When S/v is immediately contradictory, (D_S OR
NOT A_v) follows directly from a parent clause
whose entire set is forbidden by A_v.

A valid AND/OR certificate supplies D_(S/v) as a
previously established tautology for every
non-immediate child. Thus via (2) derive

    D_S OR NOT A_v                              (3)

for EVERY v in C. At most THREE such lines are needed.

Furthermore F_S implies that exactly one v in C is
1, and all variables sharing another S-clause with v
are 0. Hence there is a short local tautology

    D_S OR OR_{v in C} A_v.                     (4)

Combine (3) for all v and (4) by at most three
Boolean case-split steps (distributivity or a
fixed truth-table Frege derivation in k<=3
local selector literals). This derives D_S.

**Depth and size:** D_S has depth 2 and size O(n).
Each A_v has depth 1 and O(1) literals (degree<=3).
Equations (1)-(4), their constant-width local
instances and all case-split intermediate formulas
have depth bounded by a fixed constant; depth six
is a conservative upper bound. Their total
symbol count is O(poly(n)) per parent node and
they can be generated deterministically from the
labelled residual transitions. No formula nests
an earlier proof in its own syntax.

## 4. Root and pinned assignment handling

For an original legal SCL formula A, S_root is just
its Exact-One rows, and D_Sroot is the standard
constant-depth CNF-negation tautology.

For arbitrary Boolean pins pi, their unit literals
are appended to the original CNF and the initial
residual root is produced by substitution.
Exactly the same O(n) local implication argument
converts D_(S_root) into a refutation of
F_original AND pi. Contradictory pins themselves
yield a constant-size propositional contradiction.

Thus the simulation works for EVERY valid pinned
residual AND/OR certificate, not only unpinned E123.

## 5. Complexity and what the theorem does NOT show

Take an AND/OR proof DAG with S distinct canonical
states and at most three labelled outgoing branches
per OR node. Every state has <=n clauses and each
label uses O(log n) bits. A straightforward Frege
translation has length and generation bit cost
O(S*n^C) for a fixed small C, e.g. C=4
safely covers repeated formula transcription and
polynomial syntactic derivation templates. Formula
depth is at most a FIXED constant (e.g. six).

Therefore if any unsatisfiable LEGAL SCL family
is shown to need superpolynomial constant-depth
Frege proofs, the same family needs
superpolynomial JANUS AND/OR residual certificates,
because a hypothetical short JANUS certificate
would translate to a short Frege refutation.

The celebrated bounded-depth Frege lower bounds for
Tseitin graph contradictions do NOT yet supply such
a hard LEGAL SCL family. A new proof-complexity
preserving reduction/substitution is needed.

In particular, E118's SAT-preserving gadget reduction
is NOT, just by being equisatisfiable, a proof-size
preserving reduction for bounded-depth Frege.
One must supply a polynomial-size local substitution
mapping any proof of the target back to a proof of the
source, with an explicit bound on depth and bit size.

## 6. Executable local template checker

    python experiments/r5_universal_andor_constant_depth_frege_local_templates.py

For E61 UNSAT12, E123 UNSAT63 and E118 UNSAT90:
generate the exact memoized AND/OR negative DAG, independently
verify it with the existing checker, then audit every
AND-component subset implication and every OR-child
parent-to-residual clause implication.

Each OR branch is checked against the exact forbidden
neighbors N_S(v); every child clause must match an
explicit parent clause shortened by those zeros.
The chosen selector clause and immediate empty-branch
cases are checked too. These are the symbolic LOCAL
premises of (1)-(4).

Finite regression validates the construction, while
the all-input simulation theorem follows from the
bounded-clause, bounded-occurrence algebraic argument,
not empirical testing.

## Literature and claim boundary

- Beame, Impagliazzo, Pitassi and Segerlind,
  *Formula Caching in DPLL*, ACM TOCT 2010,
  https://eccc.weizmann.ac.il/report/2006/140/
  (different formula-caching extensions may be more powerful
  than the present two-rule JANUS proof system).
- Itsykson, Riazanov and Smirnov,
  *Tight Bounds for Tseitin Formulas*, SAT 2022,
  https://doi.org/10.4230/LIPIcs.SAT.2022.6
  (regular resolution and OBDD(AND,reordering)).
- *Bounded-depth Frege complexity of Tseitin formulas for all graphs*,
  Annals of Pure and Applied Logic 174 (2023), 103166,
  https://doi.org/10.1016/j.apal.2022.103166
  (bounded-depth Frege lower bounds for the specified
  Tseitin CNF formulas).
- *Proof Complexity Meets Algebra*, ICALP 2017,
  https://doi.org/10.4230/LIPIcs.ICALP.2017.110
  (standard CSP reductions and proof complexity;
  does not automatically cover every SCL incidence promise).

## Gate ledger

JANUS_AND_OR_REFUTATION_TO_DEPTH6_FREGE_POLY_SIMULATION = PROVED.
AND_NODE_DNF_WEAKENING = PROVED.
OR_NODE_LOCAL_IMPLICATION_AND_CASE_SPLIT = PROVED.
SHARED_STATE_DAG_NO_PROOF_TREE_EXPANSION = PROVED.
SOURCE_TSEITIN_TO_LEGAL_SCL_BOUNDED_DEPTH_PROOF_PRESERVATION = OPEN.
SUPERPOLYNOMIAL_LEGAL_SCL_BOUNDED_DEPTH_FREGE_LOWER_BOUND = OPEN.
SUPERPOLYNOMIAL_JANUS_AND_OR_MINIMUM_PROOF_SIZE = OPEN.
POLYNOMIAL_UNIVERSAL_ExactSupport = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
