# R50G25AZ — ARBITRARY-g CHAIN COMPOSITION THEOREM OR EXPLICIT COUNTEREXAMPLE

Status: **FROZEN BEFORE AZ IMPLEMENTATION/TESTING**

## Parent boundary

- sealed AY source head: `d38e9dc429e215ade6f70b77b8691fbbd7e05be1`
- final AY2 meta mirror: `c408bb82af97903641514865af13c6077da2ef9e`
- AY scientific receipt: `05bb3d4cbe57a8c7ce49b5baf908bd7cc2c5ed78`
- AY journal V42: `20e58209dfdaffd1cb9984a7f30ebb0ea0adcbe5`
- frozen AY family: `CHAIN_CONNECTED_SHIFTED_SEALED_Y_RESIDUAL_COPIES`
- sealed Y target hash: `c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb`
- AY finite ladder was `g=(1,2,3,4,6,8)` and is evidence only.

## Frozen question

For every integer `g >= 1` in the exact AY chain family, can the AX/AY proof-carrying bucket relation be certified by a finite compositional template proof with constant induced width and polynomial (in fact linear) materialized relation size, or is there an explicit failure of one of the frozen composition obligations?

This gate does **not** ask for more empirical points as its proof. The theorem candidate must be discharged by finite template obligations plus induction over arbitrary `g`.

## Exact domain

Let `U` be the exact sealed Y source unit loaded by the inherited `load_sealed_y_target()` contract.

Frozen unit facts to verify fail-closed from source before theorem construction:

- Y target hash equals the frozen hash above;
- target variable set exactly
  `[2,3,4,5,8,9,10,11,12,13,15,16,20,24,25,26,27,28,29,30]`;
- maximum variable id `m=30`;
- canonical unit CNF has `(C,L,V)=(63,155,20)`;
- hardened affine extraction has exactly 61 non-affine defect clauses and exactly 1 recognized affine equation represented by 2 affine CNF clauses;
- explicit tautology handling is active, tautology count 0, partition PASS, replay failures 0.

For arbitrary integer `g>=1`, define `F_g` exactly as AY did:

1. copies `U_j = shift(U, 30*j)` for `j=0..g-1`;
2. adjacent bridge clause
   `(30+30*j, 32+30*j)`
   between copies `j` and `j+1`, for `j=0..g-2`;
3. canonical union of all copies and bridges;
4. inherited cheap-policy replay must be a residual identity on the family (same canonical root/residual); any drift is a theorem obstruction, not a rescue opportunity;
5. hardened extraction/factorization contract must remain exact.

No other bridge, offset, family, preprocessing, or order may be introduced after outcomes.

## Frozen explicit elimination order

Do not use an adaptive selector in the theorem.

Freeze the local order discovered before AZ by AY evidence:

`O = [24,10,2,11,15,20,3,4,5,8,9,12,13,16,25,26,27,28,29,30]`.

For arbitrary `g`, define the theorem order constructively:

`O_g = concat(O + 30*j for j=0..g-1)`.

The theorem must prove this explicit order has induced width at most 13 for the exact domain. It is not necessary to prove that deterministic min-fill must discover the order for arbitrary `g`; AZ replaces the empirical selector with an explicit constructive schedule.

## Frozen finite composition templates

The arbitrary-g proof may use exactly two local templates.

### LAST template

One exact source unit `U`, no outgoing bridge, eliminate all 20 local variables in order `O`.

Required certificate facts:

- induced width <= 13;
- source materialized factor rows = 301;
- generated relation rows = 4272;
- terminal boundary scope is empty and terminal table is TRUE;
- SAT reconstruction exists and validates all 61 defects plus the affine equation on the source unit;
- no relation replay failure.

### MID template

One exact source unit `U` plus one positive binary bridge `(30,q)` to one abstract next-block endpoint `q` not eliminated by the local template. Eliminate only the 20 local variables in order `O`.

Required certificate facts:

- induced width <= 13 while `q` is retained;
- bridge factor contributes exactly 3 source rows;
- generated relation rows = 4273;
- the sole surviving boundary factor has scope `[q]` and the complete two-row table `{q=0,q=1}` (semantic NEUTRALITY);
- for each boundary value q=0 and q=1, claim-scoped reconstruction supplies a local assignment satisfying the exact unit factors and bridge;
- no relation replay failure.

The MID boundary neutrality is the only permitted induction interface. If it fails, AZ is a counterexample to this theorem candidate. No post-outcome interface widening is allowed.

## Frozen theorem candidate

If both finite templates pass and the shift/composition obligations are independently verified, prove by induction for every integer `g>=1`:

1. exact family measures:
   - `C(g)=64*g-1`
   - `L(g)=157*g-2`
   - `V(g)=20*g`
   - `D(g)=62*g-1`
   - `E(g)=g`;
2. the explicit order `O_g` has induced width `w(g) <= 13`;
3. full width-state bound `2^w <= 8192`;
4. exact source-factor rows `S_rows(g)=304*g-3`;
5. exact generated relation rows `G_rows(g)=4273*g-1`;
6. exact total materialized relation rows
   `R_rows(g)=4577*g-4`;
7. exact generated factor count `20*g` and source factor count `63*g-1`;
8. exact relation evaluation-attempt ledger under the frozen implementation model
   `A(g)=49242*g-2`;
9. maximum generated scope <=13, maximum generated table rows <=1460, maximum gathered input factors <=9;
10. decision/reconstruction/source-validation compose from the LAST template backward through `g-1` MID templates;
11. `R_rows(g) <= L(g)^4` for every `g>=1`;
12. relation construction, verification and claim-scoped reconstruction are `O(g)` under the fixed template contract, hence polynomial in `|F_g|` on this exact restricted domain.

The theorem is restricted to the exact family `F_g`. It is not arbitrary-CNF coverage.

## Proof-carrying relation / Fifth Element

Instantiate an arbitrary-g edge theorem object with at least:

- DOMAIN_SPECIFICATION
- FORWARD_PRESERVATION
- CLAIM_SCOPED_RECONSTRUCTION
- SOURCE_VALIDATION
- GLOBAL_EXACTNESS_ON_DEFINED_FAMILY
- ASYMPTOTIC_SIZE_BOUND_ON_DEFINED_FAMILY
- ASYMPTOTIC_TIME_BOUND_ON_DEFINED_FAMILY
- COMPOSITION_CERTIFICATE
- PROVENANCE
- COUNTEREXAMPLE_EXIT

The relation theorem must include the exact MID and LAST template identities and hashes. A formula for row growth without the reconstruction/composition certificates is not a PASS.

## Frozen independent verifier

A separate verifier must independently:

1. rebuild the sealed unit from source and verify its hash/CLV/extraction;
2. rebuild LAST and MID factors without trusting the theorem result JSON;
3. recompute the explicit local order width;
4. recompute exact factor tables and local bucket elimination;
5. verify LAST terminal TRUE and reconstruction;
6. verify MID unary boundary table is exactly full `{0,1}` and reconstruct/validate for both boundary bits;
7. symbolically recompute every closed-form coefficient above from template contributions rather than fitting AY ladder data;
8. prove/check algebraically for integer `g>=1` that `4577*g-4 <= (157*g-2)^4`;
9. verify the induction interface: eliminating one shifted MID block leaves a neutral factor on the next unit endpoint and otherwise an unchanged shifted tail instance.

Any disagreement fails closed.

## Frozen adversarial holdouts

After the symbolic theorem certificate is created, run exact full-family replays at previously non-AY ladder values:

`g = (5,7,9,16)`.

Holdouts are **falsification diagnostics only**. Passing them is not the theorem proof. Any mismatch with the theorem formulas or reconstruction invalidates the AZ candidate and must be recorded as a counterexample.

No holdout value may be changed after results.

## Frozen verdicts

Priority order:

1. `AZ_EXPLICIT_COMPOSITION_COUNTEREXAMPLE_FOUND`
   - any frozen unit/template/induction/holdout exactness obligation fails;
2. `AZ_RELATION_THEOREM_CERTIFICATE_FAILURE`
   - certificate or independent verifier fails without a valid mathematical counterexample classification;
3. `AZ_RESTRICTED_CHAIN_FAMILY_POLYNOMIAL_RELATION_THEOREM_PROVED`
   - all finite template obligations, symbolic induction, algebraic bounds, independent verification, holdouts, Fifth Element obligations, and Proof State Machine promotion guard pass;
4. `UNKNOWN_RESOURCE_LIMIT`.

## Proof State Machine promotion request if theorem succeeds

No theorem claim is sealed before governance validation.

On successful certificate generation, request only the following scoped promotions:

- `UNIVERSAL_COVERAGE_PROVED` with scope `EXACT_F_G_CHAIN_FAMILY_G_GE_1_ONLY`;
- `GLOBAL_EXACTNESS_PROVED` with the same restricted scope;
- `ASYMPTOTIC_POLYNOMIAL_BOUND_PROVED` with the same restricted scope;
- `POLYNOMIAL_DOOR_PROVED` with the same restricted scope;
- `PROVED` for the named restricted-family theorem only.

The required certificate bundle must include domain, universal coverage over the defined parameterized family, global exactness/reconstruction, asymptotic complexity, formal induction proof object, independent verification, and provenance.

Do not request `SAT_IN_P_PROVED` or `P_EQ_NP_PROVED` from AZ.

## Firewalls

- `P_VS_NP = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `TRUMP_finished = false`
- restricted-family theorem `!=` arbitrary-CNF theorem
- AY finite ladder `!=` AZ induction proof
- holdout PASS `!=` theorem proof
- no SAT truth oracle for candidate construction, selection, or verdict
- no post-outcome retuning of order, bridge, interface, coefficients, domain, or exponent

Do not start a successor gate from AZ in this gate.