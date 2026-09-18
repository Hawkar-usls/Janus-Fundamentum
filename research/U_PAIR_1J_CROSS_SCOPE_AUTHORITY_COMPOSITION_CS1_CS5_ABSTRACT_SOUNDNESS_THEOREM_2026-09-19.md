# U-PAIR-1J Cross-Scope Authority Composition — CS1–CS5 Abstract Soundness Theorem

**Date:** 2026-09-19  
**Authority:** `ABSTRACT_CROSS_SCOPE_AUTHORITY_COMPOSITION_SOUNDNESS__NO_COMPLETENESS_OR_POLYTIME_CLAIM`  
**Formal specification:** `1cad23f8e41d8b036804aed1cc31e19478505cf2`  
**Inherited Scoped Authority theorem:** `e11abbc6e0b8313d4bb48f65281d3d3532880518`  
**Inherited Dual-Debt theorem:** `ed203e9ebbc5699753c88f5dc8362892c720da14`

## 1. Setup

Fix a frozen source relation (F_0) with concrete semantic state space (Sigma_F).

Let

[
A_1=(F_0,Reach_1,Readout_1,Continuation_1,Capability_1,Proof_1,Expiry_1)
]

be an ACTIVE scoped-authority token over carrier (C_1), and let

[
A_2=(F_0,Reach_2,Readout_2,Continuation_2,Capability_2,Proof_2,Expiry_2)
]

be the target token over carrier (C_2).

Let

[
B_{12}=(A_1,A_2,	au_{12},ReachTransport,ScopeTransport,ProofTransport,
CapabilityTransition,DebtTransfer,CostProvenanceReceipt,ExpiryBinding)
]

be an admitted bridge satisfying B1–B7 of the formal specification.

Write

[
U_2 preceq_{B_{12}} U_1
]

when every target readout/continuation observation authorized after the switch is explicitly mapped into an observation already covered by (A_1), with the source-side and carrier-side observation equalities independently checked.

The switch itself has zero semantic- or transformation-debt discharge authority.

---

# CS1 — Local Authority Transport Soundness

### Statement

Suppose an authority-bearing fact (p_1) over (C_1) is valid under ACTIVE token (A_1), and (B_{12}) is admitted.

If (p_1) is either:

1. translated by the bridge into a target proof object (p_2) whose replay succeeds under (A_2), or
2. independently revalidated under (A_2),

then (p_2) has source-semantic authority for the declared target scope (U_2).

### Proof

Because (A_1) is ACTIVE, SA1–SA2 imply that (p_1) is anchored either to a replayable source-realizable lineage or to an accepted unreachable-state observational-irrelevance theorem, and that its observations agree with (F_0) throughout (U_1).

By B2, every authority-bearing state transported through (	au_{12}) either preserves the same source realization in (C_2) or is covered by the exact target irrelevance theorem required by (A_2).

By B3,

[
U_2 preceq_{B_{12}} U_1,
]

so every target observation is mapped into an observation already covered by the source token, and the bridge proves equality of source and target carrier readouts under the adapter.

By B4, proof authority is not inferred from representation identity: the target proof is either replayably translated or independently revalidated.

By B5, any operation used to consume (p_2) is separately licensed by (Capability_2).

Thus the authority carried by (p_2) is simultaneously source-realizable, scope-valid, proof-valid and capability-valid for the declared target use.

QED.

**Verdict:** `CS1_PROVED_FOR_ADMITTED_BRIDGE_AND_TARGET_SCOPE`.

---

# CS2 — No Scope Widening by Representation Equivalence

### Statement

An exact meaning-preserving representation switch (C_1	o C_2) does not by itself authorize any target use outside

[
U_2 preceq_{B_{12}} U_1.
]

If the requested target Readout or Continuation is not covered by the accepted ScopeTransport proof, the inherited authority is STALE/NO_AUTHORITY until a new token or revalidation theorem is accepted.

### Proof

SA3 already establishes that changing Readout or Continuation changes the hypotheses under which scoped authority was proved.

A representation equivalence establishes equality of represented meaning under its own translation contract. It does not quantify over every new future observation that might later be requested.

B3 therefore requires an explicit scope transport: identity/subscope or a checked continuation/readout adapter. Without that proof, the requested target observation is outside the quantified hypotheses inherited from (A_1).

Applying (A_1) to such a target use would be theorem application outside its domain. By the fail-closed rule, the correct status is STALE/NO_AUTHORITY rather than false.

QED.

**Verdict:** `CS2_PROVED__SEMANTIC_SWITCH_NE_SCOPE_EXPANSION`.

---

# CS3 — Switch Non-Discharge and Lifecycle Nonforgetfulness

### Statement

For a pure admitted authority bridge (B_{12}) containing no separately certified semantic discharge, transformation execution or exact supersession:

[
P_{m sem}(S')=P_{m sem}(S),
]

[
P_{m trans}(S')=P_{m trans}(S),
]

and all unresolved semantic debt, transformation debt, charged work, liabilities and provenance remain present after the switch.

### Proof

DD3 already proves zero debt-discharge authority for a pure representation switch.

B6 strengthens the lifecycle binding by requiring that bridge transport preserve both debt ledgers and append, rather than replace, historical cost/provenance receipts.

B4 cannot discharge debt because proof translation only changes the proof language/representation of an already-authorized fact; a semantic obligation changes status only through an inherited semantic DISCHARGE, and a transformation obligation changes status only through EXECUTED_CERTIFIED or SUPERSEDED_CERTIFIED.

Hence the pure bridge changes representation and authority location but no obligation status.

The monotone-history rule gives nondecreasing charged work, and DD4 prevents any later roundtrip from erasing the bridge history.

QED.

**Verdict:** `CS3_PROVED_BY_DD3_DD4_AND_BRIDGE_B6`.

---

# CS4 — Bridge Composition

### Statement

Let

[
B_{12}:A_1	o A_2
]

and

[
B_{23}:A_2	o A_3
]

be admitted bridges with exact intermediate token identity, compatible source binding, and scope relations

[
U_3preceq_{B_{23}}U_2
]

and

[
U_2preceq_{B_{12}}U_1.
]

Then the composed bridge

[
B_{13}=B_{23}circ B_{12}
]

is sound for the composed target scope (U_3), provided its composed reach/proof/cost receipts replay successfully.

### Proof

Take any authority-bearing source state/fact used by the composed route.

### Reachability

By B2 for (B_{12}), realized source state (s) mapped to (c_1) transports to a valid (c_2) realization or to an accepted target irrelevance theorem.

Applying B2 for (B_{23}) transports that authorized (c_2) use to (c_3) under the same frozen source identity, again with either a replayable source lineage or an accepted irrelevance theorem.

Thus source authority cannot appear at (C_3) without surviving both reachability gates.

### Scope

Every (U_3) observation is mapped by (B_{23}) into an authorized (U_2) observation. Every such (U_2) observation is mapped by (B_{12}) into an authorized (U_1) observation.

Therefore composition of the accepted adapters gives

[
U_3preceq_{B_{13}}U_1.
]

No intermediate bridge can enlarge the scope because CS2 applies at each hop.

### Proof authority

By B4 at the first hop, every imported proof fact is translated/revalidated under (A_2). The second hop begins from exactly that (A_2) token identity and again translates/revalidates under (A_3).

Hence proof authority is compositional only through replayable intermediate authority; opaque references are not transitively trusted.

### Debt and cost

CS3 applies to each pure switch. Therefore composing the switches preserves unresolved debt unless explicit named discharges occur. Charged work/provenance accumulates monotonically across both bridges.

Thus the composed route preserves source binding, scope adequacy, proof authority and lifecycle accounting.

QED.

**Verdict:** `CS4_PROVED_FOR_ENDPOINT_MATCHED_COMPATIBLE_BRIDGES`.

### Corollary — Finite chain

By induction, any finite chain

[
A_1	o A_2	ocdots	o A_m
]

of admitted endpoint-matched bridges transports authority soundly to the final declared scope, provided every intermediate bridge replay succeeds.

This is composition of scoped authority, not a claim of cheap translation.

---

# CS5 — Multi-Language Terminal Soundness

### Statement

Consider an accepted Dual-Debt/Scoped-Authority terminal trace that may use finitely many carrier languages

[
C_1,C_2,ldots,C_m
]

and cross-scope switches between them.

Assume:

1. DD5 terminal hypotheses hold;
2. SA5 hypotheses hold;
3. every authority-bearing switch is an admitted bridge satisfying CS1–CS4;
4. every authority-bearing fact is consumed only while its current token/bridge scope is ACTIVE;
5. all original source replay/reconstruction requirements hold.

Then

[
oxed{
D_0(B)Rightarrow F_0(f_X(B),B)
}
]

and no terminal authority can arise solely from a source-unrealizable target state, an out-of-scope continuation, an unsupported target capability, an untranslated proof object, or a stale bridge.

### Proof

By the finite-chain corollary of CS4, every carrier-derived semantic fact at every hop is transported only through source-realizable/irrelevance-justified states, non-widening scope maps and replayable proof authority.

CS2 prevents an out-of-scope Readout or Continuation from inheriting authority merely because a representation switch is semantically exact.

CS3 guarantees that switching languages cannot erase either debt class or historical liabilities.

Therefore the hypotheses required by SA5 remain true despite the multi-language trace: every carrier fact used by DD5 has ACTIVE scoped authority at the moment of use.

SA5 then reduces the carrier-rich trace to the original source-sound semantic terminal theorem, and DD5/T5 provide the composed reconstruction guarantee

[
D_0(B)Rightarrow F_0(f_X(B),B).
]

The listed authority-leak cases are excluded respectively by B2/SA1, B3/CS2, B5, B4 and B7/SA3.

QED.

**Verdict:** `CS5_PROVED_AS_MULTI_LANGUAGE_CONSERVATIVE_EXTENSION_OF_SA5_DD5`.

---

# 2. Consequences

## C1 — Data translation is weaker than authority translation

A representation can be translated exactly while previously proved facts remain unusable in the target system until ProofTransport or target revalidation succeeds.

## C2 — Scope narrowing is cheap logically, scope widening is not free

A target may safely consume a proven subset/adapter image of an old scope. A broader continuation/readout requires new proof authority.

## C3 — Capability is not inherited from semantic adequacy

A target carrier may represent the same relation exactly and still lack a certified operation needed by the next proof step.

## C4 — Multi-language synthesis is sound without a universal carrier

The solver may use different exact carriers for different stages, provided every switch carries an admitted bridge and every use stays within active scope.

## C5 — Bridge chains cannot launder complexity

Translation, proof conversion, materialization, revalidation and replay costs remain charged across the chain. A short final proof does not retroactively make the bridge sequence cheap.

---

# 3. Prior-art boundary

This theorem does **not** claim invention of:

- proof-system p-simulation;
- translation validation/certification;
- certified compilation;
- proof compilers between source and target logics;
- contextual equivalence/full abstraction;
- proof-carrying code;
- certified projected knowledge compilation.

The candidate under evaluation is the lifecycle composition:

[
	ext{Dual Debt}
+
	ext{Scoped Source/Continuation Authority}
+
	ext{Proof Transport}
+
	ext{Capability Binding}
+
	ext{Nonforgetful Bridge Composition}.
]

Historical novelty remains unresolved.

---

# 4. What remains unproved

CS1–CS5 do not prove:

- that a useful bridge always exists;
- that bridge proof translation is polynomial;
- that source-realizability transport is cheap;
- that scope adapters are efficiently discoverable;
- that a finite set of carriers suffices for arbitrary SAT/BFS/QBF;
- that arbitrary carrier switching terminates;
- that this system p-simulates SynQBF or another proof system;
- that SynQBF p-simulates this lifecycle architecture under the current hypotheses;
- that the combined architecture is historically novel;
- SAT in P or P=NP.

[
oxed{	ext{P_VS_NP=OPEN}}.
]

---

# 5. Authorized status

Under formal specification `1cad23f8e41d8b036804aed1cc31e19478505cf2`, inherited SA1–SA5, and inherited DD1–DD5:

[
oxed{
	exttt{PASS_ABSTRACT_CROSS_SCOPE_AUTHORITY_COMPOSITION_CS1_CS5}
}
]

with exact scope:

> Proof authority may move across exact carrier/language switches only through an independently checked bridge that preserves source realizability, transports a non-widening readout/continuation scope, translates or revalidates proof objects, binds destination capabilities, and carries all debt/cost/provenance forward. Such bridges compose across a finite multi-language trace and conservatively preserve the inherited source-sound terminal theorem.
