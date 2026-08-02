# JANUS Methodology

## Purpose

The laboratory searches for mathematically meaningful routes toward resolving `P` versus `NP`. It records positive results, failed mechanisms, bridge lemmas, barriers, and explicit counterattacks. The registry is not a confidence market and not a proof by accumulation.

## Admission protocol

A hypothesis enters the live registry only when all of the following are present:

1. **Formal statement** — quantified objects, size parameter, and computational or proof model are explicit.
2. **Consequence** — the exact theorem that would follow if the hypothesis were proved.
3. **Falsification condition** — a finite counterexample, infinite family, or theorem that would destroy it.
4. **Attack surface** — known hard families, lower-bound frameworks, closure properties, or structural obstructions.
5. **Reproduction plan** — code, construction, or derivation that another person can independently check.
6. **Claim boundary** — what the entry does not establish.
7. **Proof role** — the exact place occupied by the statement in a route toward `P = NP`, `P != NP`, `NP != coNP`, a required circuit lower bound, or the destruction of a central JANUS mechanism.
8. **Next gate** — the next concrete theorem, construction, implementation, or counterexample needed to advance the route.

Beginning with `H030`, `proof_role` and `next_gate` are mandatory machine-validated fields, and every admitted hypothesis must reference at least two recorded attacks.

Vague metaphors, renamed versions of the target theorem, hidden oracles, uncharged numerical precision, and interesting open problems without an explicit downstream proof role are rejected before admission.

## Proof-role classes

- **Direct target** — proving the statement itself settles `P = NP`, `P != NP`, or `NP != coNP`.
- **Direct bridge** — converts a more concrete theorem or artifact into a direct target.
- **Direct algorithm** — supplies a complete polynomial-time decision procedure with soundness, completeness, termination, and witness or refutation recovery.
- **Proof-complexity route** — yields an explicit superpolynomial lower bound for a precisely named proof system and states the exact complexity-class consequence.
- **Adversarial bridge** — translates a JANUS mechanism into a representation or proof system with a known lower-bound attack surface.
- **Target selection** — replaces an existential hard family with one explicit candidate family.
- **Barrier breaker or win-win lemma** — does not itself settle the target, but proving it forces a substantial circuit/proof lower bound or removes a recognized obstacle.
- **Algorithmic lower-bound route** — uses an executable analysis algorithm to derive circuit lower bounds; the registry must distinguish intermediate lower bounds from a direct separation for an NP language.

An entry may be valuable without being direct, but its role must never be overstated.

## Status meanings

- `PROPOSED`: formally stated but not yet attacked.
- `UNDER_ATTACK`: at least one active falsification program exists.
- `OPEN`: all recorded attacks failed to destroy the exact statement.
- `FORMALIZING`: proof obligations are being translated into a proof assistant or equivalent formal system.
- `INDEPENDENT_REPRODUCTION`: an external party is reproducing the computational or formal result.
- `PEER_REVIEW`: a complete manuscript or formal proof is under external review.
- `PROVED`: a complete proof exists, has passed the laboratory verifier, and has independent verification.
- `DESTROYED`: a counterexample or theorem contradicts the exact statement.
- `REJECTED`: the formulation is non-formal, circular, duplicate, unfalsifiable, has an invalid consequence, or lacks a proof-directed role.

`OPEN` is not evidence of truth. A hypothesis can remain open because the attacks are weak, because its model is too broad, or because it restates a major frontier precisely.

## Reproducibility levels

- `R0`: idea only.
- `R1`: exact mathematical statement.
- `R2`: executable experiment or machine-checkable derivation.
- `R3`: deterministic rerun from committed inputs, seed, environment, and expected output.
- `R4`: independent reproduction by another person or implementation.
- `R5`: formal proof checked by a proof assistant and independently reviewed.

No finite benchmark can promote a universal complexity claim to `PROVED`.

## Attack protocol

Every attack record states:

- target hypothesis;
- attack type;
- exact input family, reduction, or theorem used;
- expected failure mode;
- method;
- result;
- artifact or derivation location;
- whether the attack was decisive.

Preferred attacks, in order of force:

1. explicit small counterexample;
2. infinite counterexample family;
3. reduction to a known lower bound;
4. closure or simulation theorem;
5. adversarial generator with deterministic seed;
6. proof-complexity or representation-size lower bound;
7. hidden-oracle, hidden-precision, and hidden-exponential audits;
8. equivalence-to-the-original-problem audit;
9. invalid-consequence audit;
10. proof-existence versus proof-search versus verification audit.

A failed attack may weaken a statement by exposing a missing assumption. Weakening must be recorded; it is not counted as positive evidence.

## Proof-chain discipline

A route is only as strong as its weakest unproved link. JANUS therefore records chains rather than treating all hypotheses as parallel votes.

For every route:

- the root target is named;
- bridge lemmas identify their parents and descendants in `genealogy*.json`;
- mutually incompatible branches may coexist;
- each branch names the theorem or experiment that resolves it;
- a result for a restricted proof system is not silently transferred to a stronger system;
- a lower bound for an exponential-time class is not presented as a separation for an NP language;
- a polynomial-size certificate is not presented as a polynomial-time algorithm unless search and verification are also bounded;
- a randomized isolation or average-case result is not presented as a deterministic worst-case SAT algorithm.

## Claim boundaries

The following are never accepted as proofs of `P = NP`:

- success on finitely many instances;
- average-case speedup alone;
- a new branching heuristic without a universal complexity proof;
- a polynomial-sized object whose construction is not polynomially bounded;
- a certificate that is easy to verify but not shown to be findable in polynomial time;
- hardware parallelism using exponentially growing physical resources;
- an unproved universal compression lemma;
- a solver returning `PASS` without a mathematical proof object;
- deterministic PIT described as a direct proof of `P != NP` rather than its exact lower-bound consequence;
- isolation without deterministic existence testing and witness recovery;
- a random hard family presented as an explicit polynomial-time constructible family.

## Preservation

Destroyed and rejected hypotheses are never deleted. Their exact statements, counterexamples, rejection reasons, salvage conditions, and descendants remain in `graveyard*.json` and `genealogy*.json`. This prevents renamed dead ends from repeatedly re-entering the laboratory.

## Cycle C006 rule

C006 screened 42 formulations. Twelve failed admission before receiving live IDs. Thirty hypotheses `H030-H059` survived two attacks each and were admitted because they expose a proof role and a next gate. The count is not evidence. The useful output is the proof graph: which theorem would settle which branch, which mechanisms can be attacked together, and which missing lemma should be attempted next.
