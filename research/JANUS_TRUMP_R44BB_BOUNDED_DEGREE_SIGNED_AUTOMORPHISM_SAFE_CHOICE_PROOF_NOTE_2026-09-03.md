# JANUS TRUMP R44BB — bounded-degree signed-automorphism safe choice

## 1. Exact theorem

Let `F` be a Boolean CNF and let `g` be a signed variable permutation preserving the clause multiset of `F`. Assume `g` fixes the identity of variable `x` but reverses its polarity: `g(x)=not x` and `g(not x)=x`.

Then

`SAT(F) iff SAT(F[x=0])`.

If a model already has `x=0`, nothing is required. If a model `alpha` has `x=1`, apply `g`. Since `g` is an automorphism of the formula, `g(alpha)` is again a model; because the identity of `x` is fixed while its polarity is reversed, `g(alpha)(x)=0`. The converse implication is immediate from restriction.

Thus the rule gives a deterministic exact safe assignment with no retained second branch.

## 2. Polynomial detection on bounded-occurrence CNF

Fix a constant occurrence bound `D` and clause width at most three. Encode `F` as a colored graph:

- a center vertex for every variable;
- two literal vertices for each variable, paired to the center;
- one clause vertex per clause;
- an edge from a clause vertex to exactly the literal vertices occurring in that clause.

The maximum graph degree is at most `max(D+1,3)`. For a candidate variable `x`, uniquely individualize its center and compare two colored versions of the graph in which the distinguishing colors on literal vertices `x` and `not x` are exchanged. An isomorphism between these two versions is exactly a signed formula automorphism fixing the variable identity and reversing its polarity. By Luks' bounded-valence graph-isomorphism theorem this test is polynomial for every fixed `D`.

Reference: Eugene M. Luks, *Isomorphism of Graphs of Bounded Valence can be Tested in Polynomial Time*, JCSS 25(1), 42–65 (1982), DOI 10.1016/0022-0000(82)90009-5.

## 3. Exact witness beyond R44AW/R44AX/R44AY/R44AZ

The accompanying JSON gives a 15-variable, 34-clause exact-3CNF. Its supports are the lines of the Steiner triple system `PG(3,2)` except `{3,13,14}`. Hence the formula is linear.

Its signed automorphism uses the variable permutation

`1->5, 2->6, 3->3, 4->9, 5->12, 6->15, 7->10, 8->1, 9->4, 10->7, 11->2, 12->8, 13->13, 14->14, 15->11`

and reverses polarity only on variable `3`.

Direct substitution shows that this map permutes the 34 clauses exactly. Hence `x3=0` is an exact safe assignment.

The same witness simultaneously satisfies:

- every variable has `p*q>p+q`, so R44AT has no nonexpanding DP move;
- `sigma=5`, so it is outside R44BA;
- `mu_vd=6<=nM(5)=8`, so the R44AO surplus/min-degree trigger does not fire;
- pure sign-translation group `H(F)` is trivial because every support occurs exactly once;
- there are no width<=2 clauses, so R44AX is silent;
- every support occurs once, so R44AY extracts no nontrivial affine equation;
- linearity makes every one-variable cofactor's generated binary clauses pairwise variable-disjoint, so R44AZ finds no 2-SAT contradiction;
- there is no blocked clause.

The deterministic verifier also enumerates all `2^15` assignments: the formula has 126 models, exactly 63 of which have `x3=0`. The count is supporting finite verification; the theorem authority for safe choice is the automorphism argument above.

## 4. Boundary

This does not give universal progress. If no variable has a polarity-reversing stabilizer, R44BB returns no assignment. In particular, a purely positive CNF cannot have an automorphism taking the positive literal of a fixed variable to its negative literal, which is absent from every clause.

Therefore:

`SIGNED_AUTOMORPHISM_SAFE_CHOICE != UNIVERSAL_SAFE_CHOOSER`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
