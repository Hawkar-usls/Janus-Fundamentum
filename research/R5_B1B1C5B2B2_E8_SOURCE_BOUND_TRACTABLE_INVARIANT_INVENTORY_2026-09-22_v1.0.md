# R5 E8 — Source-Bound Tractable Invariant Inventory

Date: 2026-09-22

Authority: `SOURCE_BOUND_INVENTORY_ONLY__NO_SUCCESSOR_AUTHORIZATION__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

PR lineage: `#510 / codex/r5-e8-direct-contract-20260921-82493a57`

Parent authority:

- `research/R5_B1B1C5B2B2_E8_FROZEN_GREEDY_POSTMORTEM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_DUAL_BLOWUP_SURVIVOR_SOURCE_HISTORY_SYNTHESIS_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_DIRECT_SOURCE_AND_FIREWALL_AUDIT_2026-09-21_v1.0.md`
- `research/TRUMP_CONNECTED_MIXED_CARRIER_SCHAEFER_BARRIER_THEOREM_2026-09-15.md`
- `research/TRUMP_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER_THEOREM_2026-09-15.md`
- `research/TRUMP_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO_THEOREM_2026-09-15.md`
- `research/TRUMP_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_THEOREM_2026-09-15.md`

## 0. Purpose and ceiling

The preceding E8 source/history synthesis authorized exactly one next object:

```text
SOURCE_BOUND_TRACTABLE_INVARIANT_INVENTORY_ONLY
```

This document executes that inventory.

The search question is:

```text
Is there a known Boolean / hybrid representation invariant
with all of:

- polynomial recognition / construction,
- polynomial consistency / SAT,
- compact exact representation,
- polynomial existential projection / forgetting,
- polynomial preservation of the invariant,
- arbitrary-CNF universal entry,
- no bounded-parameter assumption,
- no SAT/equivalence oracle hidden in construction?
```

A full hit would already imply a polynomial SAT algorithm: if arbitrary CNF compiles uniformly in polynomial time/size to a representation whose consistency is polynomial, then SAT is in P.

Clay Mathematics Institute still lists P versus NP as unsolved as of 2026-09-22.

Therefore the authoritative verdict of this inventory must be scoped:

```text
FULL D1 HIT
=
NONE FOUND IN THE AUDITED SET
```

not:

```text
NO SUCH INVARIANT EXISTS.
```

## 1. CTRL-TI-1 — Few subpowers / edge polymorphism

### Sources

Foundational representation / edge-term characterization:

Joel Berman, Paweł Idziak, Petar Marković, Ralph McKenzie, Matthew Valeriote, Ross Willard,
“Varieties with few subalgebras of powers,”
Transactions of the AMS 362(3), 2010,
DOI 10.1090/S0002-9947-09-04874-0.

Source:
https://open.uns.ac.rs/handle/123456789/28517

Few-subpowers CSP algorithm summary:

Dmitriy Zhuk,
“The Constraint Satisfaction Problem,” survey/book chapter,
Theorem 73: if the polymorphism clone has few subpowers, CSP is polynomial-time solvable and the algorithm can output a generating set for the full solution set.

Source:
https://drops.dagstuhl.de/storage/02dagstuhl-follow-ups/dfu-vol007/DFU.Vol7.15301/DFU.Vol7.15301.pdf

Short pp-definitions:

Jakub Bulín, Michael Kompatscher,
“Short Definitions in Constraint Languages,”
MFCS 2023, LIPIcs 272, Article 28,
DOI 10.4230/LIPIcs.MFCS.2023.28.

Source:
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2023.28

Fresh neighboring control:

Antonios Kalampakas,
“Automatic constraints with few subpowers and graphoid recognition,”
arXiv:2609.07891, 2026-09-07.

Source:
https://arxiv.org/abs/2609.07891

Status of the last item:

```text
PREPRINT
=
YES
PEER_REVIEWED_STATUS
=
NOT CLAIMED HERE
```

### Positive control

For a fixed finite language with an edge polymorphism / few-subpowers property:

```text
POLY CSP / CONSISTENCY
=
PASS

COMPACT GENERATING REPRESENTATION
OF SOLUTION RELATIONS
=
PASS

PP / EXISTENTIAL STRUCTURE
=
STRONG POSITIVE CONTROL
```

The 2026 automatic-constraint preprint goes even closer to E8: with a common fixed edge operation, it computes compact representations of the complete solution relation and its projections in polynomial time for its automatic-input model.

### Boolean specialization

Bulín–Kompatscher, Theorem 12, gives:

```text
BOOLEAN FEW-SUBPOWERS
=>
QUADRATIC PP DEFINITIONS.
```

Its proof uses the Boolean/Post-lattice classification:

```text
every Boolean few-subpowers language
has either

a Mal'tsev polymorphism

or

the Boolean majority polymorphism.
```

Thus Boolean few-subpowers supplies the strongest audited example where:

```text
TRACTABILITY
+
COMPACT RELATION REPRESENTATION
+
PP / EXISTENTIAL DEFINABILITY
```

coexist.

### Exact blocker for the current mixed core

Internal authority:

`research/TRUMP_CONNECTED_MIXED_CARRIER_SCHAEFER_BARRIER_THEOREM_2026-09-15.md`

Frozen language:

```text
Gamma
=
{ OR2, EVEN_XOR3 }.
```

The repository already independently verifies:

```text
majority
fails EVEN_XOR3

and

affine / minority-style closure
fails OR2.
```

Concrete witnesses:

```text
majority(011,101,110)
=
111
not in EVEN_XOR3

01 XOR 10 XOR 11
=
00
not in OR2.
```

Therefore the unrestricted mixed language does not possess one common Boolean majority/Mal'tsev invariant of the few-subpowers control.

The internal Schaefer classification already seals:

```text
SAT({OR2,EVEN_XOR3})
=
NP-COMPLETE.
```

### Verdict

```text
CTRL-TI-1
=
BOOLEAN_FEW_SUBPOWERS

POLY CONSISTENCY
=
PASS FOR FIXED LANGUAGE

COMPACT SOLUTION REPRESENTATION
=
PASS

PP / EXISTENTIAL STRUCTURE
=
PASS

BOOLEAN SHORT DEFINITIONS
=
PASS, QUADRATIC

UNRESTRICTED MIXED CLAUSAL+AFFINE ENTRY
=
FAIL

FIRST BLOCKER
=
NO COMMON TRACTABLE BOOLEAN
MAJORITY / MALTSEV POLYMORPHISM
FOR THE REQUIRED MIXED LANGUAGE
```

This is the strongest positive algebraic control found in this audit.

## 2. CTRL-TI-2 — q-Horn

### Sources

Endre Boros, Peter L. Hammer, Xiaorong Sun,
“Recognition of q-Horn formulae in linear time,”
Discrete Applied Mathematics 55(1), 1994,
DOI 10.1016/0166-218X(94)90033-7.

Source:
https://www.sciencedirect.com/science/article/pii/0166218X94900337

Yisong Wang,
“On Forgetting in Tractable Propositional Fragments,”
arXiv:1502.02799, 2015.

Source:
https://arxiv.org/abs/1502.02799

### Positive control

Published/source results support:

```text
q-HORN RECOGNITION
=
LINEAR TIME

q-HORN SAT
=
TRACTABLE / LINEAR AFTER RECOGNITION

FORGETTING RESULT
=
q-HORN EXPRESSIBLE

UNIFORM INTERPOLATION
=
YES
```

Wang's Corollary 8 / Corollary 14 gives the expressibility / uniform-interpolation closure for q-Horn.

### Firewall

This does **not** provide the E8 size theorem.

Forgetting expressibility means:

```text
there exists an equivalent q-Horn result
```

not:

```text
a polynomial-time algorithm always emits
a polynomial-size result.
```

General Horn forgetting is known to admit exponential growth phenomena; the modern Horn-forgetting literature explicitly treats exponential size/time as a real obstruction.

Important precision:

```text
HORN EXPONENTIAL GROWTH
IS A WARNING AGAINST
"EXPRESSIBLE => POLY SIZE".

IT IS NOT USED HERE
AS A PROOF THAT EVERY
q-HORN REPRESENTATION
OF THE SAME PROJECTION
MUST BE EXPONENTIAL.
```

### Verdict

```text
CTRL-TI-2
=
q-HORN

RECOGNITION
=
PASS LINEAR

SAT
=
PASS TRACTABLE

FORGETTING EXPRESSIBILITY
=
PASS

UNIVERSAL POLY OUTPUT SIZE / BUILD
=
NOT ESTABLISHED

ARBITRARY-CNF UNIVERSAL ENTRY
=
NO

LESSON
=
CLOSURE UNDER FORGETTING
!=
POLYNOMIAL-SIZE CLOSURE
```

## 3. CTRL-TI-3 — Single-head definite Horn

### Source

Paolo Liberatore,
“One Head is Better than Two: A Polynomial Restriction for Propositional Definite Horn Forgetting,”
Journal of Logic, Language and Information 34, 49–88, 2025,
DOI 10.1007/s10849-025-09428-w.

Source:
https://doi.org/10.1007/s10849-025-09428-w

### Positive control

The source states that arbitrary propositional Horn forgetting may take exponential time / size, while the single-head definite Horn restriction supports polynomial-time forgetting and polynomial-size output.

For interequivalent formulae, the paper gives a polynomial complete route for reconstructing a single-head form when one exists; for unrestricted inputs the conversion algorithm is sound but incomplete.

Thus this is a clean example of the E8 desired pattern:

```text
STRUCTURAL INVARIANT
+
POLY RECOGNITION / CONSTRUCTION
+
POLY FORGETTING
```

on a scoped class.

### Blocker

```text
ARBITRARY CNF ENTRY
=
NO

AFFINE / PARITY COVERAGE
=
NO AS A UNIVERSAL CARRIER

UNRESTRICTED MIXED CORE
=
NO
```

### Verdict

```text
CTRL-TI-3
=
SINGLE_HEAD_DEFINITE_HORN

CONSISTENCY
=
POLY

FORGETTING
=
POLY IN ADMITTED SUBCLASS

OUTPUT SIZE
=
POLY IN ADMITTED SUBCLASS

UNIVERSALITY
=
FAIL / TOO NARROW
```

Method donor, not successor.

## 4. CTRL-TI-4 — beta-acyclic and DP-simplicial elimination

### Source

Sebastian Ordyniak, Daniel Paulusma, Stefan Szeider,
“Satisfiability of acyclic and almost acyclic CNF formulas,”
Theoretical Computer Science 481 (2013), 85–99,
DOI 10.1016/j.tcs.2012.12.039.

Source:
https://www.sciencedirect.com/science/article/pii/S0304397513000054

### Positive control

For beta-acyclic CNF, special Davis–Putnam elimination remains polynomial because each resolvent is a subset of a parent clause.

The authors extend this to formulas having a DP-simplicial elimination order.

### Exact blocker

The same source proves:

```text
DECIDE WHETHER A FORMULA
ADMITS A DP-SIMPLICIAL
ELIMINATION ORDER
=
NP-COMPLETE.
```

Therefore:

```text
GOOD ELIMINATION STRUCTURE EXISTS
!=
GOOD GLOBAL ORDER IS
POLYNOMIALLY DISCOVERABLE.
```

### Verdict

```text
CTRL-TI-4
=
ACYCLIC / DP-SIMPLICIAL

TRACTABLE TERMINAL
=
PASS IN CLASS

GOOD ELIMINATION
=
PASS GIVEN STRUCTURE

GENERAL ORDER EXISTENCE / MEMBERSHIP
=
NP-COMPLETE FOR THE SUPERCLASS

ARBITRARY CNF ENTRY
=
NO
```

This is a direct order-selection control for any successor invariant.

## 5. CTRL-TI-5 — Heterogeneous backdoors

### Source

Serge Gaspers, Neeldhara Misra, Sebastian Ordyniak, Stefan Szeider, Stanislav Živný,
“Backdoors into heterogeneous classes of SAT and CSP,”
Journal of Computer and System Sciences 85 (2017), 38–56,
DOI 10.1016/j.jcss.2016.10.007.

Source:
https://www.sciencedirect.com/science/article/pii/S0022000016301039

### Positive control

Different assignments to a backdoor can land in different tractable base classes.

Thus:

```text
ONE GLOBAL SCHAEFER CLASS
IS NOT THE ONLY KNOWN WAY
TO EXPLOIT HETEROGENEOUS
TRACTABLE STRUCTURE.
```

### Blocker

The theory is parameterized by backdoor structure/size; it does not provide a fixed polynomial universal arbitrary-CNF solver with no parameter bound.

### Verdict

```text
CTRL-TI-5
=
HETEROGENEOUS_BACKDOORS

MIXED TRACTABLE DESTINATIONS
=
YES

TRACTABILITY
=
PARAMETERIZED / SCOPED

UNBOUNDED UNIVERSAL ENTRY
=
NO
```

## 6. CTRL-TI-6 — Few alien constraints

### Source

Peter Jonsson, Victor Lagerkvist, George Osipov,
“CSPs with Few Alien Constraints,”
CP 2024, LIPIcs 307, Article 15,
DOI 10.4230/LIPIcs.CP.2024.15.

Source:
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2024.15

### Positive control

A tractable base language plus at most `k` alien constraints admits a detailed parameterized complexity theory; the paper gives an FPT-versus-pNP dichotomy for arbitrary finite structures and sharper Boolean results.

### Internal anti-duplication binding

This is already represented inside Janus by:

`research/TRUMP_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER_THEOREM_2026-09-15.md`

The internal theorem explicitly admits only the regime:

```text
q^k <= L,
```

so the branch lifecycle is polynomial in original input length.

### Verdict

```text
CTRL-TI-6
=
FEW_ALIEN_CONSTRAINTS

TRACTABLE
=
PARAMETERIZED / SCOPED

UNBOUNDED ALIEN COUNT
=
NO UNIVERSAL POLY CLAIM

INTERNAL STATUS
=
ALREADY REPRESENTED;
DO NOT REDISCOVER
```

## 7. CTRL-TI-7 — Mixed Horn + 2-CNF

### Source

“Satisfiability of mixed Horn formulas,”
Discrete Applied Mathematics 155(11), 2007, 1408–1419,
DOI 10.1016/j.dam.2007.02.010.

Source:
https://www.sciencedirect.com/science/article/pii/S0166218X07000327

### Result

The paper studies a formalism containing a Horn part and a 2-CNF part and proves:

```text
SAT
=
NP-COMPLETE
```

for the unrestricted mixed formalism; arbitrary CNF can be polynomially encoded into it.

### Lesson

```text
TRACTABLE CARRIER A
+
TRACTABLE CARRIER B

!=

TRACTABLE CONNECTED MIXTURE.
```

A successor must constrain cross-carrier interaction, not merely label each local piece as tractable.

This independently reinforces the internal Schaefer mixed-carrier barrier.

## 8. CTRL-TI-8 — Polynomially closed Boolean co-clones

### Source

Victor Lagerkvist, Magnus Wahlström,
“The power of primitive positive definitions with polynomially many variables,”
Journal of Logic and Computation 27(5), 2017, 1465–1488,
DOI 10.1093/logcom/exw005.

Source:
https://academic.oup.com/logcom/article-abstract/27/5/1465/2917866

### Positive control

The paper studies pp-definitions allowing only polynomially many existential variables and defines polynomially closed co-clones.

It proves:

- near-unanimity implies polynomial closure;
- absence of any edge operation implies superpolynomial closure;
- on the Boolean domain there is a complete dichotomy between polynomially and superpolynomially closed co-clones.

### Firewall

This is a result about the expressive cost of pp-definitions / existential variables.

It does **not** by itself imply:

```text
POLY SAT / CONSISTENCY.
```

Therefore:

```text
POLYNOMIAL PP EXPRESSIBILITY
!=
TRACTABLE TERMINAL CONSISTENCY.
```

This is the same type of separation already seen internally with ECNF:

```text
compact mixed definability
can coexist with
NP-hard terminal SAT.
```

## 9. Existing E8 controls that this inventory must not reopen

### ECNF

Authority:

`research/R5_B1B1C5B2B2_E8_DUAL_BLOWUP_SURVIVOR_SOURCE_HISTORY_SYNTHESIS_2026-09-22_v1.0.md`

Already sealed:

```text
ARBITRARY CNF ENTRY
=
PASS LINEAR

PARITY COMPACTNESS
=
PASS

CYCLIC LOCAL PROJECTION COMPACTNESS
=
PASS

TERMINAL CONSISTENCY
=
NP-HARD
```

Do not rediscover compact mixed syntax as a successor.

### EADT

Already sealed in the same synthesis:

```text
TRACTABLE COMPILED OBJECT
+
AFFINE-AWARE DECISIONS

BUT

GENERAL FORGETTING
=
NOT POLY UNLESS P=NP

AND

UNIVERSAL POLY CNF->SMALL EADT
=
NOT ESTABLISHED.
```

### AFF[OR]

Already sealed as a strong representation control:

```text
POLY CONSISTENCY
=
YES ON COMPILED OBJECT

POLY FORGETTING
=
YES

AFFINE-NATIVE
=
YES

UNIVERSAL POLY
ARBITRARY-CNF COMPILATION
=
NOT ESTABLISHED.
```

Any universal polynomial compiler would already imply SAT in P.

### CNF[exists] / existential closures

Already sealed hidden-existential lesson:

```text
EASY ENTRY
+
EASY SYNTACTIC FORGETTING

!=

SEMANTIC CHOICE ELIMINATION
+
TRACTABLE TERMINAL CONSISTENCY.
```

## 10. Inventory matrix

| Candidate | Recognition / construction | SAT / consistency | Projection / forgetting | Compactness | Universal arbitrary-CNF entry | First exact blocker |
|---|---|---|---|---|---|---|
| Fixed Schaefer language | poly for fixed language | poly in tractable cases | pp-semantic closure | language-dependent | no for required unrestricted mixed core | mixed language crosses dichotomy |
| Boolean few-subpowers | fixed-language algebraic condition | poly | strong pp/projection control | compact generators; quadratic Boolean pp definitions | no | required OR2+XOR mix has no common majority/Mal'tsev invariant |
| q-Horn | linear recognition | poly / linear | q-Horn-expressible | universal poly output not established | no | expressibility closure is not a size theorem |
| Single-head definite Horn | syntactically easy; some equivalent-form construction poly on interequivalent class | poly | poly in admitted subclass | poly output in admitted subclass | no | too narrow; no universal affine/mixed coverage |
| beta-acyclic | recognizable | poly | special DP elimination | scoped | no | structure not universal |
| DP-simplicial superclass | good order verifies locally | poly given order | poly given order | scoped | no | order-existence / membership NP-complete |
| Heterogeneous backdoors | parameterized | parameterized | assignment-based | parameterized | no unbounded guarantee | backdoor parameter |
| Few alien constraints | parameterized | parameterized | carrier-specific | parameterized | no unbounded guarantee | alien count |
| Polynomially closed co-clones | pp expressivity classification | not implied | compact existential-variable definitions | polynomial existential count in admitted cases | not a SAT solver | compact definability != consistency |
| ECNF | easy syntax | NP-hard | compact on audited parity/cyclic controls | strong mixed expressivity | linear | terminal consistency |
| EADT | compiled target | poly on compiled object | general forgetting barrier | affine-aware | universal poly compilation not established | forgetting / compilation |
| AFF[OR] | compiled target | poly | poly forgetting | strong | universal poly compilation not established | compiler |
| CNF[exists] | trivial entry | hard | syntactically easy forgetting | yes by hidden quantifiers | yes | terminal semantic choice remains hard |

## 11. Strongest positive control

The strongest audited answer to:

```text
Can compact relation representation,
projection,
and tractable consistency
coexist in known mathematics?
```

is:

```text
YES

FEW SUBPOWERS / EDGE POLYMORPHISM
```

with the especially clean Boolean specialization:

```text
BOOLEAN FEW-SUBPOWERS
=
MAJORITY SIDE
OR
MALTSEV SIDE

+
QUADRATIC PP DEFINITIONS.
```

The 2026 automatic-constraints preprint strengthens this as a contemporary control by explicitly constructing compact solution relations and projections under a common fixed edge operation.

The blocker is not that compact projection-friendly algebra is impossible.

The blocker is:

```text
THE REQUIRED UNRESTRICTED
MIXED CLAUSAL + AFFINE CORE
DOES NOT SHARE ONE SUCH
BOOLEAN TRACTABLE POLYMORPHISM.
```

## 12. Anti-loop synthesis

This inventory rules out several **forms of rediscovery**, not mathematical possibilities.

A future successor must not be merely:

```text
"all constraints belong to one
fixed tractable global language"
```

because the audited Boolean algebraic territory already captures the strongest few-subpowers control and the required mixed core exits that shared polymorphism regime.

It must not be merely:

```text
"forgetting stays in Horn/q-Horn/etc."
```

because expressibility closure is weaker than a uniform polynomial build/size theorem.

It must not be merely:

```text
"different pieces use different tractable languages"
```

because unrestricted mixtures of tractable pieces can already be NP-complete.

It must not be merely:

```text
"only k pieces are alien"
```

unless the parameter is charged to original input length strongly enough to yield one fixed polynomial.

## 13. Only non-duplicative shape left by this inventory

If a later theorem hunt is ever unlocked, the source/history evidence says the missing object would need to look more like an:

```text
INSTANCE-SPECIFIC
COMPOSITIONAL INVARIANT
```

rather than one fixed global constraint language.

Necessary obligations would include:

```text
1. local pieces admitted to
   known tractable carriers /
   polymorphism types;

2. unlike-piece interaction represented
   by a polynomial certificate;

3. existential projection updates
   that certificate in polynomial time;

4. aggregate certificate/state size
   remains poly(original L);

5. no bounded-parameter assumption;

6. no exponential interface enumeration;

7. no SAT/equivalence oracle;

8. universal arbitrary-CNF entry
   if D1 is claimed.
```

However, Janus already has scoped internal versions of this philosophy:

- factorized feedback-interface portfolio;
- exact interface quotient/basis;
- logarithmic alien-constraint transfer;
- affine boundary transfer;
- guarded bounded-output elimination.

Therefore this shape is **not authorized as a new successor merely by naming it**.

It would require a new theorem-level invariant genuinely beyond those scoped predecessors.

## 14. Final source-bound verdict

```text
R5_E8_SOURCE_BOUND_TRACTABLE_INVARIANT_INVENTORY_V1

SEARCH_SCOPE
=
KNOWN TRACTABLE /
PROJECTION-AWARE BOOLEAN
AND HYBRID INVARIANTS

FULL D1 HIT
=
NONE FOUND IN AUDITED SET

STRONGEST POSITIVE
ALGEBRAIC CONTROL
=
FEW SUBPOWERS /
EDGE POLYMORPHISM

BOOLEAN FEW-SUBPOWERS
=
MAJORITY OR MALTSEV SIDE
+
QUADRATIC PP DEFINITIONS

FRESH 2026 POSITIVE CONTROL
=
AUTOMATIC CONSTRAINTS
WITH COMMON FIXED EDGE OPERATION
(PREPRINT)

q-HORN
=
TRACTABLE
+
FORGETTING-EXPRESSIBLE
BUT NO UNIVERSAL POLY
OUTPUT/ENTRY THEOREM FOUND

SINGLE-HEAD HORN
=
REAL POLY-FORGETTING
SUBCLASS
BUT TOO NARROW

ACYCLIC / DP-SIMPLICIAL
=
TRACTABLE STRUCTURE
BUT UNIVERSAL GOOD-ORDER
DISCOVERY FAILS

HETEROGENEOUS / FEW-ALIEN
=
KNOWN PARAMETERIZED /
SCOPED ROUTES

MIXED TRACTABLE PIECES
=
CAN BE NP-HARD

POLYNOMIAL PP DEFINABILITY
=
DOES NOT IMPLY
TRACTABLE CONSISTENCY

ECNF-LIKE UNIVERSAL
MIXED SYNTAX
=
TERMINAL HARDNESS

KNOWN COMPILED
TRACTABLE TARGETS
=
ENTRY / COMPILATION
OR TRANSFORMATION BLOCKER

SUCCESSOR_ALGORITHM
=
KEEP LOCKED

D1
=
EMPTY

P_VS_NP
=
OPEN
```

## 15. Next authorization

```text
NO NEW SUCCESSOR ALGORITHM AUTHORIZED.

NO NEW REPRESENTATION HUNT AUTHORIZED.

NO D1 PROMOTION.

NO P=NP OR P!=NP CLAIM.

Allowed next action only after explicit strategic review:
compare any proposed instance-specific compositional invariant
against this inventory and all named internal predecessors
before opening a theorem gate.
```
