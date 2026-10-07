# R5 E110 — Exact Branch DP on the Rank-2 Subspace Arrangement

Date: 2026-10-07

Status:
GIVEN_WIDTH_K_SUBSPACE_BRANCH_DECOMPOSITION__EXACT_AVOIDANCE_DP_IN_N_TIMES_2_O_K

Scientific ceiling:

E110 does not yet prove that every Tanner-derived residual arrangement has
small branch-width, nor does it prove that an O(log n)-width decomposition can
be found in polynomial time by the currently cited generic construction.

It proves an exact solver theorem GIVEN a branch decomposition of the active
rank-2 check subspaces.

P_VS_NP = OPEN.

## 1. Why E109 direct sums are not the final decomposition

E109 decomposes the represented normal matroid into connected components.

That is the width-zero/direct-sum case.

A connected component may still admit a recursive low-order separation. To
capture this without splitting one check constraint across leaves, the atomic
objects must be the rank-2 check subspaces themselves.

For every active check c, let

L_c <= W

be the two-dimensional span of its local restriction normals.

Let phi_c in L_c^* be the forbidden character. The residual problem is:

find y in W^* such that

y restricted to L_c is not phi_c

for every active check c.

## 2. Branch decomposition of the subspace arrangement

Take a subcubic branch tree whose leaves are the subspaces L_c.

For a set X of leaves define

W_X = sum_{c in X} L_c,
W_out = sum_{c notin X} L_c,

and the cut boundary

B_X = W_X intersect W_out.

The width of the cut is dim B_X.

Let k be the maximum cut dimension in the decomposition.

This is exactly the branch-width notion for an arrangement of subspaces over
GF(2).

## 3. DP state

At a node/cut X store the set of linear functionals

beta in B_X^*

such that beta extends to some

y_X in W_X^*

with

y_X restricted to L_c != phi_c

for every c in X.

Since dim B_X<=k, there are at most

2^k

possible states.

Nothing else about the internal assignment is required.

## 4. Leaf rule

A leaf contains one 2-dimensional subspace L_c.

There are exactly four linear functionals on L_c.

Discard the one forbidden character phi_c.

Project each of the remaining three functionals onto

B_c = L_c intersect W_out.

The resulting boundary signatures are exactly the leaf DP table.

## 5. Exact join rule

Let a parent have child leaf sets A and B.

Suppose beta_A and beta_B are feasible child states.

The child functionals can be glued iff they agree on

I = W_A intersect W_B.

This intersection lies in both child boundaries because each sibling is part
of the other's outside.

If they agree on I, linear algebra gives a unique functional on

W_A + W_B

extending both child functionals.

No additional consistency condition exists.

## 6. Why the parent boundary value is determined by child states

Let

O = sum of subspaces outside the parent

and let

p in B_parent = (W_A+W_B) intersect O.

Choose any decomposition

p=a+b,
a in W_A,
b in W_B.

Because p is in O,

a=p-b belongs to W_A intersect (W_B+O),

which is contained in the child-A boundary.

Similarly b lies in the child-B boundary.

Therefore

beta_parent(p)=beta_A(a)+beta_B(b).

If another decomposition is chosen, the difference lies in
W_A intersect W_B, where the child states agree, so the value is independent
of the decomposition.

Thus the parent state can be computed using only child boundary states.

## 7. Runtime

Each node has at most 2^k states.

A naive join tests at most 2^(2k) state pairs and performs polynomial-size
GF(2) linear algebra.

Therefore, GIVEN a width-k branch decomposition, the exact residual solver runs
in

n * 2^O(k) * poly(n).

Consequently:

* fixed k is polynomial;
* if a width O(log n) decomposition is supplied, the DP phase is polynomial.

The second statement is deliberately only about the solver phase, not about
constructing the decomposition.

## 8. Constructing branch decompositions: external algorithmic support

Jeong, Kim and Oum,
"Finding Branch-Decompositions of Matroids, Hypergraphs, and More",
SIAM Journal on Discrete Mathematics 35(4), 2021, 2544-2617,
DOI 10.1137/19M1285895,

study exactly branch decompositions of input subspaces over a fixed finite
field and give a fixed-parameter algorithm that constructs a width-at-most-k
decomposition when one exists.

Their result makes E110 constructive for every FIXED k.

E110 does not infer from this alone a polynomial construction theorem when
k=O(log n), because generic FPT dependence on k must be accounted for
explicitly.

## 9. Checker replay

The companion checker first uses a synthetic F2^4 arrangement and compares the
branch DP against direct enumeration of all ambient functionals.

It then replays the E104/E105/E106 residual instance:

* 18 active rank-2 forbidden flats;
* ambient normal rank three;
* a balanced branch tree over the 18 check subspaces;
* branch width at most three;
* DP says an avoiding functional exists;
* direct enumeration independently finds four avoiding states.

Thus the DP preserves the full nonlinear raw8 repair space on the frozen
counterexample.

## 10. Solver architecture after E110

The current exact pipeline is:

1. E105: build the full zero-boundary kernel and one forbidden fiber per check.
2. E106: absorb all rank-0/rank-1 constraints by affine propagation.
3. E107: use defect quantization; NO RAW8 requires at least 12 active flats.
4. E108: quotient by the span of active normals.
5. E109: split direct-sum normal-matroid components.
6. E110: recursively solve any remaining component that has a supplied
   low-width branch decomposition of its 2D check-subspace arrangement.

So the true unresolved hard core must have a Tanner-derived rank-2 subspace
arrangement whose branch-width is large enough that the E110 DP is not already
polynomial under the available decomposition.

## 11. E111 target

The next theorem should attack the WIDTH of the Tanner-derived arrangement,
not raw rank alone.

E111 STRUCTURED SUBSPACE-BRANCHWIDTH ATTACK

For one E109 connected residual block, use:

* every leaf L_c is a binary two-space from one cubic check;
* distinct checks share at most one original variable because of C4-freeness;
* every original variable occurs in exactly three checks;
* defect multiplicity is 0 mod 3;
* forbidden characters arise from TARGET6 witness supports.

Goal:

A. prove a polynomially constructible O(log n)-width decomposition;
B. or show high branch-width forces an avoiding functional/raw8 by expansion
   or Fourier discrepancy;
C. or convert high-width pieces into E78 represented binary-delta modules;
D. or freeze the first exact TARGET6/no-raw8 high-width obstruction.

Scientific status:

E110 = EXACT GIVEN-DECOMPOSITION BRANCH DP.
FIXED BRANCHWIDTH = CONSTRUCTIVE POLYNOMIAL TERMINAL VIA KNOWN FPT DECOMPOSITION.
SUPPLIED O(log n) BRANCHWIDTH = POLYNOMIAL DP TERMINAL.
POLYNOMIAL CONSTRUCTION FOR O(log n) WIDTH = NOT YET PROVED HERE.
HIGH STRUCTURED SUBSPACE BRANCHWIDTH = OPEN.
P_VS_NP = OPEN.
