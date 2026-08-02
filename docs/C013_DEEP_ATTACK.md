# C013 — Deep attack saturation and exact theta breakthrough

C013 continues attacking the C012 pressure set until each route reaches one of
three outcomes:

1. terminal formulation failure;
2. a narrower descendant born from the attack;
3. a named open barrier that the current laboratory cannot cross.

## Terminal removals

Six historical formulations are rejected:

- `H001-H004`: unrestricted transformers can decide SAT first and emit a
  constant target object;
- `H019`: interface symbols have no fixed syntax, denotation-size charge, or
  original-variable support semantics;
- `H070`: an arbitrary polynomial compiler can decide SAT and choose between
  two fixed graphs.

These are `REJECTED` as mechanisms, not claimed false as existential statements.
Their surviving ideas continue through `H043-H045`, `H100`, `H102`, and `H103`.

## Exact theta collision

### UNSAT side

`U` contains all eight width-three clauses on `x1,x2,x3`. Every assignment
falsifies exactly one clause, so the conflict graph has alpha 7 against target
8.

### SAT side

`S` adjoins a shared positive `x4` literal to the same eight sign patterns.
The assignment `x4=true` gives alpha 8.

### Exact value

Both graphs have exact Lovasz theta value 8. The proof bundle contains:

- rational primal matrices;
- rational dual edge multipliers;
- exact rational permuted `LDL^T` certificates;
- exact alpha recomputation;
- graph-bound collision verification.

Run:

```bash
python experiments/theta/complete_3cnf_collision.py --self-test
```

The UNSAT primal is generated from 12 orbits of the 48-element signed-coordinate
automorphism group. Its exact nonzero eigenvalues are:

```text
1/3       multiplicity 1
1/6       multiplicity 3
1/18      multiplicity 3
```

The verifier does not rely on a floating-point eigensolver.

## Infinite exact family

For `r` disjoint renamed copies, use the rational primal matrix

```text
(1/r) J_r tensor X
```

and the direct dual certificate with objective `8r` and multiplier `8r` on
each intra-clause edge. This gives exact theta value `8r` on both sides.

Run:

```bash
python experiments/theta/complete_3cnf_family.py --self-test
```

The CI fixtures replay `r=1,2`; the algebraic construction is uniform for every
positive integer `r`.

This is the concrete content of `H098-H099`. It is an explicit obstruction to
the standard first theta level, not a solution of P versus NP.

## Attack-born descendants

### H100

Adds a strictly decreasing local potential and forbids global answer channels in
the local-treewidth compiler route. It remains blocked on expander-separator
invariants and a formal admissible potential language.

### H101

Combines the parity, theta-rank, restriction, and mixed-residual requirements
into one explicit generator target. The unresolved barrier is a deterministic
nonlinear gadget whose pseudoexpectation survives both restrictions and
Gaussian elimination.

### H102

Replaces H019's opaque interface symbols by typed explicit circuits with charged
original-variable supports. This precision makes a DNNF transfer attack
possible; completing that transfer may destroy H102 in the next cycle.

### H103

Restricts the theta compiler to a fixed one-pass local signed-incidence
transduction. H098 amplifications are now mandatory counterexamples for every
candidate compiler. The unresolved barrier is general local pseudoexpectation
transport.

## Saturated proof-complexity duels

The following pairs remain beyond current unconditional techniques:

```text
H006 versus H011   Extended Frege lower versus upper bound
H007 versus H014   full IPS lower versus upper bound
H012 versus H013   TC0-Frege lower versus upper bound
H022 versus H023   CP simulation versus SP/CP separation
H024 versus H025   recursive extension-PC lower versus upper bound
```

No side is promoted merely because its opponent also survives.

## Current stopping frontier

C013 reaches four hard walls:

1. explicit full-strength proof-system lower bounds;
2. pseudoexpectation transport through arbitrary fixed local gadgets;
3. restriction-robust mixed XOR/non-affine generators;
4. a formal DNNF simulation or escape theorem for typed interface elimination.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/theta/complete_3cnf_collision.py --self-test
python experiments/theta/complete_3cnf_family.py --self-test
```

## Claim boundary

C013 establishes an exact certified limitation of the standard level-one
Lovasz-theta SAT reduction and removes six unusable formulations. It does not
resolve `P` versus `NP`, `NP` versus `coNP`, Extended Frege, full IPS, TC0-Frege,
or unrestricted parity proof lower bounds.
