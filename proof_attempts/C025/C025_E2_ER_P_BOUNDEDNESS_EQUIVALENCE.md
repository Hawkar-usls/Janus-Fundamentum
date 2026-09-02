# C025-E2 — B2 / Extended-Resolution p-boundedness equivalence

**Status:** `EQUIVALENCE_PROVED_FOR_CNF_REFUTATIONS`; the global polynomial-size question remains open.

**Claim ceiling:** no polynomial upper bound or superpolynomial lower bound for Extended Resolution / Extended Frege is claimed here.

## The frozen B2 system

For UNSAT root CNF `F0`, B2 uses root axioms, fresh extension definitions

```text
e <-> (a AND b)
```

with exact clauses

```text
(~e OR a)
(~e OR b)
(e OR ~a OR ~b)
```

for literals `a,b` over root or earlier extension variables, followed by exact Resolution. At the root, the advertised reusable clause is the empty clause, so the original-variable output boundary is vacuous.

## ER -> B2

In the standard literal-AND presentation of Extended Resolution, each extension step is identical to B2. Rename extension variables in introduction order to strictly increasing ids above the root-variable range. This preserves topological dependency and has linear/polynomial encoding overhead.

Unused proof nodes may be deleted, and unused extension definitions may be removed by the same transitive definition-closure normalization already enforced by the B2 portable verifier.

If an ER presentation instead uses `z <-> (l1 OR l2)`, introduce `e <-> ((~l1) AND (~l2))` and translate source literal `z` to B2 literal `~e` and source literal `~z` to `e`; Resolution pivots translate by the same polarity swap. This is linear overhead.

Therefore ER polynomially simulates into B2.

## B2 -> ER

Every B2 extension definition is a standard Extended-Resolution extension and every B2 inference is Resolution. Dropping serialization/fingerprint metadata yields an ER refutation directly.

Therefore B2 polynomially simulates into ER.

## Theorem

For UNSAT CNF refutations,

```text
B2 ~=p ER.
```

Hence the global E2 question

> Does every UNSAT CNF of encoded length N have a B2 refutation of size poly(N)?

is, up to ordinary polynomial encoding translations, exactly the p-boundedness question for Extended Resolution on CNF refutations.

Extended Resolution is polynomially equivalent to Extended Frege, so this is a classical strong-proof-system frontier rather than a Policy-0B-local lemma.

## Complexity consequences

If E2 is positive, the polynomial-time B2 verifier makes polynomial-size UNSAT certificates available for every CNF. Thus `UNSAT in NP`, hence `NP = coNP`. This does not give `P=NP` without the separate deterministic proof-discovery/search theorem.

If E2 is negative, the lower bound transfers to Extended Resolution / Extended Frege up to p-equivalence and would constitute a major proof-complexity lower-bound breakthrough. ER non-p-boundedness is not currently known by itself to imply `NP != coNP`, because ER is not known to be an optimal propositional proof system.

## Frontier split

```text
C025_E2A_B2_ER_P_EQUIVALENCE             = PROVED
C025_E2B_GLOBAL_ER_P_BOUNDEDNESS         = OPEN_MAJOR_EXTERNAL_FRONTIER
C025_E2R_POLICY0B_RESTRICTED_PROOF_SIZE   = NEXT_TRACTABLE_ATTACK
C025_C2_DETERMINISTIC_PROOF_SEARCH       = DEFERRED_UNTIL_E2R
ISSUE_212_ACTIVE_REPRESENTATION          = OPEN
P_VS_NP                                  = OPEN
```

`E2R` is deliberately narrower: freeze the actual Policy-0B generation/retention/deletion/sharing discipline and prove or refute a polynomial bound on the certificates reachable under that deterministic resource policy. A result there speaks about JANUS even if global ER p-boundedness remains open.

## Literature boundary

This pass checked standard ER definitions and ER/EF equivalence against Sam Buss's *Proof Complexity I*, the Beame–Pitassi survey, and Jan Krajicek's recent chapter on ER. The external literature status remains that strong Extended Resolution / Extended Frege lower bounds are open.
