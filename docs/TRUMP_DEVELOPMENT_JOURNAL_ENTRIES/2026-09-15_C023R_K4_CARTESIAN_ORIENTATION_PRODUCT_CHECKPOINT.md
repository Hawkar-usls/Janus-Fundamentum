# TRUMP Journal — C023R K4 Cartesian orientation-product checkpoint

Date: 2026-09-15
Authority: `HQ_CAPTAIN_OBVIOUS_REVEALED_DIAGNOSTIC_PLUS_SYMBOLIC_THEOREM__NO_SCIENTIFIC_PROMOTION`

## Why this check was run

After the representation-firewall correction and the exact sibling tail-balance / partial-pivot defect localization the nearest cheap falsifier was an already-written revealed K4 audit:

`experiments/trump_c023r_cache_fiber/analyze_k4_fiber_product.py`

The script existed on the frozen C023R diagnostic branch but its result JSON was not committed. HQ ran it unchanged through a read-only GitHub Actions workflow. No Remote Desktop was used.

Workflow commit:

`ab9628c25ca264c8dee36dcb53a240c29b10c6a0`

GitHub Actions run:

`34901167283`

Job:

`104167201781`

Conclusion:

`success`

Authority remains `REVEALED_DIAGNOSTIC_ONLY`.

## Exact finite result

Target cache state: `1040`.

Fibre size:

`128`.

Per-block pattern counts across the six K4 MAJ3 edge blocks:

`2,2,2,2,4,2`.

Their Cartesian product size is

`2*2*2*2*4*2 = 128`.

The exact audit returned:

`exact_cartesian_product = true`.

Thus all 128 execution contexts in this fibre are exactly the Cartesian product of the observed per-block pattern sets.

Four blocks carry the fixed-pair MAJ3 orientation collision

`01 <-> 10`.

One fully assigned block contributes two same-output patterns; another contributes all four assignments of the MAJ3 output-1 fibre.

The total finite forgotten-product dimension is exactly

`log2(128)=7` bits.

Machine receipt on the active C023R branch:

`proof_attempts/C023R/K4_MAX_FIBER_CARTESIAN_PRODUCT_REVEALED_RESULT_2026-09-15.json`

Receipt commit:

`2b8d40fcd8a5d410be657e9114110bdbf12a6660`

## What this falsifies

The following strong positive claim is false even on the revealed K4 fixture:

> inherited historical metadata necessarily retains every local MAJ3 semantic-collision bit.

Seven local bits are simultaneously forgotten at one byte-identical historical cache state, and their observed combinations factor exactly.

This is a finite falsification of that universal claim. It is not an asymptotic lower bound.

## Exact symbolic generalization

The branch now contains:

`FIXED_PAIR_ORIENTATION_PRODUCT_THEOREM_2026-09-15.md`

commit:

`489c862685e306bae9fc16436952179694b8cf91`

For any edge subset `S`, assigning the same two coordinate positions of every MAJ3 block as independently `01` or `10` leaves the same third coordinate and hence the exact same restricted source byte-CNF across all `2^|S|` orientation vectors, provided all other restrictions are fixed.

If every edge block were oriented this way, the source residual would become the ordinary Tseitin relation on the remaining third coordinates. Historical Policy-0A does not rerun the root affine dispatcher on descendant states.

This theorem is about source representation only. Execution reachability and inherited-clause equality remain open.

## Derived metadata localization

Two additional exact branch lemmas sharpen the remaining obstacle:

1. `ASYMMETRY_CUTOFF_DEFECT_ONLY_THEOREM_2026-09-15.md`, commit `b21033001b009648bf263f1afbee5f08d8902c47`:
   value asymmetry of a semantically irrelevant/sign-symmetric coordinate can be newly injected only by a budget-truncated partial pivot on another variable; complete pivots, ordinary restrictions and noncontradictory UP preserve sign symmetry.

2. `SOURCE_FREQUENCY_TWIN_AND_DEFECT_SPLIT_THEOREM_2026-09-15.md`, commit `fb74fe7619ac59538ae6e1609a3e099997916be1`:
   all live coordinates of one edge block have exactly equal source occurrence frequency; any within-block frequency split is entirely due to derived/inherited metadata.

Therefore the remaining asymptotic question can be stated in terms of `DEFECT_SPLIT_COVERAGE` rather than all cache-key syntax.

## Current exact gate

`C023R_SCALABLE_FIXED_PAIR_ORIENTATION_PRODUCT_GATE`

Decisive FAIL of the cache-fibre transfer route would be an infinite frozen q=4 sequence with reachable keys `K_t` and subsets `S_t` satisfying:

- `|S_t| = Omega(L_t)`;
- each block in `S_t` realizes both fixed-pair orientations `01` and `10`;
- the orientation choices compose independently;
- inherited metadata and pre-UP agree byte-for-byte at `K_t`.

Then

`m(K_t) >= 2^{|S_t|} = 2^{Omega(L_t)}`.

Positive survival of the subexponential-fibre route requires proving that the maximum independently composable orientation-product dimension is `o(L)` (with other collision mechanisms separately bounded).

## Frozen numbering constraint

All future q=4 claims must use `Q4_CANONICAL_ENCODING_NUMBERING_CONTRACT_v1.0.md`: lexicographic matrix vertices, lexicographic undirected edges, and edge block variable IDs `(3j+1,3j+2,3j+3)`. Historical Policy-0A is not renaming-invariant.

No convenient graph automorphism or post-result reindexing is admissible.

## Claim ceiling

- K4 exact Cartesian product != asymptotic Cartesian product;
- no exponential Policy-0A cache fibre is proved;
- no Policy-0A lower bound is proved;
- C022 H137 remains primary-source blocked under GitHub-only source audit;
- global APMA frontier unchanged;
- `P_VS_NP = OPEN`.
