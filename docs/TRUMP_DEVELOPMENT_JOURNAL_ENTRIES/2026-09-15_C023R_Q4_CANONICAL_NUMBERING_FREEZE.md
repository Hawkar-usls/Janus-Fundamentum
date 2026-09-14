# TRUMP Journal — C023R q=4 canonical numbering freeze

Date: 2026-09-15
Authority: `PRE_ASYMPTOTIC_RUN_ENCODING_FREEZE__NO_SCIENTIFIC_PROMOTION`

Captain Obvious identified an encoding-level omission in the q=4 historical revisit: the earlier Morgenstern binding fixed the abstract graph family but not the vertex/edge numbering that exact Policy-0A uses through numeric pivot order and minimum-ID branch tie-breaking.

No asymptotic Policy-0A run on the q=4 family had been observed before this repair.

Canonical encoding is now frozen on branch `research/trump-c023r-reachable-coset-theorem-2026-09-15` at commit:

`f9a6f0a6bcba8fad91dd7422dac43eabdd762ebb`

Contract:

`proof_attempts/C023R/Q4_CANONICAL_ENCODING_NUMBERING_CONTRACT_v1.0.md`

The contract fixes:

- F4 element codes `0,1,a,a+1 -> 0,1,2,3`;
- K_t coefficient-vector/base-4 encoding;
- lexicographic determinant-one matrix vertex enumeration;
- frozen generator order and left multiplication;
- undirected edge normalization and lexicographic edge ordering;
- charge 1 at frozen vertex ID 0 only;
- edge `e_j` -> MAJ3 variables `(3j+1,3j+2,3j+3)`;
- exact historical CNF canonicalization and unchanged numeric policy semantics.

No structural renaming, automorphism canonicalization or post-result permutation is admissible for this route.

Scientific effect:

`ENCODING_UNDERSPECIFICATION_CLOSED_PRE_RUN`.

No cache lower bound is implied. C022/C023 claim ceilings and global APMA frontier remain unchanged.