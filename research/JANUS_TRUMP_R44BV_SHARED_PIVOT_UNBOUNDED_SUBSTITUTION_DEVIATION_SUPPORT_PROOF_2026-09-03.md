# JANUS TRUMP R44BV — shared-pivot family forces unbounded many-to-one substitution deviation support

## Claim ceiling

This theorem refutes only a **universal constant deviation-support bound** for the R44BS/R44BU many-to-one signed literal substitution class on maxdef-critical siblings.

It does not prove that unbounded-support substitution discovery is hard on critical siblings, and it does not imply `P!=NP`.

## 1. Shared-pivot critical family

Use the R44BR shared-pivot family. For `k>=1`, take `k` renamed copies of the R44AS critical parent, keep all five nonpivot variables block-disjoint, and identify all local pivot variables into one shared pivot `x`.

The already proved family theorem gives

`delta*(G_k)=3k-1`,

`delta*(G_k[x=0])=delta*(G_k[x=1])=k`,

and `G_k` is maximum-deficiency-critical.

After fixing the pivot, write

`A_k=A_1 disjoint_union ... disjoint_union A_k`,

`B_k=B_1 disjoint_union ... disjoint_union B_k`,

where every local block is a renamed copy of the base R44AS sibling `A` or `B`.

## 2. Transport class

A signed literal substitution `phi` maps each target variable to one signed source literal, repetitions allowed, with `phi(-v)=-phi(v)`.

It is a valid model transport if every target clause image is either tautological or contains some source clause. Then every source model induces a target model.

Define deviation support

`Dev(phi)={v : phi(v) != +v}`.

## 3. Pointwise-fixed block lemma

Suppose a target block `j` is pointwise fixed by `phi`: every one of its five variables satisfies `phi(v)=v`.

Then every target clause in that block maps to itself. The base sibling clauses are non-tautological, so none of these images is discarded as a tautology.

Source blocks are variable-disjoint. A source clause from block `i!=j` contains variables disjoint from a clause of block `j`, so it cannot be a subset of that unchanged clause. Therefore every witness source clause must belong to source block `j`.

Thus the restriction of `phi` to block `j` is the **identity local transport** between the base siblings in the same direction.

R44BQ exact replay excludes the identity local transport in both sibling directions.

Therefore no valid global substitution may leave an entire target block pointwise fixed.

## 4. Support lower bound

There are `k` pairwise variable-disjoint target blocks. Every block contains at least one variable in `Dev(phi)`. Therefore

`|Dev(phi)| >= k`

for every valid many-to-one substitution transport in either sibling direction.

No injectivity or permutation property was used. The argument applies to arbitrary repetitions in the images.

## 5. Finite upper bound

In the `B_k -> A_k` direction a transport exists: apply the R44BP five-variable signed permutation independently inside every block. A signed permutation is a special case of a many-to-one substitution.

Its deviation support is at most `5k`.

Hence the required deviation support is finite but grows without bound with `k`.

## 6. Consequence for R44BU

For every fixed constant `K`, choose `k>K`. Then this maxdef-critical sibling pair has no valid many-to-one signed literal substitution transport with deviation support at most `K` in either direction.

Therefore

`UNIVERSAL_CONSTANT_K_MANY_TO_ONE_SUBSTITUTION_COVERAGE = FALSE`.

R44BU remains correct as a fixed-parameter polynomial discovery primitive, but no fixed universal `K` can make that primitive complete over all maxdef-critical sibling pairs.

## 7. Remaining exact frontier

The surviving question is now **not** bounded support. It is:

Can unbounded-support substitution transports be discovered in polynomial time on every maxdef-critical both-nonterminal sibling pair, using critical structure in a way that avoids the generic NP-completeness barrier of R44BT?

Or can one prove a critical-family discovery barrier / construct a critical pair admitting no many-to-one literal substitution safe deletion at all?

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
