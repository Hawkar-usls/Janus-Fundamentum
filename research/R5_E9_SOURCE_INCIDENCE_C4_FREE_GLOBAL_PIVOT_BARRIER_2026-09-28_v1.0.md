# R5 E9 — Source-Incidence C4-Free Global-Pivot Barrier

Date: 2026-09-28

Status:
`SOURCE_BOUND_ANTI_LOOP_BARRIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_PATH_XOR_AND_OVERLAY_NORMAL_FORM_2026-09-23_v1.0.md`
- `research/R5_E9_TWO_PATH_SINGLE_VARIABLE_PROJECTION_DP_ANTI_LOOP_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_source_incidence_c4_free_pivot_barrier.py`

Scientific firewall:

```text
THIS IS A UNIVERSAL-COVERAGE BARRIER FOR A PARTICULAR PIVOT PRECONDITION.
IT DOES NOT PROVE P != NP.
IT DOES NOT RULE OUT GLOBAL PIVOTS THAT WORK WITHOUT A SOURCE-INCIDENCE C4.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source-incidence graph

For a CNF formula F, let I(F) be the ordinary bipartite variable-clause incidence graph:

- one vertex for every source variable;
- one vertex for every source clause;
- an edge x--C iff x or NOT x occurs in C.

A 4-cycle in I(F) has the form

```text
x -- C -- y -- D -- x
```

with distinct variables x,y and distinct clauses C,D.

Therefore:

### Lemma C4-1

`I(F)` contains a C4 iff two distinct source clauses share at least two source variables.

Proof: each direction is immediate from the four incidence edges. QED.

## 2. Linear CNF is exactly the relevant C4-free source class

Use the standard SAT/hypergraph definition:

```text
F is linear iff every two distinct clauses share at most one variable.
```

Hence Lemma C4-1 gives:

```text
LINEAR CNF  =>  SOURCE INCIDENCE GRAPH IS C4-FREE.
```

For simple CNF formulas the converse holds as well.

This statement is about the source variable-clause incidence graph. It does not claim that every auxiliary representation graph obtained after arbitrary gadget expansion is literally C4-free.

## 3. Hardness source audit

This is not a speculative restriction.

Open literature gives NP-completeness of Linear 3-SAT:

1. Dominik Scheder, *Unsatisfiable Linear k-CNFs Exist, for every k*, arXiv:0708.2336. The paper defines linear k-CNF by pairwise clause intersection in at most one variable and recalls the equivalence: Linear k-SAT is NP-complete iff an unsatisfiable linear k-CNF exists; it proves existence for every k, including k=3.
   - https://arxiv.org/abs/0708.2336

2. Dominik Scheder, *Unsatisfiable Linear CNF Formulas Are Large and Complex*, STACS 2010, DOI 10.4230/LIPIcs.STACS.2010.2490, again uses the standard definition `|vbl(C) intersect vbl(D)| <= 1`.
   - https://doi.org/10.4230/LIPIcs.STACS.2010.2490

3. Porschen, Speckenmeyer and Randerath, *On Linear CNF Formulas*, SAT 2006, DOI 10.1007/11814948_22, establishes NP-completeness for the general linear SAT class and studies uniform linear subclasses.
   - https://doi.org/10.1007/11814948_22

The only fact imported into JANUS from these sources is the standard complexity classification / definition. No novelty is claimed for it.

Consequently there is an NP-complete 3-SAT source class whose ordinary variable-clause incidence graph has no C4.

## 4. Global-pivot consequence

The current two-path overlay is an exact linear-size representation of arbitrary signed 3CNF. Any proposed universal GLOBAL_PIVOT must therefore cover images of Linear 3-SAT as well.

Thus the following strategy is invalid as a universal coverage theorem:

```text
FIND A SOURCE-INCIDENCE C4
-> CONTRACT THE FOUR-CYCLE
-> REPEAT UNTIL TERMINAL
```

because a hard source instance may contain no source-incidence C4 at all.

This does **not** say that a C4 contraction is useless when one exists. It says only that C4 existence cannot be the mandatory progress certificate.

## 5. Relation to the single-variable DP anti-loop

The previous theorem classified projection of one complete variable path as ordinary Davis-Putnam elimination.

Together the two barriers say:

```text
ONE COMPLETE VARIABLE PATH
= DP / BVE COORDINATES, NOT A NEW GLOBAL PIVOT

MANDATORY SOURCE C4
= NOT UNIVERSALLY AVAILABLE
```

Therefore the next valid primary object must be both:

1. genuinely multi-path / cross-layer, and
2. discoverable on C4-free Linear-3-SAT images as well as on general images.

Examples of admissible directions include:

- a contraction on an alternating structure of unbounded possible length;
- a global cycle-space / syndrome object not requiring a fixed short source cycle;
- a nonlocal witness-dominance certificate;
- a representation change with a proved strict global potential that applies whether or not a source C4 exists.

## 6. Sharpened primary gate

Define:

```text
R5_E9_C4_FREE_SAFE_MULTI_PATH_GLOBAL_PIVOT_GATE_V1
```

A PASS requires all of:

```text
SOUND
COMPLETE
POLYNOMIAL CONSTRUCTION
POLYNOMIAL SOLVE/CONTRACTION COST
POLYNOMIAL WITNESS LIFT
STRICTLY DECREASING POLYNOMIALLY BOUNDED JOINT POTENTIAL
UNIVERSAL COVERAGE INCLUDING C4-FREE LINEAR-3-SAT IMAGES
```

A proposal FAILS this gate if its only progress trigger is:

- a source-incidence C4;
- a complete single-variable projection;
- a bounded boundary truth table whose size may grow exponentially;
- a selector that simply stores the eliminated branch choice;
- a layerwise width/cycle statistic already known insufficient.

## 7. Ceiling

```text
LINEAR CNF <=> SOURCE INCIDENCE C4-FREE (for simple formulas)
= PROVED STRUCTURALLY

LINEAR 3-SAT NP-COMPLETE
= SOURCE-BOUND PRIOR ART

MANDATORY SOURCE-C4 PIVOT
= CLOSED AS UNIVERSAL COVERAGE STRATEGY

C4-FREE-SAFE MULTI-PATH GLOBAL PIVOT
= OPEN <<< PRIMARY MICRO-GAP

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```