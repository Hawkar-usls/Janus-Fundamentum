# R5 E8 — AIG QE and internal anti-duplication source audit

Date: 2026-09-22

Authority: `SOURCE_AUDIT_AND_INTERNAL_HISTORY_BINDING_ONLY__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

PR lineage: `#510 / codex/r5-e8-direct-contract-20260921-82493a57`

## Purpose

Prevent E8 from rediscovering already-known external AIG quantification / scheduling machinery or already-sealed internal JANUS proof skeletons under new names.

This audit does **not** prove the current greedy structural-AIG theorem, does not establish an arbitrary-n counterfamily, and does not change `P_VS_NP = OPEN`.

## External prior art — frozen claim map

### E-AIG-1 — Circuit-based existential quantification is prior art

Cabodi, Crivellari, Nocco, Quer, *Circuit Based Quantification: Back to State Set Manipulation within Unbounded Model Checking* (DATE 2005).

Primary/author repository metadata:
https://iris.polito.it/handle/11583/1848894

Accessible full-text mirror:
https://www.researchgate.net/publication/4125306_Circuit_Based_Quantification_Back_to_State_Set_Manipulation_within_Unbounded_Model_Checking

Audited claim boundary:

- circuit/non-canonical state-set representations are used for quantifier elimination;
- the work explicitly targets compaction after existential quantification;
- equivalence checking and logic synthesis are used to control representation growth.

Therefore:

```text
AIG/CIRCUIT COFACTOR QUANTIFICATION
=
KNOWN PRIOR ART

REPRESENTATION GROWTH AFTER QUANTIFICATION
=
KNOWN PROBLEM

SEMANTIC / SYNTHESIS COMPACTION
=
KNOWN PRACTICAL RESPONSE
```

### E-AIG-2 — AIG quantifier scheduling and BDD sweeping are prior art

Pigorsch, Scholl, Disch, *Advanced Unbounded Model Checking Based on AIGs, BDD Sweeping, And Quantifier Scheduling* (FMCAD 2006), DOI 10.1109/FMCAD.2006.4.

Accessible source:
https://www.researchgate.net/publication/220884367_Advanced_Unbounded_Model_Checking_Based_on_AIGs_BDD_Sweeping_And_Quantifier_Scheduling

Audited claim boundary:

- AIG quantifier scheduling is explicit prior art;
- the method estimates candidate elimination result sizes and chooses an elimination order;
- BDD sweeping / functional reduction are part of the practical compaction stack.

Therefore:

```text
GREEDY SIZE-AWARE QUANTIFIER SCHEDULING
=
KNOWN ENGINEERING MECHANIC

BDD/FUNCTIONAL SWEEPING
=
KNOWN

NOVELTY CANNOT BE CLAIMED
FOR THE ONE-STEP SCHEDULING MECHANIC ITSELF
```

The current E8 theorem path deliberately forbids semantic-equivalence merging, SAT sweeping and unbounded BDD sweeping. Published node counts obtained under stronger semantic compaction are reference controls only, not node-for-node replay targets.

### E-AIG-3 — symbolic OBDD QE lower bounds are a neighboring-model control only

Berkholz, Mengel, Nordström et al., *On Limits of Symbolic Approach to SAT Solving*, SAT 2024.

Primary:
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SAT.2024.19

Audited claim:

- exponential lower bounds are proved for `OBDD(AND, EXISTS, reordering)`;
- binary pigeonhole formulas are among the hard families.

Firewall:

```text
OBDD SYMBOLIC-QE LOWER BOUND
DOES NOT AUTOMATICALLY TRANSFER TO
GENERAL STRUCTURAL AIG QE

WITHOUT AN EXPLICIT SIMULATION THEOREM.
```

### E-KC-1 — representation must be audited jointly for succinctness and transformations

Darwiche, Marquis, *A Knowledge Compilation Map*, JAIR 17 (2002).

Primary/arXiv:
https://arxiv.org/abs/1106.1819

Audited relevance:

- target representations are evaluated jointly by succinctness and supported polynomial-time queries / transformations;
- existence of a semantic transformation is not sufficient when the target representation grows superpolynomially.

This is the external representation firewall already used throughout E8.

## Internal Janus-Fundamentum anti-duplication map

### I-C023 — exact residual/cache DAG is already an explicit internal object

Path:
`docs/C023_FORMULA_CACHING_CALCULUS.md`

Already established:

- exact residual states and byte-identical cache reuse are explicit;
- structural/exact cache sharing is distinguished from stronger reason/semantic reuse;
- finite residual DAG evidence is not promoted into an asymptotic theorem.

Do not relabel exact residual/cache DAG mechanics as a new E8 representation mechanism.

### I-C023R — serial-diamond multiplicity skeleton already exists

Path:
`docs/TRUMP_DEVELOPMENT_JOURNAL_ENTRIES/2026-09-15_C023R_REACHABLE_COSET_AND_EXECUTION_DAG_GATE.md`

Already established for a **different counted object**:

```text
m(v)
=
number of directed root-to-v execution-DAG paths

mu(v)
=
sum_{u!=root}(indeg(u)-1)
=
|E|-|V|+1

m(v) <= 2^{mu(v)}
```

and a linear sequence of compatible exact serial diamonds would force `2^{Omega(L)}` execution histories.

Reuse rule:

```text
C023R SERIAL-DIAMOND COUNTING
=
SIBLING PROOF SKELETON

NOT
=
A THEOREM ABOUT LIVE AIG ROOTS
```

The E8 selector-prefix amplifier counts reachable structural AIG refs, not execution histories. A separate branch-root injectivity/persistence proof remains mandatory.

### I-U1 — coordinate separation already gives 2^k exact classes

Path:
`research/TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_THEOREM_CANDIDATE_2026-09-15.md`

Theorem U1 already proves:

```text
k coordinate observables
separate all assignments in {0,1}^k

=>

2^k exact downstream-equivalence classes.
```

Reuse rule:

```text
EQ_k TAG DISTINGUISHABILITY
=
APPLICATION OF AN ALREADY-KNOWN JANUS SEPARATION SKELETON

NEW E8 CONTENT, IF ANY,
=
PROVE THOSE DISTINCTIONS SURVIVE
THE FROZEN STRUCTURAL-AIG GRAMMAR
AS DISTINCT REACHABLE REFS.
```

### I-FACT — independent factorized payload is already sealed

Path:
`research/TRUMP_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO_THEOREM_2026-09-15.md`

Already sealed:

- exact cross-independence / component separation permits additive portfolio storage;
- a Cartesian product must not be materialized when the exact dependency contract factors.

Therefore any E8 shared-payload family that decomposes under the already-sealed dependency criterion is not a new anti-explosion mechanism; it falls back to the factorized-portfolio route.

### I-GUARD — bounded-output guarded elimination is already sealed

Path:
`research/TRUMP_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_THEOREM_2026-09-15.md`

Already sealed:

- exact elimination is polynomial on the scoped route only when every bucket passes a polynomial original-input output guard;
- overbudget buckets return `OPEN` before materialization;
- bounded-output guards do not solve general elimination.

Therefore E8 must not treat a finite or scoped bounded-output observation as a universal projector theorem.

### I-REP — semantic irrelevance is not syntactic disappearance

Path:
`docs/TRUMP_DEVELOPMENT_JOURNAL_ENTRIES/2026-09-15_CAPTAIN_OBVIOUS_C023R_REPRESENTATION_CORRECTION_AND_TAIL_BALANCE.md`

Already corrected internally:

```text
SEMANTIC IRRELEVANCE
!=
SYNTACTIC DISAPPEARANCE
```

This is directly relevant to structural-only AIG QE: a semantically simple projected function may remain structurally large under the frozen rewrite grammar.

## Novelty firewall after this audit

```text
SHANNON f|0 OR f|1
=
KNOWN

AIG STRUCTURAL SHARING
=
KNOWN

QUANTIFIER SCHEDULING
=
KNOWN

ONE-STEP SIZE-AWARE GREEDY
=
KNOWN ENGINEERING FAMILY

BDD / FRAIG / SAT COMPACTION
=
KNOWN BUT FORBIDDEN ON THE THEOREM PATH

t INDEPENDENT BINARY DISTINCTIONS -> 2^t OBJECTS
=
STANDARD / INTERNALLY C023R-U1-LIKE PROOF SKELETON

FACTORIZED PAYLOAD ESCAPE
=
ALREADY SEALED INTERNALLY

BOUNDED-OUTPUT GUARD
=
ALREADY SEALED INTERNALLY
```

Potential new scoped result is restricted to:

```text
A)
A FORMAL UNIVERSAL POLY-PEAK THEOREM
FOR THE EXACT FROZEN STRUCTURAL-ONLY SELECTOR

OR

B)
AN EXPLICIT ARBITRARY-N COUNTERFAMILY
FOR THAT EXACT SELECTOR.
```

## Current non-duplication target

The cyclic shared-payload finite diagnostics are not promoted.

The next mathematical target is:

```text
m_r = 2^r

prove or refute:

t(m_r) >= alpha * m_r

for one fixed alpha > 0,

where t(m) is the number of selector eliminations
before payload cleanup breaks the branch-separation invariant
under the exact frozen executor.
```

A proof must compare every competing unresolved variable using the exact frozen key

```text
(projected_reachable_nodes, cone_size, variable_id).
```

No SAT/equivalence oracle, FRAIG, BDD sweeping, or semantic rewrite is admitted.

## Claim ceiling

```text
P_VS_NP
=
OPEN

D1
=
NOT_ADMITTED

CYCLIC_SHARED_PAYLOAD
=
FINITE_DIAGNOSTIC_ONLY

POWER_OF_TWO_LINEAR_PREFIX
=
OPEN

ARBITRARY_N_STRUCTURAL_AIG_LOWER_BOUND
=
NOT_YET_PROVED
```
