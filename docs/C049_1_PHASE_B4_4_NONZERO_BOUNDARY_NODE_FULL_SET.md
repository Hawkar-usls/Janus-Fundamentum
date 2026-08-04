# C049.1 Phase B4.4 — nonzero-boundary internal-node full set

This phase evaluates exactly one internal node of the existing B4.2 grouped
`3k` scaffold with genuine nonzero boundary transport. It is not a complete
bottom-up dynamic-programming pass and does not enable `NO_LAYOUT_AT_CAP`.

## Selected scaffold node

The node is the first spine join in the existing six-factor B4.2 fixture over
`GF(2)^4`:

```text
whole-factor blocks = <0001>, <0010>, <0100>, <1000>, <0011>, <1100>
scaffold order      = (0,4,2,3,1,5)
joined factors      = (0,4)
outside factors     = (2,3,1,5)
```

The independently recomputed RREF boundaries and coordinate transports are:

```text
left child B0        = [1]
right child B4       = [3]
common join boundary = [2,1]
parent boundary      = [2]

B0 basis in common coordinates = [2]
B4 basis in common coordinates = [3]
parent basis in common          = [1]
```

Thus `dim(B_parent)=1`, both child boundaries are nonzero, the common join
boundary has dimension two, and neither child transport is the zero-boundary
identity case from B4.3. The producer records the Proposition 4.2 expand side
conditions, the join intersection condition, and the shrink containment. The
verifier recomputes all bases and coordinate vectors independently.

The whole-factor partition and affine offsets are retained by one frozen
partition receipt. Every pair records stage references for left expand, right
expand, join, and shrink; no factor block is split.

## Complete B3 to B2 traversal

Each dimension-one child full set is the exact B2 `up_1` closure of its
canonical whole-factor leaf trajectory and has 36 entries. The node processes
the complete `36 x 36` product and every Delannoy lattice path:

```text
child pairs processed                    1,296
lattice paths / refinements            163,824
successful refinements                  12,073
failed width refinements               151,751
raw precompact join statistics       1,297,408
unique successful generators               252
duplicate successful outputs deleted   11,821
B2 dominance deletions                     250
retained B2 generators                       2
final up_1 entries                          252
cumulative work                       7,941,294
```

Every refinement retains its raw precompact join, correction receipts, both
compactification transcripts, shrink projections, final width test, failure
reason when applicable, provenance, and monotone cumulative-work checkpoint.
Every duplicate and every B2-dominated generator has a replayable deletion
witness.

## Chunked frozen transcript

The complete canonical JSON certificate is `960,692,616` bytes before
compression. It is split by fixed record counts and compressed with a
deterministic gzip encoding:

```text
PAIRS         11 chunks x 128 records  (tail 16)
REFINEMENTS   40 chunks x 4096 records (tail 4080)
GENERATORS     2 chunks x 128 records  (tail 124)
DELETIONS      6 chunks x 2048 records (tail 1581)
TOTAL         59 chunks
COMPRESSED    21,008,111 bytes
```

Each record has its own semantic digest. Each chunk has a canonical-payload
digest, compressed-byte SHA-256, record-ID range, and previous/next chunk
cross-references. The frozen manifest pins the ordered digest inventory:

```text
experiments/direct/C049.1-JANUS-PHASE-B4.4-NONZERO-BOUNDARY-NODE-FULL-SET.manifest.frozen.json
manifest bytes       = 327885
manifest file SHA-256 = 5df0513c4c693ae7d65e9a247ec782543d48bf54f912a71fca42db181e949392
manifest digest       = de6b1f376ad992550f38881ec72281bde0a38b70bc4fa23a9d96e298a4320b90
transcript root       = 5d6748f2d3b7e65aa7812ba963c7f833034d06c973ac26263a960639f5eeeea0
```

The repository stores the frozen manifest rather than duplicating 21 MB of
deterministically reproducible chunk payloads. CI regenerates every chunk,
requires exact manifest equality, reconstructs and replays the full transcript,
and exports the complete chunk directory as a short-lived workflow artifact.
Certificate volume is therefore measured and paid, not sampled or hidden.

## Independent replay and tamper control

The verifier imports neither the B4.4 producer nor the B3/B2 producer cores. It
uses the independent B3 and B2 verifier algebras to recompute:

- scaffold cuts and all RREF transport coordinates;
- both 36-entry child full sets;
- all 1,296 child pairs and all 163,824 lattice paths;
- raw joins, lambda corrections, compactification, shrink, and width outcomes;
- all 151,751 failed refinements and cumulative-work checkpoints;
- 252 generator provenance records, 11,821 duplicate deletions, 250 dominance
  deletions, and the final 252-entry `up_1` full set;
- every chunk digest, range, cross-reference, and exact certificate volume.

A transport-matrix control changes the left child coordinate vector from `[2]`
to `[1]`, then repairs the record, chunk, transcript-root, and manifest digests.
The independent semantic replay still rejects it.

## Strict boundary

This is one nonzero-boundary internal node only. It does not process every
scaffold node, compute the root full set, complete branch refinement, reconstruct
an accepting layout, or prove that no width-`k` trajectory exists.

```text
NEXT_GATE = C049.1_B4.5_UNIVERSAL_BOTTOM_UP_SCAFFOLD_EXECUTOR
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
NO_LAYOUT_AT_CAP = FORBIDDEN
P_VS_NP = OPEN
```
