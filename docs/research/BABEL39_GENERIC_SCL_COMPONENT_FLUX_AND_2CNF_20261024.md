# BABEL-39 — generic SCL component compiler with certified rational discovery, global flux pruning and 2-CNF closure

**2026-10-24, research only.** Stacked on verified BABEL-38 Draft PR #564, exact parent \`460339828149b0b52f042c8cd30a1e87f77f6cfa\`. Unlike BABEL-34–38's frozen U-only algorithms, this theorem and implementation accept **different, arbitrary square cubic linear Exact-One components of varying sizes**, subject to a verifiable original-component restoration certificate and explicit bounded complexity gates. No change to \`main\`, no claim of P=NP.

## 1. Input, exact semantics, all-n proof

Input includes an arbitrary connected legal SCL instance J and a **certificate** specifying a partition into disjoint component variable and row sets; for every component, a local square 3uniform 3regular linear Exact-One incidence matrix and the occurrences selected for cross-edge incidence exchanges. Every original J row, occurrence, reciprocal cross-edge pairing and linearity must be independently reconstructed and checked against J, with no silent representation change. The component matrices need NOT be isomorphic to U and may have DIFFERENT sizes.

For each component i with n_i variables and r_i distinct modified rows/variable ports, remove its r_i modified ORIGINAL rows and solve the surviving \`(n_i-r_i)×n_i\` positive Exact-One system. With rational coefficient matrix A_i, each surviving row still sums to3, so

    A_i x_i=1  <=>  x_i=(1/3)1 + y_i, A_i y_i=0.

Calculate a rational row-echelon form exactly, with k_i free ORIGINAL variable coordinates. Enumerate all 2^{k_i} Boolean free vectors, reconstruct the remaining rational coordinates, reject non-Boolean outputs and verify every surviving original Exact-One row. This is a COMPLETE local census. Each local Boolean assignment gives exported bit tuple a and required imported bit tuple b, using the exact intact row complements. Retain a boundary tuple iff every bit of b is 0 or1; attach one full physical local assignment as reconstructible witness. Multiple physical assignments with an identical port tuple may be merged for SAT DECISION but must not be silently interpreted as #SAT multiplicity 1.

Global exact semantic bijection across cross incidence edges (BABEL-29) follows because the JOIN forces \`a_(i,p)=b_(j,q)\` and \`a_(j,q)=b_(i,p)\` on each macro edge. No original U formula assumption is made.

If ANY local table is empty, return sound UNSAT on the certified decomposition. If any necessary admission bound fails, return UNKNOWN, not SAT/UNSAT.

## 2. Global net flux: a sound generic pruning rule

Every component obeys the exact row counting identity

    Δ_i = sum_ports(a-b) = 3|x_i|-n_i.

Each reciprocal edge cancels one output against one input, giving \`sum_i Δ_i=0\` for any joined physical SAT solution. Hence:

- If ALL locally admissible states across ALL components have Δ_i≥0, then EVERY global SAT solution uses only states with Δ_i=0. Delete each positive-Δ state.
- If ALL local states have Δ_i≤0, delete each negative-Δ state.
- If positive and negative Δ coexist, do NOT prune from this rule alone. A global solution can balance them; assuming independent Δ=0 would be unsound.

This all-n rule is independent of specific local geometry, presence of an expander, or graph width. Exact component certificates verify local tables before any pruning.

### Stronger ALL-n polynomial additive flux support DP (beyond one-sided sign)

The implementation now additionally computes the **EXACT sets of reachable net-flux sums** of independently selected local states, before enforcing edge compatibilities. Let \`D_i={Δ_i(s): s∈T_i}\`. Compute prefix sets \`P_0={0}\`, \`P_(i+1)=P_i+D_i\`; and suffix sets \`Q_t={0}\`, \`Q_i=D_i+Q_(i+1)\` using integer Minkowski sums. These are complete, not heuristic: they enumerate ALL possible aggregate flux values, not all physical state combinations.

If 0∉P_t, return a **sound global UNSAT certificate** immediately because every exact joined model must satisfy ΣΔ=0. For every local state s of component i, retain it iff

    -Δ_i(s) ∈ P_i + Q_(i+1).

This keeps exactly the local states that participate in AT LEAST ONE globally zero-flux selection (without assuming edge compatibility) and safely discards every other state. The marginal test is globally exact for the *additive equation*, but only NECESSARY for SAT: surviving states may still violate cross-edge equalities.

**Polynomiality:** each \`Δ_i=3|x_i|-n_i\` lies in \`[-n_i,2n_i]\`; for total N=Σn_i every prefix and suffix sum has O(N) range and at most 3N+1 distinct possible integer values. At most N components exist; naive integer-set prefix, suffix and per-component checks cost a conservative O(N^4 + N²·sum_i|T_i|), which is polynomial and uses O(log N)-bit sum values. No 2^t physical Cartesian product is materialized. This upgrade strictly generalizes the one-sided sign rule and is sound even when positive AND negative flux states coexist. Do NOT confuse additive-domain consistency with global SAT completion.

## 3. Generic exact 2-CNF construction for every majority-closed residual boundary relation

After sound pruning, inspect the set R_i⊆{0,1}^{2r_i} of feasible boundary tuples (a,b) for EVERY arbitrary component.

**Known finite Boolean relation theorem (bijunctive = majority-closed):** R_i is definable by a conjunction of unit/binary clauses on the 2r_i original port bit coordinates iff R_i is closed under coordinatewise ternary majority.

For each R_i, enumerate all possible 1-coordinate and 2-coordinate Boolean assignments absent from R_i. Add the corresponding forbidding 1- or 2-literal 2-CNF clauses. These are all sound consequences of R_i. If R_i is majority-closed, their conjunction represents EXACTLY R_i; the implementation verifies this **directly** by exhaustive evaluation of all 2^{2r_i} bit tuples whenever the size admission gate is met. This equivalence test avoids cubic enumeration of every triple of local states in the production algorithm, so the advertised 2^O(r_i) complexity is preserved. An independent finite validator additionally checks majority closure on the frozen control relations. If the produced CNF admits any boundary tuple outside R_i, return \`UNKNOWN_NOT_BIJUNCTIVE\`, NEVER produce a false SAT/UNSAT decision.

For each recovered cross-edge, impose both exact port equalities \`out_i=in_j\` and \`out_j=in_i\`; each is 2CNF. Solve the resulting global formula by implication-graph strongly connected components. For UNSAT, record a variable and its negation in one SCC; for SAT, reconstruct each local physical witness from the selected port tuple, concatenate and VERIFY EVERY ORIGINAL J CLAUSE.

**All-n soundness/completeness ON ADMITTED INPUTS:** Exact rational local enumerations certify complete local boundary tables; flux pruning removes no feasible global solution; 2CNF equivalence is checked for every local relation; cross-edge equalities are exact. Hence the 2CNF result is equivalent to J. SAT witness or exact UNSAT are both sound, including all original semantics. This is a generic algorithm applicable to arbitrary local SCL components that satisfy the admission conditions.

### Quantified TOTAL polynomial-composition guarantee

Let N be total original variables; K=max_i k_i, R=max_i r_i. With a supplied verified decomposition, local full physical enumeration is \`sum_i 2^{k_i} poly(n_i)\`; the explicit 2CNF reconstruction and relation check costs \`sum_i 2^{2r_i} poly(r_i)\`, plus polynomial original-incidence validation, **exact additive-flux sumset DP**, global 2SAT solve, witness reconstruction and replay. Thus conservative TOTAL bit complexity is

    poly(N) * (2^K + 2^{2R}).

For K,R≤c log₂N for ONE fixed c, the WHOLE process is polynomial in N, including construction of the relations, ALL intermediate tables, checking majority closure, solving, reconstructing and verifying. The reference implementation uses fixed conservative caps (e.g. K≤12,R≤6) and returns UNKNOWN if exceeded; the theorem allows any logarithmic budgets with a uniform fixed constant.

**CRITICAL:** No polynomial-time procedure is proved to discover a valid low-K/low-R partition for EVERY connected SCL, nor is it proved that every arbitrary SCL admits majority-closed residual tables. The four-port U relation BABEL37 fails majority closure before BABEL38's globally justified pruning; the generic compiler correctly recovers its two-state majority-closed residual. Some arbitrary local relations may still fail after all sound flux pruning; those inputs remain UNKNOWN. This is a rigorously scoped universal-*input* sound three-way solver with polynomial admitted-class two-terminal completion, NOT \`P=NP\`.

## 4. Independent controls and scientific frontier

The reference code \`experiments/babel39/generic_scl_component_compiler.py\` accepts raw joined physical SCL clauses PLUS a provenance certificate giving component matrices, selected ports and cross-port pairings. It recomputes the exact joined clauses and checks semantic identity before use. Local enumeration uses only Python Fraction and original coordinates and caches nothing from the frozen U relation library. The compiler mechanically checks majority closure via full boundary truth-table comparison and constructs 2CNF on **actual original port bits**, not a frozen template-specific selector.

Controls include:
- arbitrary 27-variable U four-port same-gadget macro controls from BABEL37/38, where Δ sign pruning eliminates C and makes the residual majority-closed (K5: UNSAT, K4,4: SAT; exact physical witness);
- a connected mixed-size U27 + affine9 one-port splice (one finite custom component not isomorphic to U) with SAT count independently computed from local table model multiplication and SAT witness recheck;
- three-port U model relations as regression (BABEL36); both positive and negative network tests where possible;
- a generic synthetic two-sided Δ+/Δ− local relation to prove that incorrectly deleting all nonzero Δ when signs balance would be UNSOUND; this is a lemma test, not a fake SCL input or universality promotion;
- deliberately restrictive rank/port caps return UNKNOWN and never infer UNSAT;
- an independent \`experiments/babel39/independent_generic_receipt_audit.py\` rederives local counts and checks the produced 2CNF against all local boundary tuples, plus small complete global state products.

\`\`\`
BABEL39_GENERIC_SCL_COMPONENT_FLUX_CONSERVATION = PROVED_ALL_N
BABEL39_EXACT_ZERO_FLUX_SUMSET_DOMAIN_PRUNING = PROVED_IN_P
BABEL39_EXACT_Q_PUNCTURED_COMPONENT_ENUMERATION = PROVED_WITH_2^K
BABEL39_MAJORITY_CLOSURE_IFF_PORT_2CNF = KNOWN_THEOREM_VERIFIED_FINITE
BABEL39_CERTIFIED_COMPONENT_COMPOSITION_IN_P_WHEN_K_R_LOG = PROVED
BABEL39_ARBITRARY_CONNECTED_SCL_AUTO_PARTITION_DISCOVERY = OPEN
BABEL39_EVERY_SCL_PORT_RELATION_BIJUNCTIVE_AFTER_PRUNING = NOT_PROVED
BABEL39_GENERAL_P_TIME_SAT = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
