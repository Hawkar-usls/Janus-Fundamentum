# JANUS Methodology

## Purpose

The laboratory searches for mathematically meaningful routes toward resolving `P` versus `NP`. It records positive results, failed mechanisms, bridge lemmas, barriers, explicit counterattacks, and the ancestry of every later idea. The registry is not a confidence market and not a proof by accumulation.

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

Beginning with `H060`, every new entry must additionally contain:

9. **Derived from** — a nonempty list of older JANUS hypotheses that materially generated the child.
10. **Delta from parents** — the precise new obligation, restriction, target family, proof system, or bridge introduced by the child.

`tools/validate_lineage.py` verifies that all parents exist, are older than the child, match the genealogy ledger exactly, and have not been added as decorative citations.

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

Every attack record states the target, failure mode, exact theorem or family, method, result, artifact, and whether the attack was decisive.

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

## Inheritance protocol

A child is admissible only when it does at least one of the following:

- replaces an existential object by an explicit target family;
- repairs a formally identified failure in a parent;
- changes the proof system in a stated way after a lower bound kills the former system;
- converts two independent branches into a checkable bridge;
- isolates a semantic escape resource such as overlap, cancellation, auxiliary projection, or stronger inference rules;
- turns a broad frontier into a concrete theorem with a smaller attack surface.

The following do **not** count as inheritance:

- renaming the parent;
- weakening a quantifier without explaining the proof benefit;
- adding another adjective such as “dynamic”, “tensor”, or “recursive” without a formal delta;
- citing a destroyed parent while silently reusing the exact destroyed mechanism;
- copying a consequence but changing no proof obligation.

A destroyed hypothesis may have descendants. The descendant must explicitly state which failed component is abandoned and which stronger or different mechanism replaces it.

## Proof-chain discipline

A route is only as strong as its weakest unproved link. JANUS therefore records chains rather than treating all hypotheses as parallel votes.

For every route:

- the root target is named;
- bridge lemmas identify parents and descendants;
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

## Cycle rules

### C006 — proof-directed admission

C006 screened 42 formulations. Twelve failed admission, and thirty `H030-H059` survived two attacks each because they exposed a proof role and next gate.

### C007 — inherited generation and ancestor attack

C007 derives `H060-H069` from older nodes, enforces machine-readable parent/delta fields, attacks both generations, destroys H048 through a general-Resolution lower bound, and salvages its constructive direction only by changing the proof system in H063. The count of descendants is not progress by itself; the useful output is the shorter and more explicit proof graph.
