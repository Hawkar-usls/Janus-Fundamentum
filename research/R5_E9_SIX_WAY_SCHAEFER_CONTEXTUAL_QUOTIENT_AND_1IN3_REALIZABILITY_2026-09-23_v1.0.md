# R5 E9 — Six-Way Schaefer Ledger, Contextual No-Free-Merge, and JANUS 1-in-3 Realizability Gate

Date: 2026-09-23

Authority: JANUS_DERIVED_CONTEXTUAL_QUOTIENT_THEOREM + SOURCE_BOUND_BOOLEAN_CSP_LEDGER + REALIZABILITY_GATE_OPEN__NO_D1_PROMOTION

Parents:
- R5_E9_BOOLEAN_SLICE_TWO_STATE_THRESHOLD_2026-09-23_v1.0
- R5_E9_TORSION_SIDE_CODE_COMPOSITION_BARRIER_2026-09-23_v1.0

Checker:
experiments/r5_e9_janus_1in3_direct_realizability_census.py

## 1. Full Schaefer ledger

For a Boolean constraint language without freely available constants, maintain all six Schaefer tractable lanes globally across the active relation family:

1. 0-valid: every active relation contains its all-zero tuple;
2. 1-valid: every active relation contains its all-one tuple;
3. Horn: all relations are closed under coordinatewise AND;
4. dual-Horn: all relations are closed under coordinatewise OR;
5. bijunctive: all relations are closed under majority;
6. affine: all relations are closed under ternary XOR/minority.

If constants are explicitly admitted as free unary relations, use the constants-version of Schaefer's theorem; then the usual statement has the four structural lanes Horn, dual-Horn, bijunctive and affine.

Therefore JANUS must record constants availability as part of the side-interface contract rather than silently mixing the two formulations.

## 2. Contextual equivalence for boundary states

Let B be one side-code block with exposed boundary coordinates S.
For two block states u,v define

u ==_CTX v

iff for every admissible external context K glued to S,

SAT(K with boundary state u) iff SAT(K with boundary state v).

Any context-independent exact quotient that is promised to remain sound under every admissible gluing can merge only states in the same CTX class.

## 3. Pin-separation theorem

### Theorem CTX-1

Assume the admissible external interface includes unary pins on exposed side coordinates.
Then any two distinct Boolean boundary states are CTX-distinguishable.

### Proof

Let u!=v.
Choose coordinate i with u_i!=v_i.
Glue the unary pin s_i=u_i.
The pinned context accepts u and rejects v.
Thus u and v are not CTX-equivalent.

QED.

Consequently, under unrestricted equality/pinning interface, the minimal exact context-independent quotient of a finite Boolean relation R has exactly |R| boundary classes.

## 4. The one-in-three atom has three irreducible local context classes

For

R_1/3={100,010,001},

every pair differs on at least one exposed coordinate.
By CTX-1:

[100]_CTX, [010]_CTX, [001]_CTX

are three distinct singleton classes.

Hence:

PURELY BLOCK-LOCAL 3-TO-2 MERGE
UNDER UNRESTRICTED PINNING CONTEXTS
=
IMPOSSIBLE AS AN EXACT CONTEXT-INDEPENDENT QUOTIENT.

This does not block:

- using the actual global context to eliminate a state;
- a restricted JANUS interface that forbids the distinguishing pins;
- representation change that preserves all three modes but acquires a common tractable polymorphism;
- contraction of several hard blocks together;
- a genuinely new polynomial solver for the hard layer.

## 5. Why abstract Z3 hardness is not yet JANUS pipeline hardness

The existing torsion-side barrier proves that the abstract Boolean language containing constraints

s_i+s_j+s_k = 1 mod 3

is Positive 1-in-3-SAT and therefore NP-complete under arbitrary sharing of the Boolean side variables.

But this is a statement about the generic side-code representation class.

To promote the stronger statement

'the actual JANUS signed-NAE/SNF pipeline contains arbitrary Positive 1-in-3-SAT instances'

one must construct the relation and its sharing/gluing from admissible JANUS blocks.

No existing artifact before this gate proves that realization theorem.

## 6. JANUS pipeline realizability contract

Define JANUS_1IN3_REALIZABILITY as PASS only if there is a polynomial transformation from an arbitrary Positive 1-in-3 instance J to an admissible JANUS torsion-side network N(J) with all of the following:

R1 BLOCK REALIZATION:
each source 1-in-3 constraint is represented by an actual block derived from the signed-NAE/SNF pipeline, not by inserting a handwritten modular relation;

R2 OCCURRENCE SHARING:
multiple occurrences of the same source Boolean variable are identified by admissible JANUS side interfaces with polynomial overhead;

R3 EXACTNESS:
J is satisfiable iff N(J) is satisfiable;

R4 WITNESS MAPS:
source witnesses map to JANUS witnesses and accepted JANUS witnesses decode to source witnesses in polynomial time;

R5 SIZE:
block construction, interface construction, state, verification and reconstruction are polynomial in |J|;

R6 NO HIDDEN ORACLE:
the construction does not need a satisfying assignment or SAT oracle.

Only after R1-R6 pass may the frontier be promoted to:

JANUS THREE-STATE LAYER CONTAINS A FULL NP-COMPLETE CORE.

## 7. Restricted direct-realization census

As a first falsifier, exhaustively enumerate the most direct block ansatz:

- exactly three signed NAE3 rows;
- their three row-side bits are the exposed relation;
- between 3 and 6 representative Boolean variables;
- arbitrary three-element supports and arbitrary literal signs.

The checker finds no block whose exact Boolean side image is

{100,010,001}

for n<=6.

This is NOT a general impossibility theorem.
It only proves that the desired atom is not already hiding in the smallest direct three-row side-image ansatz through six representatives.

Therefore the generic Z3 relation must not be called JANUS-realized on the basis of the abstract congruence alone.

## 8. Killer bifurcation

Freeze:

R5_E9_JANUS_1IN3_REALIZABILITY_GATE_V1.

PASS outcome:

- arbitrary Positive 1-in-3 embeds with polynomial overhead;
- the three-state JANUS frontier itself contains a full NP-complete core;
- any universal polynomial breaker of this layer is already a P=NP-level breakthrough.

FAIL outcome:

A FAIL must not mean 'small search found nothing'.
It requires a proved invariant obeyed by every admissible JANUS side network that prevents arbitrary 1-in-3 realization.

Examples of useful FAIL witnesses:

- forbidden incidence topology;
- global parity/orientation identity;
- bounded-width interface law;
- rank/module identity;
- restricted sharing pattern;
- common polymorphism forced by the pipeline;
- matroidal or separator structure.

Such an invariant becomes the next positive algorithmic target.

## 9. Three-state breaker contract after realizability

Only after the realizability gate is resolved should a universal three-state breaker be promoted.

Any proposed breaker must provide I' and a decoder D such that:

- SAT(I) iff SAT(I');
- every accepted witness of I' decodes to a witness of I;
- synthesis + transform + solve + decode + verify is polynomial;
- every iteration strictly decreases an explicit progress measure or moves an entire component into one globally common Schaefer lane;
- no hidden three-way selector;
- no two-bit renaming of the same three-state choice;
- no branch on the surviving state;
- no assumed representative;
- no local quotient merging CTX-distinguishable states.

A useful diagnostic progress measure is

mu(I)=sum_B max(0, |C_B|-2),

with a secondary interaction measure.

This measure is diagnostic only until a breaker theorem proves strict decrease under its admitted transformations.

## 10. Current state

TWO-STATE COMPOSITION = SEALED POLY ISLAND
SIX-WAY SCHAEFER LEDGER = PATCHED
R_1/3 LOCAL CTX CLASSES WITH PINS = 3 SINGLETONS
PURE LOCAL 3-TO-2 MERGE = BLOCKED
ABSTRACT Z3 SIDE-CODE CSP = NP-COMPLETE
ACTUAL JANUS ARBITRARY 1-IN-3 REALIZABILITY = OPEN
DIRECT THREE-ROW REALIZATION n<=6 = NOT FOUND
THREE-STATE BREAKER = HELD BEHIND REALIZABILITY GATE
D1 = EMPTY
P_VS_NP = OPEN
