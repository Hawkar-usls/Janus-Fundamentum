# JANUS TRUMP R44AC — L4 structured-state envelope barrier

## Fixed route

R44AC does **not** claim that every exact SAT algorithm needs exponential state. The fixed route is narrower:

`FULL_FUNCTION_STRUCTURED_DNNF_BOTTOM_UP_STATE`.

The live state must preserve the exact Boolean function of accumulated constraints in a structured decomposable NNF representation, and the construction proceeds bottom-up by exact conjunction/apply, with the restructuring operations allowed by the cited model.

This precision is essential. Without fixing the state language, the statement `unbounded interface width => exponential state` is too broad: a CNF is itself an exact representation of its function, and a SAT-only algorithm may preserve less information than a full compiled function.

## Barrier A — final structured representation size

Amarilli, Monet and Senellart, *Connecting Width and Structure in Knowledge Compilation* (ICDT 2018, DOI 10.4230/LIPIcs.ICDT.2018.6), prove lower bounds connecting treewidth to structured representation size. For monotone CNF of bounded clause arity and bounded variable degree, every SDNNF representation has size singly exponential in treewidth; with arity and degree fixed this is `2^{Omega(tw)}`.

Therefore a universal TRUMP route that requires an exact full-function SDNNF/d-SDNNF state cannot infer a polynomial L4 envelope merely from exactness or decomposition. On families with growing treewidth, the chosen representation class itself can force exponential size.

This is a **representation-class lower bound**, not a lower bound for arbitrary SAT algorithms.

## Barrier B — intermediate live state

The more direct L4 result is de Colnet and Mengel, *Lower Bounds on Intermediate Results in Bottom-Up Knowledge Compilation* (AAAI 2022, DOI 10.1609/aaai.v36i5.20496).

They exhibit a class of CNF formulas with constant-size final str-DNNF representations for which any bottom-up compilation in their general structured-DNNF model, using conjunction and restructuring, must produce intermediate str-DNNFs of exponential size. Hence the bottom-up process takes exponential time and space.

So even

`SMALL_FINAL_STATE`

does not imply

`SMALL_INTERMEDIATE_LIVE_STATE`.

This directly blocks using bottom-up exact structured compilation as a universal discharge of `L4_POLYNOMIAL_STATE_ENVELOPE`.

## R44AC verdict

For the fixed route:

`FULL_FUNCTION_STRUCTURED_DNNF_BOTTOM_UP_STATE`

we obtain the admissible theorem-level outcome

`EXPONENTIAL_STATE_BARRIER`.

The conclusion is deliberately narrow:

- exact structured full-function compilation can require exponential final representation size on high-width families;
- even when the final structured representation is constant-size, bottom-up compilation can require exponentially larger intermediate live states;
- therefore this route cannot by itself prove the universal polynomial live-state envelope required by L4.

## What remains open

R44AC does **not** rule out a weaker SAT-sufficient summary. A successor may legitimately try to define a state that preserves only what is necessary for satisfiability rather than the full Boolean function.

But then it must prove a context-complete equivalence theorem:

`summary(S1) = summary(S2) => for every admissible future context C, SAT(S1 ∧ C) = SAT(S2 ∧ C)`.

Without such a theorem, dropping information is not compression with exact authority; it is an information dead zone.

Hence the next admissible L4 question is:

`PROVE_POLYNOMIAL_CONTEXT_COMPLETE_COMPRESSION`

or

`PROVE_STATE_LOWER_BOUND_FOR_ONE_FIXED_SUMMARY_MODEL`.

No benchmark or empirical compactness result moves theorem authority.

Scientific boundary: `TRUMP_finished=false`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
