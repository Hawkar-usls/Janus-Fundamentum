# C009 — Maximum inherited theta-pressure cycle

C009 attacks the C008 theta branch and older SoS/affine branches before admitting descendants. It adds nine descendants `H075-H083`, registers 41 attacks `A176-A216`, rejects `H074`, and expands the inversion matrix to 30×30 while keeping 21 of 30 selected hypotheses inherited.

## Terminal result

`H074` is **REJECTED** because its observable theta profile was not finite or canonical and its open-ended statistic set could contain the SAT answer itself. The intended route is salvaged by `H078`, `H081`, and `H082`.

## New proof graph

- `H075`: Boolean-cube coordinate isomorphism invariance.
- `H076`: explicit local projection-collapse counterroute.
- `H077`: bounded-depth extension stability.
- `H078`: canonical bounded-level SAT/UNSAT theta twins.
- `H079`: local conflict-graph theta barrier.
- `H080`: nonlocality-or-depth necessity.
- `H081`: conditioned rational theta certificates.
- `H082`: fixed-level theta/SoS bit-equivalence.
- `H083`: restriction-robust mixed affine-core lower bound.

## Main fork

The auxiliary-variable question is split into three competing, falsifiable routes:

1. prove `H077` and recover a bounded-depth form of `H071`;
2. construct `H076` and show local projection can collapse theta rank;
3. construct `H078` and bypass projection monotonicity through canonical bounded-level twins.

## Attack ledger

### A176
- **Target:** `H075`
- **Type:** coordinate-ring audit
- **Result:** `SURVIVED`

### A177
- **Target:** `H075`
- **Type:** degree audit
- **Result:** `SURVIVED`

### A178
- **Target:** `H075`
- **Type:** bit-complexity audit
- **Result:** `SURVIVED`

### A179
- **Target:** `H076`
- **Type:** known-closure attack
- **Result:** `INCONCLUSIVE`

### A180
- **Target:** `H076`
- **Type:** small-model attack
- **Result:** `INCONCLUSIVE`

### A181
- **Target:** `H076`
- **Type:** hidden-oracle audit
- **Result:** `WEAKENED`

### A182
- **Target:** `H077`
- **Type:** depth-one substitution attack
- **Result:** `SURVIVED`

### A183
- **Target:** `H077`
- **Type:** sharing attack
- **Result:** `WEAKENED`

### A184
- **Target:** `H077`
- **Type:** projection attack
- **Result:** `SURVIVED`

### A185
- **Target:** `H078`
- **Type:** definition audit
- **Result:** `SURVIVED`

### A186
- **Target:** `H078`
- **Type:** separation attack
- **Result:** `INCONCLUSIVE`

### A187
- **Target:** `H078`
- **Type:** explicitness attack
- **Result:** `WEAKENED`

### A188
- **Target:** `H079`
- **Type:** known-counterexample attack
- **Result:** `WEAKENED`

### A189
- **Target:** `H079`
- **Type:** gadget escape attack
- **Result:** `INCONCLUSIVE`

### A190
- **Target:** `H079`
- **Type:** hidden-globality audit
- **Result:** `SURVIVED`

### A191
- **Target:** `H080`
- **Type:** containment attack
- **Result:** `WEAKENED`

### A192
- **Target:** `H080`
- **Type:** time-depth audit
- **Result:** `SURVIVED`

### A193
- **Target:** `H080`
- **Type:** disjunction completeness attack
- **Result:** `WEAKENED`

### A194
- **Target:** `H081`
- **Type:** weak-infeasibility attack
- **Result:** `SURVIVED`

### A195
- **Target:** `H081`
- **Type:** bit-complexity attack
- **Result:** `WEAKENED`

### A196
- **Target:** `H081`
- **Type:** rounding attack
- **Result:** `INCONCLUSIVE`

### A197
- **Target:** `H082`
- **Type:** duality attack
- **Result:** `SURVIVED`

### A198
- **Target:** `H082`
- **Type:** growing-level attack
- **Result:** `SURVIVED`

### A199
- **Target:** `H082`
- **Type:** coefficient attack
- **Result:** `WEAKENED`

### A200
- **Target:** `H083`
- **Type:** restriction attack
- **Result:** `WEAKENED`

### A201
- **Target:** `H083`
- **Type:** Gaussian-elimination attack
- **Result:** `INCONCLUSIVE`

### A202
- **Target:** `H083`
- **Type:** explicitness attack
- **Result:** `WEAKENED`

### A203
- **Target:** `H074`
- **Type:** formulation audit
- **Result:** `DESTROYED`

### A204
- **Target:** `H074`
- **Type:** adversarial-statistic audit
- **Result:** `DESTROYED`

### A205
- **Target:** `H070`
- **Type:** equivalence audit
- **Result:** `WEAKENED`

### A206
- **Target:** `H070`
- **Type:** local-barrier attack
- **Result:** `INCONCLUSIVE`

### A207
- **Target:** `H071`
- **Type:** projection-collapse attack
- **Result:** `INCONCLUSIVE`

### A208
- **Target:** `H071`
- **Type:** bounded-depth salvage attack
- **Result:** `WEAKENED`

### A209
- **Target:** `H072`
- **Type:** isomorphism audit
- **Result:** `SURVIVED`

### A210
- **Target:** `H072`
- **Type:** projection audit
- **Result:** `WEAKENED`

### A211
- **Target:** `H073`
- **Type:** fixed-level specialization
- **Result:** `WEAKENED`

### A212
- **Target:** `H073`
- **Type:** bit-complexity counterpressure
- **Result:** `WEAKENED`

### A213
- **Target:** `H045`
- **Type:** random-CSP SoS lower bound
- **Result:** `WEAKENED`

### A214
- **Target:** `H045`
- **Type:** general-SDP attack
- **Result:** `INCONCLUSIVE`

### A215
- **Target:** `H062`
- **Type:** restriction-robustness attack
- **Result:** `WEAKENED`

### A216
- **Target:** `H062`
- **Type:** quantitative-invariant attack
- **Result:** `WEAKENED`

## Reproducibility

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python experiments/theta/canonical_profile.py --self-test
```

## Claim boundary

No entry in C009 proves `P = NP`, `P != NP`, a new SoS lower bound, or novelty. `FORMALIZING` means only that a proof sketch has been narrowed enough to audit.
