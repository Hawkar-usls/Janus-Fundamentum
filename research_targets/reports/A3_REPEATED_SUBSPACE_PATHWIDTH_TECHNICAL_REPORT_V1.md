# Fundamentum repeated-subspace path-width technical report v1

Date: 2026-08-08

## Scope

This report records the progression from the admitted two-class repeated-subspace path-width theorem to the k-class endpoint-compression frontier. It is a project research record, not a claim of external peer review or universal historical priority.

## Two-class result

For two geometric subspaces U,W with multiplicities a,b >= 1, p=dim(U), q=dim(W), r=dim(U∩W), the admitted project theorem gives exact fixed-order and optimal-width formulas. A cut with both U and W represented on both sides has width dim(U+W)=p+q-r. If no such cut exists, only the p,q,r cut values remain. Consequently grouped class-orders attain the optimal piecewise value.

## k-class endpoint state

Let U_1,...,U_k be distinct geometric subspace classes and let sigma be an indexed occurrence order. For cut i define

A_i = {j : some occurrence of class j lies at or before i},
B_i = {j : some occurrence of class j lies after i}.

Then the cut width is

lambda_i = dim((sum_{j in A_i} U_j) ∩ (sum_{j in B_i} U_j)).

For each class j, A_i changes only at its first occurrence and B_i changes only at its last occurrence. Therefore middle occurrences do not change the support-state pair (A_i,B_i). Deleting all middle occurrences preserves the set of support states and hence the maximum width of the layout.

## Multiplicity saturation candidate

For path-width optimization, each multiplicity a_j can be reduced to min(a_j,2): any full layout compresses to such an endpoint layout without changing width; conversely an endpoint layout can be expanded to arbitrary larger multiplicities by inserting middle copies while the class is active, producing no new support state.

If admitted, this yields an exact algorithm parameterized by k, the number of geometric classes: enumerate event orders of at most 2k retained occurrences subject to first-before-last precedence, evaluate the corresponding subset-sum intersections by finite-field linear algebra, and take the minimum maximum width.

## Claim ceiling

- Two-class theorem: ES5 in the stated project formal domain; novelty N3 candidate pending external confirmation.
- k-class endpoint compression: ES2 candidate pending exact-head replay and semantic admission.
- External novelty N4: not established.
- General matroid path-width remains NP-hard in prior literature; this report concerns a restricted repeated-class parameterization and does not contradict that result.
- P vs NP remains OPEN.
