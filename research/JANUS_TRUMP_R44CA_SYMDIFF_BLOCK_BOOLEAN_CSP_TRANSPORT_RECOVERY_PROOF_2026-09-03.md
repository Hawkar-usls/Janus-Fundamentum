# JANUS TRUMP R44CA — symmetric-difference block recovery with Boolean compatibility CSP

## Claim ceiling

R44CA is a polynomial safe-delete theorem for a fixed structural class. It does not solve arbitrary critical sibling merge and does not imply `P=NP`.

## 1. From local ambiguity two to 2-SAT

Assume sibling CNFs `A,B` share the same active variables. Compute `D=A triangle B`, form its variable co-occurrence graph, and recover connected components `V_1,...,V_m` of fixed size at most `b`.

For one transport direction, enumerate all signed permutations internal to every block and retain those satisfying every target clause contained wholly in that block. Assume each surviving local candidate set has size at most two.

Every target clause spanning blocks is required to touch exactly two blocks. For every interacting pair `i,j`, exactly compute the allowed pairs

`R_ij subseteq C_i x C_j`

by applying the two local candidates and checking the target cross-clauses against actual source clauses.

Encode candidate choice of each two-state block by Boolean variable `X_i`. Each forbidden pair `(a,b)` is exactly the Boolean constraint

`not(X_i=a and X_j=b)`,

which is the 2-CNF clause

`(X_i != a) OR (X_j != b)`.

One-candidate blocks produce unit clauses. Therefore the entire compatibility problem is 2-SAT, regardless of the treewidth of the block interaction graph.

SCC solves the compatibility instance in polynomial time. A satisfying assignment selects one local signed permutation per block. Since blocks are disjoint, their union is a global signed permutation. It receives authority only after one final exact global transport verification.

Failure means `NO_RULE_APPLICABLE`, never UNSAT.

## 2. Application to the grid orbit family

Use the R44BZ grid family with `m=r^2` copies of the R44AS sibling block and the same 12-clause orbit connector on every grid edge.

As in R44BZ path recovery, common connector clauses and common local clauses cancel in `A triangle B`. Each block contributes exactly the four pivot-dependent binary clauses. Their variable graph is connected on all five local variables. Thus `D` recovers exactly the `r^2` five-variable blocks.

No construction labels and no global generator are passed to the recovery algorithm.

## 3. Exact local ambiguity

Complete enumeration of all

`5!*2^5=3840`

signed maps inside one block gives exactly two valid local `B -> A` transports.

Let them be `p0,p1`. This is not an assumption; it is replayed by the verifier from the actual local sibling clauses.

## 4. Exact connector relation

Take any grid edge and its complete 12-clause orbit connector. Check the four candidate pairs

`(p0,p0), (p0,p1), (p1,p0), (p1,p1)`.

Exact replay gives one allowed pair only: the pair in which both endpoints use the R44BP generator. Thus the connector relation is a Boolean binary constraint and globally forces compatible local phase choices.

Even if the interaction graph were an arbitrary graph rather than a grid, the resulting Boolean binary CSP would still be 2-SAT.

## 5. Why unbounded grid treewidth no longer blocks recovery

The grid family has unbounded primal treewidth by the already proved grid-minor argument. Nevertheless R44CA does not run a SAT dynamic program on the primal graph. It runs a 2-SAT compatibility problem on two local transport states per recovered block.

Hence

`UNBOUNDED_INTERACTION_TREEWIDTH != HARD_TRANSPORT_DISCOVERY`

for this structural class.

## 6. Exact safe deletion and rank

The grid-family theorem gives

`delta*(parent)=27r^2-24r-1`,

`delta*(A)=delta*(B)=25r^2-24r`.

The recovered `B -> A` transport proves

`SAT(B) => SAT(A)`.

Therefore `B` can be deleted from the sibling OR and the retained rank drops by

`2r^2-1`.

The child rank is `Theta(r^2)` while encoded size is `Theta(r^2)`, so the R44BC logarithmic maxdef terminal does not explain this reduction for large `r`. The family also has unbounded treewidth. Thus this is a genuinely stronger positive safe-delete primitive than the path/treewidth escape.

## 7. Next obstruction requirements

A stronger candidate obstruction must defeat at least one of:

1. bounded-size components in `A triangle B`;
2. at-most-two valid local transport states per component;
3. pairwise-only compatibility constraints;
4. existence of a block-preserving exact transport.

In particular, merely increasing support or interaction treewidth is no longer enough.

`DOMAIN_SIZE_2_IS_A_REAL_RESTRICTION`

`R44CA_GRID_SUCCESS != UNIVERSAL_CRITICAL_SIBLING_COVERAGE`

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
