# JANUS Methodology

## Purpose

The laboratory searches for mathematically meaningful routes toward resolving `P` versus `NP`. It records both positive and negative results. The registry is not a confidence market and not a proof by accumulation.

## Admission protocol

A hypothesis enters `registry/hypotheses.json` only when all fields below are present:

1. **Formal statement** — quantified objects, size parameter, and computational model are explicit.
2. **Consequence** — the exact theorem that would follow if the hypothesis were proved.
3. **Falsification condition** — a finite counterexample or a theorem that would destroy it.
4. **Attack surface** — known hard families, lower-bound frameworks, or structural obstructions.
5. **Reproduction plan** — code or a derivation that another person can independently check.
6. **Claim boundary** — what the entry does not establish.

Vague metaphors, renamed versions of `P = NP`, and claims whose decisive step is hidden in an undefined oracle are rejected before admission.

## Status meanings

- `PROPOSED`: formally stated but not yet attacked.
- `UNDER_ATTACK`: at least one active falsification program exists.
- `OPEN`: all recorded attacks have failed to destroy the exact statement.
- `FORMALIZING`: proof obligations are being translated into a proof assistant or equivalent formal system.
- `INDEPENDENT_REPRODUCTION`: an external party is reproducing the computational or formal result.
- `PEER_REVIEW`: a complete manuscript or formal proof is under external review.
- `PROVED`: a complete proof exists, has passed the laboratory verifier, and has independent verification.
- `DESTROYED`: a counterexample or theorem contradicts the exact statement.
- `REJECTED`: the formulation is non-formal, circular, duplicate, or unfalsifiable.

`OPEN` is not evidence of truth. A hypothesis can remain open merely because the attacks are weak.

## Reproducibility levels

- `R0`: idea only.
- `R1`: exact mathematical statement.
- `R2`: executable experiment or machine-checkable derivation.
- `R3`: deterministic rerun from committed inputs, seed, environment, and expected output.
- `R4`: independent reproduction by another person or implementation.
- `R5`: formal proof checked by a proof assistant and independently reviewed.

No finite benchmark can promote a universal complexity claim to `PROVED`.

## Attack protocol

Every attack record must state:

- target hypothesis;
- attack type;
- exact input family or theorem used;
- expected failure mode;
- result;
- artifact or derivation location;
- whether the attack was decisive.

Preferred attacks:

1. explicit small counterexample;
2. infinite counterexample family;
3. reduction to a known lower bound;
4. adversarial generator with deterministic seed;
5. proof-complexity or representation-size lower bound;
6. hidden-oracle and hidden-exponential audits;
7. equivalence-to-the-original-problem audit.

## Claim boundaries

The following are never accepted as proofs of `P = NP`:

- success on finitely many instances;
- average-case speedup;
- a new branching heuristic;
- a polynomial-sized object whose construction is not polynomially bounded;
- a certificate that is easy to verify but not shown to be findable in polynomial time;
- hardware parallelism that uses exponentially growing physical resources;
- an unproved universal compression lemma;
- a solver returning `PASS` without a mathematical proof object.

## Preservation

Destroyed hypotheses are never deleted. Their exact statements, counterexamples, and descendants remain in `graveyard.json` and `genealogy.json`, preventing the laboratory from repeatedly rediscovering renamed dead ends.
