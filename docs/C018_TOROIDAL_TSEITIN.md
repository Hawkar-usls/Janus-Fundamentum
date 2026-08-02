# C018 — High-treewidth local twins and length normalization

C018 continues the Genesis chronicle by attacking the two surviving direct
funnels at their exact weakest points.

## Scope

- four descendants: `H121-H124`;
- twenty-eight attacks: `A447-A474`;
- twelve inherited routes re-attacked;
- one terminal result: `H116`;
- two new executable audits;
- three primary references added.

## H116 rejected

H116 compared circuits of size `n^k` against formulas whose actual length could
be

```text
L_k(n) = n^{d(k)}
```

with a `k`-dependent exponent. A hypothetical SAT circuit of size `L^3` can
therefore have size `n^{3d(k)}`, outside the attacked `n^k` class for every
`k`.

Concrete audit:

```bash
python experiments/direct/length_parameter_audit.py --self-test
```

H124 repairs the implication by fixing every generated formula at exactly `L`
bits and attacking SAT-sound circuits of size `L^k` on that same domain.

This repairs only the quantifiers. The anti-checker construction remains open
and still faces H120's witness-cover circuit and arbitrary semantic compression.

## H121 — toroidal Tseitin twins

For radius `R`, set

```text
m = 8R + 13
```

and use two disjoint `m × m` toroidal grids. Every graph edge is a Boolean
variable. At every grid vertex, encode the parity of its four incident edge
variables with eight width-four clauses.

Charge distributions:

```text
SAT:    (2,0) charges by component
UNSAT:  (1,1) charges by component
```

A connected Tseitin system is satisfiable exactly when its total charge is
even. C018 constructs the SAT assignment through a spanning tree and checks all
clauses exactly.

The two SAT charges are separated beyond every radius-`R` incidence view. Every
root sees at most one charged gadget, and both formulas contain two such gadgets
total. Translation-normalized local signature multisets therefore agree
exactly.

```bash
python experiments/direct/toroidal_tseitin_twins.py --self-test
```

## Why this is stronger than H118

H118's cycle formulas had treewidth two, so identity compilation already met
the low-treewidth target.

For H121, the primal graph is exactly two copies of the line graph of the
`toroidal grid T_m`.

Published results give:

```text
tw(T_m) = 2m - 1
tw(L(G)) >= (tw(G)+1)/2 - 1
```

and hence:

```text
tw(primal H121) >= m - 1 = Omega(sqrt(N)).
```

Identity compilation is no longer an H106 escape.

## Remaining locality wall

H123 asks for one theorem:

> Every fixed-pass H106 transduction that maps the H121 pair to polynomial-size
> O(log N)-treewidth outputs must factor through a common local quotient that
> forgets whether the two charges lie in one component or in two.

The theorem must include the whole output assembly and every witness-recovery
annotation. Local type equality alone is not enough, as C017 already proved.

No such factorization theorem is currently known.

## Direct circuit route after repair

The formal implication is now:

```text
H124 exact-L positive anti-checker
  -> SAT not in P/poly
  -> P != NP
```

The first unproved theorem is still severe:

- generate the list uniformly;
- keep formulas at exactly `L` bits;
- exceed H120's SAT-sound witness cover;
- defeat every smaller semantic SAT-sound circuit;
- never test soundness or solve SAT inside the constructor.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/direct/toroidal_tseitin_twins.py --self-test
python experiments/direct/length_parameter_audit.py --self-test
```

The workflow also retains every earlier exact registry, theta, rewrite, local,
and anti-checker audit.

## Claim boundary

C018 does not resolve `P` versus `NP`. It produces an explicit high-treewidth
local-twin family, rejects one invalid direct implication, and isolates two
remaining theorems: global low-treewidth quotient factorization and
length-normalized SAT-sound incompressibility.
