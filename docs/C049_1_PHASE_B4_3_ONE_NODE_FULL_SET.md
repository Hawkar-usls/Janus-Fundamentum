# C049.1 Phase B4.3 — first replayable internal-node full set

This phase evaluates exactly one internal node of the existing B4.2 grouped
`3k` scaffold.  It is not a complete dynamic-programming pass and does not
enable `NO_LAYOUT_AT_CAP`.

## Selected scaffold node

The selected B4.2 case has three whole-factor blocks over `GF(2)^3`:

```text
factor 0 = <001>
factor 1 = <010>
factor 2 = <100>
scaffold order = (1,0,2)
```

The unique spine node joins whole factors `1` and `0`; factor `2` is outside.
The two leaf boundaries, their common join boundary, and the parent boundary
are all the zero subspace.  This keeps the complete `U_1(B)` universe finite
without splitting any factor block or using a supplied layout as a discovery
oracle.  Affine offsets are transported unchanged.

Each leaf full set is the complete B2 `up_1` closure of the canonical
zero-boundary one-factor trajectory.  It has six entries.  Therefore the node
processes all `6 x 6 = 36` child pairs.

## Proof-carrying B3 to B2 chain

For every child pair the producer records both expand transports and enumerates
every Delannoy lattice path.  Every one of the 124 refinements retains:

- the complete path;
- every raw precompact joined statistic and lambda correction;
- the complete B1 compactification transcript;
- every projected shrink statistic and correction;
- the shrink compactification transcript;
- the final width test, including all failed width refinements;
- a monotone cumulative-work checkpoint.

The 35 width-one refinements yield six distinct generators.  The other 89
refinements are retained as `FAILED_WIDTH_CAP`; they are not erased from the
work ledger.  Twenty-nine duplicate successful outputs carry identity deletion
witnesses.  B2 then deletes five of the six distinct generators with extension
preorder witnesses, retains one generator, and constructs the complete six-entry
`up_1` node full set.  Every retained generator and full-set entry points back
to its successful refinement provenance.

## Frozen audit

```text
child full-set entries               6 + 6
child pairs processed                   36
lattice paths / refinements             124
successful refinements                   35
failed width refinements                 89
raw precompact join statistics          448
distinct successful generators            6
duplicate successful outputs deleted     29
B2 dominance deletions                     5
retained B2 generators                     1
final up_1 entries                         6
cumulative work                         2584
```

Frozen artifact:

```text
experiments/direct/C049.1-JANUS-PHASE-B4.3-ONE-NODE-FULL-SET.frozen.json
bytes  = 453969
digest = 2d23f1fa0e5a8e3a716e9266b4279963f4dd2406636f7cd97fd0c45390a1ee68
```

## Independent replay

The verifier imports the already independent B3 and B2 verifier algebras, not
the B4.3 producer or its B3/B2 cores.  It independently recomputes scaffold
boundaries, expand transports, all lattice paths, join and shrink statistics,
both compactification transcripts, all failed/successful classifications,
B2 domination, deletion witnesses, `up_1`, grouped-factor preservation, and
the cumulative-work sequence.

Five digest-repaired semantic controls must be rejected: altered raw join,
missing failed refinement, altered B2 deletion witness, decreased cumulative
work, and split grouped partition.

## Strict boundary

This artifact covers one internal node only.  It does not compute full sets at
every scaffold node, refine every branch edge, reconstruct every accepting
width-`k` layout, or prove that an empty root full set is complete.  Even if
this node full set were empty, its only permitted terminal would remain:

```text
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
NO_LAYOUT_AT_CAP = FORBIDDEN
P_VS_NP = OPEN
```
