# R5 E9 — R1/R5 Semantic-Oracle Hardness Barrier

Date: 2026-09-27

Status:
`JANUS_DERIVED_COMPLEXITY_BARRIER__STRUCTURAL_R1_R5_ONLY__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_r1_r5_semantic_oracle_hardness_controls.py`

Parents:
- `R5_E9_WDR_LEAN_NORMAL_FORM_SCHEDULER_CONTRACT_2026-09-23_v1.0.md`
- `R5_E9_WITNESS_DOMINANCE_EXISTENCE_COLLAPSE_AND_STRUCTURAL_TRANSFORMER_GATE_2026-09-23_v1.0.md`
- `R5_E9_EXACT_ONE_BIG_ELS_LEAN_THEOREM_2026-09-27_v1.0.md`
- `R5_E9_CUBIC_LINEAR_EXACT_ONE_MATCHING_LEAN_THEOREM_2026-09-27_v1.0.md`
- `R5_E9_EXACT_ONE_LINEAR_AUTARKY_LEAN_THEOREM_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS NOTE DOES NOT PROVE P=NP OR P!=NP.
IT DOES NOT RULE OUT POLYNOMIAL STRUCTURAL SUBCLASSES OF R1/R5/R6.
IT RULES OUT TREATING COMPLETE SEMANTIC RECOGNITION AS A FREE PREPROCESSING DONOR.

D1 = EMPTY
P_VS_NP = OPEN
```

## 1. Motivation

After the current Exact-One WDR closure, the live lanes are broader R1 equivalence,
R5 structural dominance, R6 ranked/SR macro rules, and exact representation changes.

A dangerous ambiguity is to replace a structural sufficient condition by a complete
semantic query such as:

```text
are p and q really equivalent in all models?
```

or

```text
is fixing q=0 really satisfiability preserving?
```

Those queries are not innocent preprocessing. On an NP-complete source class they can
already encode UNSAT.

This note makes that reduction explicit inside Cubic Monotone 1-in-3 SAT.

## 2. Fixed cubic-linear probe

Use variables x0,...,x8 and the nine Exact-One triples

```text
(0,7,5)
(1,6,0)
(2,8,3)
(3,5,6)
(4,0,2)
(5,2,1)
(6,4,8)
(7,3,4)
(8,1,7)
```

Call this fixed instance H.

Every triple contains three distinct variables, every variable occurs in exactly three
triples, and any two triples intersect in at most one variable. Thus H is cubic,
3-uniform, and linear.

Let A_H be its incidence matrix. Solving the integer/rational system

```text
A_H x = 1
```

gives the one-parameter affine family

```text
(t, t, 1-2t, t, t, t, 1-2t, 1-2t, t).
```

Requiring all coordinates to be Boolean forces t=0. Therefore H has the unique
Exact-One model

```text
(0,0,1,0,0,0,1,1,0).
```

In particular, with

```text
p := x0,
q := x2,
```

we have in every model of H

```text
p=0,
q=1.
```

The finite checker independently verifies cubicity, linearity, and uniqueness by an
exhaustive 2^9 truth-table control. This exhaustive step is only a fixed-gadget audit;
it is not an E8 algorithmic primitive.

## 3. General disjoint-union lemma

Let C be any SAT-like class closed under disjoint union. Suppose SAT on C is NP-hard
and C contains a fixed satisfiable probe H with two designated variables p,q such that
all models of H have p != q and q=1.

For an arbitrary source instance F in C form

```text
G = F disjoint-union H.
```

Because the variable sets are disjoint,

```text
Mod(G) = Mod(F) x Mod(H).
```

Hence G is satisfiable iff F is satisfiable.

This trivial product identity is enough to turn two complete semantic R-lane queries
into UNSAT tests.

## 4. R1: complete semantic literal equivalence is coNP-hard

Define the semantic equality question

```text
EQ(G,p,q):
for every model a of G, a(p)=a(q)?
```

Unsatisfiable formulas satisfy this universally quantified condition vacuously.

For G=F disjoint-union H:

### If F is UNSAT

Then G is UNSAT, so

```text
EQ(G,p,q) = TRUE.
```

### If F is SAT

Take any model of F and combine it with the unique model of H. In that model

```text
p=0,
q=1,
```

so

```text
EQ(G,p,q) = FALSE.
```

Therefore

```text
F is UNSAT
iff
EQ(F disjoint-union H,p,q).
```

Since Cubic Monotone 1-in-3 SAT is NP-complete and the class is closed under disjoint
union, deciding full semantic literal equality on this class is coNP-hard.

The complement has a direct satisfying-assignment witness with p != q, so the usual
semantic-equivalence decision problem lies in coNP; for this restricted source the
reduction supplies the relevant hardness direction needed by the JANUS firewall.

### Consequence for R1

The already admitted BIG/SCC equivalence rule remains polynomial because it recognizes
only a syntactically certified sufficient subclass.

What is forbidden as a free upgrade is:

```text
R1 = FIND EVERY TRUE SEMANTIC LITERAL EQUIVALENCE.
```

A complete version of that operation already contains a coNP-hard query.

This does not rule out a new polynomial structural R1 donor specific to a narrower
carrier.

## 5. R5: complete semantic safe-branch recognition is coNP-hard

For a formula G, variable q, and bit b define

```text
SAFE(G,q=b):
SAT(G) iff SAT(G[q:=b]).
```

The reverse implication is automatic, so SAFE asks whether fixing the bit loses every
model or preserves at least one whenever G is satisfiable.

Use the same reduction G=F disjoint-union H and test q=0.

Because q is forced to 1 in H,

```text
G[q:=0]
```

is always UNSAT.

Therefore:

### If F is UNSAT

G is UNSAT and G[q:=0] is UNSAT, hence

```text
SAFE(G,q=0) = TRUE.
```

### If F is SAT

G is SAT but G[q:=0] is UNSAT, hence

```text
SAFE(G,q=0) = FALSE.
```

Thus

```text
F is UNSAT
iff
SAFE(F disjoint-union H,q=0).
```

So complete semantic recognition of satisfiability-preserving one-bit contraction is
coNP-hard on Cubic Monotone 1-in-3 SAT.

### Consequence for R5

A valid R5 rule must be a polynomially synthesized structural sufficient condition with
its own model-repair witness. It may not call a hidden complete semantic dominance test.

The result does not prohibit polynomial dominance subclasses; it prohibits silently
identifying `structural dominance` with exact semantic branch safety.

## 6. R6 corollary: completeness is not free

Suppose an R6 engine is advertised as a complete polynomial recognizer for arbitrary
target conditions C, returning a sound dimension-dropping ranked/SR macro exactly when

```text
SAT(F) iff SAT(F AND C).
```

Take C to be the unit condition q=0 in the reduction above. Such a complete engine would
decide SAFE and hence the coNP-hard reduction.

Therefore an admissible polynomial R6 system must again be one of:

1. an incomplete but polynomially recognizable sufficient subsystem;
2. a genuinely new structural theorem showing that the current restricted carrier
   always admits one of its macros;
3. a representation change that exposes additional polynomial structure.

Merely allowing arbitrary SR/dominance certificates does not prove polynomial synthesis;
certificate discovery is charged by the E8 contract.

## 7. Relation to the current Exact-One frontier

The current branch already has:

```text
R0 forced/unit/pure                  CLOSED on the cubic-linear survivor
R1 BIG/SCC ELS                       CLOSED on untouched Exact-One
R2 matching autarky                  CLOSED on cubic-linear Exact-One
R2 simple/linear autarky             CLOSED on standard Exact-One
R3 BCE                               CLOSED on the cubic-linear survivor
R4 no-growth DP                      CLOSED on the cubic-linear survivor
R7 Horn/dual-Horn/Krom direct tests  CLOSED on the nonempty survivor
```

This note adds the complexity firewall:

```text
R1 COMPLETE SEMANTIC EQUIVALENCE ORACLE = CO_NP_HARD
R5 COMPLETE SEMANTIC SAFE-BRANCH ORACLE = CO_NP_HARD
R6 COMPLETE ARBITRARY EQUI-SAT MACRO RECOGNIZER = INHERITS THE SAME BARRIER
```

Therefore the live scientific target is sharper:

```text
find a STRUCTURAL, polynomially synthesizable R5/R6 rule that is guaranteed on the
restricted survivor;
OR
perform an exact representation change and prove polynomial progress there.
```

## 8. Anti-loop with the existing kernel-word representation

The branch already contains the exact cubic kernel-word normal form

```text
A x = 1, x in {0,1}^n
iff
A z = 0, z in {-1,2}^n,
```

with an exact O(2^d poly(n)) solver parameterized by rational nullity d and the
I+P+Q two-permutation normalization.

Hence the following are already known and must not be rediscovered as new work:

```text
n mod 3 filter
nullity 0 UNSAT filter
O(log n) nullity polynomial island
I+P+Q / three-translate exact normal form
large-nullity survivor
```

The new information in the present note is not another normal form. It is that broad
semantic implementations of R1/R5/R6 cannot be used to bypass the large-nullity
survivor without importing a hard oracle.

## 9. Literature binding / anti-duplication

Public literature already treats semantic literal-equivalence detection as coNP-hard in
general SAT/configuration settings; JANUS does not claim that generic fact as novelty.

The source class used here, Cubic Monotone 1-in-3 SAT, is standard NP-complete; it is
used as an NP-complete source in the exact-cover/tiling literature, including the
Moore-Robson line of work.

The JANUS-derived contribution of this note is the explicit fixed cubic-linear probe and
the direct disjoint-union specialization that binds those complexity facts to the frozen
R1/R5/R6 scheduler semantics.

No novelty claim is made beyond that scoped specialization.

## 10. Next gate

Freeze:

```text
R5_E9_STRUCTURAL_R5_R6_OR_REPRESENTATION_CHANGE_GATE_V1
```

Input:
a WDR-surviving cubic-linear Exact-One / equivalent large-nullity kernel-word state.

PASS must construct in deterministic polynomial time at least one of:

A. a non-semantic-oracle R5 witness transformer fixing at least one Boolean dimension;
B. an R6 ranked/SR macro with immediate certified dimension drop and polynomial
   synthesis;
C. an exact representation change with a polynomially bounded progress measure;
D. a direct polynomial terminal solver.

Forbidden:

- exact SAT/UNSAT queries hidden inside equivalence or dominance recognition;
- complete semantic branch-safety tests;
- exponential certificate search followed by polynomial verification;
- rediscovering the already sealed low-nullity or two-permutation normal forms;
- counting finite successes as universal coverage.

Promotion to E8-D1 still requires arbitrary-input coverage and total polynomial cost.

## 11. Ceiling

```text
R1_BIG_SCC_DONOR
= POLYNOMIAL BUT NONUNIVERSAL

R1_COMPLETE_SEMANTIC_EQUIVALENCE
= CO_NP_HARD

R5_COMPLETE_SEMANTIC_SAFE_BRANCH
= CO_NP_HARD

R6_COMPLETE_ARBITRARY_TARGET_RECOGNITION
= NOT A FREE POLYNOMIAL DONOR

NEXT
= STRUCTURAL_R5_R6_OR_EXACT_REPRESENTATION_CHANGE

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
