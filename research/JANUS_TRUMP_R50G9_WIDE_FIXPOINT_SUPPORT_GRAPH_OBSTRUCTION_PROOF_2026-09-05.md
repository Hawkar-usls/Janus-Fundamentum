# JANUS TRUMP R50G9 — Wide Fixpoint Support-Graph Obstruction

## Scope

R50G8 reduced any same-pivot failure after an immediate BVE W4 escape to a final nonterminal certified normalization fixpoint containing at least one clause of width >4 and carrying replayable DP/BVE ancestry. R50G9 does not add a solver rule. It derives exact combinatorial obligations that every such final fixpoint must satisfy under the already frozen R33 definitions.

Let H be an R33 fixed point. For a variable v define:

- p_v = number of clauses containing +v;
- n_v = number of clauses containing -v;
- m_v = p_v+n_v;
- q_v = number of unique non-tautological cross-polarity resolvents on v;
- L_parent(v) = total literal count in the p_v+n_v parent clauses removed by exact DP;
- L_res(v) = total literal count in the q_v unique non-tautological resolvents.

The frozen R33 measure is (C,L,V), lexicographically, and frozen BVE accepts v exactly when q_v <= m_v and the exact transformed formula has smaller (C,L,V).

## S1 — BVE-fixed variables are bipolar

At an R33 fixed point PURE_LITERAL_AUTARKY is not applicable. Therefore every variable that occurs in H occurs with both polarities:

p_v >= 1 and n_v >= 1.

## S2 — resolvent-pressure lemma

Assume H is BVE-fixed on v. If q_v < m_v, exact DP strictly decreases the clause count C, so frozen BVE would accept v. Contradiction.

If q_v = m_v and L_res(v) < L_parent(v), clause count is equal and literal count strictly decreases, so BVE accepts. Contradiction.

If q_v = m_v and L_res(v) = L_parent(v), C and L are equal but exact DP eliminates v and introduces no fresh variable, hence V strictly decreases. BVE again accepts. Contradiction.

Therefore every BVE-fixed variable satisfies

q_v > m_v

or

q_v = m_v and L_res(v) > L_parent(v).

In particular:

q_v >= p_v+n_v.                                            (S2)

This conclusion uses only the frozen BVE definition and frozen lexicographic measure.

## S3 — polarity-degree lower bound

Always q_v <= p_v n_v because every unique non-tautological resolvent comes from at least one positive-negative parent pair. Combining with S2:

p_v n_v >= p_v+n_v.

Equivalently:

(p_v-1)(n_v-1) >= 1.

Hence every variable in a BVE-fixed R33 fixed point obeys

p_v >= 2 and n_v >= 2.                                     (S3)

Thus any literal l in a surviving wide clause C requires, besides C itself, at least one additional same-polarity parent and at least two opposite-polarity parents for abs(l).

## S4 — BCE support witness

R50G8 proved from frozen BCE that if C survives in an R33 fixed point, then for every l in C there exists a clause D_l containing -l such that the resolvent of C and D_l on l is non-tautological. Witnesses for two different literals of C are distinct: if one clause contained both -l_i and -l_j, resolving against C on either literal would leave the complementary pair l_j,-l_j or l_i,-l_i.

Therefore a width-k surviving clause has at least k distinct non-blocking support clauses.

## S5 — exact balanced 2x2 pressure

Suppose p_v=n_v=2. Then there are exactly four positive-negative parent pairs. S2 gives q_v >= 4, while q_v <=4, so q_v=4. Consequently every one of the four cross-polarity parent pairs must be non-tautological and the four resulting resolvents must be pairwise distinct.

This is stronger than BCE support: no cross pair on v is allowed to disappear as a tautology or duplicate.

## S6 — width-k consequence in the balanced case

Let C contain literals l_1,...,l_k and assume every variable abs(l_i) has balanced polarity degree 2x2 in H. For each i, C is one parent on the polarity of l_i. By S5, both opposite-polarity clauses for abs(l_i) must form non-tautological resolvents with C.

An opposite-polarity clause that is non-tautological with C on l_i cannot contain -l_j for any j != i. Hence it cannot simultaneously serve as one of the two opposite non-tautological supports for another literal l_j of C. Therefore the 2k opposite supports are all distinct.

For width 5 this already forces at least ten distinct opposite-support clauses around C, in addition to C and the required same-polarity co-parents.

## What R50G9 closes and what it does not

S1-S6 are exact source-definition consequences. They materially strengthen the obstruction: a final wide fixpoint is not merely a wide clause with one BCE witness per literal. It must carry enough cross-polarity incidence to defeat exact BVE on every remaining variable.

The remaining theorem is still nontrivial:

NO_W4_DP_BVE_ANCESTRY_CAN_END_IN_A_NONTERMINAL_R33_AFFINE_RUP_FIXED_SUPPORT_GRAPH_SATISFYING_ALL_BVE_PRESSURE_CONSTRAINTS.

R50G9 must not infer this universal theorem from finite replay. Either a later symbolic counting/ancestry argument proves the incompatibility, or an exact support-graph countermodel refutes it.

If the incompatibility is proved for the relevant reachable ancestry domain, then same-pivot R47J safety follows for every immediate BVE escape and the escape branch of a minimal U_mu OPEN state is eliminated. Only then may IMMEDIATE_BVE_CASE_ELIMINATED switch to true.
