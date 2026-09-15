# TRUMP bicameral overwidth cut-support intersection carrier — v1.1 theorem seal

Date: 2026-09-15

Authority: `SCOPED_THEOREM_SEAL__NO_GLOBAL_PROMOTION`

Frozen v1.1 preregistration:
`research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_V1_1_PREREGISTRATION_2026-09-15.json`

Frozen candidate implementation (unchanged from failed v1 run):
`research/tools/apma_cut_support_carrier/cut_support_carrier.py`

Independent v1.1 checker:
`research/tools/apma_cut_support_carrier/independent_checker_v1_1.py`

Actions authority:
- run: `34916790947`
- job: `104216055469`
- workflow head: `d25610c0beb5212315a9751162511a96e496f0f7`

Scoped verdict:

`PASS_SCOPED_BICAMERAL_OVERWIDTH_CUT_SUPPORT_INTERSECTION_CARRIER_V1_1`

The original v1 failure remains immutable as `FAIL_OR_OPEN_BICAMERAL_CUT_SUPPORT_CARRIER`; v1.1 does not rewrite it.

---

## 1. Frozen scope

Let the raw explicit Boolean relation instance have a globally minimum variable-only canonical cut

\[
B\subseteq V,
\qquad |B|=k,
\]

discovered by the already sealed polynomial min-cut mechanism. The parent route has already established

\[
2^k > L,
\]

so raw conditioning over all assignments to `B` is forbidden by the original-input polynomial envelope and the parent returns `OPEN_MINCUT_BRANCH_BUDGET` before enumerating any branch.

This theorem applies only when removing `B` leaves at least two constraint-bearing components and every such component contains exactly one explicit relation.

The downstream contract in this theorem is exactly:

- SAT/UNSAT for the frozen conjunction of these explicit relations; and
- reconstruction of one exact original witness when SAT.

No general message algebra, arbitrary multi-relation component projection, or unrestricted downstream query contract is claimed.

---

## 2. Structural lemma — global mincut + singleton components forces full cut visibility

### Lemma

Assume `B` is a globally minimum variable-only cut among all pairs of constraint nodes in the connected incidence graph. Assume further that deleting `B` leaves every constraint-bearing component with exactly one relation node.

Then every such singleton relation `R_i` is incident to every variable of `B`.

### Proof

Fix one singleton relation `R_i`. Let

\[
S_i = scope(R_i)\cap B.
\]

Because `R_i` is a singleton constraint-bearing component after deleting `B`, any variable in `scope(R_i)\setminus B` is private to `R_i`: if such a variable were incident to another relation, that edge would survive deletion of `B` and would connect `R_i` to another constraint, contradicting singleton-component status.

Therefore every incidence path from `R_i` to any other constraint must leave `R_i` through a variable in `S_i`. Deleting `S_i` consequently separates `R_i` from every other constraint node.

Thus `S_i` is itself a valid variable-only cut for some constraint-node pair. Since `B` is globally minimum,

\[
|B|\le |S_i|.
\]

But `S_i\subseteq B`, hence

\[
|S_i|\le |B|.
\]

Therefore `|S_i|=|B|` and so `S_i=B`. Hence `R_i` contains the full canonical cut. QED.

### Consequence

The v1 `PARTIAL_CUT_VISIBILITY` negative control was not a legitimate independent falsifier under the other frozen scope assumptions. Full-cut visibility is derived, not separately assumed.

---

## 3. Exact support-intersection carrier

For each singleton component relation write

\[
R_i(B,U_i),
\]

where `U_i` is the set of variables private to that relation. By the singleton-component condition the `U_i` are pairwise disjoint.

Define the exact projected support

\[
P_i = \{\sigma\in\{0,1\}^{B}: \exists u_i\;R_i(\sigma,u_i)\}.
\]

The candidate constructs `P_i` only by scanning the explicit rows already present in `R_i` and projecting each row to the coordinates of `B`. No assignment outside the explicit relation table is generated.

Define the effective exact carrier

\[
H = \bigcap_i P_i.
\]

### Theorem

Within the frozen scope,

\[
F\in SAT \iff H\ne\varnothing.
\]

### Proof — forward direction

Let `a` be a satisfying assignment of the original instance and let `sigma=a|_B`. For every relation `R_i`, the restriction `a|_{B\cup U_i}` is an allowed row, so `sigma in P_i`. Therefore

\[
\sigma\in\bigcap_i P_i = H.
\]

Hence `H` is nonempty.

### Proof — reverse direction

Let `sigma in H`. For every `i`, because `sigma in P_i`, there exists at least one explicit allowed tuple `t_i in R_i` whose projection to `B` is exactly `sigma`.

All selected tuples agree on every cut variable because they project to the same `sigma`. Their private variable sets `U_i` are pairwise disjoint, so the tuples can be concatenated without conflict into one assignment of the original variables.

That assignment satisfies every original relation. Hence `F in SAT`.

Therefore `F in SAT iff H != empty`. QED.

---

## 4. Exact reconstruction and UNSAT certificate shape

For each projected support key the implementation stores one original explicit tuple that realizes the key.

If `H` is nonempty, choose any `sigma in H` and one stored row from each component relation. The rows agree on `B` and have disjoint private variables, so they reconstruct one original witness. The candidate then rechecks that witness against every original explicit relation.

If `H` is empty, the exact projected-support receipts certify that no cut assignment has a realizing tuple in every component simultaneously. Under the theorem above, this is an exact scoped UNSAT result:

`EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION`.

This is not claimed to be a new universal proof system or a compact UNSAT language for arbitrary CNF.

---

## 5. Polynomial lifecycle bound

Let `r_i` be the number of explicit tuples in relation `R_i`, and let the canonical explicit input length be `L`.

Projection scans only explicit tuple cells, so construction cost is polynomial in `L` and

\[
|P_i|\le r_i.
\]

Set intersection never expands the representation, hence

\[
|H|\le \min_i |P_i|\le \min_i r_i\le L.
\]

The lifecycle therefore consists of:

1. the already sealed polynomial canonical-mincut discovery;
2. one scan of the explicit relation rows;
3. polynomial set intersection over at most the explicit row surface;
4. one stored-row lookup per component for one accepting cut state;
5. direct verification against the original explicit relations.

No `2^k` raw assignment cube is enumerated, no component Cartesian product is materialized, no generic transfer is called, and no SAT solver is invoked by this gate.

Thus for the frozen scope

\[
T_{construct}+T_{discover}+T_{solve}+T_{reconstruct}+T_{verify}\le poly(L).
\]

---

## 6. Frozen controls and independent replay

The independently checked positive control is the prior overwidth min-cut control:

- canonical cut size `k=20`;
- raw branch budget `2^20=1,048,576`;
- parent branch enumerations `0`;
- projected support-size multiset `{3,4}`;
- effective support size `1`;
- exact original witness reconstructed and verified;
- terminal `ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER`.

Negative controls:

- disjoint projected supports -> `EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION`;
- a cut component with multiple relations -> `OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER`;
- injected trusted hint fields -> `REJECT_RAW_INPUT`;
- tampered carrier proposal/provenance -> `REJECT_TAMPERED_PROVENANCE`.

The old v1 checker is required to continue failing. Parent min-cut v1.1, pair-separator, raw-compositional-basis, and the old exact-interface-quotient checker all remain green.

---

## 7. Claim ceiling

This theorem closes only the following scoped subproblem:

`OVERWIDTH_CANONICAL_MINCUT + SINGLE_EXPLICIT_RELATION_PER_CUT_COMPONENT -> EXACT_POLYNOMIAL_SUPPORT_INTERSECTION_CARRIER`.

It does **not** prove:

- a polynomial carrier for a cut component containing two or more interacting relations;
- polynomial join/project elimination for arbitrary explicit relation networks;
- universal affine-syndrome applicability;
- arbitrary unseen invariant discovery;
- `GENERAL_SAT_IN_P`;
- `P = NP` or `P != NP`.

Permanent status:

`P_VS_NP = OPEN`

`GENERAL_SAT_IN_P = NOT_PROVED`

`CONNECTED_MIXED_CORE_SOLVED = NO`

---

## 8. Refined next blocker

The nearest unresolved object is now an overwidth canonical cut with at least one cut-separated component containing multiple relations. The problem is no longer discovery of the cut and no longer the singleton explicit-support carrier. The missing object is an exact polynomial-size boundary relation/message for a multi-relation component without performing an exponential join/project elimination.

The next admissible mechanism families are:

1. reuse the already sealed affine-syndrome quotient only when exact factor-through adequacy is proved from the component semantics;
2. derive a bounded/factorized join-project carrier with an original-`L` polynomial output bound;
3. derive another preregistered exact component boundary quotient with independent replay;
4. otherwise return `OPEN`.
