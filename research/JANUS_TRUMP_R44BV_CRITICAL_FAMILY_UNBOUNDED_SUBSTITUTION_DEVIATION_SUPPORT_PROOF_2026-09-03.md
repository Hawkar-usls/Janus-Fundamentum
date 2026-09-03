# JANUS TRUMP R44BV — critical shared-pivot family forces unbounded many-to-one substitution deviation support

## Claim ceiling

This theorem refutes only a universal **constant deviation-support bound** for the R44BS/R44BU many-to-one signed literal substitution class on maxdef-critical siblings.

It does not prove that unbounded-support substitution discovery is hard on critical siblings, and it does not imply `P!=NP`.

## Shared-pivot critical family

For `k>=1`, take `k` renamed copies of the R44AS maxdef-critical parent, keep all five nonpivot variables block-disjoint, and identify all local pivot variables into one shared pivot `x`. Call the parent `G_k`.

The already sealed shared-pivot theorem gives

`delta*(G_k)=3k-1`,

`delta*(G_k[x=0])=delta*(G_k[x=1])=k`,

and `G_k` is maximum-deficiency-critical.

After fixing the pivot, the two siblings are variable-disjoint unions of `k` renamed copies of the base sibling formulas `A` and `B`.

## Many-to-one transport class

A signed literal substitution `phi` maps each target variable to one signed source literal, repetitions allowed, with `phi(-v)=-phi(v)`.

It is a valid model transport if every target clause image is either tautological or contains a source clause. Then every source model induces a target model.

Define deviation support

`Dev(phi)={v : phi(v) != +v}`.

## Pointwise-fixed block lemma

Assume one target block `j` is pointwise fixed by `phi`. Then every target clause in that block maps to itself and remains non-tautological.

Source blocks are variable-disjoint. A source clause belonging to a different block contains variables disjoint from the unchanged target clause, so it cannot be a subset of that clause. Therefore every source witness clause must lie in source block `j`.

Thus the restriction of `phi` to block `j` is the identity local transport between the base R44AS siblings in the same direction.

R44BQ exact replay excludes identity local transport in both directions.

Therefore every target block contains at least one deviating variable.

## Support theorem

The `k` target blocks are pairwise variable-disjoint, so

`|Dev(phi)| >= k`

for every valid many-to-one substitution transport in either sibling direction.

No injectivity or permutation assumption is used. Repetitions in substitution images are fully allowed.

A transport nevertheless exists in the `B_k -> A_k` direction: apply the R44BP signed permutation independently in every block. Since a signed permutation is a special case of literal substitution, this gives deviation support at most `5k`.

Hence required substitution support is finite but unbounded.

For every fixed constant `K`, choose `k>K`. Then this maxdef-critical both-nonterminal sibling pair admits no R44BS-style substitution safe-delete certificate with deviation support at most `K` in either direction.

Therefore

`UNIVERSAL_CONSTANT_K_MANY_TO_ONE_SUBSTITUTION_COVERAGE = FALSE`.

## Remaining exact frontier

R44BU remains a valid polynomial local primitive for fixed `K`, but no universal constant `K` can make it complete over all critical sibling pairs.

The surviving question is now:

Can **unbounded-support** literal substitutions be discovered in polynomial time on every maxdef-critical both-nonterminal sibling pair by exploiting critical structure, despite the generic NP-completeness theorem R44BT?

Or can one prove a critical-family discovery-hardness barrier / construct a both-nonterminal critical pair admitting no many-to-one literal substitution safe deletion at all?

`UNBOUNDED_SUPPORT != NP_HARD_CRITICAL_DISCOVERY`

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
