# R44BS — Connected backbone forces unbounded signed-transport support

Start from the R44BR shared-pivot family `G_k`: `k` R44AS blocks share one pivot `x`; all five nonpivot variables remain block-disjoint. R44BR proves `G_k` is maxdef-critical with `delta*=3k-1`, while both siblings have maxdef `k`.

For each adjacent pair of blocks `i,i+1` and each one of the five corresponding nonpivot variables `v`, add the two clauses

`(¬v_i ∨ v_{i+1})` and `(v_i ∨ ¬v_{i+1})`.

There are `10(k-1)` such backbone clauses and no new variables.

## Critical-extension lemma

If `F` is maxdef-critical and a new clause `C` satisfies `Var(C)⊆Var(F)`, then `F∪{C}` is maxdef-critical and `delta*(F∪{C})=delta*(F)+1`.

Proof: the full formula gains one clause and no variable. Any proper subset omitting `C` has deficiency at most `delta*(F)`. Any proper subset containing `C` is `T∪{C}` for proper `T⊊F`, so `delta(T∪{C})≤delta(T)+1≤delta*(F)`. Thus only the full extended formula attains `delta*(F)+1`.

Applying the lemma to every backbone clause gives

`delta*(G_k^conn)=(3k-1)+10(k-1)=13k-11`,

and the parent remains maxdef-critical.

## Child ranks

Before the backbone each sibling has maxdef `k` and full deficiency `k`. Let `c=10(k-1)`. Adding `c` clauses can raise maximum deficiency by at most `c`, because for every selected new-clause set `U`,

`delta(T∪U)≤delta(T)+|U|≤delta*(T)+c`.

The full child formula has deficiency exactly `k+c` because the backbone adds no variables. Therefore

`delta*(A_k^conn)=delta*(B_k^conn)=k+c=11k-10`.

Thus both branches are strict descendants:

`13k-11 -> 11k-10`, with drop `2k-1`.

## SAT and connectedness

Each local sibling is SAT. Repeating the same local model in every block satisfies all equality-backbone clauses, so both global siblings are SAT.

Each local sibling's variable-incidence/primal graph is connected. Equality clauses connect every corresponding variable track between consecutive blocks. Hence the two global siblings are connected.

## Forward signed transport exists

Apply the R44BP signed permutation independently inside each block. It transports every local `B` block into the local `A` block.

An equality relation `v_i↔v_{i+1}` is mapped under the same signed variable image in both blocks to the equality relation on the image variable. If the image sign is negated, the two defining binary clauses are merely swapped. Since the backbone contains equality for every one of the five variables, the entire backbone maps into itself.

Therefore a global `B_k^conn -> A_k^conn` transport exists with support `5k`.

## Lower bound support >= k

Consider any signed transport in either direction. If some target block were pointwise fixed, each purely local target clause in that block would remain a clause over only that block's variables. A source backbone clause uses variables from two blocks and cannot be a subset of such an image. Source local clauses from other blocks use disjoint variables. Therefore every local target clause would need its witness from the same source block, producing the forbidden identity local transport on the base sibling pair.

Hence every target block contains at least one moved variable. The target block variable sets are disjoint, so

`|supp(pi)|>=k`.

Thus the required support is finite but unbounded even when both siblings remain connected and both branch ranks grow with `k`.

## Claim ceiling

This refutes only a universal constant-support theorem for signed-permutation safe deletion on this connected critical family. It does not prove that structured unbounded-support discovery is hard, and it says nothing universal about broader quotient/substitution/model-map classes.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
