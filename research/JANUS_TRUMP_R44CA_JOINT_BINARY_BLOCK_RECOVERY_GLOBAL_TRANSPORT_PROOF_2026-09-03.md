# R44CA — Joint sibling structure recovers the global transport

R44BZ gives high-treewidth, connected, maxdef-critical siblings in which each individual binary implication graph has no nontrivial congruence and the raw signed transport moves `Theta(r^2)` variables. Nevertheless, the two siblings together expose a stronger polynomial invariant.

## 1. Recover the blocks from the raw siblings

For siblings `A,B`, define the joint binary graph `J_2(A,B)` on variables: put an undirected edge `{u,v}` whenever `u` and `v` occur together in a binary clause of `A` or `B`.

In one R44AS block:

- sibling `A` has binary clauses on variable pairs `{3,4}` and `{1,4}`;
- sibling `B` has binary clauses on `{5,6}` and `{3,6}`.

Their union is the path

`1 - 4 - 3 - 6 - 5`,

so all five local variables are connected.

Every R44BZ cross-block connector has width exactly three. Hence no connector contributes an edge to `J_2`. Different blocks have disjoint nonpivot variables. Therefore the connected components of `J_2(A,B)` are exactly the five-variable blocks.

This block decomposition is found by ordinary graph connected-components in polynomial time.

## 2. Local signed-transport domain is constant

For one recovered block, enumerate all signed permutations on its five variables. There are

`5! * 2^5 = 3840`

candidates. Check the exact R44BP clause-subsumption condition from local source `B` to local target `A`.

Complete finite enumeration gives exactly two valid local maps:

`pi0 = {1:-3, 3:-5, 4:6, 5:-1, 6:-4}`,

`pi1 = {1:-3, 3:-5, 4:6, 5:4, 6:1}`.

Thus every recovered block has the constant domain `{pi0,pi1}`.

## 3. The connector is a synchronization gadget

Take the complete 12-clause connector orbit between two adjacent blocks. Evaluate all four pairs from `{pi0,pi1} x {pi0,pi1}` using the exact clause-image/subsumption check on the connector clauses.

The exact finite relation is:

- `(pi0,pi0)` — valid;
- `(pi0,pi1)` — invalid;
- `(pi1,pi0)` — invalid;
- `(pi1,pi1)` — invalid.

Hence each block edge forces both endpoints to use `pi0`.

The R44BZ block graph is an `r x r` grid and is connected for `r>=2`. Therefore edge propagation forces `pi0` on every block. This recovers the global support-`5r^2` transport without enumerating global support sets or global signed permutations.

## 4. Complexity

Let `S` be current encoded sibling size.

- build `J_2`: polynomial, linear with standard hashing/indexing;
- connected components: linear in the joint graph;
- local transport enumeration: `3840` candidates per block, constant candidate count;
- connector compatibility: four candidate pairs per block edge after local filtering;
- propagation and final global verification: polynomial.

Thus the whole discovery algorithm is polynomial in `S`.

## 5. Exact safe deletion and rank

The global map is an exact R44BP signed model transport from the deleted sibling to the retained sibling. Hence sibling OR collapses to the retained branch. R44BZ already proves parent rank

`27r^2-24r-1`

and retained child rank

`25r^2-24r`,

so the exact safe-delete step decreases maxdef by `2r^2-1`. A retained child model lifts to the parent by setting the shared pivot to the retained branch value.

## Consequence

`INDIVIDUAL_CONGRUENCE_RIGID != JOINT_SIBLING_STRUCTURE_RIGID`.

`UNBOUNDED_RAW_SUPPORT != EXPONENTIAL_DISCOVERY`.

High treewidth and growing support do not by themselves prevent a polynomial exact safe-delete rule when a constant local transport domain is synchronized by the joint sibling structure.

## Claim ceiling

R44CA solves only the explicit R44BZ family. It does not establish a universal block-recovery theorem, a universal transport relation, or P=NP.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
