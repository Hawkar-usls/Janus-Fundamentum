# C025-E2R-L1C — Nisan-Wigderson locality transfer audit

**Status:** `CURRENT_KAPPA_LOCAL_TRANSFER_REFUTED_BY_PARAMETER_MISMATCH`; `NW_NEIGHBORHOOD_LOCAL_EXTENSION_AXIOM_MAP_PROVED_CONDITIONALLY`; full proof transfer `OPEN`.

Sokolov's functional encoding calls `g` local iff its variables lie inside one fixed NW neighborhood `Vars_i=N(v_i)`. This differs from our first cardinality restriction `|support(e)|<=kappa`.

Example: `Vars_1={x1,x2}`, `Vars_2={x3,x4}`, `kappa=2`. Support `{x1,x3}` is cardinality-local but lies in no one neighborhood, so direct transfer fails.

Refine to **NW-neighborhood-local**:

```text
support(e) subseteq Vars_i
```

for some `i`.

For a local B2 extension `e <-> (a AND b)`, if `a,b` denote local functions `g,h` in the same `Vars_i`, then `e` denotes `s=g AND h`. Sokolov's functional encoding explicitly contains the matching clauses

```text
(~y_s OR y_g)
(~y_s OR y_h)
(y_s OR ~y_g OR ~y_h)
```

when these local functions are in the selected collection. Thus extension-axiom compatibility is proved **conditional on the functional encoding containing every computed local function**.

This is not a full theorem transfer. Missing gates remain: root-formula map, literal/function map, collection-size accounting, Resolution preservation, restriction correspondence and ER3 width accounting.

```text
L1-C1 cardinality-local -> NW-local transfer = REFUTED
L1-C2 NW-local extension-axiom map            = PROVED_CONDITIONAL_ON_G
L1-C3 full proof transfer                      = OPEN
L1-D heavy-width transfer                      = BLOCKED_BY_L1-C3
```

Hard boundary: matching extension clauses do not establish object identity with the source functional encoding.