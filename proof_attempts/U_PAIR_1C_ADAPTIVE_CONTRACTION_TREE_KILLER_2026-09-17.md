# U-PAIR-1C — adaptive exact contraction tree falsifier

Date: 2026-09-17

Status:
`PASS_SCOPED_KILLER__UNIVERSAL_POLY_BOND_TREE_REALIZATION_FALSE__SYMBOLIC_HIGH_RANK_ELIMINATION_STILL_OPEN`

## Frozen model

The attacked model is an **exact cycle-free continuation realization** of an
`OR_3 + PAIR` instance.

- local primitives: `PAIR`, `OR_3`;
- composition: exact contraction / existential elimination;
- the algorithm may choose the binary/cubic decomposition tree adaptively;
- intermediate messages are exact finite bond/state tensors;
- cost is at least linear in the explicit bond-state cardinality;
- no approximation is permitted.

The claim under attack is:

> Every `OR_3 + PAIR` instance has a polynomial-time discoverable exact
> decomposition tree whose maximum explicit bond dimension is polynomial in
> input length.

This pass falsifies that claim for explicit bond/state tree realizations. It
does **not** rule out symbolic representations whose semantic rank is large but
whose algebraic description is compact.

## 1. Linear-code continuation rank

Let `C <= GF(2)^(A union B)` be a binary linear code and define its indicator
matrix

`M_C[A|B](a,b) = 1[(a,b) in C]`.

Let

- `C_A = {a : (a,0) in C}`,
- `C_B = {b : (0,b) in C}`.

Define the cut state dimension

`sigma_C(A) = dim(C) - dim(C_A) - dim(C_B)`.

### Lemma 1

Over every field of characteristic zero,

`rank(M_C[A|B]) = 2^(sigma_C(A))`.

The nonzero rows are indexed by `a in proj_A(C)`. Two nonzero rows have the
same support iff their indices differ by an element of `C_A`. Therefore the
number of distinct nonzero rows is

`|proj_A(C)| / |C_A| = 2^(dim(C)-dim(C_B)-dim(C_A)) = 2^(sigma_C(A))`.

Distinct rows are distinct cosets of `C_B`, hence have disjoint support and are
linearly independent. QED.

Thus an exact tensor/tree bond crossing `A|B` needs bond dimension at least
`2^(sigma_C(A))`.

## 2. Tree-optimized state complexity

For a cubic tree decomposition `T` of the code coordinates,

`sigma(C;T) = max_e sigma_C(A_e)`.

The code branchwidth/state complexity is

`sigma(C) = min_T sigma(C;T)`.

Kashyap's minimal-tree-realization framework gives

`sigma(C) <= kappa_tree(C) <= 2 sigma(C)`.

A separate lower bound for every `[n,k,d]` linear code is

`kappa_tree(C) >= c0 * k*d / (n log_2 n)`

for an absolute constant `c0>0`.

Therefore every asymptotically good binary code family (`k>=Rn`, `d>=delta n`)
satisfies

`sigma(C_n) = Omega(n/log n)`.

Consequently every cubic exact tree realization of its full continuation
relation contains a bond of cardinality

`2^(Omega(n/log n))`.

## 3. Sparse adversarial family

Sipser-Spielman expander codes give explicit asymptotically good binary LDPC
families: constant rate, linear minimum distance, and bounded-density local
constraints.

Each bounded-arity parity check can be compiled with constant-factor overhead
to 3-XOR constraints; each 3-XOR is equivalent to four width-3 CNF clauses;
the universal pair-selector compiler then maps the 3-CNF to `OR_3 + PAIR`.

Hence there is an `OR_3 + PAIR` family `F_n` with encoded length `L=Theta(n)`
whose projected continuation relation on the original code coordinates is the
expander code. Any exact tree realization of that full continuation relation
therefore has

`max bond dimension >= 2^(Omega(L/log L))`.

So adaptive tree choice does not guarantee polynomial explicit bond dimension.

## 4. Frozen verdict

`FAIL_UNIVERSAL_POLYNOMIAL_EXPLICIT_BOND_TREE_REALIZATION`

The falsified statement is specifically

`for every F in OR_3+PAIR, exists tree T_F with max_e bond_dim(F,T_F) <= poly(|F|)`

for exact explicit continuation-state/tensor bond dimensions in a cycle-free
full-relation realization.

## 5. Claim ceiling

This is **not** a proof that SAT is not in P and not a lower bound against every
exact contraction algorithm.

It does not exclude symbolic high-rank representations. Linear codes themselves
show the escape: Gaussian elimination stores a compact system of linear
equations despite exponentially large explicit continuation rank.

The surviving target is:

`U-PAIR-1D__SYMBOLIC_HIGH_RANK_MIXED_SEMANTIC_ELIMINATION`

A successful representation must support `PAIR + OR_3`, tolerate semantic ranks
as large as `2^(Omega(n/log n))`, and keep representation size plus exact
composition/elimination/reconstruction/verification polynomial.

Scientific firewall:

`GENERAL_SAT_IN_P = NOT_PROVED`
`P_VS_NP = OPEN`
