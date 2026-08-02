# C006 Screening Report — Thirty Proof-Directed Survivors

## Outcome

Cycle C006 began with 42 candidate formulations.

- 12 were rejected before admission.
- 30 received live identifiers `H030-H059`.
- Every admitted hypothesis received exactly two immediate registered attacks, `A077-A136`.
- No attack was decisive.
- Survival means only that the recorded attack did not contradict the exact statement.

The cycle does not treat quantity as progress. Each survivor contains two mandatory fields:

- `proof_role`: the exact theorem chain it serves;
- `next_gate`: the next construction, lower bound, implementation, or counterexample that can advance or kill it.

## Route map

### Direct `P != NP` and `NP != coNP` targets

`H030-H038` cover explicit NP circuit lower bounds, certified SAT anti-checkers, witnessing formulas, Nisan-Wigderson and strong proof generators, Extended-Frege circuit rewriting, canonical disjoint NP pairs, full-IPS extraction, and PIT-axiom lower-bound routes.

These entries are not interchangeable. Some are direct targets; others are bridge lemmas whose assumptions must be proved independently.

### Constructive `P = NP` routes

`H040-H049` are complete algorithmic mechanisms. They require two-sided correctness, termination, polynomial total resources, and witness or refutation recovery. They include repaired certified quotient search, finite-gate variable elimination, affine-cardinality decomposition, finite local submodular/TU/SoS lifts, deterministic extension-PC proof search, deterministic isolation into a tractable residual class, canonical CDCL, and certified exact model-counting decomposition.

The broad or vacuous ancestors of several of these routes were rejected rather than silently reused.

### Adversarial bridges

`H050-H056` attempt to destroy or constrain constructive mechanisms by translating them into lower-bounded representation classes, communication protocols, explicit algebraic hard families, mixed residual expanders, proof-search lower bounds, or range-avoidance reductions.

A proved adversarial bridge is progress even when it kills a route to `P = NP`, because it removes a false path and may yield an independent lower-bound theorem.

### Barrier-breaking routes

`H039`, `H057-H059` address PIT derandomization, Circuit-SAT self-improvement, sparse non-natural properties, and explicit linear-function lower bounds. Their consequences are stated as intermediate unless they reach an explicit NP language.

## Rejected before admission

The twelve rejected candidates are permanently recorded as `H000-G10` through `H000-G21`. The principal failure modes were:

- a vague invariant with no formal object;
- isolation without existence testing;
- projected representations already contradicted by DNNF closure and lower bounds;
- invalid direct consequences from PIT or NEXP lower bounds;
- conflating short-proof existence with efficient search;
- finite benchmark evidence presented as an asymptotic proof;
- free semantic canonicalization;
- assuming local rules are non-universal;
- random families presented as explicit;
- uncharged coefficient precision;
- an open problem with no proof-directed role.

## Highest-value next gates

1. **H035 — circuit-rewriting diameter.** Find an explicit pair of equivalent circuits and an invariant that changes slowly under the exact local rewriting relation.
2. **H041/H050 — elimination versus DNNF.** Either build the first finite-gate elimination template set or prove that every valid run compiles to ordinary DNNF and then apply explicit lower bounds.
3. **H048/H054 — canonical CDCL.** Implement one fully specified policy, enumerate minimal failures, and seek a uniform formula family hard for every fixed policy description.
4. **H053 — mixed residual expansion.** Construct an explicit XOR-plus-non-affine family whose expansion survives every certified affine substitution.
5. **H031/H056 — certified anti-checkers.** Resolve the asymmetry between certifying positive and negative SAT-circuit errors.

## Reproduction

Run:

```bash
python tools/validate_registry.py
```

The validator checks IDs, cross-references, terminal shadows, sources, genealogy, mandatory proof roles, nonempty next gates, and the minimum attack count for all hypotheses beginning with `H030`.

## Claim boundary

C006 creates a structured proof-search graph. It does not prove `P = NP`, `P != NP`, `NP != coNP`, or the novelty of any JANUS-generated statement.
