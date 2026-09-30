# C025-E2R-L1 — Support-local ER3 restricted frontier

**Status:** `OPEN_RESTRICTED_FRONTIER__MECHANICS_PROVED`.

## Frozen support restriction

For a root literal `x`, `support(x)={x}`. For each B2 definition

```text
e_i <-> (a_i AND b_i)
```

set

```text
support(e_i)=support(a_i) union support(b_i).
```

A proof is `kappa-local` when every extension has support size at most `kappa`. Initial regime: `kappa=O(log N)`.

## Provider-established mechanics

Provider run `32728789959`, job `97436024608`, conclusion `SUCCESS`, verifies:

```text
C025_E2R_L1_TRANSITIVE_SUPPORT = PASS
C025_E2R_L1_POLARITY_INVARIANCE = PASS
C025_E2R_L1_FORWARD_DEPENDENCY_REJECTION = PASS
C025_E2R_L1_KAPPA_LOCAL_ADMISSION = PASS
C025_E2R_L1_ROOT_RESTRICTION_SUPPORT_MONOTONICITY = PASS
C025_E2R_L1_ROOT_RESTRICTION_LOCALITY_STABILITY = PASS
C025_E2R_L1C_KAPPA_LOCAL_TO_NW_LOCAL_TRANSFER = REFUTED
C025_E2R_L1C_SAME_NEIGHBORHOOD_EXTENSION_CLOSURE = PASS
C025_E2R_L1C_DIFFERENT_NEIGHBORHOOD_ESCAPE = PASS
```

## Root-restriction theorem

For a partial assignment `rho` to root variables, the residual Boolean function represented by an extension can depend only on roots it depended on before and which remain unassigned. Therefore

```text
S_rho(e) subseteq S(e) minus dom(rho),
```

so `kappa`-locality is preserved under root restrictions.

## NW locality split

Sokolov locality is not cardinality locality. A local function must be supported inside one fixed NW neighborhood `Vars_i=N(v_i)`. Thus `|support(e)|<=kappa` does not imply NW-locality.

The correct refined subregime is

```text
support(e) subseteq Vars_i
```

for some `i`.

For a conjunction extension, closure requires both operands to be in the **same** neighborhood. Under that condition and conditional on the source function collection `G` containing the represented local functions, the functional encoding's clauses for `s=g AND h` exactly match B2 extension axioms.

This establishes extension-axiom compatibility only, not a heavy-width theorem transfer.

## Current gates

```text
L1-A support calculator / verifier                    = PROVED_IN_SCOPE / PROVIDER PASS
L1-B root-restriction locality stability              = PROVED / PROVIDER PASS
L1-C1 kappa-local -> NW-local direct transfer         = REFUTED / PROVIDER PASS
L1-C2 NW-local extension-axiom compatibility          = PROVED CONDITIONAL ON G
L1-C3 full functional-encoding proof transfer         = OPEN ACTIVE
L1-D heavy-width transfer                             = BLOCKED BY L1-C3
L1-E explicit restricted counterfamily                = OPEN
```

Full-transfer checklist:

```text
ROOT_FORMULA_MAP
PROOF_LITERAL_FUNCTION_MAP
FUNCTION_COLLECTION_SIZE_ACCOUNTING
RESOLUTION_STEP_PRESERVATION
RESTRICTION_CORRESPONDENCE
ER3_WIDTH_ACCOUNTING
```

Hard boundary:

```text
ER3[LOCAL] LOWER BOUND != FULL ER3 LOWER BOUND
P_VS_NP = OPEN
```
