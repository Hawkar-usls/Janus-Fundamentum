# Source audit — universal selector / WDR contraction frontier

Date: 2026-09-27
Decision: `PASS_NEW_BARRIER_SCOPE_CONFIRMED`
New math authorized: `true`
Scope: `R5_E9_UNIVERSAL_SELECTOR_WDR_CONTRACTION_GATE_V1`

## Internal anti-loop sweep

Checked the E8 direct algorithm contract, WDR lean normal-form scheduler, improving-mapping/persistency audit, matching-autarky theorem, no-growth DP charge, partial WDR closure, and the branch's universal-selector barrier note. The key anti-loop invariant is that an existential SAT-preserving branch is useless unless the branch is computable in polynomial time without querying SAT.

## External names / queries

Checked autarkies, linear autarkies, matching autarkies, lean clause-sets, persistency/improving mappings, SAT self-reducibility, equivalence substitution, blocked-clause elimination, Davis-Putnam elimination, and polynomial kernel/reduction systems.

## Sources checked

- O. Kullmann, *Investigations on autark assignments*, Discrete Applied Mathematics 107 (2000), 99–137, DOI `10.1016/S0166-218X(00)00262-6`; linear autarkies are polynomial-time accessible via linear programming and linearly lean clause-sets are defined.
- O. Kullmann, *Lean clause-sets: generalizations of minimally unsatisfiable clause-sets*, Discrete Applied Mathematics 130 (2003), 209–249, DOI `10.1016/S0166-218X(02)00406-7`; general, linear, and matching autarky systems and canonical lean normal forms.
- Existing JANUS improving-mapping/persistency source audit and WDR prior-art firewall, including Buss–Thapen style redundancy/substitution systems and the ranked/SR boundary.

## Collision result

Known preprocessing/autarky/redundancy systems are donors or barriers, not a universal polynomial SAT decider. Rephrasing a safe branch as a `universal selector` is not novelty: a total polynomial SAT-equivalent strict-decrease selector with a polynomially bounded potential would already constitute the missing algorithmic content. The scoped live work is therefore restricted to proving or falsifying concrete polynomially computable R1/R2/R5/R6 contractions without a SAT oracle.

## Authorized work

Authorize theorem/checker work for the current `STRICT_EQSAT_CONTRACTION_DISCOVERY` route only. This includes exact analysis of matching/linear-autarky, no-growth elimination, universal-selector equivalence barriers, and the remaining WDR structural lanes. It does not authorize a claim that P=NP.

`P_VS_NP = OPEN`.
