# C019 — Connected twins and exact-list covers

C019 continues the Genesis chronicle by removing one visible global side channel
from the locality route and one hidden nonuniform compression from the direct
SAT circuit route.

## Scope

- three descendants: `H125-H127`;
- twenty-four attacks: `A475-A498`;
- twelve inherited targets re-attacked;
- no terminal result;
- two new executable audits.

## H125 — connected high-treewidth local twins

H121 used two disjoint toroidal Tseitin components. A compiler could potentially
branch on the component decomposition before any deeper locality argument.

C019 connects the components with fresh variables `z,w` and five clauses:

```text
(x ∨ z)
(¬x ∨ z)
(y ∨ w)
(¬y ∨ w)
(z ∨ w)
```

Setting `z=w=1` satisfies the bridge for every endpoint assignment. The bridge
is therefore satisfiability-neutral.

Its primal edges create the path

```text
x — z — w — y,
```

so the whole primal graph is connected.

The bridge is placed farther than the visible radius from every charged Tseitin
gadget. A local ball can see a charge or the bridge, never both. Since the bridge
is identical in the SAT and UNSAT members, H121's exact local equality extends
to the connected pair.

The original toroidal primal component remains a subgraph, so the published
lower bound

```text
tw(primal) >= m - 1
```

survives.

Reproduce:

```bash
python experiments/direct/connected_toroidal_tseitin_twins.py --self-test
```

## H127 — the remaining locality wall

The connected family removes:

- the identity compiler, through high input treewidth;
- branching on disconnected input components;
- direct bounded-radius observation of both charges;
- loss of satisfiability through the connector.

One theorem remains:

> every legal fixed-pass transduction producing polynomial-size `O(log N)`
> treewidth output must factor through a common quotient that cannot preserve
> same-lobe versus split-lobe charge parity.

The theorem must include the complete output assembly and every witness-recovery
annotation. C019 does not prove it and does not claim H106 is refuted.

## H126 — witness-independent exact-list cover

Let an H124 positive list contain `m` distinct satisfiable formula strings of
exactly `L` bits. Hardwire one equality test for each string and OR the tests.
The resulting circuit accepts exactly the list.

Because every listed string is satisfiable, the circuit is globally SAT-sound.
A loose standard-basis bound is

```text
size <= 3mL.
```

Therefore an H124 list hitting every SAT-sound circuit of size `L^k` must obey

```text
m > L^(k-1)/3.
```

This attack is stronger than witness counting on lists with many distinct
formulas but compressible witness structure: it ignores witnesses completely.
For each proposed list, JANUS must charge both:

```text
H120 witness-union cover
H126 exact-formula membership cover
```

and use the smaller circuit as the stronger attack.

Reproduce:

```bash
python experiments/direct/exact_list_sound_cover.py --self-test
```

## Direct route after C019

```text
H124 exact-L positive anti-checker
  + more than L^(k-1)/3 distinct formulas
  + witness-cover escape
  + incompressibility against every other L^k SAT-sound circuit
  -> SAT not in P/poly
  -> P != NP
```

The implication is correct. The construction and the universal
incompressibility theorem remain open.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/direct/connected_toroidal_tseitin_twins.py --self-test
python experiments/direct/exact_list_sound_cover.py --self-test
```

The workflow retains every earlier exact registry, theta, rewrite, local, and
anti-checker test.

## Claim boundary

C019 does not resolve `P` versus `NP`. It strengthens one restricted locality
target and narrows one direct circuit-lower-bound target without manufacturing a
terminal result.
