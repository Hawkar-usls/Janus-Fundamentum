# R5 — All-SCL constant-size pin-to-UNPINNED compilation and complete search-to-decision

Date: 2026-10-13 (Europe/Kyiv).
Research PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516
Parent authenticated checkpoint HEAD: acef436c4d24ba094a2d61459fdede5eebad020b.
Main untouched, PR DRAFT.

## SCIENTIFIC CONTRACT

The only accepted P=NP-level objective is ONE UNIFORM deterministic
n^C-bit-time `SolveLinearCubicXSAT` sound+complete for EVERY
original legal square+cubic+linear Positive Exact-One SCL,
returning source SAT witness or sound UNSAT.

**No universal polynomial zero test or solver is constructed here.**
`P_VS_NP=OPEN`.

This checkpoint DOES prove an important genuinely all-input POSITIVE
closure theorem: **arbitrary ORIGINAL-source Boolean pins can be
compiled into an ordinary, completely unpinned legal SCL source
using just 21 extra variables/clauses per pin**.
Thus a hypothetical complete polynomial UNPINNED SCL zero
oracle suffices for full original SAT-witness extraction.
We do NOT need the expanded local signed-loop moments
introduced in the preceding checkpoint for that reduction.

## 1. Two explicit tiny legal SCL gadgets with strict transfer matrices

Fix the following ORIGINAL sources as rows of variable IDs.
These are permanent constants; every verifier replays
square size, 3 occurrences per original variable,
three distinct literals per row, and 4-cycle-free linearity.

```
G10 (n=10):
(0,6,5), (1,3,0), (2,0,8), (3,8,4), (4,1,6),
(5,4,9), (6,7,2), (7,9,3), (8,5,7), (9,2,1).
Cut the original incidence between row {1,4,6} and variable 4.

G11 (n=11):
(0,5,2), (1,10,0), (2,9,10), (3,0,4), (4,1,9),
(5,7,8), (6,2,7), (7,3,1), (8,4,6), (9,6,5),
(10,8,3).
Cut between original row {5,7,8} and variable 7.
```

Cutting one Tanner wire of such a gadget exposes:
- W-side one dangling Boolean value a at the cut clause row;
- variable/Equality-side dangling Boolean value b,
  equal to the cut variable's original Boolean value.
All other original rows must satisfy exact one. The cut row
must satisfy `a+sum(other two Boolean variables)=1`.

An independent exhaustive 2^10 / 2^11 ORIGINAL 0/1
enumeration verifies the ENTIRE binary transfer tables:
```
              b=0  b=1
  G10  a=0     0    0
       a=1     1    0

  G11  a=0     0    2
       a=1     0    0
```

The boundary support is additionally forced structurally
by source counting: for any such n-row/variable gadget
with one cut W-side and one cut Equality-side port,
sum original open-clauses gives
`n=3*sum_v x_v - b + a`, so `a-b≡n (mod3)`.
n10≡1 gives (a,b)=(1,0) only; n11≡2 gives
(a,b)=(0,1) only. Source enumeration independently proves
these boundary configurations actually exist and have
exact integer multiplicities 1 and 2, respectively.
Both gadgets' fully closed originals are UNSAT by n mod3;
this is EXPECTED, not a defect.

## 2. THEOREM: one source-legal 3-switch fixes any original variable

Let F be ANY original legal SCL on n variables and clauses.
Take an original incidence (row i, variable v) with v in row i.
Take disjoint original 10/11 gadget sources G1,G2 with
their distinguished original cut incidence edges.

Delete exactly three edges of the disjoint Tanner union:
```
source W_i -- source V_v;
G1 W_1 -- G1 V_1;
G2 W_2 -- G2 V_2.
```
Insert three cross-incidences:
```
source W_i -> G1 V_1;
G1 W_1   -> G2 V_2;
G2 W_2   -> source V_v.
```
This is the THREE-COMPONENT CYCLIC PORT REWIRE.

- Every original row and column remains 3-regular, because
  one old incidence was removed and exactly one added.
- The matrix remains square with n+10+11=n+21 rows/columns.
- It remains C4-free/linear: internal old components only
  LOSE an incidence; a new cross-edge connects one of each
  pair of initially DISJOINT components. A simple cycle
  involving cross-edges must traverse all three cross-edges
  (one edge does not close a cycle, and there are not two
  cross-edges joining the same pair of components).
  Such a cycle must also traverse an internal path inside
  each component between its distinct cross ports, and so
  has length at least six; thus NO new 4-cycle is created.
  This remains correct when original F is itself disconnected.

The two opened gadget transfer constraints enforce:
```
source row-side port     = G1 column-side b1,
G1 row-side a1           = G2 column-side b2,
G2 row-side a2           = source variable-side port.
```
Order G1=G10, G2=G11:
  G10 (a1,b1)=(1,0), G11 (a2,b2)=(0,1).
  Then source row-side=0 and source variable-side=0:
  both are FIXED TO 0, with multiplicity 1*2=2.

Order G1=G11, G2=G10:
  G11 (a1,b1)=(0,1), G10 (a2,b2)=(1,0).
  Then source row-side=1 and source variable-side=1:
  both are FIXED TO 1, with multiplicity 2*1=2.

Because the original source edge requires row and variable
ports to agree, the substitution implements a sound,
complete, exactly count-preserving-up-to-factor-two pin:
```
#SAT(CompilePin(F,v,t))=2 * #SAT(F and x_v=t).
```

No clause became length1 or2. No variable lost cubic
degree. All OUTPUT instances remain in the very SAME
original legal SCL class, not an extended pinned CSP.

## 3. ALL-input MANY PINS corollary — polynomial size and count multiplier

For any source-consistent distinct original variable
assignment map P with q<=n pins, apply the preceding
3-switch sequentially to the original variable IDs
in deterministic sorted order. Each original variable
ID is preserved; each source row may be canonically
resorted but the full current source is independently
rechecked at each step.

The EXACT inductive theorem is
```
n_compiled=n+21q <=22n
#SAT(CompilePins(F,P))=2^q * #SAT(F respecting P).
```

Therefore the transformed source is SAT iff the
original source has a SAT extension consistent with P.
The source-to-source compiler and certificate replay
are deterministic polynomial time. A skeptical
verifier reconstructs all source rows, variable
IDs, ports and each intermediate 3-switch from the
authenticated original source; it does NOT trust
a producer's SAT/UNSAT status or claimed gadget metadata.

Proof uses the uniform source-independent single-pin
transfer theorem by induction, NOT extrapolation from
the finite source controls.

## 4. Source-level search-to-decision using only UNPINNED LoopZeroTest

Hypothesis: one deterministic sound+complete uniform
bit-polynomial `ZeroTest(F)` for EVERY ordinary,
**unmarked legal SCL** original source.

Given any original F:
1. Query ZeroTest(F). If zero, return UNSAT.
2. If nonzero, for v=0..n-1:
   create F' = CompilePins(F, previously fixed prefix plus x_v=0);
   F' is an UNPINNED legal SCL of size <=n+21(v+1)<=22n.
   Query ZeroTest(F'). If nonzero, retain x_v=0.
   If zero, retain x_v=1 (prior prefix is extendible,
   so at least one branch remains).
3. Read the full original Boolean witness and verify
   EVERY original Exact-One row.

At most n+1 ordinary legal SCL ZERO calls and
total constructed source size per call O(n).
If ZeroTest costs O(m^C) bit time, full recovery
cost O(n(22n)^C+poly(n))=n^{O(1)} with ONE
uniform exponent. This closes the WITNESS
EXTRACTION REDUCTION as a conditional theorem,
but does NOT construct the required ZeroTest.

Earlier checkpoint established an exact *marked-loop*
witness reduction but noted unpinned local degree-
(0,2,3) signature closure breaks under pins. The
new explicit constant source gadgets PROVIDE A WAY
AROUND that problem: every pin can be compiled
back into the original unmarked legal SCL class.
This is a positive improvement in the logical
requirements for the universal solver; do not
mistake it for the missing polynomial zero algorithm.

## 5. Real independent scientific checks / provenance

Executable:
`experiments/r5_universal_scl_pin_to_unpinned_constant_gadget.py`.
GitHub workflow:
`.github/workflows/r5-universal-scl-pin-compiler.yml`.

First full compiler CI [#38320496173 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38320496173):
- source-audited exact G10 transfer matrix only (a,b)=(1,0), count1;
- G11 only (a,b)=(0,1), count2;
- legal independently source-authenticated affine-plane SAT9:
  one pin x0=0 gives transformed legal SCL30 exact count 4;
  x0=1 gives legal SCL30 exact count 2;
  two INCOMPATIBLE 1-pins x0=x1=1 gives legal SCL51
  exact count0 (independently FINITE checked);
  two compatible pins x0=1,x1=0 gives legal SCL51
  exact count4;
- a source SAT witness with the requested pin has
  precisely TWO independently valid transformed
  original-source lifted witnesses (not just a Boolean label);
- original legality/checkpoint replay for Fano7,
  Holyer K4, Petersen, J5, non-Holyer E61 SAT12
  and E61 UNSAT12.

Stronger end-to-end real UNPINNED oracle test:
[#38320589571 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38320589571)
at `bc7c8744b40e67361a5b9a5528a248524245ab0b`.
Starting with original source affine SCL9 (3 independent
SAT witnesses), the finite exact NONPINNED rank-two
network evaluator was called TEN times on:
`n=9,30,51,72,93,114,135,156,177,198`.
Each returned SAT/UNSAT through an ORIGINAL LEGAL
source-only T4 network, NEVER through a marked
gate oracle. The source witness
`(0,0,1,1,0,0,0,1,0)` was recovered and
every original row replayed. Total 327,259
finite network search states across the ten calls.

This finite evaluator can use exponentially many
states in general. None of the source count controls
or ten successful calls proves worst-case polynomial
ZERO/NONZERO evaluation on all SCL.

## 6. Precise frontier, no inflated P=NP claim

COMPLETED:
- Source-authenticated constant size unary-pinning
  machinery purely inside original linear cubic
  square ExactOne class.
- Polynomial compiler of arbitrary source pins
  with exact multiplicity 2^q and size <=22n.
- Conditional all-source self-reduction using only
  an unmarked decision oracle.
- Independent full actual finite witness recovery
  by ten genuine unpinned SCL source queries.

MISSING:
- One deterministic n^C-bit-time unmarked
  `LoopZeroTest` on ALL original legal SCL
  including adversarial high-girth/high-genus/
  high-treewidth/low-symmetry atomic instances.
- Proof that ANY proposed compressed signed-loop
  boundary/signature representation supports
  such a zero test with all-input uniform n^C
  complexity.
- Therefore NO universal polynomial
  `SolveLinearCubicXSAT` has been constructed
  and `P_VS_NP` stays OPEN.

GATES:
```
ORIGINAL_SCL_G10_G11_BINARY_TRANSFER_CERTIFICATES = PROVED
ALL_SCL_ONE_SOURCE_PIN_TO_UNPINNED_3SWITCH = PROVED
ALL_SCL_Q_PINS_SOURCE_SIZE_N_PLUS21Q = PROVED
ALL_SCL_Q_PINS_EXACT_COUNT_MULTIPLIER_2POWQ = PROVED
UNPINNED_LOOPZERO_IMPLIES_NPLUS1_ORIGINAL_WITNESS_EXTRACTION = PROVED_CONDITIONAL
AFFINE9_TEN_UNPINNED_SCL_ORACLE_CALLS_WITNESS = CI_SUCCESS_FINITE
GENERAL_POLY_UNPINNED_LOOP_ZERO_TEST = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
