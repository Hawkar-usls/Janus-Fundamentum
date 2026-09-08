# R50G25AY — SEPARATOR WIDTH SCALING OR RELATION LEDGER BLOWUP COUNTEREXAMPLE

Status: **FROZEN BEFORE IMPLEMENTATION/TESTING**

## Parent boundary

- sealed/governed AX source head: `79d976215037655740bf999db3908d6e80025046`
- final AX2 meta mirror: `69ffdf46d4d8ec3cc704831900526dbaa37be78b`
- AR/AS historical backfill reconciliation: `a12a77d591a83f3ee8fe53cde261409f79f3fae4`
- inherited AX relation result is local only: `w=13`, `2^w=8192`, actual materialized rows `5675`, proof-carrying relation rows with AX affine-parity charge `11350`, reconstruction/source-validation PASS on the exact frozen AW shifted-Y component.

## Frozen question

Does the AX-style within-component structural door survive a preregistered scaling ladder when the shifted sealed-Y core is replicated and made into one connected defect component, or does separator width / the actual proof-carrying relation ledger produce an explicit `L^4` obstruction?

A finite ladder PASS is **not** an asymptotic theorem. The gate may only report finite frozen-ladder evidence or an explicit counterexample.

## Frozen source unit

Use the already sealed Y target loaded by the inherited `load_sealed_y_target()` contract.

- expected Y target hash: `c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb`
- source generation/selection/verdict uses no SAT truth oracle.

## Frozen scaling family

Family id:

`CHAIN_CONNECTED_SHIFTED_SEALED_Y_RESIDUAL_COPIES`

Frozen ladder, in this exact order:

`g = (1, 2, 3, 4, 6, 8)`

For each `g`:

1. load the exact sealed Y source unit;
2. let `m` be its maximum variable id;
3. create `g` disjoint shifted copies using offsets `j*m`, `j=0..g-1`;
4. for every adjacent pair `j,j+1`, add exactly one all-positive binary bridge clause
   `(max(vars(copy_j)), min(vars(copy_{j+1})))`;
5. canonicalize;
6. run the inherited frozen cheap policy exactly once on the combined root;
7. if policy exits TERMINAL/AFFINE, classify that rung as `NON_FALSIFYING_CHEAP_POLICY_ABSORPTION` and do not count it as scaling coverage;
8. if policy returns RESIDUAL, use hardened AT extraction and require explicit tautology handling, partition PASS, and zero replay failures;
9. require a unique defect-containing factor component containing all bridge endpoints; this is the AY target component.

No family, rung, bridge rule, variable-offset rule, or policy may be changed after outcomes are observed.

## Frozen proof-carrying relation

For each relevant residual component instantiate an explicit relation object.

Source factors:

- each non-affine defect clause becomes an exact Boolean factor over its variables;
- each extracted affine equation becomes an exact Boolean parity factor over its equation scope.

Build the primal graph from **all source factor scopes** and use deterministic min-fill:

`score(v) = (missing_fill_edges, current_degree, variable_id)`

with ascending lexicographic choice.

Use exact bucket elimination in that frozen order. Every generated factor stores the chosen eliminated-variable value needed for claim-scoped reconstruction.

The relation must provide:

- DOMAIN
- FORWARD_PRESERVATION
- CLAIM_SCOPED_RECONSTRUCTION
- SOURCE_VALIDATION
- EXACTNESS
- SIZE_BOUND
- TIME_BOUND for the materialized finite relation ledger
- COMPOSITION_SCOPE
- PROVENANCE
- COUNTEREXAMPLE_TRACE

A small width number without actual reconstruction/source validation is not a PASS.

## Frozen ledgers

For every relevant rung record at minimum:

`g, V, D, E, L, w, 2^w, total_materialized_rows, maximum_generated_scope, maximum_generated_table_rows, decision, reconstruction_pass, source_validation_pass`.

Inherited polynomial budget:

`B(L) = L^4`.

Two separately recorded finite doors:

1. **width-state envelope** survives iff `2^w <= L^4`;
2. **direct sparse relation ledger** survives iff `total_materialized_rows <= L^4`.

The second door may survive even when the full `2^w` envelope fails.

No exponent retuning is allowed.

## Frozen classifications

Per relevant rung:

- `WIDTH_AND_RELATION_LEDGER_WITHIN_L4`
- `SPARSE_RELATION_LEDGER_ONLY_WITHIN_L4`
- `RELATION_LEDGER_EXCEEDS_L4`
- `RELATION_CONTRACT_FAILURE`
- `NON_FALSIFYING_CHEAP_POLICY_ABSORPTION`
- `UNKNOWN_RESOURCE_LIMIT`

## Frozen gate verdicts

Priority order:

1. `AY_RELATION_LEDGER_BLOWUP_COUNTEREXAMPLE_FOUND`
   - at least one relevant rung has exact proof-carrying `total_materialized_rows > L^4`;
2. `AY_RELATION_CONTRACT_COUNTEREXAMPLE_FOUND`
   - reconstruction/source validation/exact relation replay fails on a relevant rung;
3. `AY_SPARSE_RELATION_LEDGER_SURVIVES_WIDTH_ENVELOPE_FAILURE_ON_FROZEN_LADDER__ASYMPTOTIC_OPEN`
   - at least one relevant rung has `2^w > L^4`, all relevant rungs still have actual relation rows `<= L^4`, and all relation contracts pass;
4. `AY_WIDTH_AND_RELATION_LEDGER_WITHIN_L4_ON_FROZEN_LADDER__ASYMPTOTIC_OPEN`
   - all relevant rungs satisfy both ledgers and all relation contracts;
5. `AY_INSUFFICIENT_RELEVANT_SCALING_COVERAGE`
   - fewer than four relevant rungs or either endpoint `g=1` / `g=8` is not relevant;
6. `UNKNOWN_RESOURCE_LIMIT`.

## Independent verification

Each rung must be replayed fail-closed from a serialized source payload by a verifier that recomputes:

- source factor semantics;
- deterministic min-fill order;
- exact bucket decision;
- materialized row count;
- reconstruction;
- direct source validation.

Aggregate verdict must fail closed if any rung identity or independent replay disagrees.

## Proof State Machine

Before sealing, `TRUMP_PROOF_STATE_MACHINE_V1_0` must validate the promotion manifest.

Even a full frozen-ladder PASS may promote only finite/local scaling evidence. It may not promote to:

- universal separator bound;
- asymptotic polynomial runtime;
- arbitrary-CNF coverage;
- SAT in P;
- P=NP.

## Firewalls

- `P_VS_NP = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `TRUMP_finished = false`
- finite ladder `!=` asymptotic proof
- empirical scaling `!=` polynomial bound theorem
- no SAT truth oracle for generation, selection, or verdict
- no post-outcome family/rung/budget/operator changes

Do not start R50G25AZ from this gate.
