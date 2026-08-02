# C014 — Seeded arches through surviving walls

Seed: `9379992`.

C014 interprets an arch as a bridge that crosses a wall without pretending the
wall vanished. The cycle strengthens the exact theta obstruction, destroys one
compiler by transfer, rejects one unstable formulation, and builds narrower
bridges at the remaining certificate and locality barriers.

## Scope

- six descendants: `H104-H109`;
- forty attacks: `A331-A370`;
- two terminal results: `H100`, `H102`;
- fifteen inherited routes re-attacked;
- deterministic seed manifest committed;
- two new exact self-tests.

## Arch 1 — connected exact theta twins

The H098/H099 collision used repeated components. C014 chooses bridge edges
whose entries in the amplified primal matrix are exactly zero.

```text
seed       9379992
SAT arch   (31,22)
UNSAT arch (22,13)
```

For `r` copies, the primal matrix remains

```text
(1/r) J_r tensor X
```

and the old dual remains feasible by assigning every new arch multiplier zero.
The graphs become connected while retaining exact theta `8r`.

The SAT independent set avoids every arch endpoint. On the UNSAT side, adding
edges cannot increase alpha, so alpha remains below the target.

Reproduce:

```bash
python experiments/theta/seeded_arches.py --self-test
```

The result is graph-level. CNF conflict-graph realizability of the added arches
is a separate open gate.

## Wall broken — H102

H102 required:

- explicit circuits over original variables;
- disjoint support at every AND;
- deterministic alternatives at every OR.

That is precisely a d-DNNF. The translation preserves size and has no
projection loophole. Existing explicit DNNF lower bounds therefore destroy the
universal polynomial compiler.

Read:

```text
proof_attempts/H102/REFUTATION.md
```

## Wall cleaned — H100

H100's potential and no-global-answer clauses had no formal syntax. A local
rewrite machine could still carry a work tape and a decreasing clock.

H106 replaces the ambiguous prohibition by:

- constant `q` synchronous passes;
- radius `r` per pass;
- radius `qr` ancestry for every output symbol;
- no persistent adaptive scheduler.

This is narrower but falsifiable.

## Arch 2 — exact LDL bit complexity

H108 clears denominators, uses fraction-free symmetric elimination, and bounds
all determinant numerators and denominators by Hadamard's inequality. This
provides a candidate polynomial bit bound for every explicit rational PSD input.

The seeded stress suite generates fourteen exact rational PSD fixtures:

```bash
python experiments/theta/seeded_ldl_stress.py --self-test
```

Finite stress is not used as proof.

## Arch 3 — strict dual rounding

H109 adds the multiplier bound omitted by H097. If the dual slack has margin
`delta`, the objective has gap `gamma`, and all coordinates are bounded by
`2^B`, dyadic rounding with mesh

```text
min(gamma/2, delta/(2(m+1)))
```

preserves half of both margins. H108 then supplies an exact polynomial-size LDL
certificate.

The remaining wall is whether H097's original promises imply a suitable
multiplier bound.

## Local theta front

H107 asks for a uniform pseudoexpectation transport theorem for every H103
one-pass signed-incidence gadget. H104 removes disconnectedness as an escape,
but does not yet bridge graph arches back to every CNF transduction.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/theta/seeded_arches.py --self-test
python experiments/theta/seeded_ldl_stress.py --self-test
```

The full workflow also runs every earlier exact theta and registry test.

## Claim boundary

C014 does not resolve P versus NP. It establishes a connected graph-level
first-theta obstruction, destroys one exact d-DNNF-equivalent compiler, and
narrows two certificate walls to explicit reviewable lemmas.
