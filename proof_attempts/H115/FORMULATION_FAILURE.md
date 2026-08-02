# H115 — formulation failure and explicit transfer counterexample

## Terminal status

`REJECTED` by attack `A420`.

H115 has two possible readings. On the strong reading it assumes the conclusion
already contained in the phrase “an H114 pair.” On the intended weak reading,
where only exact local-neighborhood equality is assumed, the transfer to global
low-treewidth decision is false.

## Explicit local twins

For any fixed radius `R`, choose a cycle length

```text
L = 8R + 12.
```

Encode an equality edge `x_i = x_j` by

```text
(¬x_i ∨ x_j) ∧ (x_i ∨ ¬x_j)
```

and an inequality edge `x_i != x_j` by

```text
(x_i ∨ x_j) ∧ (¬x_i ∨ ¬x_j).
```

Construct two formulas on two disjoint length-`L` cycles.

### SAT member

- first cycle: two inequality edges, separated by `L/2`;
- second cycle: no inequality edges.

Each component has even parity, so the formula is satisfiable.

### UNSAT member

- first cycle: one inequality edge;
- second cycle: one inequality edge.

Each component has odd parity, so both components are inconsistent.

Both formulas contain exactly two marked edge gadgets. The marks are farther
apart than any radius-`R` incidence ball can see. Therefore the exact multiset
of rooted signed incidence neighborhoods through radius `R` is identical: a
root sees either no marked edge or one marked edge at the same relative
position, and the total multiplicities agree.

The executable artifact verifies exact rooted signed-graph canonical forms for
radii zero through four:

```bash
python experiments/direct/xor_cycle_local_twins.py --self-test
```

## Low treewidth does not erase global assembly

The primal graph of each formula is a disjoint union of two cycles, hence has
treewidth at most two.

Consider the identity compiler:

- every output symbol is the corresponding input symbol;
- ancestry radius is zero;
- output size is linear;
- output treewidth is two;
- witness recovery is the identity map.

A standard dynamic program on each cycle computes the parity of inequality
edges and therefore returns opposite correct SAT decisions.

Thus identical local type inventories and local recovery behavior do **not**
imply identical global low-treewidth dynamic-program behavior. The DP receives
the full assembly of the output graph, including which marked gadgets lie in
the same connected component.

## Why H115 is rejected rather than merely weakened

If “an H114 pair” means a pair already satisfying H114's universal compiler
impossibility clause, then H115 assumes the desired conclusion and is circular.

If it means only the intended constructive premises—opposite labels and exact
local-neighborhood equality—then the XOR-cycle family above refutes the claimed
transfer.

Either reading prevents H115 from functioning as an independent bridge.

## Salvage

A replacement theorem must control global assembly, not merely local type
multiplicity. It may need:

- high-treewidth input pairs, excluding the identity compiler;
- a covering or lift relation preserved by the entire transduction;
- a theorem that every allowed low-treewidth output factors through a common
  quotient;
- explicit accounting of connected components and global parity channels.

This strengthened target is recorded in H119.

## Claim boundary

The counterexample does not show that H106 exists. It shows that H115's proposed
local-inventory argument cannot refute it.
