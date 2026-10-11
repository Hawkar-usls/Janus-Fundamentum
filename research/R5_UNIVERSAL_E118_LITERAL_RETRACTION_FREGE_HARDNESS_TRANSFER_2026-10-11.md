# R5 — E118 Literal Retraction: PROVED Frege-Hardness Transport for Any Cubic Source

Date 2026-10-11. Repository Hawkar-usls/Janus-Fundamentum.
Branch research/parity-isolation-trade-checkpoint-20261009, PR #515.

## Scientific verdict

**NEW PROVED ALL-SOURCE TRANSFER LEMMA:**
For ANY source instance F consisting of n distinct 3-variable
Positive Exact-One clauses on n variables, each variable occurring
exactly three times, the E118 construction T(F) consists of exactly
10n 3-variable clauses/10n variables, each variable has occurrence
degree three, and any two clauses meet in at most one variable.

More importantly, there is a literal/constant SUBSTITUTION sigma
mapping target variables to the original source variables or
their negations or Boolean constants such that

    sigma(CNF(T(F))) = CNF(F) AND (Boolean tautologies).

This yields a size-linear/polytime reduction from ANY depth-d
Frege refutation of T(F) to a depth-at-most-d+O(1)
Frege refutation of F. Substitution never increases the depth
in standard bounded-depth Frege presentations with negation
normalization. In particular if a family of CUBIC 3-uniform
source formulas has superpolynomial bounded-depth Frege
proof-size lower bounds, its legal square/cubic/linear
E118 images retain the lower bounds up to a polynomial
factor in instance size.

This closes **one of two previously missing proof-complexity
transport arrows**. The remaining arrow is NOT proved:
provide a concrete HARD CUBIC source family, not merely
an arbitrary finite-template CSP or Tseitin source.
Satisfiability-preserving cubicization does not
automatically preserve bounded-depth Frege complexity.

The universal polynomial ExactSupport and SolveLinearCubicXSAT
are NOT constructed. The desired superpolynomial lower
bound on JANUS AND/OR certificates is NOT yet proved.
P vs NP remains OPEN.

## I. Exact gadget substitution

E118 uses ports (x,y,z), internal (a,b,c,d,e,f,g),
and nine exact-one rows

    (d,f,g), (z,c,e), (y,e,f),
    (x,b,f), (z,a,b), (a,e,g),
    (x,a,d), (y,c,d), (b,c,g).

The gadget's SAT relation is the EQUAL3 relation at ports,
with 2 internal extensions for port 0 and 1 for port 1.
Previous E118 only needed this existential relation.

Here we define a **uniform deterministic choice of internal
extension**, which exists for EVERY Boolean port value v:

    x=y=z=g = v;
    a=c=f = 0;
    b=d=e = NOT v.

Substituting these values into ALL nine exact-one equations,
each row becomes

    v + (1-v) + 0 = 1

possibly with permuted summands, and is a Boolean tautology.
No assumption about whether the original F is SAT is needed
for the substitution: the nine identities hold for BOTH v=0
and v=1. Thus the retraction is a genuine syntactic
substitution of Boolean variables, not a SAT witness
selected by solving an NP-hard constraint.

## II. Whole-target retraction

For each source variable v (occurring in exactly three source
clauses), split its three occurrences into 3 distinct E118
ports v_occ0,v_occ1,v_occ2. Put the nine-row EQUAL3 gadget
on these ports with the seven internal variables.

Define sigma for each v by

    sigma(v_occ0)=sigma(v_occ1)=sigma(v_occ2)=v,
    sigma(G_v_g)=v,
    sigma(G_v_a)=sigma(G_v_c)=sigma(G_v_f)=0,
    sigma(G_v_b)=sigma(G_v_d)=sigma(G_v_e)=NOT v.

Then each transformed SOURCE clause becomes literally
the corresponding original Exact-One clause on v,w,t.
Every GADGET clause becomes a tautology.

For the exact-one CNF representation

    EO(u,v,w)
        = (u OR v OR w)
          AND (NOT u OR NOT v)
          AND (NOT u OR NOT w)
          AND (NOT v OR NOT w),

the substitution of a gadget EO yields true for both values
of its single source variable. Its CNF clauses are
individually Boolean tautologies after simplification,
possibly in more than one syntactic clause.

Therefore sigma(CNF(T(F))) is precisely CNF(F) with
O(n) trivial tautological clauses, removable in polynomial
time by standard propositional weakening/constant axioms.

## III. Proof-size transport lemma

Suppose T(F) has a refutation P of size S in a fixed
bounded-depth Frege proof system over AND/OR/NOT.
Apply sigma to EVERY proof line and simplify all
constants and double negations in each line.

All axioms and Frege inference schemata are closed under
uniform substitution. Any target-input axiom becomes
either an original F axiom or a Boolean tautology
provable in O(1) or O(poly(n)) fixed-depth steps.
All deduction steps remain valid; the final
contradiction remains contradiction.

Each target variable is replaced by exactly ONE
source literal or one constant, so no line grows
asymptotically under sigma. Total length and depth
change by at most polynomial size and an additive
fixed depth constant (or no increase with appropriate
NNF convention). This yields

    Size_Frege_d+O(1)(F) <= poly(n, Size_Frege_d(T(F))).

Consequently any known superpolynomial lower bound
for depth-d+O(1) Frege refutations of CUBIC F transfers
to depth-d Frege for legal SCL T(F).

Combining with the predecessor
`R5_UNIVERSAL_ANDOR_TO_CONSTANT_DEPTH_FREGE_SIMULATION_2026-10-11.md`:

    (hard bounded-depth Frege CUBIC source family)
           => (hard bounded-depth Frege legal E118 SCL family)
           => (superpolynomial JANUS cached AND/OR refutation size).

**One leg remains unproved.** Neither the Atserias–Ochremiak
finite-CSP gap theorem for unrestricted occurrence counts
nor the Galesi–Itsykson–Riazanov–Sofronova Tseitin
depth-d lower bound directly states that their hard
instances are 3-uniform, **3-regular** positive Exact-One
source hypergraphs. A uniform proof-complexity-preserving
degree-three regularization is still the critical
construction task.

## IV. Literature audit and exact transfer scope

1. Albert Atserias and Joanna Ochremiak,
   *Proof Complexity Meets Algebra* (2019),
   ACM TOCL 20(1), DOI 10.1145/3265985.
   Finite-CSP pp-interpretability preserves
   bounded-depth Frege proof complexity; a CSP
   language is either bounded-width or has hard
   unrestricted-input families for bounded-depth Frege.
   Source: https://arxiv.org/abs/1711.07320

2. Nicola Galesi, Dmitry Itsykson, Artur Riazanov,
   Anastasia Sofronova,
   *Bounded-depth Frege complexity of Tseitin formulas
   for all graphs* (2023), APAL 174(1):103166.
   The theorem supplies lower bounds depending on
   treewidth of Tseitin graph, for depth d.
   DOI 10.1016/j.apal.2022.103166.

3. E118 proof-carrying equal-three gadget:
   experiments/r5_e118_universal_linear_cubic_exactone_hardness_bridge.py

The new explicit sigma closes target-to-cubic-source
proof-transport exactly, with no unexplained gadget
extension variables. But no new theorem makes the
full NP-complete E118 input class hard for bounded-depth
Frege without a hard cubic source construction.

## V. Reproducible mathematical checker

    python experiments/r5_universal_e118_literal_substitution_frege_retraction.py

The checker:
- uses the E118 canonical nine-row gadget;
- verifies for BOTH Boolean v assignments and all
  9 rows that the substituted sum is exactly 1;
- symbolically asserts each row contains exactly the
  three terms {0,v,NOT v}, up to permutation;
- constructs complete E118 targets from:
  K4 cubic source n=4, cyclic q9 source SAT,
  cyclic q9 source UNSAT;
- checks square size 10n, literal-substitution
  cardinality and restored original rows;
- independently enumerates all 2^n source assignments
  on these finite fixtures and verifies pointwise
  source SAT iff retracted target SAT.

This finite test is not a proof of asymptotic hard
families. The all-input substitution theorem follows
from the nine symbolic identities.

## Gate ledger

E118_LOCAL_VARIABLE_RETRACTION_LITERAL_CONSTANT = PROVED_ALL_SOURCES.
E118_10N_LEGAL_SCL_TARGET = PREDECESSOR_PROVED.
E118_FREGE_PROOF_SIZE_TRANSFER_FROM_TARGET_TO_CUBIC_SOURCE = PROVED.
E118_BOUNDED_DEPTH_TRANSFER_WITH_O1_OVERHEAD = PROVED.
UNRESTRICTED_CSP_HARD_TO_CUBIC_SOURCE_PROOF_PRESERVATION = OPEN.
LEGAL_SCL_SUPERPOLYNOMIAL_BOUNDED_DEPTH_FREGE_LOWER_BOUND = OPEN.
JANUS_ANDOR_SUPERPOLYNOMIAL_REFUTATION_LOWER_BOUND = OPEN.
UNIVERSAL_POLYNOMIAL_ExactSupport = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
