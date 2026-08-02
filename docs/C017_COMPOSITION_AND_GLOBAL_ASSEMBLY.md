# C017 — Composition upper bounds and global assembly

C017 attacks three active funnels after C016:

1. fixed-gadget amplification toward an Extended-Frege lower bound;
2. local SAT/UNSAT twins toward a constant-pass compiler obstruction;
3. positive SAT lists against sound circuits.

## Cycle output

```text
new descendants          H117-H120
new attacks              A419-A446
terminal results         H111, H115
inherited targets        9
expected live inventory  104
expected terminal nodes  16
```

## H111 destroyed: transparent composition is proof-easy

Let `A` and `B` be a fixed constant-size equivalent gadget pair. Their
equivalence has one constant-size Circuit-Frege proof.

For a polynomial-size acyclic context, propagate that equivalence bottom-up.
Every NOT, AND, or OR gate requires only a constant congruence derivation.
Shared DAG gates are proved once, regardless of how many times they occur after
formula unwinding.

Thus the composed endpoints have a polynomial-size Circuit-Frege proof.
Krajíček's exact 2026 theorem converts that proof into a polynomial-length chain
under the rewrite relation targeted by H110/H111.

Therefore fixed EF-easy gadgets cannot be transparently amplified into a
superpolynomial rewrite gap.

```bash
python experiments/direct/contextual_ef_upper_bound.py --self-test
```

The fixture contrasts twenty-five DAG nodes with more than sixteen million
unfolded port occurrences.

Read:

```text
proof_attempts/H111/REFUTATION.md
```

## Exact local twins exist

For every radius `R`, set `L = 8R+12` and construct two 2-CNF formulas on two
length-`L` variable cycles.

- SAT: two inequality edges in the first cycle, zero in the second;
- UNSAT: one inequality edge in each cycle.

Satisfiability is componentwise XOR parity. Both formulas contain the same two
marked gadgets, separated beyond radius `R`, so their complete rooted signed
incidence-neighborhood multisets agree exactly.

```bash
python experiments/direct/xor_cycle_local_twins.py --self-test
```

The test verifies radii zero through four with exact rooted graph
canonicalization.

## H115 rejected: local inventory does not control assembly

Both XOR-cycle formulas already have primal treewidth two. The identity
compiler is radius zero, linear size, equisatisfiable, and has identity witness
recovery. A global dynamic program distinguishes the formulas by checking
whether each connected cycle has even parity.

Thus the same local type inventory may assemble into globally different
low-treewidth instances.

H115 fails under both interpretations:

- if “an H114 pair” includes the universal compiler obstruction, H115 assumes
  its conclusion;
- if it means only exact local twins, the XOR-cycle pair refutes the transfer.

Read:

```text
proof_attempts/H115/FORMULATION_FAILURE.md
```

## Repaired locality target

H119 replaces local-type counting by two explicit global requirements:

1. the input pair must have high treewidth, excluding the identity compiler;
2. every allowed low-treewidth output must factor through a common quotient or
   covering object that erases the decisive lift parity.

The first unproved theorem is now a low-treewidth factorization theorem for the
exact H106 transduction syntax.

## H116 narrowed by witness covers

For a positive list `(F_i,a_i)`, let `A` be the distinct listed assignments.
The circuit

```text
C_A(G) = OR over a in A of [a satisfies G]
```

is globally SAT-sound and accepts every listed formula. Its size is polynomial
in the encoding length times the number of distinct witnesses.

```bash
python experiments/direct/sound_witness_cover.py --self-test
```

Therefore H116 must exceed this explicit cover budget and must still prove that
no smaller semantic property accepts the entire positive list.

## Surviving direct routes

### Extended Frege

```text
H110 potential route
  no fixed-gadget transparent endpoints
  endpoint equivalence itself must be EF-hard
  -> superpolynomial rewrite distance
  -> EF lower bound
  -> NP != coNP
  -> P != NP
```

### Sound SAT anti-checkers

```text
H116
  -> witness diversity beyond H120 cover
  -> incompressibility against every sound circuit
  -> SAT not in P/poly
  -> P != NP
```

### Local compiler obstruction

```text
H119
  -> high-treewidth opposite-parity lifts
  -> low-treewidth common-quotient factorization
  -> no H106 compiler
```

The third route eliminates only the restricted compiler architecture and does
not itself imply `P != NP`.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/direct/contextual_ef_upper_bound.py --self-test
python experiments/direct/xor_cycle_local_twins.py --self-test
python experiments/direct/sound_witness_cover.py --self-test
```

The workflow also replays all earlier theta, parser, certificate, and direct
funnel tests.

## Claim boundary

C017 does not resolve `P` versus `NP`. Its progress is negative but concrete:
two attractive shortcuts are gone, one exact local-twin family is constructed,
and the remaining routes now expose the global resource each proof must
control.
