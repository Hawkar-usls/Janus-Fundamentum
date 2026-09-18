# U-PAIR-1J Scoped Carrier Authority — SA1–SA5 Abstract Soundness Theorem

**Date:** 2026-09-19  
**Authority:** `ABSTRACT_SCOPED_AUTHORITY_SOUNDNESS__NO_COMPLETENESS_OR_COMPLEXITY_CLAIM`  
**Formal specification:** `e64fe909764f331e1f52b8f2ab306039e0c6e827`  
**Inherited Dual-Debt theorem:** `ed203e9ebbc5699753c88f5dc8362892c720da14`

## 1. Definitions

Fix a frozen source identity (F_0), concrete/source semantic state space (Sigma_F), carrier state space (C), and an authority token

[
A_{m scope}
=
(F_0,operatorname{Reach},operatorname{Readout},
operatorname{Continuation},operatorname{Capability},
operatorname{Proof},operatorname{Expiry}).
]

Let

[
hosubseteq Sigma_F	imes C
]

be the token-bound realization relation.

For a continuation/context (k) in the frozen continuation language (K), let

[
R_F(s,k)
]

denote the exact declared readout obtained from source state (s), and let

[
R_C(c,k)
]

denote the corresponding carrier-side readout.

An ACTIVE token certifies at minimum:

### A1 — Source binding

The source identity used by the current trace equals the token's frozen (F_0) identity.

### A2 — Reachability authority

For every authority-bearing carrier state used by the accepted trace, either:

1. it has a replayable realization lineage to some (sinSigma_F) with (ho(s,c)), or
2. the token contains a stronger **unreachable-state observational irrelevance theorem** establishing that, for every allowed continuation in (K), evaluating with the full formal carrier space versus restricting to source-realizable carrier states yields the same declared readout.

The second form is intentionally stronger than proving that one isolated unreachable state appears harmless.

### A3 — Continuation adequacy

For every realized pair (ho(s,c)) and every allowed (kin K),

[
R_F(s,k)=R_C(c,k).
]

If the carrier is a quotient, every merged source-reachable fiber is monochromatic for all declared (R_F(cdot,k)), (kin K).

### A4 — Capability binding

Every authority-bearing carrier operation used by the trace is licensed by the exact capability digest and is inside the declared continuation/operation contract.

### A5 — Replayable proof authority

The adequacy/source/capability proof payloads independently replay and bind to the token digest.

A token is STALE when the requested use no longer exactly matches an authority-defining field; it is INVALID if proof/integrity replay fails.

---

# SA1 — Source Realizability Soundness

### Statement

Under an ACTIVE token satisfying A1–A5, an accepted carrier-derived fact cannot gain source-semantic authority solely from a source-unrealizable formal carrier state.

More precisely, every authority-bearing fact used by the accepted trace is justified either:

1. through a realized carrier state (c) with replayable (ho(s,c)) lineage from the frozen source; or
2. through an exact observational-irrelevance theorem proving that inclusion of source-unrealizable carrier states cannot change the declared readout under any allowed continuation.

### Proof

Consider an authority-bearing carrier fact (p) used by an accepted trace.

By the SOURCE_REALIZABILITY_GATE, the checker must classify its supporting carrier semantics under one of the two authorized ReachContract forms.

#### Case 1 — PREIMAGE_REQUIRED

The supporting carrier state/transitions possess replayable lineage to a concrete source state (s) satisfying (ho(s,c)). Therefore the carrier fact is not being justified by carrier grammar membership alone; its semantic authority is anchored to the frozen source semantics.

By A3, every allowed continuation/readout applied to that realized carrier state agrees with the source result.

#### Case 2 — UNREACHABLE_IRRELEVANT

The token contains a checked theorem that restricting carrier semantics to the source-realizable image or allowing the larger formal carrier state space yields identical declared readout for every allowed continuation.

Hence any source-unrealizable formal carrier states may participate in an implementation or symbolic representation only because their presence is observationally irrelevant to the exact authority claim being made.

If neither case is proved, A2 fails, the token cannot be ACTIVE for that use, and the carrier fact has no accepted source authority.

Thus no accepted terminal authority can be obtained merely by reasoning through fictitious carrier states without either source realization or an exact theorem excluding their influence.

QED.

**Verdict:** `SA1_PROVED_UNDER_ACTIVE_REACH_CONTRACT`.

---

# SA2 — Query/Continuation Adequacy

### Statement

Let an ACTIVE token satisfy A1–A5. Then replacing source-realizable concrete states by their carrier representatives preserves the declared Readout for every allowed continuation

[
kin K.
]

If multiple source-realizable states are merged into one carrier/quotient state, the merge is exact for the declared scope.

### Proof

Take any source state (sinSigma_F) and any carrier state (c) with

[
ho(s,c).
]

By A3, for every allowed continuation (kin K),

[
R_F(s,k)=R_C(c,k).
]

Therefore replacing (s) by (c) in an authority-bearing computation preserves the declared observable under every allowed future context.

Now suppose two source-realizable states (s_1,s_2) are merged into the same carrier representative (q).

The quotient admission condition requires monochromaticity under the complete declared continuation family:

[
R_F(s_1,k)=R_F(s_2,k)
qquad
orall kin K.
]

Thus no continuation admitted by the token can distinguish the merged states with respect to the declared readout.

For formal carrier states outside the source-realizable image, SA1 either excludes their authority or uses the stronger observational-irrelevance theorem, so they cannot invalidate the conclusion.

Hence the carrier/quotient is exact for the declared source/readout/continuation scope.

QED.

**Verdict:** `SA2_PROVED_FOR_DECLARED_SCOPE`.

---

# SA3 — Scope Staleness

### Statement

Let (A) be a previously ACTIVE authority token. If a later requested authority use changes any authority-defining field:

- frozen source identity,
- ReachContract,
- Readout,
- ContinuationLanguage,
- CapabilityDigest,
- adequacy-proof identity/contract,
- ExpiryRule version,

then (A) cannot authorize that changed use unless an independently accepted equivalence/revalidation theorem establishes a new token.

Historical validity of (A) for its old scope remains unchanged.

### Proof

The soundness statements SA1 and SA2 are quantified over the exact components bound by (A).

Changing the source can change the realizable carrier image.

Changing Reach can change which formal states or transitions are authorized.

Changing Readout can change fiber monochromaticity: a quotient sufficient for SAT existence need not preserve model count or witnesses.

Changing ContinuationLanguage changes the set of contexts over which indistinguishability was proved. A formula-specific quotient may be exact for one frozen continuation family while becoming unsound under a broader family.

Changing Capability may introduce operations whose semantics, verifier assumptions, budgets or proof interpretation were not covered by the old adequacy proof.

Changing the proof/expiry contract changes the evidence or validity rule that made the token authoritative.

Therefore the premises of SA1/SA2 no longer match the requested use. Reusing the token would amount to applying a theorem outside its quantified hypotheses.

The safe state is STALE, not false: old receipts remain historically valid for the old scope. A new proof may revalidate the same carrier under a changed scope, producing a new authority token.

QED.

**Verdict:** `SA3_PROVED_BY_SCOPE_BINDING`.

---

# SA4 — Scoped Open-Vault Safety

### Statement

Let an OPEN refusal record be keyed by

[
(operatorname{core_digest},
operatorname{capability_digest},
operatorname{authority_scope_digest}).
]

If exact key equality, payload integrity and independent refusal-ledger replay all hold, the record may safely suppress repetition of the identical scoped portfolio attempt.

It cannot:

- prove SAT,
- prove UNSAT,
- prove intrinsic hardness,
- discharge semantic debt,
- discharge transformation debt.

If capability or authority scope changes, the old OPEN record is STALE for the new use.

### Proof

By construction, an OPEN record states only that a specific ordered capability/portfolio failed to close a specific exact core under a specific authority scope and budget/protocol contract.

Exact triple-key equality plus replay establishes that the current request is exactly the previously exhausted scoped attempt. Therefore repeating that identical search is unnecessary for reproducing the same portfolio-scoped refusal.

However, the refusal ledger contains no SAT witness, UNSAT proof, semantic reconstruction discharge, or executed/superseded transformation receipt. Under the Dual-Debt rules, only named accepted discharge/execution transitions may change those ledgers.

Therefore an OPEN lookup changes no semantic or transformation authority.

If capability or authority scope changes, the prior refusal quantified over different search power or different semantic scope. By SA3, the old authority context cannot be reused for the changed request, so the OPEN record is logically STALE.

QED.

**Verdict:** `SA4_PROVED_FOR_EXACT_TRIPLE_KEY_REPLAY`.

---

# SA5 — Scoped Terminal Composition

### Statement

Assume an accepted Dual-Debt terminal trace satisfies DD5 and, additionally, every carrier-derived semantic fact used in the trace is covered at the moment of use by an ACTIVE token satisfying A1–A5.

Then the original-source terminal soundness theorem remains valid:

[
oxed{
D_0(B)Rightarrow F_0(f_X(B),B)
}
]

and no source-unrealizable or out-of-continuation carrier state can supply unlicensed terminal authority.

### Proof

DD5 already establishes that, if the strengthened semantic terminal conditions and transformation closure conditions hold, the accepted terminal inherits the Projected Semantic Debt Kernel reconstruction theorem:

[
D_0(B)Rightarrow F_0(f_X(B),B).
]

The only new risk introduced by using aggressive specialized carriers is that some intermediate semantic fact used by the DD5 trace might not actually be authorized by the original source semantics or might only be exact for a narrower query/future context.

By hypothesis, every such carrier fact was produced under an ACTIVE token.

SA1 therefore guarantees that the fact is anchored either to a replayable source-realizable lineage or to a theorem proving unreachable carrier states observationally irrelevant for the declared scope.

SA2 guarantees that carrier substitution/merging preserves the declared readout under every continuation actually used while the token is active.

SA3 guarantees that if source/readout/continuation/capability changed, old authority could not silently survive; a new/revalidated token was required before further authority-bearing use.

SA4 guarantees that cached OPEN refusals cannot substitute for semantic or transformation proof authority.

Consequently all carrier-derived premises used by the Dual-Debt trace remain source-sound and scope-valid. The inherited DD5 reverse reconstruction/source replay therefore composes only licensed exact facts.

Hence the terminal conditional Skolem/source-soundness conclusion remains valid, and no authority leakage from unreachable or out-of-scope carrier semantics is admitted.

QED.

**Verdict:** `SA5_PROVED_AS_CONSERVATIVE_EXTENSION_OF_DD5`.

---

# 2. Corollaries

## C1 — Universal contextual equivalence is not required

A carrier may legitimately be exact for a smaller frozen continuation language (K). Soundness requires explicit scope and staleness, not indistinguishability under every conceivable future context.

This permits formula-specific/query-specific exact compression without pretending it is universally congruent.

## C2 — Source grammar membership is not semantic authority

A formal carrier state can satisfy every syntactic invariant of a representation and still lack source authority if it has no realization lineage and no unreachable-state irrelevance theorem.

## C3 — Query changes are semantic changes to authority

A SAT-existence carrier does not automatically authorize model counting, witness extraction, occupancy polynomial evaluation or another readout.

## C4 — Capability and semantic scope are orthogonal

A carrier can remain semantically adequate for a scope while the current capability profile becomes stale, or capability can remain unchanged while a new readout/continuation invalidates the semantic scope.

## C5 — Large residual-function count is not a lower bound

The theorem gives no authority to infer representation pressure from the cardinality of semantic residual functions alone. Allowed factorized computation under the active scope must also be ruled out before such a lower-bound interpretation.

---

# 3. Blind-discovery status

The historical observer-noninterference and APMA blind-freeze mechanisms are recommended as an experimental wrapper for discovering future scope tokens/carriers.

They are **not premises of SA1–SA5 soundness**. A mathematically valid scope token remains valid regardless of who proposed it; blindness controls the credibility/generality of discovery claims, not semantic truth.

---

# 4. Prior-art boundary

The theorem does not claim invention of:

- property/query-directed abstraction,
- reachability-aware abstraction,
- contextual equivalence,
- query-specific knowledge compilation,
- translation validation,
- certified projected knowledge compilation,
- blinded evaluation.

The scoped-authority contribution under evaluation is the integration of those concerns as a proof-state admission contract around the previously formalized Dual-Debt lifecycle.

External historical novelty remains unresolved.

---

# 5. What remains unproved

SA1–SA5 do not establish:

- that useful nontrivial scope tokens are efficiently discoverable;
- that source-preimage/reachability certificates remain polynomial;
- that a broad continuation language has compact exact carriers;
- that arbitrary carrier switching terminates;
- that scoped authority yields a polynomial SAT/BFS/QBF solver;
- that the combined architecture is historically novel.

The complexity firewall remains:

[
oxed{	ext{P_VS_NP=OPEN}}.
]

---

# 6. Authorized status

Under the formal specification at `e64fe909764f331e1f52b8f2ab306039e0c6e827` and the inherited Dual-Debt theorem:

[
oxed{
	exttt{PASS_ABSTRACT_SCOPED_CARRIER_AUTHORITY_SOUNDNESS_SA1_SA5}
}
]

with exact scope:

> An accepted carrier has semantic authority only inside its independently certified source-realizability, readout, continuation and capability scope. Scope changes make old authority stale rather than silently transferable. Exact scoped OPEN memory has refusal authority only. Adding this discipline conservatively preserves Dual-Debt terminal source soundness.

