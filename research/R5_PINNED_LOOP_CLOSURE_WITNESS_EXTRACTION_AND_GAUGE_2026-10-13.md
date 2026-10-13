# R5 — Pinned generalized-loop algebra, reversible holographic transform, and source-witness extraction theorem

Date: 2026-10-13 (Europe/Kyiv)
Research PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516
Starting independently verified HEAD: 875b2a4429a1e23bc4ec6ba08795ac1bf8be0661.
Main unchanged, PR intentionally DRAFT.

## 0. Hard scientific requirement, not weakened

Goal is a UNIFORM deterministic bit-polynomial n^C source-sound and source-complete `SolveLinearCubicXSAT(F)` on EVERY legal square+cubic+linear Positive Exact-One (SCL) instance, returning original SAT witness or sound UNSAT, with NO unresolved atomic/high-treewidth class.

No such algorithm is constructed in this checkpoint. `P_VS_NP=OPEN`.

Previously source-verified on ALL SCL: polynomial Hall matching converts F into a quartic n-cell 2n-edge network Q with local tensor
`T4=|1000>+|0100>+|0011>` and exact partition function `Z(F)=#SAT(F)`. The original homogeneous BP change of basis yielded exact unpinned signed generalized-loop correction
`L(F)=Z(F)/Z_B(F)`,
`Z_B=(2^(4/3)/3)^n>0`,
with 16 local integer moments M, local degree1/4 entries zero.
This identity is exact, but naïve global evaluation is exponential.

## 1. NEW ALL-SCL EXACT PINNED LOOP THEOREM

Let P be ANY CONSISTENT partial assignment to ORIGINAL source variables.

Each variable occurs in exactly ONE of the matching's n column nodes, so it corresponds to exactly one quartic cell. When original variable matched to cell i is fixed:
- x=1: replace T4 at i by `E4=|0011>`;
- x=0: replace T4 at i by `O4=|1000>+|0100>`.
All nonpinned cells retain T4. The ORIGINAL graph Q, n cells, 2n edges, and original source row labels remain unchanged; the local gate's last two ports equal the matched source variable.

Define pi(0)=2/3, pi(1)=1/3 and psi(0)=-1,psi(1)=2. For each cell v, let
```
M_v^P(J)= (1/3) sum_{a in original T4 allowed}
        [a satisfies matched variable pin at v, if any]
        prod_{port in J} psi(a_port).
```
No local re-normalization is performed after pinning.

The same exact edge identity holds for all a,b:
```
   [a=b]/pi(a) = 1+psi(a)psi(b)/2.
```
Thus for ANY partial source P, the completely exact marked signed-loop expansion is
```
L(F|P)=sum_{S subset of 2n quotient edges}
           2^(-|S|) prod_v M_v^P(S∩δ(v))
      = #SAT(F respecting P) / Z_B(F).
```
This uses the **unpinned original** positive Z_B, and DOES NOT posit or require a BP fixed point of the pinned network.

Proof of the normalization: every satisfying original assignment (also after pins) has sum x=n/3. Every true original variable labels two unmatched Tanner incidences, so there are exactly 2n/3 quotient TRUE edge bits. Multiplying the edge inverses 1/pi over all 2n shared wires and local factors (1/3)^n yields
`(1/3)^n (3/2)^(4n/3) 3^(2n/3) = 1/Z_B`.
If 3 does not divide n, there are no surviving assignments, so both sides are exactly zero. Every source statement follows directly from exact source equations and finite 0/1 tensor algebra.

Independent source finite CI:
`experiments/r5_universal_pinned_loop_witness_extraction_gate.py`
GitHub [#38319521764 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38319521764)
verified:
- Fano7 original UNSAT, both values of a source pin yield exact loop0;
- non-Holyer E61 SAT12 original source, matched variable0 pin0 gives exact source count1 and L=531441/65536; pin1 gives count0 and exact L0;
- non-Holyer E61 UNSAT12 pin0 and pin1 both give L0.
All finite loop summands were enumerated exactly by a deliberately *EXPONENTIAL* resource-guarded proof control, never claimed polynomial.

## 2. Witness extraction, precisely what ZERO TEST must support

**Conditional theorem (all original SCL):** IF there exists a uniformly bit-polynomial sound+complete `PinnedLoopZeroTest(F,P)`, accepting every consistent ORIGINAL-source partial pin P, then `SolveLinearCubicXSAT(F)` and original source witness extraction are uniformly polynomial.

Proof: one initial empty-P call detects UNSAT. On SAT, visit matched variables in arbitrary fixed order; at step i ask whether a satisfying extension exists with already chosen prefix and x_i=0. If nonzero retain 0; otherwise, because the prior prefix was extendible, retain 1. Induction preserves an extendible prefix. After n steps the resulting entire vector satisfies all ORIGINAL Exact-One rows. Number of zero tests <=n+1; a direct original row verifier checks final SAT witness. The algorithm outputs UNSAT only if the initial signed-loop zero test is sound and complete. If each oracle is polynomial n^C, total runtime O(n^(C+1)) plus polynomial pin-building/source verification.

Important SCOPE: a zero-test proved only for UNPINNED degree-(0,2,3) loop grammar cannot be substituted blindly for `PinnedLoopZeroTest`. One must prove closure under pins or a different source-preserving pin-reduction to unpinned legal inputs. We have NOT constructed such a polynomial pinned oracle.

**NEW end-to-end SAT9 control with ACTUAL signed loop oracle, not fake original brute oracle**. Independent legal SAT9 source comprises 9 points (x,y) in F3² and 9 Exact-One lines of classes x=c, y=c, x+y=c. It has exactly 3 SAT witnesses (omitted class x-y=c). Code:
`affine_plane_scl9` inside `r5_universal_pinned_loop_witness_extraction_gate.py`.
Fresh [#38319871821 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38319871821):
- 10 exact pinned signed-loop zero-test invocations;
- each intermediate exact answer independently checked against original 2^9 enumeration;
- source witness `(0,0,1,1,0,0,0,1,0)` produced and all original 9 clauses checked;
- 2,222,394 loop-evaluator states visited across ten calls.
This is VALID FINITE search-to-decision execution but manifestly NOT a worst-case polynomial result. The separate earlier SAT12 test used the independently enumerated original source oracle only to audit the abstract reduction.

## 3. STRICT NONCLOSURE of old loop degree-(0,2,3) grammar under PINNING

In mask order 0..15, the previous UNPINNED local moments are:
```
M=(1,0,0,-1,0,-1,-1,2,0,-1,-1,2,2,-1,-1,0).
```
The pinned raw numerator tables (each denominator exactly3) are:
```
3*M_pin1=(1,-1,-1,1,2,-2,-2,2,2,-2,-2,2,4,-4,-4,4)
3*M_pin0=(2,1,1,-4,-2,-1,-1,4,-2,-1,-1,4,2,1,1,-4).
```
And the exact termwise identity is
`M_pin0+M_pin1=M`.
Unlike M, EACH pinned signature has NONZERO local singleton
moments and NONZERO full degree4 moment.

Therefore the unpinned simplification 'degree1 and degree4 vanish'
is NOT stable under original source witness-extraction conditions.
This is a structural, all-input theorem and a concrete caution
against claiming polynomial closure of the unpinned loop grammar.

## 4. NEW REVERSIBLE HOLOGRAPHIC BACK-TRANSFORM: loop M is T4 in disguise

Use invertible
```
H=[[1,1],[-1,2]], determinant(H)=3;
D=diag(1,1/2), the loop selected-edge weight.
```
For every unpinned cell (and each corresponding pin):
```
M    = (H tensor4) T4 /3,
M^P  = (H tensor4) T4^P /3;
H^T D H = diag(3/2,3) = diag(1/pi(0),1/pi(1)).
```
Hence the generalized-loop factor graph is **exactly an invertible local change of basis** of the original source quartic T4 Holant, with its known global normalization. This is algebraic equivalence, not a separate polynomial contraction theorem, and must supersede any earlier loose description of the moments as a magically simpler new problem.

In particular a 2|2 tensor flattening changes by invertible left/right Kronecker matrices. The three exact ranks remain
```
rank(T4)=(2,3,3)=rank(M).
```
From previous source-verified R5 arity4 matchgate noncrossing rank3 obstruction, no extra invertible 2x2 edge gauge can make original M ONE standard matchgate; the exact loop rewrite is NOT automatically one planar Pfaffian contraction.

Executable:
`experiments/r5_universal_loop_holographic_backtransform_and_pin_obstruction.py`.
GitHub [#38319753000 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38319753000):
- all 16 unpinned and all 16 of EACH pinned moment coefficients exactly checked under same H;
- independent full 2x2 identity H^T D H;
- exact three flattening ranks (2,3,3);
- direct source-incompatible-pin cancellation.

## 5. Source-specific explicit first-order false signal even after pinning

Pick ANY original unmatched incidence edge (row i, variable v)
in the universal matched quotient Q. Its two quotient endpoint cells
correspond respectively to original variables m(i) and v.
They are distinct and BOTH appear in original Exact-One source row i.
Pin BOTH to 1. The original source is immediately UNSAT without
any global search. Yet the pinned loop local degree1 moments are
nonzero. Choosing ONLY this quotient edge in the signed-loop
expansion yields a nonzero rational, for the canonical source-port
ordering of our constructor exactly
```
empty-loop term = +1/9,
single-edge loop term = -1/9,
full pinned signed loop sum = 0.
```
This holds source-wise even when graph girth is arbitrarily high:
pinning creates leaf terms, so the high-girth 'nonempty loop
contains a graph cycle' no-go CANNOT be used unchanged in
conditioned witness search.

Independent full finite signed-loop sum controls source-Fano7,
non-Holyer E61 SAT12 and E61 UNSAT12, all source-refuted by two
incompatible original 1-pins, return exactly zero. Further
original source structural checks on Holyer K4 and J5.

## 6. Exact next positive theorem, still MISSING

Need a uniformly constructible family of polynomial-length,
bit-polynomial-evaluable algebraic signatures supporting:
(A) every original source-authenticated unpinned and pinned
    T4 moment gate (pinned, not just old degree-0/2/3 grammar);
(B) arbitrary quartic incidence contractions on all
    connected high-treewidth/high-genus legal SCL sources;
(C) exact zero/nonzero in worst-case n^C bit time;
(D) original SAT witness recovery in n+1 zero tests,
    including sound global UNSAT output.

No proof of such closure or all-input polynomial decision
exists. Local invertible holographic gauge and finite SAT9
extraction do NOT constitute P=NP. Distinguish mathematically
VALID exact representations from computationally hard
exact zero-tests at every new checkpoint.

GATES:
```
ALL_SCL_PARTIALLY_PINNED_EXACT_LOOP_IDENTITY = PROVED
ALL_SCL_POLYNOMIAL_PIN_ENCODING = PROVED
WITNESS_EXTRACTION_LE_N_PLUS1_PINNED_ZERO_CALLS = PROVED_CONDITIONAL
AFFINE9_ACTUAL_EXACT_PINNED_LOOP_WITNESS = CI_SUCCESS_FINITE
DEGREE_0_2_3_UNPINNED_GRAMMAR_CLOSED_UNDER_PINS = REFUTED
ALL_SCL_LOOP_IS_INVERTIBLE_H_TRANSFORM_OF_T4 = PROVED
ALL_SCL_PINNED_UNIT_EDGE_FALSE_SIGNAL = PROVED
GENERAL_UNIFORM_POLY_PINNED_LOOP_ZERO_TEST = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
