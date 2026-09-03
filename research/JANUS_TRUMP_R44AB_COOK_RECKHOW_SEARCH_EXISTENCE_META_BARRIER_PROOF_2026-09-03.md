# JANUS TRUMP R44AB — Cook–Reckhow search/existence meta-barrier

## Theorem

There exists a Cook–Reckhow propositional proof system that is both polynomially bounded and polynomial-time automatizable if and only if `P = NP`.

### Forward direction

Let `Psys` be a Cook–Reckhow proof system. Assume:

1. **Polynomial boundedness.** There is a fixed polynomial `q` such that every tautology `phi` has a `Psys`-proof of length at most `q(|phi|)`.
2. **Polynomial automatizability.** There is a fixed polynomial `r` and an algorithm `A` such that, whenever `phi` is a tautology, `A(phi)` outputs a valid `Psys`-proof of `phi` within `r(|phi| + s_Psys(phi))` steps, where `s_Psys(phi)` is the shortest `Psys`-proof length.

For every tautology, `s_Psys(phi) <= q(|phi|)`. Hence `A` must output a valid proof within

`T(n) = r(n + q(n))`,

which is polynomial in `n`.

Define a deterministic decision procedure for `TAUT`: on input `phi`, simulate `A(phi)` for exactly `T(|phi|)` steps. Accept iff a valid `Psys`-proof of `phi` is produced and verifies; otherwise reject.

If `phi` is a tautology, the automatizability guarantee forces a proof to appear before the cutoff. If `phi` is not a tautology, soundness/range correctness of the Cook–Reckhow system forbids any valid `Psys`-proof of `phi`. Thus `TAUT in P`.

Since `TAUT` is coNP-complete and deterministic polynomial time is closed under complement, `SAT in P`. Therefore `P = NP`.

### Reverse direction

Assume `P = NP`. Then `SAT in P`, hence by complement closure `TAUT in P`.

Define a Cook–Reckhow proof system `Q` by taking a string `pi` as a candidate formula. If `pi` is a tautology, output `pi`; otherwise output one fixed tautology. The tautology test is polynomial-time under `P = NP`, so `Q` is a valid Cook–Reckhow proof system.

Every tautology `phi` has the proof `pi = phi`, so proof length is `O(|phi|)`: `Q` is polynomially bounded. An automatizer on tautological input simply outputs `phi`, hence is polynomial-time.

Therefore such a proof system exists.

## Consequence for TRUMP L3

This gives a system-independent boundary:

`P_BOUNDED_PROOF_EXISTENCE + GENERIC_POLYTIME_PROOF_DISCOVERY <=> P=NP` at the existential proof-system level.

So increasing proof-language strength does not itself create an easier path to `L3_POLYNOMIAL_DISCOVERY_AND_LOCAL_WORK`. Proof-size strength and proof-search complexity must remain separate.

Cook–Reckhow gives the weaker existence frontier:

`there exists a polynomially bounded propositional proof system <=> NP=coNP`.

R44AB identifies the additional discovery jump:

`there exists a polynomially bounded + polynomial-time automatizable Cook–Reckhow system <=> P=NP`.

## Firewalls

- `SHORT_PROOF_EXISTS != SHORT_PROOF_CAN_BE_FOUND`
- `P_BOUNDED != AUTOMATIZABLE`
- `NP=coNP != P=NP`
- `PROOF_SIZE_STRENGTH != SEARCH_EASINESS`
- `AUTOMATIZER_PROMISE_ON_TAUTOLOGIES != TOTALITY_ASSUMPTION`
- the polynomial cutoff argument is required to turn automatizability plus p-boundedness into a total decision algorithm
- `NO_PROOF_FOUND != PROOF_DOES_NOT_EXIST`
- `META_BARRIER != P!=NP`
- `P_VS_NP = OPEN`

## Next admissible move

Do not choose another proof language merely because it is stronger than Cutting Planes. A successor must explicitly avoid one premise of this meta-barrier or prove polynomial total decision/discovery directly. Otherwise it is the same machine under new syntax.
